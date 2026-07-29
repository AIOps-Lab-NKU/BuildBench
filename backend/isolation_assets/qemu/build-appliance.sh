#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat >&2 <<'EOF'
usage: build-appliance.sh OUTPUT_DIR WEBSITE_ROOT STARTER_KIT_ROOT VALIDATOR_ROOT

Builds a reusable Ubuntu QEMU/KVM appliance. The host needs only Docker.
The resulting base.qcow2 is immutable; every evaluation uses a disposable
overlay.
EOF
}

[[ $# -eq 4 ]] || { usage; exit 2; }
OUTPUT_DIR="$(realpath -m "$1")"
WEBSITE_ROOT="$(realpath "$2")"
STARTER_KIT_ROOT="$(realpath "$3")"
VALIDATOR_ROOT="$(realpath "$4")"
ASSET_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LAUNCHER_IMAGE="${BB_QEMU_LAUNCHER_IMAGE:-buildbench-qemu-launcher:v0}"
CLOUD_IMAGE_URL="${BB_QEMU_CLOUD_IMAGE_URL:-https://cloud-images.ubuntu.com/jammy/current/jammy-server-cloudimg-amd64.img}"
AGENT_IMAGE="${BB_AGENT_IMAGE:-python:3.11.9-slim-bookworm}"
VALIDATOR_IMAGE="${BB_VALIDATOR_IMAGE:-buildbench-validator-runtime:v0}"
CLEANUP_IMAGE="${BB_CLEANUP_IMAGE:-ubuntu:24.04}"
OBS_BASE_IMAGE="${BB_OBS_BASE_IMAGE:-registry.opensuse.org/opensuse/tumbleweed:latest}"

mkdir -p "$OUTPUT_DIR"
WORK_DIR="$OUTPUT_DIR/.build"
rm -rf "$WORK_DIR"
mkdir -p "$WORK_DIR/provision"

docker build -t "$LAUNCHER_IMAGE" "$ASSET_ROOT"

if [[ ! -f "$OUTPUT_DIR/ubuntu-jammy-cloudimg-amd64.img" ]]; then
  curl -fL --retry 3 "$CLOUD_IMAGE_URL" \
    -o "$OUTPUT_DIR/ubuntu-jammy-cloudimg-amd64.img"
fi
cp --reflink=auto "$OUTPUT_DIR/ubuntu-jammy-cloudimg-amd64.img" \
  "$WORK_DIR/base.qcow2"

docker run --rm \
  -v "$WORK_DIR:/work" \
  --entrypoint qemu-img \
  "$LAUNCHER_IMAGE" \
  resize /work/base.qcow2 40G

mkdir -p "$WORK_DIR/provision/website" \
  "$WORK_DIR/provision/starter-kit" \
  "$WORK_DIR/provision/docker-validator"
cp -a "$WEBSITE_ROOT/backend" "$WORK_DIR/provision/website/"
cp -a "$STARTER_KIT_ROOT/runner" "$WORK_DIR/provision/starter-kit/"
validator_container="$(docker create "$VALIDATOR_IMAGE")"
trap 'docker rm -f "$validator_container" >/dev/null 2>&1 || true' EXIT
rm -rf "$WORK_DIR/provision/docker-validator"
mkdir -p "$WORK_DIR/provision/docker-validator"
docker cp \
  "$validator_container:/opt/docker-validator/." \
  "$WORK_DIR/provision/docker-validator/"
docker rm "$validator_container" >/dev/null
trap - EXIT
cp "$ASSET_ROOT/guest/run-job.sh" \
  "$WORK_DIR/provision/buildbench-run-isolated-job"
cp "$ASSET_ROOT/guest/buildbench-isolated-worker.service" \
  "$WORK_DIR/provision/"
chmod -R a+rX \
  "$WORK_DIR/provision/website" \
  "$WORK_DIR/provision/starter-kit" \
  "$WORK_DIR/provision/docker-validator"

OBS_BUILD_PACKAGE="$VALIDATOR_ROOT/vendor/obs-build_20260623-1_all.deb"
OBS_BUILD_PATCH="$VALIDATOR_ROOT/tools/patch-obs-build-deb.py"
[[ -f "$OBS_BUILD_PACKAGE" ]] || {
  echo "pinned obs-build package is missing: $OBS_BUILD_PACKAGE" >&2
  exit 1
}
[[ -f "$OBS_BUILD_PATCH" ]] || {
  echo "obs-build compatibility patch is missing: $OBS_BUILD_PATCH" >&2
  exit 1
}
cp "$OBS_BUILD_PACKAGE" "$WORK_DIR/provision/obs-build.deb"
cp "$OBS_BUILD_PATCH" "$WORK_DIR/provision/patch-obs-build-deb.py"
obs_build_sha256="$(sha256sum "$OBS_BUILD_PACKAGE" | awk '{print $1}')"
cat >"$WORK_DIR/provision/install-validator-runtime" <<EOF
#!/bin/sh
set -eu
printf '%s  %s\n' \
  '$obs_build_sha256' \
  /mnt/bb-provision/obs-build.deb \
  | sha256sum -c -
dpkg -i /mnt/bb-provision/obs-build.deb
python3 /mnt/bb-provision/patch-obs-build-deb.py
test -x /usr/bin/build
EOF
chmod 0555 "$WORK_DIR/provision/install-validator-runtime"

for image in "$AGENT_IMAGE" "$VALIDATOR_IMAGE" "$CLEANUP_IMAGE" "$OBS_BASE_IMAGE"; do
  docker image inspect "$image" >/dev/null
done
agent_host_digest="$(
  docker image inspect "$AGENT_IMAGE" --format '{{.Id}}'
)"
cat >"$WORK_DIR/provision/record-managed-agent-image" <<EOF
#!/bin/sh
set -eu
printf '%s\n' '$agent_host_digest' \
  >/etc/buildbench-managed-agent-host-digest
docker image inspect '$AGENT_IMAGE' --format '{{.Id}}' \
  >/etc/buildbench-managed-agent-local-digest
chmod 0444 \
  /etc/buildbench-managed-agent-host-digest \
  /etc/buildbench-managed-agent-local-digest
EOF
chmod 0555 "$WORK_DIR/provision/record-managed-agent-image"
docker save \
  "$AGENT_IMAGE" "$VALIDATOR_IMAGE" "$CLEANUP_IMAGE" "$OBS_BASE_IMAGE" \
  -o "$WORK_DIR/provision/images.tar"

cat >"$WORK_DIR/user-data" <<'EOF'
#cloud-config
package_update: true
packages:
  - binfmt-support
  - docker.io
  - dpkg
  - findutils
  - git
  - libarchive-tools
  - python3
  - qemu-user-static
  - rpm
  - xz-utils
  - zstd
write_files:
  - path: /etc/buildbench-appliance-version
    permissions: '0444'
    content: |
      schema_version=0.1
      isolation_provider=qemu_kvm
runcmd:
  - [mkdir, -p, /mnt/bb-provision]
  - [mount, -t, 9p, -o, "trans=virtio,version=9p2000.L,ro,nodev,nosuid", bb-provision, /mnt/bb-provision]
  - [mkdir, -p, /opt/buildbench]
  - [cp, -a, /mnt/bb-provision/website, /opt/buildbench/website]
  - [cp, -a, /mnt/bb-provision/starter-kit, /opt/buildbench/starter-kit]
  - [cp, -a, /mnt/bb-provision/docker-validator, /opt/buildbench/docker-validator]
  - [cp, /mnt/bb-provision/buildbench-run-isolated-job, /usr/local/bin/buildbench-run-isolated-job]
  - [chmod, '0755', /usr/local/bin/buildbench-run-isolated-job]
  - [cp, /mnt/bb-provision/buildbench-isolated-worker.service, /etc/systemd/system/buildbench-isolated-worker.service]
  - [docker, load, -i, /mnt/bb-provision/images.tar]
  - [/mnt/bb-provision/install-validator-runtime]
  - [/mnt/bb-provision/record-managed-agent-image]
  - [usermod, -aG, docker, ubuntu]
  - [systemctl, enable, docker.service]
  - [systemctl, enable, buildbench-isolated-worker.service]
  - [umount, /mnt/bb-provision]
  - [touch, /var/lib/buildbench-appliance-ready]
power_state:
  mode: poweroff
  timeout: 30
  condition: true
EOF

cat >"$WORK_DIR/meta-data" <<'EOF'
instance-id: buildbench-appliance-builder-v0
local-hostname: buildbench-appliance
EOF

docker run --rm \
  -v "$WORK_DIR:/work" \
  --entrypoint cloud-localds \
  "$LAUNCHER_IMAGE" \
  /work/seed.img /work/user-data /work/meta-data

docker run --rm \
  --device /dev/kvm:/dev/kvm:rwm \
  -v "$WORK_DIR:/work" \
  -v "$WORK_DIR/provision:/provision:ro" \
  --entrypoint qemu-system-x86_64 \
  "$LAUNCHER_IMAGE" \
  -enable-kvm \
  -machine q35,accel=kvm \
  -cpu host \
  -smp 4 \
  -m 8192 \
  -display none \
  -serial stdio \
  -no-reboot \
  -drive if=virtio,format=qcow2,file=/work/base.qcow2,cache=none \
  -drive if=virtio,format=raw,file=/work/seed.img,readonly=on \
  -fsdev local,id=provision,path=/provision,security_model=none,readonly=on \
  -device virtio-9p-pci,fsdev=provision,mount_tag=bb-provision \
  -netdev user,id=net0 \
  -device virtio-net-pci,netdev=net0

mv "$WORK_DIR/base.qcow2" "$OUTPUT_DIR/base.qcow2"
sha256sum "$OUTPUT_DIR/base.qcow2" >"$OUTPUT_DIR/base.qcow2.sha256"
docker image inspect "$LAUNCHER_IMAGE" \
  --format '{{.Id}}' \
  >"$OUTPUT_DIR/launcher-image.txt" || true
rm -rf "$WORK_DIR"

printf 'Appliance: %s\n' "$OUTPUT_DIR/base.qcow2"
printf 'Digest:    %s\n' "$(cat "$OUTPUT_DIR/base.qcow2.sha256")"

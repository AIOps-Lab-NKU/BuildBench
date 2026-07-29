#!/usr/bin/env bash
set -euo pipefail

install -d -m 0755 /mnt/bb-input /mnt/bb-output
mount -t 9p -o trans=virtio,version=9p2000.L,ro,nodev,nosuid bb-input /mnt/bb-input
mount -t 9p -o trans=virtio,version=9p2000.L,nodev,nosuid bb-output /mnt/bb-output

cd /opt/buildbench/website
export PYTHONDONTWRITEBYTECODE=1
export BB_GATEWAY_SOCKET_ROOT=/tmp
worker_console=/tmp/buildbench-worker-console.log
: >"$worker_console"

set +e
# The organizer Worker is root only inside this disposable VM so it can run
# guest-local chroot validation. DockerAgentExecutor still launches the
# untrusted Agent as explicit UID/GID 1000 with no capabilities, network, or
# Docker socket.
python3 -m backend.isolated_case_worker \
  --input /mnt/bb-input \
  --output /mnt/bb-output \
  --starter-kit /opt/buildbench/starter-kit \
  --validator-command "/opt/buildbench/docker-validator/bin/build-case" \
  >"$worker_console" 2>&1
status=$?
set -e
cp "$worker_console" /mnt/bb-output/worker-console.log

sync
umount /mnt/bb-output || true
umount /mnt/bb-input || true
exit "$status"

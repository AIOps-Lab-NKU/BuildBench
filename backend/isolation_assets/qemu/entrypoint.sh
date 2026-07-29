#!/usr/bin/env bash
set -euo pipefail

CPUS=4
MEMORY_MB=8192
while [[ $# -gt 0 ]]; do
  case "$1" in
    --cpus) CPUS="$2"; shift 2 ;;
    --memory-mb) MEMORY_MB="$2"; shift 2 ;;
    *) echo "unknown argument: $1" >&2; exit 2 ;;
  esac
done

test -r /appliance/base.qcow2
test -r /job/input/job.json
test -d /job/output
test -d /job/run
test -r /dev/kvm
test -w /dev/kvm

OVERLAY="/job/run/worker-${RANDOM}-${RANDOM}.qcow2"
cleanup() {
  rm -f -- "$OVERLAY"
}
trap cleanup EXIT INT TERM

qemu-img create \
  -q \
  -f qcow2 \
  -F qcow2 \
  -b /appliance/base.qcow2 \
  "$OVERLAY"

qemu-system-x86_64 \
  -enable-kvm \
  -machine q35,accel=kvm \
  -cpu host \
  -smp "$CPUS" \
  -m "$MEMORY_MB" \
  -display none \
  -serial stdio \
  -no-reboot \
  -nodefaults \
  -device virtio-rng-pci \
  -drive "if=virtio,format=qcow2,file=$OVERLAY,cache=none,discard=unmap" \
  -fsdev local,id=jobinput,path=/job/input,security_model=none,readonly=on \
  -device virtio-9p-pci,fsdev=jobinput,mount_tag=bb-input \
  -fsdev local,id=joboutput,path=/job/output,security_model=none \
  -device virtio-9p-pci,fsdev=joboutput,mount_tag=bb-output \
  -net none


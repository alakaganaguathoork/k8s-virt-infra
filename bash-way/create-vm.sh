#!/bin/bash

###
## This script automates the creation of cloud-ish networking

set -euo pipefail

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
DISKS_DIR="disks"
VM_DISK="Arch-Linux-x86_64-basic.qcow2"
VM_RAMSIZE="2048"
VM_CORES="2"
VM_DISKSIZE="10"
VM_NETNAT="network=default" # nat network
VM_NETBRIDGE="bridge=virbr1" # bridge network

create_images_dir() {
  if [[ -d "$DISKS_DIR" ]]; then
    echo "$DISKS_DIR directory already exists.";
  else
    echo "Creating $DISKS_DIR..."
    mkdir -p $DISKS_DIR;
  fi
}

# Generate a unique MAC-address
generate_mac() {
  mac=$(echo "52:54:00:$(openssl rand -hex 3 | sed 's/\(..\)/\1:/g; s/:$//')")
  echo "$mac"
}

create_golden_disk() {
  local image="$1"

  create_images_dir
  echo "Copying golden image to $image..."
  cp $VM_DISK "$image"

  # A required step in order to retrieve a unique IP address from DHCP based on `machine-id` (pov: `machine-id` duplicates on the golden image copying)
  echo "Cleaning an image..."
  sudo virt-sysprep -a "$image" \
    --operations machine-id,net-hwaddr,udev-persistent-net,ssh-hostkeys,logfiles,tmp-files
}

create_one_vm() {
  local count=$1
  local name=$2
  local vm_name="$name-$count"
  local image="$DISKS_DIR/$vm_name.qcow2"
  local mac

  mac=$(generate_mac)
  create_golden_disk "$image"

  virt-install \
    --name "$vm_name" \
    --disk path="$image" \
    --ram "$VM_RAMSIZE" \
    --vcpus "$VM_CORES" \
    --network "$VM_NETNAT",model=virtio,mac="$mac" \
    --os-variant archlinux \
    --import \
    --noautoconsole
}

create_one_vm 1 arch-test
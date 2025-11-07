#!/usr/bin/env bash

set -o errexit
set -o pipefail
IFS=$'\n\t'

# ────────────────────────────────────────────────────────────────────────────────
# This script automates cloud-ish network creation using libvirt.
# Usage: create-libvirt-network.sh --action <start|destroy> 
# ────────────────────────────────────────────────────────────────────────────────

ACTION=""
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
NETWORKS=("vpc-public" "private-subnet-a" "private-subnet-b")

# ────────────────────────────────────────────────────────────────────────────────
# Helpers
# ────────────────────────────────────────────────────────────────────────────────

_color() {
  # prints in bold magenta
  printf "\e[1;35m%b\e[0m" "$1\n"
}

_italic() {
  printf "\e[3m%b\e[0m" "$1"
}

_die() {
  echo >&2 "❌ ${1}"
  exit "${2:-1}"
}

_create_dir() {
  if [[ -d "$1" ]]; then
    _color "$1 directory already exists.";
  else
    _color "Creating $1..."
    mkdir -p "$1";
  fi
}

_parse_yaml() {
  while read -r line; do
    if [[ $line =~ name: ]]; then
      NAMES+=("$(echo "$line" | sed 's/.*name: *//;s/"//g')") # sed used to get rid of quotes
    elif [[ $line =~ count: ]]; then
      COUNT+=("$(echo "$line" | awk '{print $2}')") # awk used as it simplier to take a number
    fi
  done < "$FILE"
}

# ────────────────────────────────────────────────────────────────────────────────
# Parse args
# ────────────────────────────────────────────────────────────────────────────────

_parse_args() {
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --action|-a)
        ACTION="${2:-}"; shift 2 
        ;;
      -h|--help)
        _color "Usage: $(_italic "$0 --action <start|destroy>")"
        exit 0 
        ;;
      *)
        _die "Unknown argument: $1"
        ;;
    esac
  done

  # validate required args
  if [[ -z "$ACTION" ]]; then
    _die "$(_color "Missing required argument: --action")"
  fi
}

# ────────────────────────────────────────────────────────────────────────────────
# Functions
# ────────────────────────────────────────────────────────────────────────────────

create_config_xml() {
  local name=$1
  local idx=$2
  local config_folder="$SCRIPT_DIR/configs"
  local file_name="$config_folder/$name.xml"

  _create_dir "$config_folder"

  tee "$file_name" <<EOF
<network>
  <name>$name</name>
  <forward mode='nat'/>
  <bridge name='virbr10$idx' stp='on' delay='0'/>
  <ip address='10.10.$idx.1' netmask='255.255.255.0'>
    <dhcp>
      <range start='10.10.$idx.100' end='10.10.$idx.254'/>
    </dhcp>
  </ip>
</network>
EOF
  
  _color "$name network file stored in $file_name." 
}

start() {
  for i in "${!NETWORKS[@]}"; do
    local name="${NETWORKS[$i]}"
    local file_name="$SCRIPT_DIR/configs/$name.xml"

    create_config_xml "$name" "$i"

    if ! virsh net-info "$name" &>/dev/null; then
      _color "Defining $name network..."
      virsh net-define "$file_name"
    else
      _color "$name network already defined."
    fi

    virsh net-autostart "$name"

    if ! virsh net-info "$name" 2>/dev/null | grep -q '^Active:\s\+yes$'; then
      virsh net-start "$name"
      _color "$name network started."
    else
      _color "$name network already exists."
    fi
  done
}

destroy() {
  for i in "${!NETWORKS[@]}"; do
    local name="${NETWORKS[$i]}"

    if virsh net-info "$name" &>/dev/null; then
      _color "Destroying $name network..."
      virsh net-destroy "$name"
      virsh net-undefine "$name"
    else
      _color "Nothing to destroy."
    fi
  done
}

# ────────────────────────────────────────────────────────────────────────────────
# Main logic
# ────────────────────────────────────────────────────────────────────────────────

_parse_args "$@"

_color "Performing $ACTION..."

case "$ACTION" in
  start)
    start
    ;;
  
  destroy)
    destroy
    ;;
  
  *)
    _die "$(_color Unknown action: "$ACTION")"
    ;;
esac

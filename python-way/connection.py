from typing import Optional, Type
from pathlib import Path

import libvirt

from helpers.parser import _load_values, render

class Connection:

    def __init__(
            self, 
            hypervisor, 
            source_path, 
            output_path, 
            values_path
        ):
        self.connection = None
        self.uri = self._resolve_uri(hypervisor)
        self.source_path = source_path
        self.output_path = output_path
        self.values_path = values_path

    
    def __enter__(self) -> "Connection":
        self._open()
        return self

    def __exit__(
            self, 
            exc_type: Optional[Type[BaseException]], 
            exc: Optional[BaseException], 
            tb
        ) -> bool:
        self._close()
        return False
    
    def _open(self) -> libvirt.virConnect:
        if self.connection: return

        try:
            self.connection = libvirt.open(self.uri)
            
            if self.connection is None:
                raise RuntimeError(f"libvirt.open returned None for {self.uri}")
            return self.connection
        except libvirt.libvirtError as e:
            raise RuntimeError(f"Failed to open {self.uri}: {e}") from e

    def _close(self) -> None:
        if self.connection:
            try:
                self.connection.close()
            finally:
                self.connection = None
        print(f"Connection has been closed.")

    @staticmethod
    def _resolve_uri(hv: str)-> str:
        hv = hv.lower()

        if hv in ("qemu", "kvm"):
            return "qemu:///system"
        raise ValueError(f"Unsupported hypervisor: {hv}")
    
    def create_infra(self) -> None:
        values = Path(self.values_path)
        if not values.is_file():
            raise FileNotFoundError(f"Values file not found: {values}")
        for type in _load_values(values):
            print(f"Starting {type} using {values} values...")
            self.start(type)

    def start(self, type) -> None:
        match type:
            case "networks":
                print(f"Starting networks...")
                self.start_networks()
            # case "vms":
            # case "lb":

    def start_networks(self) -> None:
        networks = _load_values(self.values_path, "networks")
        template_name = "network.xml.jinja2"

        existing_active = set(self.connection.listNetworks())
        existing_defined = set(self.connection.listDefinedNetworks())

        render(
            "networks",
            self.source_path,
            template_name, 
            self.values_path, 
            self.output_path)

        for network in networks:
            name = network.get("name")
            print(f"Generating {network} network...")
            if name in existing_active or name in existing_defined:
                net = self.connection.networkLookupByName(name)
                if net.isActive() != 1:
                    net.create()
                    print(f"Existing {name} network was started.")
                if not net.autostart():
                    net.setAutostart(1)
                continue
            
            xml = Path(f"{self.output_path}/networks/{name}.xml").read_text(encoding="utf-8")
            net = self.connection.networkDefineXML(xml)

            if net is None:
                raise RuntimeError("networkDefineXML returned `None`")
            net.setAutostart(1)
            net.create()
            print(f"Network {name} was created.")

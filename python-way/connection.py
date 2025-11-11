from typing import Optional, Type
from pathlib import Path
import libvirt

from helpers.parser import load_values, render_resource


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
        self.source_path = Path(source_path)
        self.output_path = Path(output_path)
        self.values = load_values(Path(values_path))


    @staticmethod
    def _resolve_uri(hv: str)-> str:
        hv = hv.lower()

        if hv in ('qemu', 'kvm'):
            return 'qemu:///system'
        raise ValueError(f"Unsupported hypervisor: {hv}")
        
    def __enter__(self) -> 'Connection':
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
        print('Connection has been closed.')


    def get_network(self, name: str) -> libvirt.virNetwork:
        existing_active = set(self.connection.listNetworks())
        existing_defined = set(self.connection.listDefinedNetworks())
        network = None

        if name in existing_active or name in existing_defined:
            print(f"{name} network already exists.")
            network = self.connection.networkLookupByName(name)
        
        print(f"{name} network doesn't exist.")        
        return network

    def create_infra(self) -> None:
        print('Starting infra...')
        for type in self.values:
            self.start(type)

    def destroy_infra(self) -> None:
        print('Destroying infra...')
        for type in self.values:
            self.destroy(type)

    def start(self, type: str) -> None:
        match type:
            case 'networks':
                print('Starting networks...')
                for item in self.values['networks']:
                    print(item)
                    name = item.get('name')
                    self.start_network(name, item)
            # case 'vms':
                # print('TBD VMS')
            # case 'lb':
                # print('TBD LB')
    
    def destroy(self, type: str) -> None:
        match type:
            case 'networks':
                print('Destroying networks...')
                for network in self.values['networks']:
                    name = network.get('name')
                    self.destroy_network(name)
                Path(f"{self.output_path}/networks").rmdir()
            # case 'vms':
                # print('TBD VMS DESTRUCTION IS UNDER CONSTRUCTION')
            # case 'lb':
                # print('TBD LB DESTRUCTION IS UNDER CONSTRUCTION')
        # self.output_path.rmdir()


    def start_network(self, name: str, item: dict) -> None:
        template_name = 'network.xml.jinja2'
        net = self.get_network(name)
        out_path = f"{self.output_path}/networks"

        if net is not None:
            if net.isActive() != 1:
                net.create()
                print(f"Existing {name} network was started.")
            if not net.autostart():
                net.setAutostart(1)
        else:
            render_resource(
                source_path=self.source_path,
                template_name=template_name, 
                values=item, 
                output_path=out_path
                )    
            xml = Path(f"{out_path}/{name}.xml").read_text(encoding='utf-8')
            net = self.connection.networkDefineXML(xml)

            if net is None:
                raise RuntimeError('networkDefineXML returned `None`')
            else:
                net.setAutostart(1)
                net.create()
                print(f"Network {name} was created and started.")
    
    def destroy_network(self, name: str) -> None:
        net = self.get_network(name)
        xml = Path(f"{self.output_path}/networks/{name}.xml")
        if net is not None:
            net.destroy()
            net.undefine()
            xml.unlink()
            print(f"{name} network was destroyed.")
        
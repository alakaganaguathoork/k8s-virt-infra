import libvirt
import os


class Connection:

    URI = ""
    connection = ""

    def __init__(self, hypervisor):
        self.uri = self._resolve_uri(hypervisor)

        match self.hypervisor:
            case "qemu":
                self.URI = "qemu://system"
            case "kvm":
                self.URI = ""

    def open_connection(URI):
        try:
            connection = libvirt.open(URI)
            return connection
        except:
            raise RuntimeError(f"Failed to open connection {URI}.")
        finally:
            print("All is good.")

    def _resolve_uri(hv: str)-> str:
        hv = hv.lower()

        if hv in ("qemu", "kvm"):
            return "qemu:///system"
        raise ValueError(f"Unsupported hypervisor: {hv}") 

    def create_dir(path):
        if not os.path.dirname(path):
            os.mkdir(path)
        else:
            print("Directory exists.")

    def createNetwork(net_name):
       if not connection.networkLookupByName(net_name):
           connection.networkCreateXML()


    def closeConnection():
        connection.close()
        print("Connection has been closed.")
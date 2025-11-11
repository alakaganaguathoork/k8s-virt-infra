from time import sleep
from connection import Connection
from helpers.parser import load_values
from pathlib import Path


if __name__ == '__main__':

    hypervisor = "qemu"
    source_path = '../templates'
    values_path = '../values.yml'
    output_path = '../generated'


    with Connection(
        hypervisor,
        source_path,
        output_path,
        values_path
    ) as conn:
        conn.create_infra()
        sleep(3)
        # conn.destroy_infra()
    
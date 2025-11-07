from pathlib import Path

from connection import Connection
from helpers.parser import render

if __name__ == '__main__':
    # conn = Connection('qemu')
    # conn.openConnection()
    # conn.create_dir('config')
    # conn.closeConnection()

    source_path: Path = '../templates'
    values_path: Path = '../values.yml'
    output_path: Path = '../generated'

    render(
        'networks',
        source_path, 
        'network.xml.jinja2', 
        values_path, 
        output_path)
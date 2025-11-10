from connection import Connection

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
    
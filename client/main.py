import requests
import argparse
import os
from tqdm import tqdm


# -----------------------------------------
SERVERS_IP = 'localhost'
# -----------------------------------------


def get_manager_url():
    return f'http://{SERVERS_IP}:8020'


HOST_MANAGER = get_manager_url()
CHUNK_SIZE = 1024


def add_file(file):
    file = os.path.basename(file)
    try:
        url = f'{HOST_MANAGER}/gen_chunk_distro'
        filesize = os.path.getsize(file)

        data = {
            'filename': file,
            'filesize': filesize
        }

        print('# Generating chunks')
        response = requests.post(url, json=data)

        assert response.status_code == 200, 'error'

        response = response.json()

        handlers = response['handlers']
        servers = response['servers']

        with open(file, 'rb') as input_file:
            bar = tqdm(zip(servers, handlers), desc=f' Uploading {file}')

            for chs, chh in bar:
                part = input_file.read(CHUNK_SIZE)

                chs = chs.split(':')
                chs = f'{SERVERS_IP}:{chs[1]}'

                chunk_server = f'http://{chs}/update_chunk/{chh}'

                response = requests.post(chunk_server, files={'file': part})

                assert response.status_code == 200, 'error'

        print(f'# File {file} added :)')
    except Exception as ex:
        print(f'> Error: {str(ex)}')


def get_file(file):
    file = os.path.basename(file)
    try:
        url = f'{HOST_MANAGER}/get_chunk_distro/{file}'

        print('# Getting chunks')
        response = requests.get(url)

        body = response.json()

        assert response.status_code == 200, body['message']

        handler = body['handlers']
        servers = body['servers']

        bar = tqdm(zip(handler, servers), desc=f'Downloading {file}')

        for chh, chs in bar:
            with open(file, 'ab') as output_file:
                chs = chs.split(':')
                chs = f'{SERVERS_IP}:{chs[1]}'

                chunk_url = f'http://{chs}/get_chunk/{chh}'
                response = requests.get(chunk_url)

                assert response.status_code == 200, 'error'

                output_file.write(response.content)

        print(f'# File {file} Downloaded :)')
    except Exception as ex:
        print(f"> Error {str(ex)}")


def remove_file(file):
    file = os.path.basename(file)
    try:
        url = f'{HOST_MANAGER}/delete/{file}'
        response = requests.delete(url)

        assert response.status_code == 200, response.json()['message']

        print(f'# File {file} deleted')
    except Exception as ex:
        print(f"> Error: {str(ex)}")


def describe_file(file):
    file = os.path.basename(file)
    try:
        url = f'{HOST_MANAGER}/getsize/{file}'
        response = requests.get(url)

        assert response.status_code == 200, response.json()['message']

        body = response.json()
        name = body['filename']
        size = body['filesize']
        # fid = body['fileid']

        print("\t------------------------------------------------")
        print(f'\tFile Name:\t{name}')
        print(f'\tFile Size:\t{size}')
        # print(f'\tServer File Id:\t{fid}')
        print("\t------------------------------------------------")

    except Exception as ex:
        print(f"> Error: {str(ex)}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Simple GFS client")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    add_parser = subparsers.add_parser("add", help="Add a file")
    add_parser.add_argument("file", type=str, help="File name")

    get_parser = subparsers.add_parser("get", help="Get a file")
    get_parser.add_argument("file", type=str, help="File name")

    rm_parser = subparsers.add_parser("rm", help="Remove a file")
    rm_parser.add_argument("file", type=str, help="File name")

    desc_parser = subparsers.add_parser("desc", help="Describe a file")
    desc_parser.add_argument("file", type=str, help="File name")

    args = parser.parse_args()

    if args.command == "add":
        add_file(args.file)
    elif args.command == "get":
        get_file(args.file)
    elif args.command == "rm":
        remove_file(args.file)
    elif args.command == "desc":
        describe_file(args.file)
    else:
        print("Invalid command")

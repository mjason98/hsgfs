import os
import random
import requests
from .connect import hash_string_to_sha256


def get_chunks():
    raw_strings = os.environ.get('CHUNKS_PORTS')
    ports = raw_strings.split(';')

    return ports


PORTs = get_chunks()


def check_health(addr):
    return True

    response = requests.get(addr + '/health')

    if response.status_code == 200:
        return True
    else:
        return False


def get_distro_chunks(n: int):
    available = [u for u in PORTs if check_health(u)]
    # available = [u.split(':')[1] for u in available]

    distro = random.choices(available, k=n)

    return distro


def __gen_handler(filename, pos):
    str_ = f'the file {filename} with chunk {pos}'
    hash = hash_string_to_sha256(str_)

    return hash


def gen_chunks_handlers(filename, ini, end):
    chandlers = [__gen_handler(filename, i) for i in range(ini, end)]
    return chandlers

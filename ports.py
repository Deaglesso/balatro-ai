import random


BASE_PORT = 12000
PORT_RANGE = 2000


def generate_ports(n: int, seed: int | None = None,):
    if seed is not None:
        rng = random.Random(seed)
    else:
        rng = random.Random()

    ports = set()

    while len(ports) < n:
        ports.add(BASE_PORT + rng.randint(0, PORT_RANGE))

    return sorted(ports)
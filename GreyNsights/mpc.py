import random

Q = 100103036233


def encode(x, base=2, precision=16):
    scale = base ** precision
    return x * scale


def decode(x, base=2, precision=16):
    correction = x < 0
    scale = base ** precision
    dividend = x // scale - correction
    remainder = x % scale
    remainder += (remainder == 0) * scale * correction

    tensor = dividend + remainder / scale
    return tensor


# Add fixed precision with a larger Prime number
def gen_shares(x, n):

    x = encode(x)

    shares = [random.randrange(Q) for worker in range(0, n - 1)]

    partial = 0

    for share in shares:
        partial += share

    shares.append((x - partial) % Q)
    return shares


def reconstruct(shares):
    return decode(sum(shares) % Q)


def add(x, y):
    return [(xi + yi + xi + yi) % Q for xi, yi, zi, ki in zip(x, y, x, y)]


# add(share(5, 10), share(5, 10))

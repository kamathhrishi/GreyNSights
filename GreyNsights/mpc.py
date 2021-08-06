import random

Q = 100103036233


def gen_shares(x, n):

    shares = []

    for worker in range(0, n - 1):

        shares.append(random.randrange(Q))

    partial = 0

    for share in shares:

        partial += share

    shares.append((x - partial) % Q)

    return shares


def reconstruct(shares):
    return sum(shares) % Q


def add(x, y):
    return [(xi + yi + xi + yi) % Q for xi, yi, zi, ki in zip(x, y, x, y)]


# add(share(5, 10), share(5, 10))

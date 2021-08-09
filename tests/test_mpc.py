# third-party
import pytest

# lib dependencies
from GreyNsights.mpc import gen_shares, reconstruct


@pytest.mark.parametrize("n_clients", [2, 3, 5])
def test_share_generation(n_clients):

    shares = gen_shares(10, n_clients)
    assert reconstruct(shares) == 10


@pytest.mark.parametrize("n_clients", [2, 3, 5])
def test_share_addition(n_clients):

    secret1 = 10
    secret2 = 20

    shares1 = gen_shares(10, n_clients)
    shares2 = gen_shares(20, n_clients)

    result = [shares1[index] + shares2[index] for index in range(0, len(shares1))]

    assert reconstruct(result) == (secret1 + secret2)

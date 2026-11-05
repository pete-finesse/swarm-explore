import pytest


@pytest.fixture(scope="session")
def h():
    from sdharness.load import load

    return load("tiny")


@pytest.fixture(scope="session")
def pool():
    from sdharness import facts as F

    return F.load()


@pytest.fixture(scope="session")
def mozart(pool):
    from sdharness import facts as F

    return F.find(pool, "Wolfgang Amadeus Mozart")

import pytest

from stairlight import StairLight


@pytest.fixture(scope="session")
def stair_light():
    return StairLight()

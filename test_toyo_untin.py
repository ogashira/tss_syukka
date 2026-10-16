import pytest
from toyo_untin import ToyoUntin

@pytest.fixture
def toyo_untin():
    toyoUntin = ToyoUntin()
    return toyoUntin

def test_toyo_untin(toyo_untin):
    assert toyo_untin.get_basic_fee('T0410', '', 8) == 0
    assert toyo_untin.get_basic_fee('T0410', '', 7) == 10
    assert toyo_untin.get_basic_fee('T0060', 'H084', 10) == 30
    assert toyo_untin.get_basic_fee('T0060', 'H084', 3) == 70
    assert toyo_untin.get_basic_fee('T0070', 'H009', 8) == 0
    assert toyo_untin.get_basic_fee('T0070', 'H009', 3) == 30
    assert toyo_untin.get_basic_fee('T0070', 'H009', 250) == 0


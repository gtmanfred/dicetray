import pytest

import dicetray


@pytest.mark.parametrize(
    "sides",
    [
        (2),
        (4),
        (6),
        (8),
        (10),
        (12),
        (20),
    ],
)
def test_random(sides):
    count = 0
    numbers = set(range(1, sides + 1))
    while count < 1000 and numbers:
        count += 1
        die = dicetray.Dice(sides=sides)
        if die.result in numbers:
            numbers.remove(die.result)
        if die.result == 1:
            assert die.ismin is True
        else:
            assert die.ismin is False
        if die.result == sides:
            assert die.ismax is True
        else:
            assert die.ismax is False
    assert not numbers


def test_fate_random():
    count = 0
    numbers = set(range(-1, 2))
    while count < 1000 and numbers:
        count += 1
        die = dicetray.FateDice()
        if die.result in numbers:
            numbers.remove(die.result)
        if die.result == 1:
            assert die.ismax is True
        if die.result == -1:
            assert die.ismin is True
    assert not numbers


def test_zero_sides():
    die = dicetray.Dice(sides=0)
    assert die.result == 0


def test_dice_compare_lt():
    assert dicetray.Dice(sides=0) < dicetray.Dice(sides=1)
    assert dicetray.Dice(sides=4) < 5


def test_dice_add():
    assert dicetray.Dice(sides=0) + dicetray.Dice(sides=1) + 1 == 2
    assert dicetray.Dice(sides=0) + dicetray.Dice(sides=1) + dicetray.Dice(sides=1) == 2


def test_dice_sub():
    assert dicetray.Dice(sides=1) - 1 == 0
    assert dicetray.Dice(sides=1) - dicetray.Dice(sides=0) == 1


def test_dice_compare_eq():
    assert dicetray.Dice(sides=1) == dicetray.Dice(sides=1)
    assert not dicetray.Dice(sides=1) == dicetray.Dice(sides=0)


def test_dice_str():
    assert str(dicetray.Dice(sides=20, result=10)) == "<Dice (d20): 10>"

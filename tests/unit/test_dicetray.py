import pytest

import dicetray


@pytest.mark.parametrize(
    "formula,num_dice",
    [
        ("1d20 + 1", 1),
        ("1d20 + 1df - 1", 2),
        ("(1d20 + 2d8) * 2", 3),
        ("(1d20 + 2d8) / 1", 3),
        ("2d20kh1", 2),
        ("4d6dl1", 4),
        ("2d20dh1", 2),
        ("4d6kl1", 4),
    ],
)
def test_dicetray_formulas(formula, num_dice):
    tray = dicetray.Dicetray(formula)
    assert tray.result is None
    assert not tray.dice
    tray.roll()
    assert isinstance(tray.result, (int, float))
    assert len(tray.dice) == num_dice

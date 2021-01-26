import pytest

import dicetray.parser
import sly.lex


@pytest.mark.parametrize(
    "formula,num_dice",
    [
        ("1d20", 1),
        ("1d20 + 1", 1),
        ("1d20 + 1df - 1", 2),
        ("(1d20 + 2d8) * 2", 3),
        ("(1d20 + 2d8) / 1", 3),
        ("1/1", 0),
        ("2d20kh4", 2),
        ("4d6dl1", 4),
        ("2d20dh2", 2),
        ("4d6kl3", 4),
        ("4d6dl", 4),
        ("2d20dh", 2),
        ("4d6kl", 4),
        ("2d20kh + 1d4 + 3", 3),
        ("1d% / 1", 1),
        ("d6", 1),
        ("df", 1),
    ],
)
def test_dicetray_formulas(formula, num_dice):
    tray = dicetray.Dicetray(formula)
    assert tray.result is None
    assert not tray.dice
    tray.roll()
    assert isinstance(tray.format(), str)
    assert isinstance(tray.format(verbose=True, markdown=True), str)
    assert isinstance(tray.result, (int, float))
    assert len(tray.dice) == num_dice



@pytest.mark.parametrize(
    'formula,max_dice', [
        ('100d20', 99),
        ('1001d20', None),
        ('50d20+100d6', 149),
    ],
)
def test_dicetray_maxdice_exception(formula, max_dice):
    with pytest.raises(dicetray.MaxDiceExceeded):
        if max_dice is None:
            dicetray.Dicetray(formula).roll()
        else:
            dicetray.Dicetray(formula, max_dice=max_dice).roll()


@pytest.mark.parametrize(
    'formula', [
        ('1d20+'),
        ('1d10+-'),
        ('1dfF%20'),
    ],
)
def test_dicetray_parsing_exception(formula):
    with pytest.raises(dicetray.parser.ParserError):
        dicetray.Dicetray(formula).roll()

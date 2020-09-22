Dicetray
========

.. image:: https://github.com/gtmanfred/dicetray/workflows/Tests/badge.svg
    :target: https://github.com/gtmanfred/dicetray

.. image:: https://img.shields.io/codecov/c/github/gtmanfred/dicetray
    :target: https://codecov.io/gh/gtmanfred/dicetray

.. image:: https://img.shields.io/pypi/v/dicetray
    :target: https://pypi.org/project/dicetray

.. image:: https://img.shields.io/pypi/l/dicetray
    :target: http://www.apache.org/licenses/LICENSE-2.0

.. image:: https://img.shields.io/pypi/dm/dicetray
    :target: https://pypi.org/project/dicetray/


Tabletop RPG Dice rolling manager for handling `Standard Dice Notation`_

Example
-------

.. code-block:: python

    >>> from dicetray import Dicetray
    >>> Dicetray('1d20 + 3').roll()
    15
    >>> Dicetray('4d6dl').roll()
    10
    >>> Dicetray('4d6kh3').roll()
    12
    >>> d = Dicetray('2d20kh + 1d4 + 3')
    >>> d.result
    >>> d.dice
    set()
    >>> d.roll()
    18
    >>> d.dice
    {<Dice (d20): 14>, <Dice (d20): 14>, <Dice (d4): 1>}
    >>> d.result
    18

.. _Standard Dice Notation: https://en.wikipedia.org/wiki/Dice_notation

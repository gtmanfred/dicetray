import os
import random
import struct
import typing

from .parser import parse


class Dice:
    def __init__(self, sides=None, result=None):
        self.sides = sides or 0
        self.result = self.roll() if result is None else result

    def __repr__(self):
        return f"<Dice (d{self.sides}): {self.result}>"

    def __hash__(self):
        return hash(id(self))

    def roll(self):
        """
        Roll dice

        This uses os.urandom to to generate actually random data, then we
        convert to an integer, and modulos divide by the sides and add 1
        """
        if self.sides == 0:
            return 0
        return (struct.unpack("I", os.urandom(4))[0] % self.sides) + 1

    @staticmethod
    def _handle_int(other):
        if not isinstance(other, int):
            other = other.result
        return other

    def __add__(self, other):
        other = self._handle_int(other)
        return Dice(sides=0, result=self.result + other)

    def __sub__(self, other):
        other = self._handle_int(other)
        return Dice(sides=0, result=self.result - other)

    def __eq__(self, other):
        other = self._handle_int(other)
        return self.result == other

    def __mul__(self, other):
        other = self._handle_int(other)
        return self.result * other

    def __lt__(self, other):
        other = self._handle_int(other)
        return self.result < other

    @property
    def ismax(self):
        """
        Check if this is the maximum result
        """
        return self.result == self.sides

    @property
    def ismin(self):
        """
        Check if this is the minimum result
        """
        return self.result == 1


class FateDice(Dice):
    def __init__(self):
        self.sides = "fate"
        self.result = self.roll()

    def roll(self):
        """
        Roll dice
        """
        return random.randint(-1, 1)

    @property
    def ismax(self):
        """
        Check if this is the maximum result
        """
        return self.result == 1

    @property
    def ismin(self):
        """
        Check if this is the minimum result
        """
        return self.result == -1


class Dicetray:
    dice: typing.List[Dice]
    result: int
    statement: str

    def __init__(self, statement):
        self.statement = statement
        self.dice = set()
        self.result = None

    def roll(self):
        equation = parse(self.statement)
        self.result = self.solve(equation)
        if isinstance(self.result, Dice):
            self.result = self.result.result
        return self.result

    def solve(self, equation):
        """
        Recursively solve the equation for dice rolls
        """
        if equation[0] == "NUMBER":
            return equation[1]
        if equation[0] == "DICE":
            dice = []
            for _ in range(equation[1]):
                if isinstance(equation[2], str) and equation[2].lower() == "f":
                    dice.append(FateDice())
                else:
                    dice.append(Dice(sides=equation[2]))
                self.dice.update(dice)
            return dice
        func = equation[0].lower()
        return getattr(self, f"_{func}")(*equation[1:])

    def _sum(self, expr):
        if isinstance(expr, (int, float)):
            return expr
        if isinstance(expr, Dice):
            return expr
        ret = 0
        for item in expr:
            ret = item + ret
        return ret

    def _plus(self, expr1, expr2):
        return self._sum(self.solve(expr1)) + self._sum(self.solve(expr2))

    def _minus(self, expr1, expr2):
        return self._sum(self.solve(expr1)) - self._sum(self.solve(expr2))

    def _times(self, expr1, expr2):
        return self._sum(self.solve(expr1)) * self._sum(self.solve(expr2))

    def _divide(self, expr1, expr2):
        one = self.solve(expr1)
        if isinstance(one, Dice):
            one = one.result
        return self._sum(one) / self._sum(self.solve(expr2))

    def _keephigh(self, count, expr):
        return self._sum(sorted(self.solve(expr), reverse=True)[:count])

    def _keeplow(self, count, expr):
        return self._sum(sorted(self.solve(expr))[:count])

    def _drophigh(self, count, expr):
        return self._sum(sorted(self.solve(expr), reverse=True)[count:])

    def _droplow(self, count, expr):
        return self._sum(sorted(self.solve(expr))[count:])

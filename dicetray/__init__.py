import collections
import os
import random
import typing

from .parser import parse

try:
    random = random.SystemRandom()
except NotImplementedError:  # pragma: nocover
    import warnings
    warnings.warning(
        'System random number generator is not available. Falling back to pseudo-random generator'
    )


class MaxDiceExceeded(Exception):
    ...


class Dice:
    def __init__(self, sides=None, result=None):
        self.sides = sides or 0
        self.result = self.roll() if result is None else result

    def __dict__(self):
        return {
            'result': self.result,
            'sides': self.sides,
            'ismin': self.ismin,
            'ismax': self.ismax,
        }

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
        return random.randint(1, self.sides)

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


class Diceset(list):
    def __init__(self, sides, count=1):
        for _ in range(count):
            if isinstance(sides, str) and sides.lower() == "f":
                self.append(FateDice())
            elif isinstance(sides, str) and sides == '%':
                self.append(Dice(sides=100))
            else:
                self.append(Dice(sides=sides))


class Dicetray:
    dice: typing.List[Dice]
    result: int
    statement: str

    def __init__(self, statement, max_dice=1000):
        self.statement = statement
        self.dice = set()
        self.result = None
        self.max_dice = max_dice
        self._tree = {}

    def roll(self):
        equation = parse(self.statement)
        self.result = self._sum(self.solve(equation))
        return self.result

    @staticmethod
    def _highlight(die, markdown):
        if markdown is False:
            return False
        return die.ismax or die.ismin

    def format(self, verbose=False, markdown=False, tree=None):
        """
        Format dice formula output

        .. note:: Do not pass anything to ``tree``
        """
        if tree is None:
            tree = self._tree
        equation = None

        if 'NUMBER' in tree:
            equation = str(tree['NUMBER'])
        elif 'KEEP' in tree:
            kept = ', '.join([
                f'**{die.result}**'
                if self._highlight(die, markdown)
                else str(die.result)
                for die in tree['KEEP']
            ])
            dropped = ', '.join([
                f'**{die.result}**'
                if self._highlight(die, markdown)
                else str(die.result)
                for die in tree['DROP']
            ])
            if verbose is True:
                equation = f'{tree["FRAGMENT"]}(scores:[{kept}], dropped:[{dropped}])'
            else:
                equation = kept
        elif 'DICE' in tree:
            dice = ', '.join([
                f'**{die.result}**'
                if self._highlight(die, markdown)
                else str(die.result)
                for die in tree['DICE']
            ])
            if verbose is True:
                equation = f'{tree["FRAGMENT"]}(scores:[{dice}])'
            else:
                equation = dice
        else:
            operations = [
                ('PLUS', '+'),
                ('MINUS', '-'),
                ('TIMES', '*'),
                ('DIVIDE', '/'),
            ]

            for oper, symbol in operations:  # pragma: nocover
                if oper in tree:
                    equation = (
                        f'{self.format(verbose=verbose, tree=tree[oper]["LEFT"])}'
                        f' {symbol} '
                        f'{self.format(verbose=verbose, tree=tree[oper]["RIGHT"])}'
                    )
                    break

        return equation

    def solve(self, equation, tree=None):
        """
        Recursively solve the equation for dice rolls
        """
        if tree is None:
            tree = self._tree
        if equation[0] == "NUMBER":
            number = equation[1]
            tree['FRAGMENT'] = number
            tree['RESULT'] = number
            tree['NUMBER'] = number
            return number
        if equation[0] == "DICE":
            tree['FRAGMENT'] = f'{equation[1]}d{equation[2]}'
            count, sides = equation[1:]
            if count + len(self.dice) > self.max_dice:
                raise MaxDiceExceeded(f'Dice count too high: {count}>{self.max_dice}')
            diceset = Diceset(sides=sides, count=count)
            tree['DICE'] = diceset
            self.dice.update(diceset)
            return diceset
        func = equation[0].lower()
        return getattr(self, f"_{func}")(*equation[1:], tree=tree)

    def _sum(self, expr):
        if isinstance(expr, (int, float)):
            return expr
        return sum(expr, start=Dice(result=0)).result

    def _plus(self, expr1, expr2, tree):
        left = self.solve(expr1, tree.setdefault('PLUS', {}).setdefault('LEFT', {}))
        right = self.solve(expr2, tree.setdefault('PLUS', {}).setdefault('RIGHT', {}))
        leftsum = tree['PLUS']['LEFT']['RESULT'] = self._sum(left)
        rightsum = tree['PLUS']['RIGHT']['RESULT'] = self._sum(right)

        result = tree['PLUS']['RESULT'] = leftsum + rightsum
        return result

    def _minus(self, expr1, expr2, tree):
        left = self.solve(expr1, tree.setdefault('MINUS', {}).setdefault('LEFT', {}))
        right = self.solve(expr2, tree.setdefault('MINUS', {}).setdefault('RIGHT', {}))
        leftsum = tree['MINUS']['LEFT']['RESULT'] = self._sum(left)
        rightsum = tree['MINUS']['RIGHT']['RESULT'] = self._sum(right)

        result = tree['MINUS']['RESULT'] = leftsum - rightsum
        return result

    def _times(self, expr1, expr2, tree):
        left = self.solve(expr1, tree.setdefault('TIMES', {}).setdefault('LEFT', {}))
        right = self.solve(expr2, tree.setdefault('TIMES', {}).setdefault('RIGHT', {}))
        leftsum = tree['TIMES']['LEFT']['RESULT'] = self._sum(left)
        rightsum = tree['TIMES']['RIGHT']['RESULT'] = self._sum(right)

        result = tree['TIMES']['RESULT'] = leftsum * rightsum
        return result

    def _divide(self, expr1, expr2, tree):
        left = self.solve(expr1, tree.setdefault('DIVIDE', {}).setdefault('LEFT', {}))
        right = self.solve(expr2, tree.setdefault('DIVIDE', {}).setdefault('RIGHT', {}))
        if isinstance(left, list):
            left = self._sum(left)
        right = self.solve(expr2, tree.setdefault('DIVIDE', {}).setdefault('RIGHT', {}))
        leftsum = tree['DIVIDE']['LEFT']['RESULT'] = left
        rightsum = tree['DIVIDE']['RIGHT']['RESULT'] = self._sum(right)

        result = tree['DIVIDE']['RESULT'] = leftsum / rightsum
        return result

    def _keephigh(self, count, expr, tree):
        dice = sorted(self.solve(expr, tree=tree))
        tree['DROP'], tree['KEEP'] = dice[:count], dice[count:]

        result = tree['RESULT'] = self._sum(tree['KEEP'])
        tree['FRAGMENT'] = f'{tree["FRAGMENT"]}kh{count}'
        return result

    def _keeplow(self, count, expr, tree):
        dice = sorted(self.solve(expr, tree=tree))
        tree['DROP'], tree['KEEP'] = dice[count:], dice[:count]

        result = tree['RESULT'] = self._sum(tree['KEEP'])
        tree['FRAGMENT'] = f'{tree["FRAGMENT"]}kl{count}'
        return result

    def _drophigh(self, count, expr, tree):
        dice = sorted(self.solve(expr, tree=tree))
        tree['DROP'], tree['KEEP'] = dice[count:], dice[:count]

        result = tree['RESULT'] = self._sum(tree['KEEP'])
        tree['FRAGMENT'] = f'{tree["FRAGMENT"]}dh{count}'
        return result

    def _droplow(self, count, expr, tree):
        dice = sorted(self.solve(expr, tree=tree))
        tree['DROP'], tree['KEEP'] = dice[:count], dice[count:]

        result = tree['RESULT'] = self._sum(tree['KEEP'])
        tree['FRAGMENT'] = f'{tree["FRAGMENT"]}dl{count}'
        return result

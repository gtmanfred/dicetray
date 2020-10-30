# type: ignore
# flake8: noqa
import sly

from .lexer import DiceLexer


class DiceParser(sly.Parser):
    tokens = DiceLexer.tokens

    precedence = (
        ("left", PLUS, MINUS),
        ("left", TIMES, DIVIDE),
    )

    @_("statement")
    def statements(self, p):
        return p.statement

    @_("expr PLUS expr")
    def expr(self, p):
        return ("PLUS", p.expr0, p.expr1)

    @_("expr MINUS expr")
    def expr(self, p):
        return ("MINUS", p.expr0, p.expr1)

    @_("expr TIMES expr")
    def expr(self, p):
        return ("TIMES", p.expr0, p.expr1)

    @_("expr DIVIDE expr")
    def expr(self, p):
        return ("DIVIDE", p.expr0, p.expr1)

    @_("LPAREN expr RPAREN")
    def expr(self, p):
        return p.expr

    @_("expr")
    def statement(self, p):
        return p.expr

    @_("NUMBER")
    def expr(self, p):
        return ("NUMBER", int(p.NUMBER))

    @_("dice")
    def expr(self, p):
        return p.dice

    @_("func")
    def expr(self, p):
        return p.func

    @_("NUMBER DIE TYPE")
    def dice(self, p):
        return ("DICE", int(p.NUMBER), p.TYPE)

    @_("NUMBER DIE NUMBER")
    def dice(self, p):
        return ("DICE", int(p.NUMBER0), int(p.NUMBER1))

    @_("dice KEEPHIGH")
    def func(self, p):
        return ("KEEPHIGH", 1, p.dice)

    @_("dice KEEPLOW")
    def func(self, p):
        return ("KEEPLOW", 1, p.dice)

    @_("dice DROPHIGH")
    def func(self, p):
        return ("DROPHIGH", 1, p.dice)

    @_("dice DROPLOW")
    def func(self, p):
        return ("DROPLOW", 1, p.dice)

    @_("dice KEEPHIGH NUMBER")
    def func(self, p):
        return ("KEEPHIGH", int(p.NUMBER), p.dice)

    @_("dice KEEPLOW NUMBER")
    def func(self, p):
        return ("KEEPLOW", int(p.NUMBER), p.dice)

    @_("dice DROPHIGH NUMBER")
    def func(self, p):
        return ("DROPHIGH", int(p.NUMBER), p.dice)

    @_("dice DROPLOW NUMBER")
    def func(self, p):
        return ("DROPLOW", int(p.NUMBER), p.dice)


def parse(expr):
    return DiceParser().parse(tokens=DiceLexer().tokenize(text=expr))

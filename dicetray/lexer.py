# type: ignore
# flake8: noqa
import sly


class DiceLexer(sly.Lexer):

    tokens = {
        NUMBER,
        TYPE,
        LPAREN,
        RPAREN,
        PLUS,
        TIMES,
        MINUS,
        DIVIDE,
        KEEPHIGH,
        KEEPLOW,
        DROPHIGH,
        DROPLOW,
        DIE,
    }
    ignore = " \t"

    NUMBER = r"[0-9]+"
    TYPE = r"[fF%]"
    LPAREN = r"\("
    RPAREN = r"\)"
    PLUS = r"\+"
    MINUS = r"-"
    TIMES = r"\*"
    DIVIDE = r"/"
    KEEPHIGH = r"kh"
    KEEPLOW = r"kl"
    DROPHIGH = r"dh"
    DROPLOW = r"dl"
    DIE = r"d"

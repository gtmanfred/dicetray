# type: ignore
# flake8: noqa
import sly


class DiceLexer(sly.Lexer):

    tokens = {
        NUMBER,
        DICE,
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
    }
    ignore = " \t"

    NUMBER = r"[0-9]+"
    DICE = r"d[0-9fF]+"
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

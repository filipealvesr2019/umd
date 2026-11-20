"""Núcleo do UMD: lexer, parser, AST e validação."""
from .ast import Diagnostic, IdAllocator, Node
from .lexer import lex
from .parser import ParseResult, parse
from .tokens import Attribute, Token, TokenType
from .validator import validate

__all__ = [
    "Attribute",
    "Diagnostic",
    "IdAllocator",
    "Node",
    "ParseResult",
    "Token",
    "TokenType",
    "lex",
    "parse",
    "validate",
]

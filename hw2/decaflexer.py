import sys
import decimal
sys.path.insert(0, "../..")
from ply import *

import ply.lex as lexer

tokens =[
    'ID',
    'INTEGER',
    'FLOAT',
    'EQ',
    'ASSIGN',
    'LT',
    'GT',
    'LE',
    'GE',
    'PLUS',
    'PLUSPLUS',
    'MULT',
    'DIV',
    'COMMA',
    'SEMICOLON',
    'MINUS',
    'MINUSMINUS',
    'STRING',
    'LPAR',
    'RPAR',
    'LBRA',
    'RBRA',
    'LSB',
    'RSB',
    'DOT',
    'AND',
    'OR',
    'NOT',
    'NE'
]

t_EQ = r'=='
t_ASSIGN = r'='
t_LT = r'<'
t_GT = r'>='
t_LE = r'<='
t_GE = r'>'
t_PLUS = r'\+'
t_PLUSPLUS = r'\+\+'
t_MINUS = r'-'
t_MINUSMINUS = r'--'
t_MULT = r'\*'
t_DIV = r'/'
t_COMMA = r','
t_SEMICOLON = r';'
t_DOT = r'\.'
t_AND = r'&&'
t_OR = r'\|\|'
t_NOT = r'!'
t_NE = r'!='

RESERVED = {

    "boolean" :"BOOLEAN",
    "break" : "BREAK" ,
    "continue" : "CONTINUE",
    "class" : "CLASS",
    "do" : "DO",
    "else" : "ELSE",
    "extends" : "EXTENDS",
    "false" : "FALSE",
    "for" : "FOR",
    "if" : "IF" ,
    "int" : "INT",
    "new" : "NEW" ,
    "null" : "NULL",
    "private" : "PRIVATE",
    "public" : "PUBLIC" ,
    "return" : "RETURN" ,
    "static" : "STATIC",
    "super" : "SUPER" ,
    "this" : "THIS" ,
    "true" : "TRUE" ,
    "void" : "VOID" ,
    "while" : "WHILE",
}

tokens = tokens+RESERVED.values()

def t_INTEGER(t):
    r'\d+'
    t.value = int(t.value)
    return t

def t_FLOAT(t):
    r'(\d+(\.\d*)?|\.\d+)([eE][-+]? \d+)?'
    t.value = decimal.Decimal(t.value)
    return t

def t_newline(t):
    r'\n+'
    t.lexer.lineno += t.value.count("\n")
    t.vale = "NEWLINE"

def t_ID(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    t.type = RESERVED.get(t.value, "ID")
    return t

def t_STRING(t):
    r'\"([^\"\\]|\\.)*\"'
    t.value = t.value[1:-1].decode("string-escape")  # .swapcase() # for fun
    return t

def t_comment(t):
    r'(/\*([^*]|[\r\n]|(\*+([^*/]|[\r\n])))*\*+/)|(//.*)'
    pass

def t_WS(t):
    r'\s+'
    pass

def t_LBRA(t):
    r'\{'
    t.lexer.fparen_count += 1
    return t

def t_RBRA(t):
    r'\}'
    t.lexer.fparen_count -= 1
    return t

def t_LPAR(t):
    r'\('
    t.lexer.paren_count += 1
    return t

def t_RPAR(t):
    r'\)'
    # check for underflow?  should be the job of the parser
    t.lexer.paren_count -= 1
    return t

def t_LSB(t):
    r'\['
    t.lexer.sparen_count += 1
    return t

def t_RSB(t):
    r'\]'
    t.lexer.sparen_count -= 1
    return t

def t_error(t):
    raise SyntaxError("Unknown symbol %r" % (t.value[0],))
    print "Skipping", repr(t.value[0])
    t.lexer.skip(1)

def reset(self):
	self.lexer.lineno=1

lex.lex()
def parse(code):
    
    lex.input(code)
    while True:
        lex.at_line_start = ""
        lex.lexer.lineno = 1
        lex.lexer.paren_count=0
        lex.lexer.fparen_count=0
        tok = lex.token()
        if not tok:
            break
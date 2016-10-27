import decaflexer
import ply.yacc as yacc
from decaflexer import tokens

def p_classBlock(p):
    """
    classBlock : classDec classBlock
                 | empty
    """

def p_classDec(p):
    """
    classDec : CLASS ID LBRA classBody RBRA
               | CLASS ID EXTENDS ID LBRA classBody RBRA
    """

def p_classBody(p):
    """
    classBody : bodyContent classBody
                | bodyContent
    """

def p_bodyContent(p):
    """
    bodyContent : classField
                  | classMethod
                  | classConstructor
    """
def p_classMethod(p):
    """
    classMethod : classModifier type ID LPAR FORMALS RPAR Block
				  | classModifier VOID ID LPAR FORMALS RPAR Block
    """
	
def p_classField(p):
    """
    classField : classModifier var_declaration
    """


def p_classConstructor(p):
    """
    classConstructor : classModifier ID LPAR FORMALS RPAR Block
    """

def p_FORMALS(p):
    """
    FORMALS : formal
              | empty
    """

def p_formal(p):
    """
    formal : formal_param
             | formal_param COMMA formal
    """

def p_formal_param(p):
    """
    formal_param : type variable
    """

def p_var_declaration(p):
    """
    var_declaration : type variables SEMICOLON
    """

def p_type(p):
    """
    type : INT
           | FLOAT
           | BOOLEAN
           | ID
    """

def p_variables(p):
    """
    variables : variable more_variable
    """

def p_more_variable(p):
    """
    more_variable : COMMA variable more_variable
                    | empty
    """

def p_variable(p):
    """
    variable : ID SB
    """

def p_SB(p):
    """
    SB : LSB RSB SB
         | empty
    """

def p_classModifier(p):
    """
    classModifier : PUBLIC
                    | PUBLIC STATIC
                    | PRIVATE
                    | PRIVATE STATIC
                    | STATIC
                    | empty

    """

def p_Block(p):
    """
    Block : LBRA stmnts RBRA
    """

def p_stmnts(p):
    """
    stmnts : stmnt stmnts
             | empty
    """

def p_stmnt(p):
    """
    stmnt : IF LPAR expr RPAR stmnt 
            | IF LPAR expr RPAR stmnt ELSE stmnt %prec ELSE
            | WHILE LPAR expr RPAR stmnt
            | FOR LPAR SEMICOLON SEMICOLON RPAR stmnt
            | FOR LPAR stmnt_expr SEMICOLON SEMICOLON RPAR stmnt
            | FOR LPAR SEMICOLON expr SEMICOLON RPAR stmnt
            | FOR LPAR SEMICOLON SEMICOLON stmnt_expr RPAR stmnt
            | FOR LPAR stmnt_expr SEMICOLON expr SEMICOLON RPAR stmnt
            | FOR LPAR SEMICOLON expr SEMICOLON stmnt_expr RPAR stmnt
            | FOR LPAR stmnt_expr SEMICOLON SEMICOLON stmnt_expr RPAR stmnt
            | FOR LPAR stmnt_expr SEMICOLON expr SEMICOLON stmnt_expr RPAR stmnt
            | RETURN SEMICOLON
            | RETURN expr SEMICOLON
            | stmnt_expr SEMICOLON
            | BREAK SEMICOLON
            | CONTINUE SEMICOLON
            | Block
            | var_declaration
            | SEMICOLON
    """
def p_literal(p):
    """
    literal : FLOAT
              | INTEGER
              | STRING
              | NULL
              | TRUE
              | FALSE
    """

def p_primary(p):
    """
    primary : literal
              | THIS
              | SUPER
              | LPAR expr RPAR
              | NEW ID LPAR arguments RPAR
              | lhs
              | method_invocation
    """

def p_arguments(p):
    """
    arguments : argument
                | empty
    """

def p_argument(p):
    """
    argument : expr
               | expr COMMA arg 
    """

def p_arg(p):
    """
    arg : LPAR COMMA expr RPAR
          | LPAR COMMA expr RPAR arg
    """

def p_lhs(p):
    """
    lhs : field_access
          | array_access
    """

def p_field_access(p):
    """
    field_access : primary DOT ID
                   | ID
    """

def p_array_access(p):
    """
    array_access : primary LSB expr RSB
    """

def p_method_invocation(p):
    """
    method_invocation : field_access LPAR arguments RPAR
    """

def p_expr(p):
    """
    expr : primary
           | assign
           | new_array
           | expr PLUS expr %prec PLUS
           | expr MINUS expr %prec MINUS
           | expr MULT expr %prec MULT
           | expr DIV expr %prec DIV
           | expr AND expr %prec AND
           | expr OR expr %prec OR
           | expr EQ expr %prec EQ
           | expr NE expr %prec NE
           | expr LT expr %prec LT
           | expr GT expr %prec GT
           | expr LE expr %prec LE
           | expr GE expr %prec GE
           | unary_op expr
    """

def p_assign(p):
    """
    assign : lhs ASSIGN expr
             | lhs PLUSPLUS
             | PLUSPLUS lhs
             | lhs MINUSMINUS
             | MINUSMINUS lhs
    """

def p_new_array(p):
    """
    new_array : NEW type new_expr SB
    """

def p_new_expr(p):
    """
    new_expr : LSB expr RSB
               | LSB expr RSB new_expr
    """

def p_unary_op(p):
    """
    unary_op : PLUS %prec PLUS
               | MINUS %prec MINUS
               | NOT %prec NOT
    """

def p_stmnt_expr(p):
    """
    stmnt_expr : assign
                 | method_invocation
    """

precedence = (
    ('right', 'ASSIGN'),
    ('left', 'OR'),
    ('left', 'AND'),
    ('left', 'EQ', 'NE'),
    ('nonassoc', 'LT', 'GT', 'LE', 'GE'),
    ('left', 'PLUS', 'MINUS'),
    ('left', 'MULT', 'DIV'),
    ('left', 'NOT'),
    ('right','ELSE')
)

def p_empty(p):
    """
    empty :
    """

def p_error(p):
    if p:
        global isValid
        isValid = False
        print ("Syntax error at line number %s and lex position %s"%(p.lineno, p.lexpos), p.value)
        while True:
            tok = parser.token()             # Get the next token
            if not tok or tok.type == 'SEMICOLON' or tok.type == 'ID' or tok.type == 'LBRA' or tok.type == 'RBRA' or tok.type == 'LPAR' or tok.type == 'RPAR': break
        parser.errok()

isValid = True	
parser = yacc.yacc()
def parse(code):
    parser.parse(code)
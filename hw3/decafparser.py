import ply.yacc as yacc
import decaflexer
import ast
from decaflexer import tokens
from decaflexer import lex
from ast import *

import sys
import logging
precedence = (
    ('right', 'ASSIGN'),
    ('left', 'OR'),
    ('left', 'AND'),
    ('nonassoc', 'EQ', 'NEQ'),
    ('nonassoc', 'LEQ', 'GEQ', 'LT', 'GT'),
    ('left', 'PLUS', 'MINUS'),
    ('left', 'MULTIPLY', 'DIVIDE'),
    ('right', 'NOT'),
    ('right', 'UMINUS'),
    ('right', 'ELSE'),
    ('right', 'RPAREN'),
)
#This list is accomodate all the classes which are defined in the input. Class names are put in this list when a new
#class object is created. Only class name is saved in the classList and when dublicate class name is encountered error
#is thrown. This list is also checked while checking class-ref
classList=set()

#this list is to accomodate all the filed in a give class. Filed list names are put in this set and checked while adding
#into it for dublicates. If field with same name is tried to add again then error is thrown and nothing is printed.
# this list is reset when new classDecl is made.
fieldList=set()

#this list to maintain all the methodds wchich are created in the given class. When a new method is create a method name
# is added into this list and checked for dublicates and invalidated when already existing method with different parameters
# list is created. While checking for method-access in blocks this list is parsed for cchecking valid methods in a given
#
methodList=set()

def init():
    decaflexer.errorflag = False


### DECAF Grammar

# Top-level
def p_pgm(p):
    'pgm : class_decl_list'
    p[0]=p[1]

def p_class_decl_list_nonempty(p):
    'class_decl_list : class_decl class_decl_list'
    if p[2] is not None:
        # create a list of class objects and send them
        p[0]=[p[1]]+p[2]
    else:
        p[0]=[p[1]]
def p_class_decl_list_empty(p):
    'class_decl_list : '

def p_class_decl(p):
    'class_decl : CLASS ID extends LBRACE class_body_decl_list RBRACE'
    global classList
    if p[2] not in classList:
        classList.add(p[2])
    else:
       # print ("Unexpected token '{0}' near line {1}".format(p.value, p.lineno))
        print "Class Name %s already in use "%(p[2])
        decaflexer.errorflag = True
    p[0]=ClassDecl(p[2],p[3],p[5])
    global fieldList
    fieldList=set()
    global methodList
    methodList= set()


def p_class_decl_error(p):
    'class_decl : CLASS ID extends LBRACE error RBRACE'
    # error in class declaration; skip to next class decl.

def p_extends_id(p):
    'extends : EXTENDS ID '
    p[0]=p[2]

def p_extends_empty(p):
    ' extends : '
    pass

def p_class_body_decl_list_plus(p):
    'class_body_decl_list : class_body_decl_list class_body_decl'
    if p[1] is not None :
        p[0] = p[1] + [p[2]]
    else:
        p[0]=[p[2]]

def p_class_body_decl_list_single(p):
    'class_body_decl_list : class_body_decl'
    p[0]=[p[1]]

def p_class_body_decl_field(p):
    'class_body_decl : field_decl'
    p[0]=p[1]

def p_class_body_decl_method(p):
    'class_body_decl : method_decl'
    p[0]=p[1]

def p_class_body_decl_constructor(p):
    'class_body_decl : constructor_decl'
    p[0]=p[1]


# Field/Method/Constructor Declarations

def p_field_decl(p):
    'field_decl : mod var_decl'
    global fieldList
    global localVarList
    for var in p[2][1]:
        p[0]=Field(var,'',p[1][0],p[1][1],p[2][0])
        if var not in fieldList:
            fieldList.add(var)
        else:
            print "Field with name %s already in use "%(var)
            decaflexer.errorflag = True
            break
    localVarList=[]

localVarList=[]
def p_method_decl_void(p):
    'method_decl : mod VOID ID LPAREN param_list_opt RPAREN block'
    global localVarList
    global methodList
    methodList.add(p[3])
    checkVariableValidity(p[5]+localVarList)
    p[0]=Method(p[3],"",p[1][0],p[1][1],"void",variableTable=p[5]+localVarList,body='Block([\n'+str(p[7])+'])')
    localVarList=[]
    global varList
    varList={}

def checkVariableValidity(localVarList):
    dict=set()
    for var in localVarList:
        if var.name not in dict:
            dict.add(var.name)
        else:
            print "local variable %s already used "%(var.name)
            decaflexer.errorflag = True
            break

def p_method_decl_nonvoid(p):
    'method_decl : mod type ID LPAREN param_list_opt RPAREN block'
    global localVarList
    global methodList
    methodList.add(p[3])
    checkVariableValidity(p[5]+localVarList)
    p[0]=Method(p[3],"",p[1][0],p[1][1],p[2],variableTable=p[5]+localVarList,body='Block([\n'+str(p[7])+'])')
    localVarList=[]
    global varList
    varList={}

def p_constructor_decl(p):
    'constructor_decl : mod ID LPAREN param_list_opt RPAREN block'
    global localVarList
    checkVariableValidity(p[4]+localVarList)
    p[0]=Constructor(p[1][0],variableTable=p[4]+localVarList,body='Block([\n'+str(p[6])+'])')
    localVarList=[]
    global varList
    varList={}


def p_mod(p):
    'mod : visibility_mod storage_mod'
    p[0]=[p[1],p[2]]

def p_visibility_mod_pub(p):
    'visibility_mod : PUBLIC'
    p[0]=p[1]

def p_visibility_mod_priv(p):
    'visibility_mod : PRIVATE'
    p[0]=p[1]

def p_visibility_mod_empty(p):
    'visibility_mod : '
    p[0]="private"

def p_storage_mod_static(p):
    'storage_mod : STATIC'
    p[0]=p[1]

def p_storage_mod_empty(p):
    'storage_mod : '
    p[0]='instance'

def p_var_decl(p):
    'var_decl : type var_list SEMICOLON'
    global localVarList
    global varList
    for var in p[2]:
        localVarList+=[Variable(var, p[1], kind='local')]
        varList[var]=localVarList[-1].node_id
    p[0]=[p[1],p[2],localVarList]

def p_type_int(p):
    'type :  INT'
    p[0]=p[1]

def p_type_bool(p):
    'type :  BOOLEAN'
    p[0]=p[1]

def p_type_float(p):
    'type :  FLOAT'
    p[0]=p[1]

def p_type_id(p):
    'type :  ID'
    p[0]='user('+p[1]+')'

def p_var_list_plus(p):
    'var_list : var_list COMMA var'
    p[0]=p[1]+[p[3]]

def p_var_list_single(p):
    'var_list : var'
    p[0]=[p[1]]

def p_var_id(p):
    'var : ID'
    p[0]=p[1]

def p_var_array(p):
    'var : var LBRACKET RBRACKET'
    if len(p[1]) >= 2:
        p[0] = (p[1][0], p[1][1]+1)
    else:
        p[0] = (p[1], 1)
    pass

varList={}
def p_param_list_opt(p):
    'param_list_opt : param_list'
    p[0]=p[1]

def p_param_list_empty(p):
    'param_list_opt : '
    p[0]=[]
    pass

def p_param_list(p):
    'param_list : param_list COMMA param'
    p[0]=p[1]+[p[3]]
    pass

def p_param_list_single(p):
    'param_list : param'
    p[0]=[p[1]]

def p_param(p):
    'param : type ID'
    p[0]=Variable(p[2],p[1], kind='formal')
    global varList
    varList[p[2]]=p[0].node_id

# Statements

def p_block(p):
    'block : LBRACE stmt_list RBRACE'
    p[0]=p[2]

def p_block_error(p):
    'block : LBRACE stmt_list error RBRACE'
    # error within a block; skip to enclosing block

def p_stmt_list_empty(p):
    'stmt_list : '
    p[0]=''

def p_stmt_list(p):
    'stmt_list : stmt_list stmt'
    if p[1] is not None :
        if p[2] is not None:

            p[0] = str(p[1]) +str(p[2])
        else:
            p[0] = str(p[1])
    else:
        p[0] = str(p[2])


def p_stmt_if(p):
    '''stmt : IF LPAREN expr RPAREN stmt ELSE stmt
          | IF LPAREN expr RPAREN stmt'''
    if len(p) > 6:
        p[0] = p[1]+'('+ p[3]+', '+p[5]+', '+p[7]+')'
    else:
        print p[3]
        p[0] = p[1]+'(' + p[3] + ', ' + str(p[5]) + ')'

def p_stmt_while(p):
    'stmt : WHILE LPAREN expr RPAREN stmt'
    p[0] = 'While('+p[3]+' , '+str(p[5])+')\n'

def p_stmt_for(p):
    'stmt : FOR LPAREN stmt_expr_opt SEMICOLON expr_opt SEMICOLON stmt_expr_opt RPAREN stmt'
    p[0] = p[1]+'('+p[3]+', '+p[5]+', '+p[7]+', '+p[9]+')'
    pass

def p_stmt_return(p):
    'stmt : RETURN expr_opt SEMICOLON'
    p[0] = 'Return('+p[2]+')'

def p_stmt_stmt_expr(p):
    'stmt : stmt_expr SEMICOLON'
    p[0] = 'Expr(' + p[1]+ ')\n,'

def p_stmt_break(p):
    'stmt : BREAK SEMICOLON'
    p[0] = 'break'

def p_stmt_continue(p):
    'stmt : CONTINUE SEMICOLON'
    p[0] = 'continue'

def p_stmt_block(p):
    'stmt : block'
    p[0]=p[1]

def p_stmt_var_decl(p):
    'stmt : var_decl'
    global localVarList
    localVarList = p[1][2]

def p_stmt_error(p):
    'stmt : error SEMICOLON'
    print("Invalid statement near line {}".format(p.lineno(1)))
    decaflexer.errorflag = True

# Expressions
def p_literal_int_const(p):
    'literal : INT_CONST'
    p[0]='Constant ('+('Integer-constant('+str(p[1])+')')+')'

def p_literal_float_const(p):
    'literal : FLOAT_CONST'
    p[0]='Constant ('+('Float-constant('+str(p[1])+')')+')'

def p_literal_string_const(p):
    'literal : STRING_CONST'
    p[0]='Constant ('+('String-constant('+str(p[1])+')')+')'

def p_literal_null(p):
    'literal : NULL'
    p[0]='Constant ('+('Integer-constant('+'Null'+')')+')'

def p_literal_true(p):
    'literal : TRUE'
    p[0]='Constant ('+str(p[1])+')'

def p_literal_false(p):
    'literal : FALSE'
    p[0]='Constant ('+str(p[1])+')'

def p_primary_literal(p):
    'primary : literal'
    p[0] = p[1]

def p_primary_this(p):
    'primary : THIS'
    p[0]='This'

def p_primary_super(p):
    'primary : SUPER'
    p[0]='Super'

def p_primary_paren(p):
    'primary : LPAREN expr RPAREN'
    p[0]=p[1]+p[2]+p[3]

def p_primary_newobj(p):
    'primary : NEW ID LPAREN args_opt RPAREN'
    p[0] = 'New-object('+p[2]+', '+str(p[4])+')'

def p_primary_lhs(p):
    'primary : lhs'
    p[0]=p[1]

def p_primary_method_invocation(p):
    'primary : method_invocation'
    p[0] = p[1]

def p_args_opt_nonempty(p):
    'args_opt : arg_plus'
    p[0] = p[1]

def p_args_opt_empty(p):
    'args_opt : '
    p[0] = []

def p_args_plus(p):
    'arg_plus : arg_plus COMMA expr'
    p[0] = p[1] + [p[3]]

def p_args_single(p):
    'arg_plus : expr'
    p[0]=[p[1]]

def p_lhs(p):
    '''lhs : field_access
           | array_access'''
    if type(p[1]) is tuple:
        p[0]="Field-access(Super, "+p[1][1]+")"
    else:
        p[0]=str(p[1])

def p_field_access_dot(p):
    'field_access : primary DOT ID'
    global classList
    global fieldList
    global methodList
    if p[1] is "This":
        #check field list for possible fields resolvment
        if p[3] in fieldList:
            p[0]="Field-access(This, "+p[3]+")"
        #check method list for posible names of methods.
        elif p[3] in methodList:
            p[0]="This, "+p[3]+", "
        else:
            p[0]="This, "+p[3]+", "
    #if super then replace it with super field list
    elif p[1] is "Super":
        p[0]=("Super", p[3])
    #if varibale is name of class then replace with class-reference -expression
    elif p[1] in classList:
        p[0]="Class-reference-expression("+p[3]+")"
    else:
        p[0]="Field-access("+p[1]+", "+p[3]+")"

def p_field_access_id(p):
    'field_access : ID'
    global varList
    global fieldList
    global methodList
    if p[1] in  varList:
        p[0]="Variable("+str(varList[p[1]])+")"
    elif p[1] in methodList:
        p[0]="This, "+p[3]+", "
    else :
        p[0]="Field-access(This, "+p[1]+")"

def p_array_access(p):
    'array_access : primary LBRACKET expr RBRACKET'
    p[0] = 'Array-access('+p[1]+', '+p[3]+')'

def p_method_invocation(p):
    'method_invocation : field_access LPAREN args_opt RPAREN'
    if type(p[1]) is tuple:
        p[0]="Method-call(Super, "+p[1][1]+", "+str(p[3])+")"
    else:
        p[0] = "Method-call("+p[1]+str(p[3])+")"

def p_expr_basic(p):
    '''expr : primary
            | assign
            | new_array'''
    p[0]=p[1]

def p_expr_binop(p):
    '''expr : expr PLUS expr
            | expr MINUS expr
            | expr MULTIPLY expr
            | expr DIVIDE expr
            | expr EQ expr
            | expr NEQ expr
            | expr LT expr
            | expr LEQ expr
            | expr GT expr
            | expr GEQ expr
            | expr AND expr
            | expr OR expr
    '''
    global binaryDic
    p[0] = 'Binary('+binaryDic[p[2]]+', '+p[1]+', '+p[3]+')'

# dictionary is maintained for each binary expression adn each value is retrieved from the dictionary
binaryDic = {'+':'add','-':'sub','*':'mul','/':'div','&&':'and','||':'or','==':'eq','!=':'neq','<':'lt','>':'gt','<=':'leq','>=':'geq'}

def p_expr_unop(p):
    '''expr : PLUS expr %prec UMINUS
            | MINUS expr %prec UMINUS
            | NOT expr'''
    if p[1] == '+':
        p[0] = p[2]
    elif p[1] == '-':
        p[0] = 'Unary(uminus, '+p[2]+')'
    else:
        p[0] = 'Unary(neg, ' + p[2] + ')'

def p_assign_equals(p):
    'assign : lhs ASSIGN expr'
    p[0] = 'Assign('+str(p[1])+', '+p[3]+')'

def p_assign_post_inc(p):
    'assign : lhs INC'
    p[0] = 'Auto(' + p[1] + ', inc, post)'

def p_assign_pre_inc(p):
    'assign : INC lhs'
    p[0] = 'Auto(' + p[2] + ', inc, pre)'

def p_assign_post_dec(p):
    'assign : lhs DEC'
    p[0] = 'Auto(' + p[1] + ', dec, post)'

def p_assign_pre_dec(p):
    'assign : DEC lhs'
    p[0] = 'Auto(' + p[2] + ', dec, pre)'

def p_new_array(p):
    'new_array : NEW type dim_expr_plus dim_star'
    p[0] = 'New-array('+p[4].replace('None', p[2])+ ', ' +str(p[3])+')'

def p_dim_expr_plus(p):
    'dim_expr_plus : dim_expr_plus dim_expr'
    p[0] = p[1] + p[2]

def p_dim_expr_single(p):
    'dim_expr_plus : dim_expr'
    p[0]=p[1]
    pass

def p_dim_expr(p):
    'dim_expr : LBRACKET expr RBRACKET'
    p[0] = [p[2]]

def p_dim_star(p):
    'dim_star : LBRACKET RBRACKET dim_star'
    p[0] = 'array('+p[3]+')'

def p_dim_star_empty(p):
    'dim_star : '
    p[0] = 'None'

def p_stmt_expr(p):
    '''stmt_expr : assign
                 | method_invocation'''
    p[0]=p[1]

def p_stmt_expr_opt(p):
    'stmt_expr_opt : stmt_expr'
    p[0]=p[1]

def p_stmt_expr_empty(p):
    'stmt_expr_opt : '
    p[0]=''

def p_expr_opt(p):
    'expr_opt : expr'
    p[0]=p[1]

def p_expr_empty(p):
    'expr_opt : '
    p[0]=''

def p_error(p):
    if p is None:
        print ("Unexpected end-of-file")
    else:
        print ("Unexpected token '{0}' near line {1}".format(p.value, p.lineno))
    decaflexer.errorflag = True

parser = yacc.yacc()

def from_file(filename):
    try:
        with open(filename, "rU") as f:
            init()
            parseTree = parser.parse(f.read(), lexer=lex.lex(module=decaflexer), debug=None)
            if not decaflexer.errorflag:
                for classObj in parseTree:
                    print classObj
        return not decaflexer.errorflag
    except IOError as e:
        print "I/O error: %s: %s" % (filename, e.strerror)
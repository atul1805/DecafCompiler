import ast
from ast import *

def isStrictSubtype(type1, type2):
    #if types are same
    if str(type1) == str(type2):
        return True
    #null is subtype of class object
    elif str(type1) == 'null' and "user" in str(type2):
        return True
    elif str(type1)=='null' and 'array(' in str(type2):
        return True

    return False

# subtype contains validations for all valid subtypes defined
def isSubtype(type1, type2):
    #if types are same
    if str(type1) == str(type2):
        return True
    # predefined int float relationship
    elif str(type1) == 'int' and str(type2) == 'float':
        return True
    # checking subtype relation between two class objects if
    # type2 is superclass of type1
    elif "user" in str(type1) and "user" in str(type2):
        A = str(type1)[5:-1]
        B = str(type2)[5:-1]
        classA = ast.lookup(ast.classtable, A)
        if (classA != None and classA.superclass != None and classA.superclass.name == B):
            return True
    #null is subtype of class object
    elif str(type1) == 'null' and "user" in str(type2):
        return True
    #if a is subclass of b then class-leteral of a is subtype of class-literal of b
    elif 'class-literal' in str(type1) and 'class-literal' in str(type2):
        A = str(type1)[14:-1]
        B = str(type2)[14:-1]
        classA = ast.lookup(ast.classtable, A)
        if (classA != None and classA.superclass.name == B):
            return True
    #recursively check if array types are same by stripping of the array( part
    elif 'array(' in str(type1) and 'array(' in str(type2):
        A = str(type1)[6:-1]
        B = str(type2)[6:-1]
        if(isSubtype(A,B)):
            return True
    elif str(type1)=='null' and 'array(' in str(type2):
        return True

    return False

def main():
    #boolean value returned to the calling class
    isProgramCorrect = True
    for cid in ast.classtable:
        #type check all the classes in classtable recursively and return true if everything is fine.
        c = ast.classtable[cid]
        if not c.builtin:
            if not checkClass(c):
                isProgramCorrect = False
    return isProgramCorrect

def checkClass(c):
    isClassCorrect = True
    #iterate all the methods
    for m in c.methods:
        checkMethod(m, c)
        if not m.isTypeCorrect:
            isClassCorrect = False
    #iterate all the constructors
    for cn in c.constructors:
        checkConstructor(cn, c)
        if not cn.isTypeCorrect:
            isClassCorrect = False
    return isClassCorrect

def checkMethod(method, Class):
    body = method.body
    checkBody(body, Class)
    #type the body of the class
    if body.isTypeCorrect:
        method.isTypeCorrect = True

def checkConstructor(constructor, Class):
    body = constructor.body
    #do typechecking for the body of constructor
    checkBody(body, Class)
    if body.isTypeCorrect:
        constructor.isTypeCorrect = True

def checkBody(body, Class):
    stmtlist = body.stmtlist
    body.isTypeCorrect = True
    # take list of statements from body and do type checking for all the statemtns.
    for stmnt in stmtlist:
        checkStatement(stmnt, Class)
        if not stmnt.isTypeCorrect:
            body.isTypeCorrect = False

def checkStatement(stmnt, Class):
    #each statemtn is redirected to its own typeChecker
    if isinstance(stmnt, IfStmt):
        checkIfStmt(stmnt, Class)
    elif isinstance(stmnt, WhileStmt):
        checkWhileStmt(stmnt, Class)
    elif isinstance(stmnt, ForStmt):
        checkForStmt(stmnt, Class)
    elif isinstance(stmnt, ReturnStmt):
        checkReturnStmt(stmnt, Class)
    elif isinstance(stmnt, BlockStmt):
        checkBlockStmt(stmnt, Class)
    elif isinstance(stmnt, ExprStmt):
        checkExprStmt(stmnt, Class)

def checkIfStmt(stmnt, Class):
    condition = stmnt.condition
    thenpart = stmnt.thenpart
    elsepart = stmnt.elsepart
    #check the condition part
    checkExpr(condition, Class)
    #since then and else are statements they are sent back to checkStatement method for typechecking
    checkStatement(thenpart, Class)
    checkStatement(elsepart, Class)

    #check if all the conditions are met
    if condition.type == 'boolean' and thenpart.isTypeCorrect and elsepart.isTypeCorrect:
        stmnt.isTypeCorrect = True

def checkWhileStmt(stmnt, Class):
    condition = stmnt.cond
    body = stmnt.body
    #type check the condition part and get the final type of condition
    checkExpr(condition, Class)
    #type check the body and get the
    checkStatement(body, Class)

    if condition.type == 'boolean' and body.isTypeCorrect:
        stmnt.isTypeCorrect = True

def checkForStmt(stmnt, Class):
    init = stmnt.init
    cond = stmnt.cond
    update = stmnt.update
    body = stmnt.body

    #type check for init expression
    checkExpr(init, Class)
    # type check for conditino
    checkExpr(cond, Class)
    #type check for udpate expression
    checkExpr(update, Class)
    #type  check for body statements
    checkStatement(body, Class)

    if cond.type == 'boolean' and body.isTypeCorrect and str(init.type) is not 'error' and str(update.type) is not 'error':
        stmnt.isTypeCorrect = True

def checkReturnStmt(stmnt, Class):
    lines = stmnt.lines
    expr = stmnt.expr
    #type checking for expr
    checkExpr(expr, Class)

    if expr.type is not 'error':
        stmnt.isTypeCorrect = True

def checkBlockStmt(stmnt, Class):
    stmtlist = stmnt.stmtlist
    isValidBlock = True
    #type checking for all the stamentsin block statements
    for s in stmtlist:
        checkStatement(s, Class)
        if not s.isTypeCorrect:
            isValidBlock = False
    stmnt.isTypeCorrect = isValidBlock

def checkExprStmt(stmnt, Class):
    lines = stmnt.lines
    expr = stmnt.expr
    checkExpr(expr, Class)
    if str(expr.type) != 'error':
        stmnt.isTypeCorrect=True

#important method where all the expressions are checked for type error.
#all the methods eventually call this method
def checkExpr(expr, Class):
    # check type errors fo constant expr
    if isinstance(expr, ConstantExpr):
        kind = expr.kind
        if kind == 'int':
            expr.type = 'int'
        elif kind == 'float':
            expr.type = 'float'
        elif kind == 'string':
            expr.type = 'string'
        elif kind == 'True' or kind == 'False':
            expr.type = 'boolean'
        elif kind == 'Null':
            expr.type = 'null'
    # check type errors for Var Expression
    elif isinstance(expr, VarExpr):
        var = expr.var
        expr.type = var.type
    # check type errors for Unary Expressions
    elif isinstance(expr, UnaryExpr):
        uop = expr.uop
        arg = expr.arg
        checkExpr(arg, Class)
        if str(arg.type) == 'int' and uop == 'uminus':
            expr.type = 'int'
        elif str(arg.type) == 'float' and uop == 'uminus':
            expr.type = 'float'
        elif str(arg.type) == 'boolean' and uop == 'neg':
            expr.type = 'boolean'
        else:
            expr.type = 'error'
            print "UnaryExpr Error at line %s: '%s' operation found invalid argument '%s'" % (expr.lines, uop, arg.type)
    elif isinstance(expr, BinaryExpr):
        bop = expr.bop
        arg1 = expr.arg1
        arg2 = expr.arg2
        checkExpr(arg1, Class)
        checkExpr(arg2, Class)

        if bop == 'add' or bop == 'sub' or bop == 'mul' or bop == 'div':
            if (str(arg1.type) == 'int' and str(arg2.type) == 'int'):
                expr.type = 'int'
            elif (str(arg1.type) == 'int' or str(arg1.type) == 'float') and (str(arg2.type) == 'int' or str(arg2.type) == 'float'):
                expr.type = 'float'
            else:
                expr.type = 'error'
                print "BinaryExpr Error at line %s: '%s' operation found invalid arguments '%s', '%s'" % (expr.lines, bop, arg1.type, arg2.type)
        elif bop == 'and' or bop == 'or':
            if str(arg1.type) == 'boolean' and str(arg2.type) == 'boolean':
                expr.type = 'boolean'
            else:
                expr.type = 'error'
                print "BinaryExpr Error at line %s: '%s' operation found invalid arguments '%s', '%s'" % (expr.lines, bop, arg1.type, arg2.type)
        elif bop == 'lt' or bop == 'leq' or bop == 'gt' or bop == 'geq':
            if (str(arg1.type) == 'int' or str(arg1.type) == 'float') and (str(arg2.type) == 'int' or str(arg2.type) == 'float'):
                expr.type = 'boolean'
            else:
                expr.type = 'error'
                print "BinaryExpr Error at line %s: '%s' operation found invalid arguments '%s', '%s'" % (expr.lines, bop, arg1.type, arg2.type)
        elif bop == 'eq' or bop == 'neq':
            if isSubtype(arg1.type, arg2.type) or isSubtype(arg2.type, arg1.type):
                expr.type = 'boolean'
            else:
                expr.type = 'error'
                print "BinaryExpr Error at line %s: '%s' operation found invalid arguments '%s', '%s'" % (expr.lines, bop, arg1.type, arg2.type)
    elif isinstance(expr, AssignExpr):
        lhs = expr.lhs
        rhs = expr.rhs
        checkExpr(lhs, Class)
        checkExpr(rhs, Class)
        if str(lhs.type) != 'error' and str(rhs.type) != 'error' and isSubtype(rhs.type, lhs.type):
            expr.type = rhs.type
        else:
            expr.type = 'error'
            if str(lhs.type) != 'error' and str(rhs.type) != 'error':
                print "AssignExpr Error at line %s: '%s' expression found when '%s' is expected" % (expr.lines, rhs.type, lhs.type)
    elif isinstance(expr, AutoExpr):
        arg = expr.arg
        checkExpr(arg, Class)
        if str(arg.type) == 'int' or str(arg.type) == 'float':
            expr.type = arg.type
        else:
            expr.type = 'error'
            print "AutoExpr Error at line %s: '%s' found int or float expected" % (expr.lines, arg.type)
    elif isinstance(expr, FieldAccessExpr):
        base= expr.base
        fname = expr.fname
        checkExpr(base, Class)
        if 'user' in str(base.type):
            A = str(base.type)[5:-1]
            storage = 'instance'
        elif 'class-literal' in str(base.type):
            A = str(base.type)[14:-1]
            storage = 'staic'

        classA = ast.lookup(ast.classtable,A)
        inSuperClass = False
        while (classA is not None):
            fields = classA.fields
            if fname in fields and fields[fname].storage is storage and (not inSuperClass or fields[fname].visibility is 'public'):
                expr.resolvedID = fields[fname].id
                expr.type = fields[fname].type
                break
            else:
                classA = classA.superclass
                inSuperClass = True
        if classA is None:
            expr.type = 'error'
            expr.resolvedID = None
            print "FieldAccessExpr Error at line %s:, couldn't find field '%s'"%(expr.lines, fname)
    elif isinstance(expr, MethodInvocationExpr):
        base = expr.base
        checkExpr(base, Class)
        mname = expr.mname
        args = expr.args

        if 'user' in str(base.type):
            A = str(base.type)[5:-1]
            storage = 'instance'
        elif 'class-literal' in str(base.type):
            A = str(base.type)[14:-1]
            storage = 'static'

        classA = ast.lookup(ast.classtable,A)
        inSuperClass = False
        argMatch = True
        methodFound = False
        isAllSubtype = True
        while (classA is not None):
            methods = classA.methods
            for m in methods:
                if m.name == mname and m.storage is storage and ((not inSuperClass and str(classA.name) == str(Class.name)) or m.visibility is 'public'):
                    formalPar = m.vars.vars[0]
                    if len(args) == len(formalPar):
                        argMatch = True
                        for ID in range(0, len(formalPar)):
                            for fp in formalPar:
                                if formalPar[fp].id == ID + 1:
                                    checkExpr(args[ID], Class)
                                    if not isStrictSubtype(args[ID].type, formalPar[fp].type):
                                        ID = len(formalPar)
                                        argMatch = False
                                        break
                        if argMatch and methodFound:
                            expr.type = 'error'
                            expr.resolvedID = None
                        elif argMatch:
                            methodFound = True
                            expr.type = m.rtype
                            expr.resolvedID = m.id
            if not methodFound:
                classA = classA.superclass
                inSuperClass = True
            else:
                break
        if not methodFound:
            classA = ast.lookup(ast.classtable,A)
            while (classA is not None):
                methods = classA.methods
                for m in methods:
                    if m.name == mname and m.storage is storage and (not inSuperClass or m.visibility is 'public'):
                        formalPar = m.vars.vars[0]
                        if len(args) == len(formalPar):
                            argMatch = True
                            isAllSubtype = True
                            for ID in range(0, len(formalPar)):
                                for fp in formalPar:
                                    if formalPar[fp].id == ID + 1:
                                        checkExpr(args[ID], Class)
                                        #if isStrictSubtype(args[ID].type, formalPar[fp].type):
                                        isAllSubtype = False
                                        if not isSubtype(args[ID].type, formalPar[fp].type):
                                            ID = len(formalPar)
                                            argMatch = False
                                            break
                            if argMatch and methodFound and not isAllSubtype:
                                expr.type = 'error'
                                expr.resolvedID = None
                            elif argMatch and not isAllSubtype:
                                methodFound = True
                                expr.type = m.rtype
                                expr.resolvedID = m.id
                if not methodFound:
                    classA = classA.superclass
                    inSuperClass = True
                else:
                    break

        if classA is None:
            expr.type = 'error'
            print "MethodInvocationExpr Error at line %s: couldn't find method with name '%s'" % (expr.lines,mname)
        elif expr.type == 'error':
            print "MethodInvocationExpr Error at line %s: couldn't find valid method with name '%s'" % (expr.lines,mname)
    elif isinstance(expr, NewObjectExpr):
        classref = expr.classref
        args = expr.args

        argMatch = True
        constructorFound = False
        inSuperClass = False
        constructors = classref.constructors
        for c in constructors:
            if c.visibility is 'public' or Class.name == classref.name:
                formalPar = c.vars.vars[0]
                if len(args) == len(formalPar):
                    argMatch = True
                    for ID in range(0, len(formalPar)):
                        for fp in formalPar:
                            if formalPar[fp].id == ID + 1:
                                checkExpr(args[ID], Class)
                                if not isStrictSubtype(args[ID].type, formalPar[fp].type):
                                    ID = len(formalPar)
                                    argMatch = False
                                    break
                    if argMatch and constructorFound:
                        expr.type = 'error'
                        expr.resolvedID = None
                    elif argMatch:
                        constructorFound = True
                        expr.resolvedID = c.id
                        expr.type = 'user('+classref.name+')'
        if not constructorFound:
            for c in constructors:
                if c.visibility is 'public' or Class.name == classref.name:
                    formalPar = c.vars.vars[0]
                    if len(args) == len(formalPar):
                        argMatch = True
                        isAllSubtype = True
                        for ID in range(0, len(formalPar)):
                            for fp in formalPar:
                                if formalPar[fp].id == ID + 1:
                                    checkExpr(args[ID], Class)
#                                    if isStrictSubtype(args[ID].type, formalPar[fp].type):
                                    isAllSubtype = False
                                    if not isSubtype(args[ID].type, formalPar[fp].type):
                                        ID = len(formalPar)
                                        argMatch = False
                                        break
                        if argMatch and constructorFound and not isAllSubtype:
                            expr.type = 'error'
                            expr.resolvedID = None
                        elif argMatch and not isAllSubtype:
                            constructorFound = True
                            expr.resolvedID = c.id
                            expr.type = 'user('+classref.name+')'
        if not constructorFound:
            expr.type = 'error'
            print "NewObjectExpr Error at line %s: couldn't find valid class with name '%s'" % (expr.lines,classref.name)
    elif isinstance(expr, ThisExpr):
        expr.type = 'user('+Class.name+')'
    elif isinstance(expr, SuperExpr):
        if Class.superclass.name is not None:
            expr.type = 'user('+Class.superclass.name+')'
        else:
            expr.type= 'error'
            print "ThisExpr Error at line %s" % (expr.lines)
    elif isinstance(expr, ClassReferenceExpr):
        classref = expr.classref
        expr.type='class-literal('+classref.name+')'
    elif isinstance(expr, ArrayAccessExpr):
        base = expr.base
        index = expr.index
        checkExpr(base,Class)
        checkExpr(index,Class)
        baseType = str(base.type)
        if 'array(' in baseType and index.type is 'int':
            expr.type = baseType[6:-1]
        else:
            expr.type ='error'
            if index.type is not 'int':
                print "ArrayAccessExpr Error at line %s: 'int' index expected found %s" % (expr.lines,index.type)
            else:
                print "ArrayAccessExpr Error at line %s: 'array(' base type expected found %s" % (expr.lines,baseType)
    elif isinstance(expr, NewArrayExpr):
        baseType = expr.basetype
        args = expr.args
        checkExpr(baseType,Class)
        type = str(baseType)
        for arg in args:
            checkExpr(arg,Class)
            if str(arg.type) is 'int':
                type = 'array('+type+')'
            else:
                type='error'
                print "NewArrayExpr Error at line %s: 'int' argument expected found %s" % (expr.lines,arg.type)
                break
        expr.type = type

import ast
import absmc
from ast import *
from absmc import *

# this variable is used to keep track if the method is static method or non static
# which can be used to allocate argument register from a0 if static and a1 if non static
isStatic = 0

# prev label is used in continue statement when encountered will jmp to this prev label
prevLabel = ''

# next label is used in break statement when encountered will jmp to the next label
nxtLabel = ''

def main():
    arm = ARM()
    arm.initializeFields()
    # iterate through each class and generate instructions
    for cid in ast.classtable:
        c = ast.classtable[cid]
        if not c.builtin:
             codegenClass(c, arm)
    return arm.codeStr

def codegenClass(c, arm):
    # iterate all the methods
    for m in c.methods:
        # if classname is "main" and class storage is static and it should be visible
        # then we are generating __main__ label for that class
        # toherwise general standard is maintinaed.
        if str(m.name) == 'main' and str(m.storage) == 'static' and str(m.visibility) == 'public':
            arm.add_label('__main__')
        else:
            arm.add_label('M_%s_%d' %(m.name, m.id))
        codegenMethod(m, arm)
        arm.add_newLine()
    # iterate all the constructors
    for cn in c.constructors:
        # for all the constructors C_%d label is createdd
        arm.add_label('C_%d' %(cn.id))
        codegenConstructor(cn, arm)
        arm.add_newLine()

def codegenMethod(method, arm):
    body = method.body
    # for a given method all the registered as taken from t0
    # argument counter is also resent but it will start with a1 for methods which are not static

    arm.resetRegisterCount()
    if len(method.vars.vars) > 0:
        arm.argumentRegCount = len(method.vars.vars[0])
    if len(method.vars.vars) > 1:
        arm.tempregisterCount = len(method.vars.vars[1])
    global isStatic
    if str(method.storage)is 'static':
        # set the static variable value to 1 so that a0 is set as argument register
        isStatic = 1

    # generate instructions for body
    codegenBody(body, arm)
    # reset the variable to normal value
    isStatic = 0

def codegenConstructor(constructor, arm):
    # for a given constructors all the registered as taken from t0
    # argument counter is also reset but it will start with a1 since a0 is allocated for objects
    body = constructor.body
    arm.resetRegisterCount()
    if len(constructor.vars.vars) > 0:
        arm.argumentRegCount = len(constructor.vars.vars[0])
    if len(constructor.vars.vars) > 1:
        arm.tempregisterCount = len(constructor.vars.vars[1])

    codegenBody(body, arm)
    arm.ret()

def codegenBody(body, arm):
    if not isinstance(body, SkipStmt):
        # parse through all the statements and generate instuctions for each fo the statement
        stmtlist = body.stmtlist
        for stmnt in stmtlist:
            codegenStatement(stmnt, arm)

def codegenStatement(stmnt, arm):
    if isinstance(stmnt, IfStmt):
        codegenIfStmt(stmnt, arm)
    elif isinstance(stmnt, WhileStmt):
        codegenWhileStmt(stmnt, arm)
    elif isinstance(stmnt, ForStmt):
        codegenForStmt(stmnt, arm)
    elif isinstance(stmnt, ReturnStmt):
        codegenReturnStmt(stmnt, arm)
    elif isinstance(stmnt, BlockStmt):
        codegenBlockStmt(stmnt, arm)
    elif isinstance(stmnt, ExprStmt):
        codegenExprStmt(stmnt, arm)
    elif isinstance(stmnt, BreakStmt):
        codegenBreakStmt(stmnt, arm)
    elif isinstance(stmnt, ContinueStmt):
        codegenContinueStmt(stmnt, arm)

def codegenIfStmt(stmnt, arm):
    condition = stmnt.condition
    thenpart = stmnt.thenpart
    elsepart = stmnt.elsepart
    # generate instructions to process conditionn and then put the result in one register
    # get the register value in condition expr use to next time
    codegenExpr(condition, arm)
    label = arm.incLabelCounter()
    # jmp to label if this condition is not true
    arm.bz(condition.reg, label)
    # if above mentioned condition is not met then continue to if block and execute
    codegenStatement(thenpart, arm)
    # after executing the if statement jump to end of if else block hence next label
    nextLabel = arm.incLabelCounter()
    arm.jmp(nextLabel)
    # generate label for else part and put instruction for else part after which jmp to label after if else block
    arm.add_label(label)
    codegenStatement(elsepart, arm)
    arm.add_label(nextLabel)



def codegenWhileStmt(stmnt, arm):
    condition = stmnt.cond
    body = stmnt.body
    # label to the begining of the statement so that after executing the loop statement jmp to initial part
    label = arm.incLabelCounter()
    global prevLabel  # prev label is used to keep tracck of start position and used when continue is called
    prevLabel = label
    # label so that after not meeting the condition loop ends by jumping to this
    nextLabel = arm.incLabelCounter()
    global nxtLabel
    nxtLabel = nextLabel
    arm.add_label(label)
    # generate instructions to process condition and then put the result in one register
    # get the register value in condition expr use to next time
    codegenExpr(condition, arm)
    arm.bz(condition.reg, nextLabel)
    # generate code for body and jmp to the first label after executing all the instructions in the label.
    codegenStatement(body, arm)
    arm.jmp(label)
    arm.add_label(nextLabel)

def codegenForStmt(stmnt, arm):
    init = stmnt.init
    cond = stmnt.cond
    update = stmnt.update
    body = stmnt.body

    codegenExpr(init, arm)
    label = arm.incLabelCounter()
    nextLabel = arm.incLabelCounter()
    global nxtLabel
    nxtLabel = nextLabel
    arm.add_label(label)
    codegenExpr(cond, arm)
    arm.bz(cond.reg, nextLabel)
    updateLabel = arm.incLabelCounter()
    global prevLabel
    prevLabel = updateLabel
    codegenStatement(body, arm)
    arm.add_label(updateLabel)
    codegenExpr(update, arm)
    arm.jmp(label)
    arm.add_label(nextLabel)


# save the value in a0 register and print ret
def codegenReturnStmt(stmnt, arm):
    lines = stmnt.lines
    expr = stmnt.expr
    codegenExpr(expr, arm)
    if expr is not None:
        arm.move('a0', expr.reg)
    arm.ret()


#  generate code for each of the statement in block statement.
def codegenBlockStmt(stmnt, arm):
    stmtlist = stmnt.stmtlist
    for s in stmtlist:
        codegenStatement(s, arm)

def codegenExprStmt(stmnt, arm):
    lines = stmnt.lines
    expr = stmnt.expr
    codegenExpr(expr, arm)

# jmp the statement to next Label
def codegenBreakStmt(stmnt, arm):
    global nxtLabel
    arm.jmp(nxtLabel)

# jmp the statment to prev lable which was saved.
def codegenContinueStmt(stmnt, arm):
    global prevLabel
    arm.jmp(prevLabel)


def codegenExpr(expr, arm):
    # for constant expression we are putting it in one register and using that register
    # register value can be accessed in reg by doing expr.reg
    if isinstance(expr, ConstantExpr):
        if str(expr.kind) == 'int':
            r = "t" + `arm.tempregisterCount`
            arm.tempregisterCount += 1
            arm.move_immed_i(r, expr.int)
            expr.reg = r
        elif str(expr.kind) == 'float':
            r = "t" + `arm.tempregisterCount`
            arm.tempregisterCount += 1
            arm.move_immed_f(r, expr.float)
            expr.reg = r

    # var expr can be of two types one method arguments and another local variables
    # for method arguments registered are assignmetn as a0, a1, a2,
    # for local variables t0, t1, t2 are assigned
    elif isinstance(expr, VarExpr):
        var = expr.var
        global isStatic
        if str(var.kind) == "formal":
            expr.reg = "a" + `var.id - isStatic`
        elif str(var.kind) == "local":
            expr.reg = "t" + `var.id - 1 - arm.argumentRegCount`

    elif isinstance(expr, UnaryExpr):
        uop = expr.uop
        arg = expr.arg
        codegenExpr(arg, arm)
        r = "t" + `arm.tempregisterCount`
        arm.tempregisterCount += 1
        if str(arg.typeof()) == 'int' and uop == 'uminus':
            arm.move_immed_i(r, -1)
            arm.imul(r, r, arg.reg)
        elif str(arg.typeof()) == 'float' and uop == 'uminus':
            arm.move_immed_f(r, -1)
            arm.fmul(r, r, arg.reg)
        elif str(arg.typeof()) == 'boolean' and uop == 'neg':
            r1 = "t" + `arm.tempregisterCount`
            arm.tempregisterCount += 1
            arm.move_immed_i(r1, 2)
            arm.isub(r, r1, arg.reg)
            arm.idiv(r, r, r1)
        expr.reg = r

    # all binary expressions are handled similarly by evaluating each expr separately and then
    # using respective instructions Except for and and or
    # for 'and' and 'or' short circuit is handled hence first expression is evaluated first checked for being true or
    # false and second statement is checked
    elif isinstance(expr, BinaryExpr):
        bop = expr.bop
        arg1 = expr.arg1
        arg2 = expr.arg2
        codegenExpr(arg1, arm)
        r = ""

        if bop == 'add':
            codegenExpr(arg2, arm)
            # each expression is checked if its of type float or int
            # corresponding add expression is called
            if str(arg1.typeof()) == 'float' or str(arg1.typeof()) == 'float':
                r = "t" + `arm.tempregisterCount`
                arm.tempregisterCount += 1
                arm.fadd(r, arg1.reg, arg2.reg)
            else:
                r = "t" + `arm.tempregisterCount`
                arm.tempregisterCount += 1
                arm.iadd(r, arg1.reg, arg2.reg)
        elif bop == 'sub':
            # each expression is checked if its of type float or int
            # corresponding sub expression is called
            codegenExpr(arg2, arm)
            if str(arg1.typeof()) == 'float' or str(arg1.typeof()) == 'float':
                r = "t" + `arm.tempregisterCount`
                arm.tempregisterCount += 1
                arm.fsub(r, arg1.reg, arg2.reg)
            else:
                r = "t" + `arm.tempregisterCount`
                arm.tempregisterCount += 1
                arm.isub(r, arg1.reg, arg2.reg)
        elif bop == 'mul':
            # each expression is checked if its of type float or int
            # corresponding add expression is called
            codegenExpr(arg2, arm)
            if str(arg1.typeof()) == 'float' or str(arg1.typeof()) == 'float':
                r = "t" + `arm.tempregisterCount`
                arm.tempregisterCount += 1
                arm.fmul(r, arg1.reg, arg2.reg)
            else:
                r = "t" + `arm.tempregisterCount`
                arm.tempregisterCount += 1
                arm.imul(r, arg1.reg, arg2.reg)
        elif bop == 'div':
            # each expression is checked if its of type float or int
            # corresponding div expression is called
            codegenExpr(arg2, arm)
            if str(arg1.typeof()) == 'float' or str(arg1.typeof()) == 'float':
                r = "t" + `arm.tempregisterCount`
                arm.tempregisterCount += 1
                arm.fdiv(r, arg1.reg, arg2.reg)
            else:
                r = "t" + `arm.tempregisterCount`
                arm.tempregisterCount += 1
                arm.idiv(r, arg1.reg, arg2.reg)
        elif bop == 'and':
            # and is short circuted
            # first value is evaluated first and then checked if its false
            # then on zero jump to final without executing the second expression
            # expr.reg value is set to first epxression if true other set to second reg .
            r = "t" + `arm.tempregisterCount`
            arm.tempregisterCount += 1
            label = arm.incLabelCounter()
            nextLabel = arm.incLabelCounter()
            arm.bz(arg1.reg, label)
            codegenExpr(arg2, arm)
            arm.move(r, arg2.reg)
            arm.jmp(nextLabel)
            arm.add_label(label)
            arm.move(r, arg1.reg)
            arm.add_label(nextLabel)
        elif bop == 'or':

            # or is short circuited only frist expression is evaluated
            # if first value is true then jmp to final statement other wise second expression
            # label is created which ennable the above property
            r = "t" + `arm.tempregisterCount`
            arm.tempregisterCount += 1
            label = arm.incLabelCounter()
            nextLabel = arm.incLabelCounter()
            arm.bnz(arg1.reg, label)
            codegenExpr(arg2, arm)
            arm.move(r, arg2.reg)
            arm.jmp(nextLabel)
            arm.add_label(label)
            arm.move(r, arg1.reg)
            arm.add_label(nextLabel)
        elif bop == 'eq':
            # to check neq we have considered doing both greater than or equal to and  less than ore equal to check and
            # if both of them is true then its  equal to so the value should be one in output
            # hence mult the results of leq and geq and putting in final register
            codegenExpr(arg2, arm)
            if str(arg1.typeof()) == 'float' or str(arg1.typeof()) == 'float':
                r = "t" + `arm.tempregisterCount`
                arm.tempregisterCount += 1
                r1 = "t" + `arm.tempregisterCount`
                arm.tempregisterCount += 1
                r2 = "t" + `arm.tempregisterCount`
                arm.tempregisterCount += 1
                arm.fgeq(r1, arg1.reg, arg2.reg)
                arm.fleq(r2, arg1.reg, arg2.reg)
                arm.fmul(r, r1, r2)
                arm.tempregisterCount -= 2
            else:
                r = "t" + `arm.tempregisterCount`
                arm.tempregisterCount += 1
                r1 = "t" + `arm.tempregisterCount`
                arm.tempregisterCount += 1
                r2 = "t" + `arm.tempregisterCount`
                arm.tempregisterCount += 1
                arm.igeq(r1, arg1.reg, arg2.reg)
                arm.ileq(r2, arg1.reg, arg2.reg)
                arm.imul(r, r1, r2)
                arm.tempregisterCount -= 2
        elif bop == 'neq':
            # to check neq we have considered doing both greater than not less than check and
            # if anyof them is true then its not equal to so the value should be one in output
            # hence adding the results of leq and geq
            codegenExpr(arg2, arm)
            if str(arg1.typeof()) == 'float' or str(arg1.typeof()) == 'float':
                r = "t" + `arm.tempregisterCount`
                arm.tempregisterCount += 1
                r1 = "t" + `arm.tempregisterCount`
                arm.tempregisterCount += 1
                r2 = "t" + `arm.tempregisterCount`
                arm.tempregisterCount += 1
                arm.fgeq(r1, arg1.reg, arg2.reg)
                arm.fleq(r2, arg1.reg, arg2.reg)
                arm.fadd(r, r1, r2)
                arm.tempregisterCount -= 2
            else:
                r = "t" + `arm.tempregisterCount`
                arm.tempregisterCount += 1
                r1 = "t" + `arm.tempregisterCount`
                arm.tempregisterCount += 1
                r2 = "t" + `arm.tempregisterCount`
                arm.tempregisterCount += 1
                arm.igeq(r1, arg1.reg, arg2.reg)
                arm.ileq(r2, arg1.reg, arg2.reg)
                arm.iadd(r, r1, r2)
                arm.tempregisterCount -= 2
        elif bop == 'lt':
            # both the expressions are calcculated and respective instructions are generated
            codegenExpr(arg2, arm)
            if str(arg1.typeof()) == 'float' or str(arg1.typeof()) == 'float':
                r = "t" + `arm.tempregisterCount`
                arm.tempregisterCount += 1
                arm.flt(r, arg1.reg, arg2.reg)
            else:
                r = "t" + `arm.tempregisterCount`
                arm.tempregisterCount += 1
                arm.ilt(r, arg1.reg, arg2.reg)
        elif bop == 'gt':
            # both the expressions are calculated and respective instructions are generated
            codegenExpr(arg2, arm)
            if str(arg1.typeof()) == 'float' or str(arg1.typeof()) == 'float':
                r = "t" + `arm.tempregisterCount`
                arm.tempregisterCount += 1
                arm.fgt(r, arg1.reg, arg2.reg)
            else:
                r = "t" + `arm.tempregisterCount`
                arm.tempregisterCount += 1
                arm.igt(r, arg1.reg, arg2.reg)
        elif bop == 'leq':
            # both the expressions are calculated and respective instructions are generated
            codegenExpr(arg2, arm)
            if str(arg1.typeof()) == 'float' or str(arg1.typeof()) == 'float':
                r = "t" + `arm.tempregisterCount`
                arm.tempregisterCount += 1
                arm.fleq(r, arg1.reg, arg2.reg)
            else:
                r = "t" + `arm.tempregisterCount`
                arm.tempregisterCount += 1
                arm.ileq(r, arg1.reg, arg2.reg)
        elif bop == 'geq':
            # both the expressions are calculated and respective instructions are generated
            codegenExpr(arg2, arm)
            if str(arg1.typeof()) == 'float' or str(arg1.typeof()) == 'float':
                r = "t" + `arm.tempregisterCount`
                arm.tempregisterCount += 1
                arm.fgeq(r, arg1.reg, arg2.reg)
            else:
                r = "t" + `arm.tempregisterCount`
                arm.tempregisterCount += 1
                arm.igeq(r, arg1.reg, arg2.reg)
        expr.reg = r

    elif isinstance(expr, AssignExpr):
        lhs = expr.lhs
        rhs = expr.rhs
        # lhs.isload is used such that when field acccess is on the right hand side its value
        # is loaded into local register but when its on left hand side just offset is caluclated
        lhs.isLoad = False
        rhs.isLoad = True
        codegenExpr(lhs, arm)
        codegenExpr(rhs, arm)
        if isinstance(rhs, NewArrayExpr):
            lhs.var.dim = rhs.dim
        if isinstance(lhs, FieldAccessExpr) or isinstance(lhs, ArrayAccessExpr):
            # fieldacccessis then do hstore
            arm.hstore(lhs.baseReg, lhs.offsetReg, rhs.reg)
        else:
            # otherwise move
            arm.move(lhs.reg, rhs.reg)

    elif isinstance(expr, AutoExpr):
        arg = expr.arg
        oper = expr.oper
        when = expr.when
        codegenExpr(arg, arm)
        r = "t" + `arm.tempregisterCount`
        arm.move_immed_i(r, 1)
        # 1 is copied in a register and then added or subtracted
        if str(oper) == 'inc':
            if str(arg.typeof()) == 'float':
                arm.fadd(arg.reg, arg.reg, r)
            else:
                arm.iadd(arg.reg, arg.reg, r)
        else:
            if str(arg.typeof()) == 'float':
                arm.fsub(arg.reg, arg.reg, r)
            else:
                arm.isub(arg.reg, arg.reg, r)
        expr.reg = arg.reg

    elif isinstance(expr, FieldAccessExpr):
        base= expr.base
        fname = expr.fname
        codegenExpr(base, arm)
        r1 = "t" + `arm.tempregisterCount`
        arm.tempregisterCount += 1
        r2 = "t" + `arm.tempregisterCount`
        arm.tempregisterCount += 1

        expr.baseReg = ''
        # if field access of type user which means filed value will be in heap space
        # hload the field using base as the base address

        if 'user' in str(base.typeof()):
            A = str(base.typeof())[5:-1]
            arm.move_immed_i(r1, arm.nsFieldOffset[A][expr.field.id])
            if expr.isLoad:
                arm.hload(r2, base.reg, r1)
                expr.reg = r2
            expr.baseReg = base.reg
        # if field access is of static then value is taken from sap
        elif 'class_literal' in str(base.typeof()):
            A = str(base.typeof())[14:-1]
            arm.move_immed_i(r1, arm.sFieldOffset[A][expr.field.name])
            if expr.isLoad:
                arm.hload(r2, 'sap', r1)
                expr.reg = r2
            expr.baseReg = 'sap'
        expr.offsetReg = r1

    elif isinstance(expr, MethodInvocationExpr):
        base = expr.base
        codegenExpr(base, arm)
        mname = expr.mname
        args = expr.args
        prevTempRegCount = arm.tempregisterCount
        # if method is static then there wont be any object reference in a0
        # so no need to save any value in a0
        # after saving all the registers method is called

        for i in range(0, len(args)):
            codegenExpr(args[i], arm)
        start = 1
        if isinstance(base, ClassReferenceExpr):
            start = 0
        for i in range(0, prevTempRegCount):
            arm.save("t" + `i`)
        for i in range(0, arm.argumentRegCount):
            arm.save("a" + `i`)
        for i in range(start, len(args) + start):
            arm.move('a' + `i`, args[i - start].reg)
        arm.callMethod(expr.method.name, expr.method.id)
        # and restored back after method call is over.
        r = "t" + `arm.tempregisterCount`
        arm.tempregisterCount += 1
        arm.move(r, 'a0')
        for i in range(prevTempRegCount - 1, -1, -1):
            arm.restore("t" + `i`)
        for i in range(arm.argumentRegCount - 1, -1, -1):
            arm.restore("a" + `i`)
        expr.reg = r

    elif isinstance(expr, NewObjectExpr):
        classref = expr.classref
        args = expr.args
        # generate registers for all the arguments

        for i in range(0, len(args)):
            codegenExpr(args[i], arm)
        # define the object size by counting all the variables present.
        objSize = arm.getObjectSize(classref.name)
        r1 = "t" + `arm.tempregisterCount`
        arm.tempregisterCount += 1
        arm.move_immed_i(r1, objSize)
        # after getting size of the object create heap memory for alll the variables
        r2 = "t" + `arm.tempregisterCount`
        arm.tempregisterCount += 1
        arm.halloc(r2, r1)

        # heere save all the argument register and all the temp registers
        # then copy object reference in a0
        # then afte copying call constructor

        for i in range(0, arm.tempregisterCount):
            arm.save("t" + `i`)
        for i in range(0, arm.argumentRegCount):
            arm.save("a" + `i`)
        arm.move('a0', r2)
        for i in range(1, len(args)):
            arm.move('a' + `i`, args[i - 1].reg)
        arm.callConstructor(expr.constructor.id)
        r = "t" + `arm.tempregisterCount`
        arm.tempregisterCount += 1
        # after getting the value from constructor save the value in temp register
        # restore all the registeres
        # copy the value to the object reference
        arm.move(r, 'a0')
        for i in range(arm.tempregisterCount - 2, -1, -1):
            arm.restore("t" + `i`)
        for i in range(arm.argumentRegCount - 1, -1, -1):
            arm.restore("a" + `i`)
        expr.reg = r

    elif isinstance(expr, ThisExpr):
        # set the reg value to class instance which will be in a0
        expr.reg = 'a0'

    elif isinstance(expr, SuperExpr):
        expr.reg = 'a0'

    elif isinstance(expr, ClassReferenceExpr):
        pass

    elif isinstance(expr, ArrayAccessExpr):
        base = expr.base
        index =[]
        codegenExpr(expr.index, arm)
        index += [expr.index.reg]
        # take the var expr from the base
        while not isinstance(base, VarExpr):
            codegenExpr(base.index, arm)
            index += [base.index.reg]
            base = base.base
        index.reverse()

        dim = []
        # get the list of registered where dimenstions of the array are set.
        for i in range(0, len(base.var.dim)):
            dim += [base.var.dim[i]]
        # get the base register value by calling codegen for base
        codegenExpr(base, arm)

        r = "t" + `arm.tempregisterCount`
        arm.tempregisterCount += 1
        arm.move_immed_i(r, 0)
        # calculate the exact position of th eindex andd then use it to update or access
        for i in range(0, len(index)):
            arm.imul(r, r, dim[i])
            arm.iadd(r, r, index[i])

        r1 = "t" + `arm.tempregisterCount`
        arm.tempregisterCount += 1
        # if statement is of type load
        # i.e in assignment operation we are setting isLiad true if the expression is in right hand side
        if expr.isLoad:
            # loading instructions are generated
            arm.hload(r1,base.reg, r)
            expr.reg = r1
        # base reg and offset reg are set to handle assignment if expr is on lhs
        expr.baseReg = base.reg
        expr.offsetReg = r

    elif isinstance(expr, NewArrayExpr):
        baseType = expr.basetype
        args = expr.args
        size = 1
        dim = []
        # each index is sent for code generation
        # after that reg value is taken expr.reg and that value is used
        # in setting dim of var expr
        # dim in var expression will be used when arrayAccess expr
        for i in range(0, len(args)):
            codegenExpr(args[i], arm)
            dim += [args[i].reg]

        r1 = "t" + `arm.tempregisterCount`
        arm.tempregisterCount += 1
        arm.move_immed_i(r1, 1)
        # multiple all the values in registers of indexes and count the offset
        # and space to be allocated in the heap
        for i in range(0, len(args)):
            # instructions which will run to calculate the size of the array
            arm.imul(r1, r1, args[i].reg)

        r2 = "t" + `arm.tempregisterCount`
        arm.tempregisterCount += 1
        # allocate space in the heap
        arm.halloc(r2, r1)
        expr.reg = r2
        expr.dim = dim
import ast
from ast import *

class ARM:
    def __init__(self):
        self.static_data = 0
        self.codeStr = ""
        self.tempregisterCount = 0
        self.labelCounter = -1
        self.sFieldOffset = {}
        self.nsFieldOffset = {}

    def resetRegisterCount(self):
        self.tempregisterCount = 0
        self.argumentRegCount = 0

    def initializeFields(self):
        self.allocateStaticFields()
        self.initializeInstanceFields()

    def initializeInstanceFields(self):
        count = 0
        for cid in ast.classtable:
            c = ast.classtable[cid]
            if not c.builtin:
                self.nsFieldOffset[c.name] = {}
                superClass = c.superclass
                while superClass is not None:
                    self.nsFieldOffset[c.name].update(self.nsFieldOffset[superClass.name])
                    superClass = superClass.superclass
                for field in c.fields:
                    if str(c.fields[field].storage) is 'instance':
                        self.nsFieldOffset[c.name][c.fields[field].id] = count
                        count += 1

    def getObjectSize(self, className):
        return len(self.nsFieldOffset[className])

    def allocateStaticFields(self):
        for cid in ast.classtable:
            c = ast.classtable[cid]
            if not c.builtin:
                self.sFieldOffset[c.name] = {}
                for field in c.fields:
                    if str(c.fields[field].storage) is 'static':
                        self.sFieldOffset[c.name][c.fields[field].name] = self.static_data
                        self.static_data += 1
        self.codeStr += ".static_data %d" % (self.static_data)
        self.codeStr += "\n\n"

    def add_label(self, l):
        self.codeStr += "%s:" % (l)
        self.codeStr += "\n"

    def add_newLine(self):
        self.codeStr += "\n"

    def incLabelCounter(self):
        self.labelCounter += 1
        return 'L_' + `self.labelCounter`

    def move_immed_i(self, r, i):
        self.codeStr += "move_immed_i %s, %d" % (r, i)
        self.codeStr += "\n"

    def move_immed_f(self, r, f):
        self.codeStr += "move_immed_f %s, %d" % (r, f)
        self.codeStr += "\n"

    def move(self, r1, r2):
        self.codeStr += "move %s, %s" % (r1, r2)
        self.codeStr += "\n"

    def iadd(self, r1, r2, r3):
        self.codeStr += "iadd %s, %s, %s" % (r1, r2, r3)
        self.codeStr += "\n"

    def isub(self, r1, r2, r3):
        self.codeStr += "isub %s, %s, %s" % (r1, r2, r3)
        self.codeStr += "\n"

    def imul(self, r1, r2, r3):
        self.codeStr += "imul %s, %s, %s" % (r1, r2, r3)
        self.codeStr += "\n"

    def idiv(self, r1, r2, r3):
        self.codeStr += "idiv %s, %s, %s" % (r1, r2, r3)
        self.codeStr += "\n"

    def imod(self, r1, r2, r3):
        self.codeStr += "imod %s, %s, %s" % (r1, r2, r3)
        self.codeStr += "\n"

    def igt(self, r1, r2, r3):
        self.codeStr += "igt %s, %s, %s" % (r1, r2, r3)
        self.codeStr += "\n"

    def igeq(self, r1, r2, r3):
        self.codeStr += "igeq %s, %s, %s" % (r1, r2, r3)
        self.codeStr += "\n"

    def ilt(self, r1, r2, r3):
        self.codeStr += "ilt %s, %s, %s" % (r1, r2, r3)
        self.codeStr += "\n"

    def ileq(self, r1, r2, r3):
        self.codeStr += "ileq %s, %s, %s" % (r1, r2, r3)
        self.codeStr += "\n"

    def fadd(self, r1, r2, r3):
        self.codeStr += "fadd %s, %s, %s" % (r1, r2, r3)
        self.codeStr += "\n"

    def fsub(self, r1, r2, r3):
        self.codeStr += "fsub %s, %s, %s" % (r1, r2, r3)
        self.codeStr += "\n"

    def fmul(self, r1, r2, r3):
        self.codeStr += "fmul %s, %s, %s" % (r1, r2, r3)
        self.codeStr += "\n"

    def fdiv(self, r1, r2, r3):
        self.codeStr += "fdiv %s, %s, %s" % (r1, r2, r3)
        self.codeStr += "\n"

    def fgt(self, r1, r2, r3):
        self.codeStr += "fgt %s, %s, %s" % (r1, r2, r3)
        self.codeStr += "\n"

    def fgeq(self, r1, r2, r3):
        self.codeStr += "fgeq %s, %s, %s" % (r1, r2, r3)
        self.codeStr += "\n"

    def flt(self, r1, r2, r3):
        self.codeStr += "flt %s, %s, %s" % (r1, r2, r3)
        self.codeStr += "\n"

    def fleq(self, r1, r2, r3):
        self.codeStr += "fleq %s, %s, %s" % (r1, r2, r3)
        self.codeStr += "\n"

    def ftoi(self, r1, r2):
        self.codeStr += "ftoi %s, %s" % (r1, r2)
        self.codeStr += "\n"

    def itof(self, r1, r2):
        self.codeStr += "itof %s, %s" % (r1, r2)
        self.codeStr += "\n"

    def bz(self, r, l):
        self.codeStr += "bz %s, %s" % (r, l)
        self.codeStr += "\n"

    def bnz(self, r, l):
        self.codeStr += "bnz %s, %s" % (r, l)
        self.codeStr += "\n"

    def jmp(self, l):
        self.codeStr += "jmp %s" % (l)
        self.codeStr += "\n"

    def hload(self, r1, r2, r3):
        self.codeStr += "hload %s, %s, %s" % (r1, r2, r3)
        self.codeStr += "\n"

    def hstore(self, r1, r2, r3):
        self.codeStr += "hstore %s, %s, %s" % (r1, r2, r3)
        self.codeStr += "\n"

    def halloc(self, r1, r2):
        self.codeStr += "halloc %s, %s" % (r1, r2)
        self.codeStr += "\n"

    def callMethod(self, name, id):
        self.codeStr += "call M_%s_%d" % (name, id)
        self.codeStr += "\n"

    def callConstructor(self, id):
        self.codeStr += "call C_%d" % (id)
        self.codeStr += "\n"

    def ret(self):
        self.codeStr += "ret"
        self.codeStr += "\n"

    def save(self, r):
        self.codeStr += "save %s" % (r)
        self.codeStr += "\n"

    def restore(self, r):
        self.codeStr += "restore %s" % (r)
        self.codeStr += "\n"
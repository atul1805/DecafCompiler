class MIPS:
    def __init__(self):
        self.static_data = 0
        self.initStr= ''
        self.codeStr = ''
        self.finalStr = ''
        self.saveCount = 0
        self.stackMap = {}
        self.stackOff = 0
        self.opcodeMap = {
                'iadd' : 'add',
                'isub' : 'sub',
                'imul' : 'mul',
                'idiv' : 'div',
                'imod' : 'rem',
                'igt' : 'sgt',
                'igeq' : 'sge',
                'ilt' : 'slt',
                'ileq' : 'sle',
                'bz' : 'beqz',
                'bnz' : 'bnez',
                'jmp' : 'j',
                'ret' : 'jr $ra',
                'call' : 'jal',
                'save' :'sw',
                'restore' : 'lw'
                }

    def add_preamble(self):
        self.finalStr += '# preamble \n'
        self.finalStr += '.text'
        self.finalStr += "\n"


    def add_label_str(self, label):
        self.codeStr += "%s:" % (label)

    def icToMips(self, funcName, fObj):
        for instruct in fObj.instrns:
            if instruct.opcode is None:
                self.add_label_str(instruct.label)
            elif str(instruct.opcode) == 'move_immed_i':
                self.codeStr += "li %s, %s" % (getReg(instruct.args[0], fObj), instruct.args[1])
            elif str(instruct.opcode) == 'move':
                self.codeStr += "move %s, %s" % (getReg(instruct.args[0], fObj), getReg(instruct.args[1], fObj))
            elif str(instruct.opcode) == 'iadd' or str(instruct.opcode) == 'isub' or str(instruct.opcode) == 'imul' or str(instruct.opcode) == 'idiv' or str(instruct.opcode) == 'imod' \
                     or str(instruct.opcode) == 'igt' or str(instruct.opcode) == 'igeq' or str(instruct.opcode) == 'ilt' or str(instruct.opcode) == 'ileq':
                self.codeStr += "%s %s, %s, %s" % (self.opcodeMap[instruct.opcode], getReg(instruct.args[0], fObj), getReg(instruct.args[1], fObj), getReg(instruct.args[2], fObj))
            elif str(instruct.opcode) == 'bz' or str(instruct.opcode) == 'bnz':
                self.codeStr += "%s %s, %s" % (self.opcodeMap[instruct.opcode], getReg(instruct.args[0], fObj), instruct.args[1])
            elif str(instruct.opcode) == 'jmp' or str(instruct.opcode) == 'call':
                self.codeStr += "%s %s" % (self.opcodeMap[instruct.opcode], instruct.args[0])
                if(str(instruct.opcode) == 'call'):
                    self.codeStr += '\nmove $a0, $v0'
            elif str(instruct.opcode) == 'save' or str(instruct.opcode) == 'restore':
                if str(instruct.opcode) == 'save':
                    self.codeStr += "sw %s, %d($sp)"%(getReg(instruct.args[0], fObj), self.stackOff)
                    self.stackMap[getReg(instruct.args[0], fObj)] = self.stackOff
                    self.stackOff -= 4
                    self.saveCount += 1
                if str(instruct.opcode) == 'restore':
                    self.codeStr += "lw %s, %d($sp)" % (getReg(instruct.args[0], fObj), self.stackMap[getReg(instruct.args[0], fObj)])
            elif str(instruct.opcode) == 'ret':
                if funcName == 'main_entry_point':
                    self.codeStr += 'li $v0, 10\nsyscall'
                else:
                    self.codeStr += "move $v0, $a0\nlw $ra, %d($sp)\nlw $fp, %d($sp)\naddu $sp, $sp, %d\njr $ra"%(self.sizeOfStack - 4,self.sizeOfStack - 8, self.sizeOfStack)
            self.codeStr += "\n"

    def getCounts(self, funcName, fObj):
        for instruct in fObj.instrns:
            if str(instruct.opcode) == 'move_immed_i':
                getReg(instruct.args[0], fObj)
            elif str(instruct.opcode) == 'move':
                getReg(instruct.args[0], fObj)
                getReg(instruct.args[1], fObj)
            elif str(instruct.opcode) == 'iadd' or str(instruct.opcode) == 'isub' or str(instruct.opcode) == 'imul' or str(instruct.opcode) == 'idiv' or str(instruct.opcode) == 'imod' \
                     or str(instruct.opcode) == 'igt' or str(instruct.opcode) == 'igeq' or str(instruct.opcode) == 'ilt' or str(instruct.opcode) == 'ileq':
                getReg(instruct.args[0], fObj)
                getReg(instruct.args[1], fObj)
                getReg(instruct.args[2], fObj)
            elif str(instruct.opcode) == 'bz' or str(instruct.opcode) == 'bnz':
                getReg(instruct.args[0], fObj)
            elif str(instruct.opcode) == 'save' or str(instruct.opcode) == 'restore':
                if str(instruct.opcode) == 'save':
                    getReg(instruct.args[0], fObj)
                    self.saveCount += 1
                if str(instruct.opcode) == 'restore':
                    getReg(instruct.args[0], fObj)

    def generatePreamble(self, funcName):
        global argSet
        self.initStr += "%s:\n" % (funcName)
        self.sizeOfStack = (len(argSet) + self.saveCount + 2)*4
        self.saveCount = 0
        if self.sizeOfStack <= 32:
            self.initStr += 'subu $sp, $sp, 32\n'
            self.sizeOfStack = 32
        else:
            self.initStr += 'subu $sp, $sp, %d\n'%(self.sizeOfStack)
        self.initStr += 'sw $ra, %d($sp)\n'%(self.sizeOfStack - 4)
        self.initStr += 'sw $fp, %d($sp)\n'%(self.sizeOfStack - 8)
        self.initStr += 'addu $fp, $sp, %d\n'%(self.sizeOfStack)
        self.stackOff = self.sizeOfStack - 8

    def generateCode(self, labelFuncMap):
        global argSet
        for funcName in labelFuncMap:
            self.getCounts(funcName, labelFuncMap[funcName])
            self.generatePreamble(funcName)
            self.icToMips(funcName, labelFuncMap[funcName])
            self.codeStr += '\n'
            self.finalStr += self.initStr + self.codeStr.replace("sizeOfStack", str(self.sizeOfStack))
            self.initStr = ''
            self.codeStr = ''
            argSet = set()

argSet = set()
def getReg(reg, fObj):
    global argSet
    if reg in fObj.tempLookup:
        return fObj.tempLookup[reg]
    argSet.add(reg)
    return '$' + reg
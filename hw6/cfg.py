import re
from copy import deepcopy
from mips import *
# class to represent each function in ic
# contains list of blocks and all instructions.
class function:
    def __init__(self):
        self.blockList = []
        self.instrns = []
        self.tempLookup = {}
        self.argLookup = {}

    def addBlock(self, b):
        self.blockList += [b]

    def addInstructions(self, i):
        self.instrns += [i]

    def setTempLookup(self, t):
        self.tempLookup = deepcopy(t)

    def setArgLookup(self, a):
        self.argLookup = deepcopy(a)

# class to represent each block,
# contains list of instructions present in the block
#each block  should be instantiated using and ID

class Block:
    def __init__(self, id):
        self.id = id
        self.instrns = []
        self.successors = []
        self.defined = set()
        self.used = set()
        self.In = set()
        self.Out = set()

    def addInstructions(self, i):
        self.instrns += [i]

    def addSucc(self, s):
        self.successors += [s]

    def addDef(self, d):
        self.defined.add(d)

    def addUsed(self, u):
        self.used.add(u)


#instructions object for each line in the IC
# Contains Label if any, opcode and args
class instructions:
    def __init__(self, label, opcode, args):
        self.label = label
        self.opcode = opcode
        self.args = args

def canIgnore(l):
    l.strip()
    if (len(l) == 0) or (l[0] == '.'):
        return True
    else:
        return False

wordpattern = "[ \t\n]+|,"
# read each linne and process
def read_instr(str):
    instr = str
    if (":" in instr):
        parts = instr.split(":")
        label = parts[0]
        instr = parts[1]
    else:
        label = ""
    opargs = re.split(wordpattern, instr)
    opargs = [w for w in opargs if w != '']
    if (len(opargs) < 1):
        return (label, None, None)
    else:
        return (label, opargs[0], opargs[1:])

labelToBlock = {}

#Give block objects populate successors for each block
#For each block check if jump statements exist in the last instruction
# if yes then add successor as the line number of the label to which we are jumping
def populateSucc(blkObj, countBlks):
    if blkObj.id + 1 < countBlks:
        blkObj.addSucc(blkObj.id + 1)

    if len(blkObj.instrns) == 0:
        return

    lastInstruction = blkObj.instrns[len(blkObj.instrns) - 1]
    lastInsLabel = ''
    ## if lastinstruction is bz or bnz then take the label present in argument 1
    if str(lastInstruction.opcode) == 'bz'or str(lastInstruction.opcode) == 'bnz':
        lastInsLabel = lastInstruction.args[1]
    ## if last Instruction is jmp then take the label from argument 0
    elif str(lastInstruction.opcode) == 'jmp':
        lastInsLabel = lastInstruction.args[0]
    if lastInsLabel != '':
        blkObj.addSucc(labelToBlock[lastInsLabel])

# populate defined variable in a block,
# check if ipcode doesn't belong to types : bz bnz jmp hstore call ret
#then take arg 0 since it is defined in that instruction
def populateDef(blkObj):
    for ins in blkObj.instrns:
        if str(ins.opcode) != 'bz' and str(ins.opcode) != 'bnz'and str(ins.opcode) != 'jmp' \
            and str(ins.opcode) != 'hstore' and str(ins.opcode) != 'call' and str(ins.opcode) != 'ret' \
            and str(ins.opcode) != 'save' and ins.opcode is not None:
            blkObj.addDef(ins.args[0])

# populate used variables
def populateUse(blkObj):
    for ins in blkObj.instrns:

        if str(ins.opcode) == 'jmp' or str(ins.opcode) == 'call' or str(ins.opcode) == 'ret' \
            or str(ins.opcode) == 'restore' or 'move_immed' in str(ins.opcode):
            continue
        elif str(ins.opcode) == 'bz' or str(ins.opcode) == 'bnz' or str(ins.opcode) =='save':
            blkObj.addUsed(ins.args[0])
        elif str(ins.opcode) == 'hstore':
            for arg in ins.args:
                blkObj.addUsed(arg)
        elif ins.opcode is not None:
            for i in range(1, len(ins.args)):
                blkObj.addUsed(ins.args[i])

## read the instructions and create blocks.
##
def createBlocks(fObj):
    insCounter = 0
    start = []
    labelIndex = {}
    for ins in fObj.instrns:
        if len(ins.label) != 0:
            labelIndex[ins.label] = insCounter
        insCounter += 1
    insCounter = 0
    for ins in fObj.instrns:
        ## check for jump statements and add into a list
        if str(ins.opcode) == 'bz' or str(ins.opcode) == 'bnz':
            start += [labelIndex[ins.args[1]]]
            start += [insCounter + 1]
        elif str(ins.opcode) == 'jmp':
            start += [labelIndex[ins.args[0]]]
            start += [insCounter + 1]
        insCounter += 1
    if 0 not in start:
        start += [0]
    if insCounter not in start:
        start += [insCounter]
    start.sort()
    blockCounter = 0
    blkObj = Block(blockCounter)
    blockCounter += 1
    for i in range(0, len(start) - 1):
        for idx in range(start[i], start[i + 1]):
            ## create a dict with label as key and block id as value.
            blkObj.addInstructions(fObj.instrns[idx])
            if len(fObj.instrns[idx].label) != 0:
                labelToBlock[fObj.instrns[idx].label] = blkObj.id
        fObj.addBlock(blkObj)
        blkObj = Block(blockCounter)
        blockCounter += 1
    for blk in fObj.blockList:
        populateSucc(blk, len(fObj.blockList))
        populateDef(blk)
        populateUse(blk)


def getBlock(id, fObj):
    for blk in fObj.blockList:
        if blk.id == id:
            return blk
#  check if register allocation is converged by checking present value with previous values
def hasConverged(prevIn, prevOut, fObj):
    i = 0
    for blk in reversed(fObj.blockList):
        if blk.In != prevIn[i] or blk.Out != prevOut[i]:
            return False
        i += 1
    return True

# Liveness analysis by calculating In and out for each of the block
# initially assign empty set for in and out
# then substitute those for all the blocks and check if the values converge
# when converges exit
def liveness(fObj):
    prevIn = []
    prevOut = []
    for blk in reversed(fObj.blockList):
        prevIn.append(blk.In)
        prevOut.append(blk.Out)
    while True:
        for blk in reversed(fObj.blockList):
            for s in blk.successors:
                blk.Out |= getBlock(s, fObj).In
            blk.In = blk.used | (blk.Out - blk.defined)
        if hasConverged(prevIn, prevOut, fObj):
            break
        prevIn = []
        prevOut = []
        for blk in reversed(fObj.blockList):
            prevIn.append(blk.In)
            prevOut.append(blk.Out)

## create Register Interference graph for all the nodes in a method
## each node will have a map from one register to all the interfering registers
def createRIG(InList):
    graph = {}
    for In in InList:
        for reg in In:
            if reg not in graph:
                graph[reg] = set()
            for otherReg in In:
                if str(reg) != str(otherReg):
                    graph[reg].add(otherReg)
    return graph

## allocate reg by looking up
def allocateReg(fObj):
    temp = []
    arg = []
    for blk in fObj.blockList:
        tSet = set()
        aSet = set()
        for reg in blk.In:
            if 't' in reg:
                tSet.add(reg)
            elif 'a'in reg:
                aSet.add(reg)
        temp.append(tSet)
        arg.append(aSet)
    # call color graph for each tree
    fObj.setTempLookup(colorGraph(createRIG(temp), 10, True))
    fObj.setArgLookup(colorGraph(createRIG(arg), 4, False))

def getVertex(graph, K):
    for v in graph:
        if len(graph[v]) < K:
            return v
    return None

def removeEdges(graph, v):
    graph.pop(v)
    for node in graph:
        graph[node] -= {v}

def getSpillNode(graph):
    max = -1
    v = ''
    for node in graph:
        if len(graph[node]) > max:
            max = len(graph[node])
            v = node
    return v

def getRegister(vertex, graph, regLookup, regList):
    neighbours = graph.get(vertex)
    regUsed = set()

    for v in neighbours:
        if v in regLookup:
            regUsed.add(regLookup.get(v))
    tempRegList = deepcopy(regList)
    tempRegList -= regUsed
    if not tempRegList:
        return None
    else:
        return tempRegList.pop()

def colorGraph(graph, K, isTemp):
    regLookup = {}
    regList = set()

    regPrefix = 'a'
    if isTemp:
        regPrefix = '$t'
    graphCopy = deepcopy(graph)
    stack = []
    for i in range(0, K):
        regList.add(regPrefix + str(i))
    while len(graphCopy) != 0:
        v = getVertex(graphCopy, K)
        if v is not None:
            removeEdges(graphCopy, v)
        else:
            v = getSpillNode(graphCopy)
            removeEdges(graphCopy, v)
        stack += [v]
    for vertex in reversed(stack):
        reg =  getRegister(vertex, graph, regLookup, regList)
        regLookup.update({vertex : reg})
    return regLookup

labelFuncMap = {}
# takes intermediate code string as input, reads each line and creates function objects
# each function objects contains list of blocks and each block contains list of instructions

def main(IC):
    global blockCounter
    fObj = function()
    mips = MIPS()

    prevLabel = ''
    for line in IC.splitlines():
        if canIgnore(line):
            continue
        (label, opcode, args) = read_instr(line)
        if 'C_' in label or 'M_' in label or 'main_entry_point' in label:
                if len(fObj.instrns) != 0:
                    createBlocks(fObj)
                    labelFuncMap[prevLabel] = fObj
                    fObj = function()
                prevLabel = label
        else:
            fObj.addInstructions(instructions(label, opcode, args))

    mips.add_preamble()
    for label in labelFuncMap:
        liveness(labelFuncMap[label])
        allocateReg(labelFuncMap[label])
    mips.generateCode(labelFuncMap)
    return mips.finalStr
import sys
import Queue

Word = str
class Stack:
     def __init__(self):
         self.items = []

     def isEmpty(self):
         return self.items == []

     def push(self, item):
         self.items.append(item)

     def pop(self):
         return self.items.pop()

     def peek(self):
         return self.items[len(self.items)-1]

     def size(self):
         return len(self.items)

counter = 0
variables = Queue.Queue()
varValue = {}
memory = {}
operator = Stack()
operand = Queue.Queue()

def convertToSSM():
    global counter
    global variables
    global varValue
    
    while not variables.empty():
        var = variables.get()
        value = varValue[var]
        print "ildc ", counter
        memory[var] = counter
        counter += 1
        for item in value:
            if item == '+' or item == '-' or item == '*' or item == '/' or item == '%':
                operator.push(item)
            else:
                operand.put(item)
        while not operand.empty():
            opr = operand.get()
            try: 
                if opr == int(opr):
                    print "ildc", opr
            except:
                if opr not in memory:
                    print "ERROR: not initialized"
                    exit()
                else:
                    print "ildc", memory[opr]
                    print "load"
        while not operator.isEmpty():
            op = operator.pop()
            if op == '+':
                print "iadd"
            elif op == '-':
                print "isub"
            elif op == '*':
                print "imul"
            elif op == '/':
                print "idiv"
            elif op == '%':
                print "imod"				
        print "store"

def validate(token):
    global variables
    global varValue

    if len(token) == 0:
        return	
    if token[1] is not '=':
        print "Syntax Error"
        exit()

    variables.put(token[0])
    value = []
    for i in range(2, len(token)):
        value.append(tokenise(token[i]))
    varValue[token[0]] = value

def tokenise(token):
    try:
        if '~' in token:
            return -1 * int(token[+1:])
        else:
            return int(token)
    except ValueError:
        return Word(token)

def parse(program):
    lists = program.split(';')
    for list in lists:
        if len(list) > 0:
            validate(list.split())

def read():
    for line in sys.stdin:
        parse(line)
    convertToSSM()

if __name__ == '__main__':
    read()
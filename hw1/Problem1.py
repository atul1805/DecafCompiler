import re
import sys
import copy
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

programStack = Stack()
store ={}
label = {}
pattern = re.compile("\w+[\\:]+(?= |$)")
commentPattern = re.compile("[\\#]+\w+(?= |$)")
presentLabel ='empty'
labelInstructions = []
def evaluate(input, index,env=programStack):
    if len(input)==0:
        return
    iValue = input[index]
    if iValue=='ildc':
        index=index+1
        next = input[index]
        if isinstance(next,int):
            programStack.push(next)
        else:
            print "Invalid Syntax"
            sys.exit()
    elif iValue=='iadd':
        x = programStack.pop()
        y = programStack.pop()
        z = x+y
        programStack.push(tokenise(z))

    elif iValue=='isub':
        x = programStack.pop()
        y = programStack.pop()
        z = y-x
        programStack.push(tokenise(z))

    elif iValue=='imul':
        x = programStack.pop()
        y = programStack.pop()
        z = y*x
        programStack.push(tokenise(z))

    elif iValue=='idiv':
        x = programStack.pop()
        x = programStack.pop()
        y = programStack.pop()
        z = y/x
        programStack.push(tokenise(z))

    elif iValue=='pop':
        programStack.pop()

    elif iValue=='dup':
        x = programStack.peek()
        programStack.push(x)

    elif iValue=='swap':
        x = programStack.pop()
        y = programStack.pop()
        programStack.push(x)
        programStack.push(y)

    elif iValue=='store':
        x= programStack.pop()
        y=programStack.pop()
        store.update({y:x})

    elif iValue=='load':
        x = programStack.pop()
        programStack.push(store.get(x))

    elif iValue=='jmp':
        index = index+1
        new_label = input[index]
        try:
            new_index = input.index(new_label+":")
        except ValueError:
            print('wrong label ::'+new_label)
            sys.exit()
        index = new_index
    elif iValue=='jz':
        index = index+1
        x = programStack.pop()
        if x ==0:
            new_label = input[index]
            new_index= input.index(new_label+":")
            index = new_index

    index = index+1
    return index



def validate(token,presen = presentLabel):
    global presentLabel
    global labelInstructions
    global label

    if len(token)==0:
        return


    L=[]
    for var in token:
        if(commentPattern.match(var)):
            return L
        if pattern.match(var):
            presentLabel = var[:-1]
            labelInstructions=[]
        else:
            if presentLabel is not 'empty':
                labelInstructions.append(tokenise(var))
                label.update({presentLabel: labelInstructions})

        L.append(tokenise(var))


    return L

def tokenise(token):

    try: return int(token)
    except ValueError:
        return Word(token)

def parse(program):

    return validate(program.split())

def read():

    input=[]
    for line in sys.stdin:
        value = parse(line)
        if value is not None:
            input= input+value
    index = 0
    size= len(input)

    while(size-index>0):
        index =evaluate(input,index)

    if programStack.isEmpty():
        print "Nothing in stack"
    else :
        print(str(programStack.pop()))

if __name__ == '__main__':
    read()
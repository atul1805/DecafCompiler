
#each class, variabl and method constructor field is considered as an object and instantiated from this class.
# each object is part of another object Node which keeps track of the id's of the respective entitiy.

class Node(object):
    # to accoun the class ids
    class_count = 0
    # to account the number of constructors in a given class and reset everytime a new class is created
    constructor_count = 0
    # keepts count the number of methods in a class and resets the vlaue everytime a new class is created
    method_count = 0
    #same as constructor and method
    field_count = 0
    # variable count is specific to a method and constructor so, is reset whenevver a new method or constrcutro is callled.
    var_count = 0

    def __init__(self, case):
        if case is "class":
            Node.class_count += 1
            #class count is incremented everytime a class is created
            self.node_id = Node.class_count

    	if case is "constructor":
            #variable list count is reset evertime a constructor is called here
            Node.var_count=0
            #constructor number is set here incremented evertime a new constructor is called
            Node.constructor_count += 1
            self.node_id = Node.constructor_count
    	if case is "method":
            #variable list count is reset everytime a method is called
            Node.var_count=0
            #method count is increamented
            Node.method_count += 1
            #node id of method is set using method_cuiunt
            self.node_id = Node.method_count
    	if case is "field":
            Node.field_count += 1
            self.node_id = Node.field_count
        if case is "variable":
            Node.var_count += 1
            self.node_id = Node.var_count

class Helper():
    def setVariableID(self, variableTable):
        if variableTable is None:
            return
        varCount = 0
        for var in variableTable:
            varCount += 1
            var.node_id = varCount

#variable class which contains name type and kind
#object is initialized with mnetioned args and
class Variable(Node):
    def __init__(self, name, type, kind=None):
        super(Variable,self).__init__("variable")
        self.name = name
        self.kind = kind
        self.type = type

    #to string for variable class, this is called when print is called for variable object.
    def __str__(self):
        return "\nVARIABLE %s, %s, %s, %s" % (self.node_id, self.name, self.kind, self.type)

# constructor objecct is called from the decafParser.py with arguments as visibility paramenters  vriableTable body
#variableTable is  a list of variable objects and body is a string returned from yacc.

class Constructor(Node):
    def __init__(self, visibilty, parameters=None, variableTable=None, body=None):
        super(Constructor,self).__init__("constructor")
        self.visibilty = visibilty
        self.parameters = []
        #parameters list is populated from variable table by checking for formal type variable and assigning the variable id to this paramenter list.
        for var in variableTable:
            if var.kind is "formal":
                self.parameters += [var.node_id]
        self.variableTable = variableTable
        self.body = body
        #Helper().setVariableID(variableTable)

    def __str__(self):
        return "CONTRUCTOR: %s, %s\nConstructor Parameters: %s\nVariable Table: %s\nConstructor Body:\n%s" % \
		(self.node_id, self.visibilty, ','.join(map(str, self.parameters)), ''.join(map(str, self.variableTable)), self.body)

class Method(Node):
    def __init__(self, methodName, className, visibility, applicability,  returnType, parameters=None, variableTable=None, body=None):
        super(Method,self).__init__("method")
        self.methodName = methodName
        self.className = className
        self.visibility = visibility
        self.applicability = applicability
        self.parameters = []
        #parameters list is populated from variable table by checking for formal type variable and assigning the variable id to this paramenter list.

        for var in variableTable:
            if var.kind is "formal":
                self.parameters += [var.node_id]
        self.returnType = returnType
        self.variableTable = variableTable
        self.body = body
        #Helper().setVariableID(variableTable)

    def __str__(self):
        return "Method: %s, %s, %s, %s, %s, %s\nMethod Parameters: %s\nVariable Table: %s\nMethod Body:\n%s" % \
		(self.node_id, self.methodName, self.className, self.visibility, self.applicability, self.returnType, ','.join(map(str, self.parameters)), ''.join(map(str, self.variableTable)), self.body)

class Field(Node):
    def __init__(self, fieldName, className, visibility, applicability, type):
        super(Field,self).__init__("field")
        self.fieldName =fieldName
        self.className =className
        self.visibility = visibility
        self.applicability = applicability
        self.type = type

    def __str__(self):
        return "Field: %s, %s, %s, %s, %s, %s" % (self.node_id,self.fieldName,self.className,self.visibility,self.applicability,self.type)

class ClassDecl(Node):
    def __init__(self, className, superClassName , classDeclarationList):
        super(ClassDecl,self).__init__("class")
        self.className =className
        self.superClassName = superClassName
        self.constructor = []
        self.methods = []
        self.fields = []
        # class declarationList contains Constructor declarations, methodDeclarations and FieldDeclarations
        #which should be added to their respective list by checking the instance type of each object.
        for classDeclaration in classDeclarationList:
            if isinstance(classDeclaration, Method):

                classDeclaration.className = className
                # adding to method list
                self.methods += [classDeclaration]
            elif isinstance(classDeclaration, Constructor):
                # add to constructor list
                self.constructor += [classDeclaration]
            elif isinstance(classDeclaration, Field):
                classDeclaration.className = className
                #add to filed list
                self.fields += [classDeclaration]

    #to string to print hte class object after the end of the processing.
    def __str__(self):
        return "class name : %s\nSuper ClassName: %s\nConstructors:\n" \
               "%s\nMethods :\n%s\nFields: \n%s\n"% (self.className,self.superClassName, '\n'.join(map(str, filter(None,self.constructor))),'\n'.join(map(str, filter(None,self.methods))), '\n'.join(map(str, filter(None,self.fields))))

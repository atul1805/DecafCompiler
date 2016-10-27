Problem 1 :
	Run details :
	
	> Problem1.py
	> ildc 20
    > ildc 5
	> here: 
	> ildc 1
    > isub
    > dup
    > jz   there
    > swap
    > ildc 10
    > iadd
    > swap
    > jmp  here
	> there:
    > pop
	
	Ctrl + D to terminate and get the result
	
	The code runs in two steps 
	1. Lexical Analysis
		In the first step input is parsed and checked for any errors, but code is not evaluated yet. Each input is added into a list, 
	and that list contains all the variables except for whitespaces added into it. 
	2. Evaluation
		Evaluation will happen when end of line is observer i.e when user enters Ctrl + D, then the input list is sent for evaluation.
	while evaluating each string is checked against valid arguments and accordingly the action is taken. 
	
	Program can handle multiple instructions in single line. and error will be thrown when argument is not integer.
	
Problem 2 :
	Run Details :
	
	> python Problem2.py
	> x = ~10;
	> y = - x 1;
	> z = * x * y + x y;
	
	Ctrl + D to terminate and get the result
	
	The code runs in two steps
	1. Syntax Analysis and populating the data structures
		In the first step input is parsed and checked for any errors. Every encountered variable is added to a queue and its associated evaluation string
		is mapped in a dictionary. e.g y = - x 1; so y is added to a queue and mapped as y -> ['-', 'x', '1'] and so on for every variable.
	2. Evaluation
		Evaluation will happen when end of line is observer i.e. when user enters Ctrl + D. In evaluation phase, for each variable a combination of stack
		and queue has been used to get the desired result. Queue is used to load all the variables and integers needed for evaluation. Stack is used to 
		add all the arithmetic codes (iadd, isub ...).
		
	Assumption:
		1. No whitespace characters should be there between '~' and variable.
		2. WhiteSpace characters should be present between other operators(+, - , *, /, %), variables(x, y, z....) and '='.
		
	The program can handle multiple instructions in one line. For e.g. x = 10; y = - x 1;
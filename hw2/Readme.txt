To Run the code:

	python decafch.py --input="path/to/input_file"
	
Main Top Level - decafch.py

	If everything goes well "YES" would be displayed, otherwise the errors with line numbers and lexical positions will be displayed.


LEXER - decaflexer.py
	
	All possible tokens were accounted for. Additionally, Reserved Words and constants were also included. Line Numbers and lexical positions are incremented
	accordingly and has been used in diplaying syntax errors.


PARSER - decafparser.py

	Syntax is Specified in EBNF form. For example:
		classDec : CLASS ID LBRA classBody RBRA
                   | CLASS ID EXTENDS ID LBRA classBody RBRA
	Precedence has been defined for binary operators. Multiple Errors can be detected by using the Panic mode recovery technique.
	
Our parser gives 14 shift/reduce conflicts. On examination of parser.out, all the shift/reduce conflicts occur due to arithmetic and boolean operators.
Since the precendence has been set, the conflicts are being resolved by the parser by shifting the correct operator.
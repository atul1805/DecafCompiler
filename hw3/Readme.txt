To Run:

python decafch.py filename.decaf

README.txt:		this file
decaflexer.py	PLY/lex specification of Decaf tokens.
decafparser.py	PLY/yacc specification of Decaf grammar.
				The encoded grammar rules appear in the same order as in decaf manual.
				Defines "from_file" function that takes a file name and parses that file's contents.
				"from_file" returns True if no error, and False if error.
				While matching various expressions, the objects in ast.py are populated accordingly to build an AST.
decafch.py		Driver: processes arguments and gets file name to pass to decafparser.from_file
				Decaf programs are assumed to be in files with ".decaf" suffix.
				Argument given to decafch may omit this suffix; e.g.
				python decafch test
				will read from test.decaf.

		
ast.py	This contains class declaration for various objects like constructors, methods, fields, variable and class itself.


# Run As python decafch.py --input="code.decaf"

import argparse
import decaflexer
import decafparser

def parse(input):
    code = ""
    with open(input) as f:
        for line in f:
            code += line

    decaflexer.parse(code)
    decafparser.parse(code)
    if decafparser.isValid:
        print "YES"
    

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="LEXER")
    parser.add_argument("--input", type=str)
    args = parser.parse_args()
    parse(args.input)
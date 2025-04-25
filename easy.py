import ply.lex as lex
import ply.yacc as yacc
import sys

# --- Lexer ---
tokens = (
    'NUMBER', 'IDENTIFIER', 'EQUALS', 'PLUS', 'MINUS', 'MULTIPLY', 'DIVIDE',
    'PRINT', 'SEMICOLON', 'LPAREN', 'RPAREN', 'IF', 'ELSE', 'WHILE', 'FOR',
    'LBRACE', 'RBRACE', 'COMMA', 'STRING', 'TRUE', 'FALSE', 'AND', 'OR', 'NOT',
    'EQUAL', 'NOTEQUAL', 'LESS', 'GREATER', 'LESSEQUAL', 'GREATEREQUAL'
)

# Keywords
def t_IF(t):
    r'if'
    return t

def t_ELSE(t):
    r'else'
    return t

def t_WHILE(t):
    r'while'
    return t

def t_FOR(t):
    r'for'
    return t

def t_PRINT(t):
    r'print'
    return t

def t_TRUE(t):
    r'true'
    t.value = True
    return t

def t_FALSE(t):
    r'false'
    t.value = False
    return t

# Operators
t_EQUALS = r'='
t_PLUS = r'\+'
t_MINUS = r'-'
t_MULTIPLY = r'\*'
t_DIVIDE = r'/'
t_AND = r'&&'
t_OR = r'\|\|'
t_NOT = r'!'
t_EQUAL = r'=='
t_NOTEQUAL = r'!='
t_LESS = r'<'
t_GREATER = r'>'
t_LESSEQUAL = r'<='
t_GREATEREQUAL = r'>='

# Delimiters
t_SEMICOLON = r';'
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_LBRACE = r'\{'
t_RBRACE = r'\}'
t_COMMA = r','

def t_STRING(t):
    r'"[^"]*"'
    t.value = t.value[1:-1]  # Remove quotes
    return t

def t_IDENTIFIER(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    return t

def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)
    return t

t_ignore = ' \t'

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

def t_error(t):
    print(f"Illegal character '{t.value[0]}' at line {t.lineno}")
    t.lexer.skip(1)

lexer = lex.lex()

# --- Parser ---
precedence = (
    ('left', 'OR'),
    ('left', 'AND'),
    ('right', 'NOT'),
    ('nonassoc', 'EQUAL', 'NOTEQUAL', 'LESS', 'GREATER', 'LESSEQUAL', 'GREATEREQUAL'),
    ('left', 'PLUS', 'MINUS'),
    ('left', 'MULTIPLY', 'DIVIDE'),
    ('nonassoc', 'UMINUS'),
)

def p_program(p):
    '''program : statements'''
    p[0] = p[1]

def p_statements_multiple(p):
    '''statements : statements statement'''
    p[0] = p[1] + [p[2]]

def p_statements_single(p):
    '''statements : statement'''
    p[0] = [p[1]]

def p_statement_assign(p):
    '''statement : IDENTIFIER EQUALS expression SEMICOLON'''
    p[0] = ('assign', p[1], p[3])

def p_statement_print(p):
    '''statement : PRINT expression SEMICOLON'''
    p[0] = ('print', p[2])

def p_statement_if(p):
    '''statement : IF expression LBRACE statements RBRACE
                 | IF expression LBRACE statements RBRACE ELSE LBRACE statements RBRACE'''
    if len(p) == 6:
        p[0] = ('if', p[2], p[4], [])
    else:
        p[0] = ('if', p[2], p[4], p[8])

def p_statement_while(p):
    '''statement : WHILE expression LBRACE statements RBRACE'''
    p[0] = ('while', p[2], p[4])

def p_statement_for(p):
    '''statement : FOR IDENTIFIER EQUALS expression SEMICOLON expression SEMICOLON IDENTIFIER EQUALS expression LBRACE statements RBRACE'''
    p[0] = ('for', p[2], p[4], p[6], p[8], p[10], p[12])

def p_expression_binop(p):
    '''expression : expression PLUS expression
                  | expression MINUS expression
                  | expression MULTIPLY expression
                  | expression DIVIDE expression
                  | expression AND expression
                  | expression OR expression
                  | expression EQUAL expression
                  | expression NOTEQUAL expression
                  | expression LESS expression
                  | expression GREATER expression
                  | expression LESSEQUAL expression
                  | expression GREATEREQUAL expression'''
    p[0] = ('binop', p[2], p[1], p[3])

def p_expression_not(p):
    '''expression : NOT expression'''
    p[0] = ('not', p[2])

def p_expression_number(p):
    '''expression : NUMBER'''
    p[0] = ('number', p[1])

def p_expression_string(p):
    '''expression : STRING'''
    p[0] = ('string', p[1])

def p_expression_bool(p):
    '''expression : TRUE
                  | FALSE'''
    p[0] = ('bool', p[1])

def p_expression_identifier(p):
    '''expression : IDENTIFIER'''
    p[0] = ('identifier', p[1])

def p_expression_paren(p):
    '''expression : LPAREN expression RPAREN'''
    p[0] = p[2]

def p_expression_uminus(p):
    '''expression : MINUS expression %prec UMINUS'''
    p[0] = ('uminus', p[2])

def p_error(p):
    if p:
        print(f"Syntax error at '{p.value}' on line {p.lineno}")
    else:
        print("Syntax error at EOF")

parser = yacc.yacc()

# --- Interpreter ---
class Interpreter:
    def __init__(self):
        self.variables = {}

    def interpret(self, ast):
        for statement in ast:
            self.execute_statement(statement)

    def execute_statement(self, statement):
        if statement[0] == 'assign':
            self.variables[statement[1]] = self.evaluate_expression(statement[2])
        elif statement[0] == 'print':
            print(self.evaluate_expression(statement[1]))
        elif statement[0] == 'if':
            if self.evaluate_expression(statement[1]):
                self.interpret(statement[2])
            elif statement[3]:
                self.interpret(statement[3])
        elif statement[0] == 'while':
            while self.evaluate_expression(statement[1]):
                self.interpret(statement[2])
        elif statement[0] == 'for':
            self.variables[statement[1]] = self.evaluate_expression(statement[2])
            while self.evaluate_expression(statement[3]):
                self.interpret(statement[5])
                self.variables[statement[4]] = self.evaluate_expression(statement[5])

    def evaluate_expression(self, expr):
        if expr[0] == 'number':
            return expr[1]
        elif expr[0] == 'string':
            return expr[1]
        elif expr[0] == 'bool':
            return expr[1]
        elif expr[0] == 'identifier':
            if expr[1] not in self.variables:
                raise NameError(f"Variable '{expr[1]}' not defined")
            return self.variables[expr[1]]
        elif expr[0] == 'binop':
            left = self.evaluate_expression(expr[2])
            right = self.evaluate_expression(expr[3])
            if expr[1] == '+': return left + right
            elif expr[1] == '-': return left - right
            elif expr[1] == '*': return left * right
            elif expr[1] == '/': return left / right
            elif expr[1] == '&&': return left and right
            elif expr[1] == '||': return left or right
            elif expr[1] == '==': return left == right
            elif expr[1] == '!=': return left != right
            elif expr[1] == '<': return left < right
            elif expr[1] == '>': return left > right
            elif expr[1] == '<=': return left <= right
            elif expr[1] == '>=': return left >= right
        elif expr[0] == 'not':
            return not self.evaluate_expression(expr[1])
        elif expr[0] == 'uminus':
            return -self.evaluate_expression(expr[1])

# --- Compiler ---
class Compiler:
    def __init__(self):
        self.instructions = []
        self.constants = []
        self.variables = {}

    def compile(self, ast):
        for statement in ast:
            self.compile_statement(statement)
        return self.instructions, self.constants, self.variables

    def compile_statement(self, statement):
        if statement[0] == 'assign':
            self.compile_expression(statement[2])
            self.instructions.append(('STORE', statement[1]))
        elif statement[0] == 'print':
            self.compile_expression(statement[1])
            self.instructions.append(('PRINT', None))
        elif statement[0] == 'if':
            self.compile_expression(statement[1])
            self.instructions.append(('JUMP_IF_FALSE', len(self.instructions) + 2))
            self.compile_block(statement[2])
            if statement[3]:
                self.instructions.append(('JUMP', len(self.instructions) + 2))
                self.compile_block(statement[3])
        elif statement[0] == 'while':
            start = len(self.instructions)
            self.compile_expression(statement[1])
            self.instructions.append(('JUMP_IF_FALSE', len(self.instructions) + 2))
            self.compile_block(statement[2])
            self.instructions.append(('JUMP', start))
        elif statement[0] == 'for':
            self.compile_expression(statement[2])
            self.instructions.append(('STORE', statement[1]))
            start = len(self.instructions)
            self.compile_expression(statement[3])
            self.instructions.append(('JUMP_IF_FALSE', len(self.instructions) + 2))
            self.compile_block(statement[5])
            self.compile_expression(statement[5])
            self.instructions.append(('STORE', statement[4]))
            self.instructions.append(('JUMP', start))

    def compile_expression(self, expr):
        if expr[0] == 'number':
            self.instructions.append(('LOAD_CONST', expr[1]))
        elif expr[0] == 'string':
            self.instructions.append(('LOAD_CONST', expr[1]))
        elif expr[0] == 'bool':
            self.instructions.append(('LOAD_CONST', expr[1]))
        elif expr[0] == 'identifier':
            self.instructions.append(('LOAD_VAR', expr[1]))
        elif expr[0] == 'binop':
            self.compile_expression(expr[2])
            self.compile_expression(expr[3])
            self.instructions.append(('BINOP', expr[1]))
        elif expr[0] == 'not':
            self.compile_expression(expr[1])
            self.instructions.append(('NOT', None))
        elif expr[0] == 'uminus':
            self.compile_expression(expr[1])
            self.instructions.append(('NEG', None))

    def compile_block(self, statements):
        for statement in statements:
            self.compile_statement(statement)

# --- Main Function ---
def run_easylang(code, mode='interpret'):
    try:
        ast = parser.parse(code)
        if mode == 'interpret':
            interpreter = Interpreter()
            interpreter.interpret(ast)
        else:
            compiler = Compiler()
            instructions, constants, variables = compiler.compile(ast)
            # Here you could save the compiled code to a file or execute it
            print("Compilation successful!")
            print("Instructions:", instructions)
            print("Constants:", constants)
            print("Variables:", variables)
    except Exception as e:
        print(f"Error: {e}")

# --- Example Program ---
if __name__ == "__main__":
    # Example program with simpler syntax (no parentheses)
    code = """
    x = 5;
    y = 10;
    if x < y {
        print "x is less than y";
    } else {
        print "x is not less than y";
    }
    
    i = 0;
    while i < 5 {
        print i;
        i = i + 1;
    }
    """
    
    print("Running in interpreter mode:")
    run_easylang(code, mode='interpret')
    
    print("\nRunning in compiler mode:")
    run_easylang(code, mode='compile')
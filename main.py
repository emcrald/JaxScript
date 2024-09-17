import tkinter as tk
from tkinter import scrolledtext
import re

def lexer(input_code):
    token_specification = [
        ('MULTI_COMMENT', r'---.*?---', re.DOTALL), # multi line comment
        ('COMMENT', r'--[^\n]*'), # single comment
        ('DISPLAY', r'display'),
        ('STRING', r"'[^']*'"),
        ('LPAREN', r'\('),
        ('RPAREN', r'\)'),
        ('NEWLINE', r'\n'),
        ('SKIP', r'[ \t]+'),
        ('MISMATCH', r'.'),
    ]

    tokens = []
    input_pos = 0

    while input_pos < len(input_code):
        match = None
        for token_type, regex, *flags in token_specification:
            regex_match = re.match(regex, input_code[input_pos:], *flags)
            if regex_match:
                match = regex_match.group(0)
                if token_type in ['COMMENT', 'MULTI_COMMENT']:
                    # skip comments
                    input_pos += len(match)
                    break
                if token_type != 'SKIP':  # skip ignore
                    tokens.append((token_type, match))
                input_pos += len(match)
                break
        
        if not match:
            raise RuntimeError(f'Unexpected character: {input_code[input_pos]}')

    return tokens

def parse(tokens):
    ast = []
    while tokens:
        # handle newlines
        while tokens and tokens[0][0] in ['NEWLINE', 'SKIP']:
            tokens.pop(0)
        
        if tokens:
            node = parse_display(tokens)
            if node:
                ast.append(node)
        else:
            break
    return ast

def parse_display(tokens):
    while tokens and tokens[0][0] in ['NEWLINE', 'SKIP']:
        tokens.pop(0)

    if tokens and tokens[0][0] == 'DISPLAY':
        tokens.pop(0)
        while tokens and tokens[0][0] in ['NEWLINE', 'SKIP']:
            tokens.pop(0)
        if tokens and tokens[0][0] == 'LPAREN':
            tokens.pop(0)
            while tokens and tokens[0][0] in ['NEWLINE', 'SKIP']:
                tokens.pop(0)
            if tokens and tokens[0][0] == 'STRING':
                value = tokens.pop(0)[1][1:-1]
                while tokens and tokens[0][0] in ['NEWLINE', 'SKIP']:
                    tokens.pop(0)
                if tokens and tokens[0][0] == 'RPAREN':
                    tokens.pop(0)
                    return ('display', value)
    raise ValueError('Syntax error')

def interpret(ast):
    output = []
    for node in ast:
        if node[0] == 'display':
            value = node[1]
            output.append(value)
    return '\n'.join(output)

def run_code():
    code = text_area.get("1.0", tk.END)
    try:
        tokens = lexer(code)
        ast = parse(tokens)
        result = interpret(ast)
        output_area.config(state=tk.NORMAL)
        output_area.delete("1.0", tk.END)
        output_area.insert(tk.END, result)
        output_area.config(state=tk.DISABLED)
    except Exception as e:
        output_area.config(state=tk.NORMAL)
        output_area.delete("1.0", tk.END)
        output_area.insert(tk.END, f"Error: {e}")
        output_area.config(state=tk.DISABLED)

root = tk.Tk()
root.title("JaxScript IDE")


text_area = scrolledtext.ScrolledText(root, width=80, height=20)
text_area.pack()

run_button = tk.Button(root, text="Run", command=run_code)
run_button.pack()

output_area = scrolledtext.ScrolledText(root, width=80, height=10, state=tk.DISABLED)
output_area.pack()

root.mainloop()

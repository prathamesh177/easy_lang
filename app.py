from flask import Flask, render_template, request, jsonify
from easy import run_easylang
import io
import sys
import re

app = Flask(__name__)
app.config['ENV'] = 'development'
app.config['DEBUG'] = True

# Security configuration
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024  # 1MB max file size
app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # 1 hour session lifetime

# Allowed EasyLang keywords and patterns
ALLOWED_KEYWORDS = {
    'print', 'if', 'else', 'while', 'for', 'true', 'false'
}

ALLOWED_OPERATORS = {
    '+', '-', '*', '/', '=', '==', '!=', '<', '>', '<=', '>=', '&&', '||', '!'
}

def validate_easylang_code(code):
    # Check for dangerous patterns
    dangerous_patterns = [
        r'import\s+',
        r'from\s+',
        r'__import__',
        r'eval\s*\(',
        r'exec\s*\(',
        r'open\s*\(',
        r'file\s*\(',
        r'subprocess',
        r'os\.',
        r'sys\.',
        r'__builtins__',
        r'__import__',
    ]
    
    for pattern in dangerous_patterns:
        if re.search(pattern, code, re.IGNORECASE):
            return False, f"Security violation: {pattern.strip()} is not allowed"
    
    # Check for allowed keywords and operators
    words = re.findall(r'[a-zA-Z_][a-zA-Z0-9_]*', code)
    for word in words:
        if word.lower() not in ALLOWED_KEYWORDS and not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', word):
            return False, f"Invalid keyword or identifier: {word}"
    
    return True, "Code is valid"

# Capture stdout for the web interface
class OutputCapture:
    def __init__(self):
        self.output = []

    def write(self, text):
        self.output.append(text)

    def get_output(self):
        return ''.join(self.output)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/run', methods=['POST'])
def run_code():
    code = request.json.get('code', '')
    mode = request.json.get('mode', 'interpret')
    
    # Validate code
    is_valid, message = validate_easylang_code(code)
    if not is_valid:
        return jsonify({
            'success': False,
            'error': message
        })
    
    # Capture output
    output_capture = OutputCapture()
    old_stdout = sys.stdout
    sys.stdout = output_capture
    
    try:
        run_easylang(code, mode)
        output = output_capture.get_output()
        return jsonify({
            'success': True,
            'output': output
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })
    finally:
        sys.stdout = old_stdout

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000) 
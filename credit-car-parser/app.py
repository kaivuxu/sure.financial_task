from flask import Flask, render_template, request, jsonify
import os
from werkzeug.utils import secure_filename
from parsers.hdfc_parser import HDFCParser
from parsers.icici_parser import ICICIParser
from parsers.sbi_parser import SBIParser
from parsers.axis_parser import AxisParser
from parsers.kotak_parser import KotakParser

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Bank parser mapping
PARSERS = {
    'HDFC': HDFCParser,
    'ICICI': ICICIParser,
    'SBI': SBIParser,
    'AXIS': AxisParser,
    'KOTAK': KotakParser
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/parse', methods=['POST'])
def parse_statement():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    bank = request.form.get('bank', '').upper()
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if bank not in PARSERS:
        return jsonify({'error': 'Invalid bank selected'}), 400
    
    if file and file.filename.endswith('.pdf'):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        try:
            # Parse the PDF
            parser = PARSERS[bank](filepath)
            data = parser.parse()
            
            # Clean up uploaded file
            os.remove(filepath)
            
            return jsonify({
                'success': True,
                'data': data
            })
        except Exception as e:
            # Clean up on error
            if os.path.exists(filepath):
                os.remove(filepath)
            return jsonify({'error': f'Parsing error: {str(e)}'}), 500
    
    return jsonify({'error': 'Invalid file type. Please upload a PDF'}), 400

if __name__ == '__main__':
    app.run(debug=True, port=5000)
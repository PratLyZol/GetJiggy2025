from flask import Blueprint, request, jsonify, current_app
import os
from werkzeug.utils import secure_filename
import google.generativeai as genai
from .file_processor import process_file

main = Blueprint('main', __name__)

# Configure Gemini API
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
model = genai.GenerativeModel('gemini-pro')

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'docx', 'csv', 'json'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@main.route('/api/test', methods=['GET'])
def test_cors():
    return jsonify({'message': 'CORS is working!'})

@main.route('/api/upload', methods=['POST', 'OPTIONS'])
def upload_file():
    if request.method == 'OPTIONS':
        return '', 204
        
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        try:
            # Process the file and get text content
            text_content = process_file(filepath)
            
            # Generate structured output using Gemini
            prompt = f"""Analyze the following text and extract key fields and their descriptions in a structured format:
            {text_content}
            
            Return the output in this JSON format:
            {{
                "fields": [
                    {{"name": "Field Name", "description": "Field Description"}},
                    ...
                ],
                "summary": "Brief summary of the document"
            }}
            """
            
            response = model.generate_content(prompt)
            structured_data = response.text
            
            return jsonify({
                'message': 'File processed successfully',
                'data': structured_data
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
        finally:
            # Clean up the uploaded file
            if os.path.exists(filepath):
                os.remove(filepath)
    
    return jsonify({'error': 'File type not allowed'}), 400 
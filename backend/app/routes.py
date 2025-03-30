from flask import Blueprint, request, jsonify, current_app, send_file
import os
from werkzeug.utils import secure_filename
import google.generativeai as genai
from gtts import gTTS
from .file_processor import process_file
import json
import re

main = Blueprint('main', __name__)

# Configure Gemini API
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
model = genai.GenerativeModel('gemini-1.5-pro')
model_output = ""


ALLOWED_EXTENSIONS = {'txt', 'pdf', 'docx', 'csv', 'json'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
@main.route('/api/generate-voice', methods=['POST', 'OPTIONS'])
def generate_voice():
    global model_output
    print("Generating voice...")
    if request.method == 'OPTIONS':
        response = jsonify({"message": 'CORS is working!'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'POST')
        return response, 200
    
    prompt = f"""Given the input create lyrics for a song. The song should tell the user the elements of the form that the user needs to fill out, make it around 80 to 100 words long, not longer, not shorter. Here is what the user needs to fill out: {model_output}"""
    print(model_output)
    response = model.generate_content(prompt)
    text = response.text
    text = re.sub(r'\(verse \d+\)|\(chorus\)', '', text, flags=re.IGNORECASE)
    tts = gTTS(text=text, lang='en')
    filename = 'output.mp3'
    tts.save("app/" + filename)

    response = send_file(filename, mimetype='audio/mpeg')
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
    response.headers.add('Access-Control-Allow-Methods', 'POST')
    return response, 200
    

@main.route('/api/test', methods=['GET', 'OPTIONS'])
def test_cors():
    if request.method == 'OPTIONS':
        return '', 204
    return jsonify({
        'message': 'CORS is working!',
        'status': 'success'
    })

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
            prompt = f"""Analyze the following form/document and extract all form fields that need to be filled out. For each field:
            1. Identify the exact field name as it appears in the form
            2. Provide a clear, detailed description of what information should be entered in that field
            3. Include any specific formatting requirements or special instructions
            4. Note if the field is required or optional

            Document content:
            {text_content}

            Return the output in this JSON format:
            {{
                "fields": [
                    {{
                        "name": "Exact field name from the form",
                        "description": "Detailed description of what should be entered, including any special requirements or formatting instructions",
                        "required": true/false,
                        "format": "Any specific format requirements (e.g., MM/DD/YYYY, XXX-XX-XXXX)"
                    }},
                    ...
                ],
                "summary": "Brief summary of the form's purpose and what type of information it collects"
            }}

            For example, for a W-4 form:
            {{
                "fields": [
                    {{
                        "name": "First name and middle initial",
                        "description": "Enter your legal first name and middle initial exactly as they appear on your Social Security card",
                        "required": true,
                        "format": "Text only, no special characters"
                    }},
                    {{
                        "name": "Social Security Number",
                        "description": "Enter your 9-digit Social Security Number as shown on your Social Security card",
                        "required": true,
                        "format": "XXX-XX-XXXX"
                    }}
                ],
                "summary": "Employee's Withholding Certificate form used to determine federal income tax withholding from wages"
            }}
            """
            
            response = model.generate_content(prompt)
            # Parse the response text to extract the JSON part
            response_text = response.text
            model_output = response_text
            # Remove markdown code block markers if present
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]
            # Parse the JSON string
            structured_data = json.loads(response_text)
            
            return jsonify({
                'message': 'File processed successfully',
                'data': structured_data,
                'status': 'success'
            })
            
        except Exception as e:
            return jsonify({
                'error': str(e),
                'status': 'error'
            }), 500
        finally:
            # Clean up the uploaded file
            if os.path.exists(filepath):
                os.remove(filepath)
    
    return jsonify({
        'error': 'File type not allowed',
        'status': 'error'
    }), 400 
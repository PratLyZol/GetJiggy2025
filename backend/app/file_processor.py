import os
import PyPDF2
import pandas as pd
from docx import Document
import json

def process_file(filepath):
    """Process different file types and extract text content."""
    file_extension = os.path.splitext(filepath)[1].lower()
    
    if file_extension == '.pdf':
        return process_pdf(filepath)
    elif file_extension == '.docx':
        return process_docx(filepath)
    elif file_extension == '.csv':
        return process_csv(filepath)
    elif file_extension == '.json':
        return process_json(filepath)
    elif file_extension == '.txt':
        return process_txt(filepath)
    else:
        raise ValueError(f"Unsupported file type: {file_extension}")

def process_pdf(filepath):
    """Extract text from PDF files."""
    text = ""
    with open(filepath, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
    return text

def process_docx(filepath):
    """Extract text from DOCX files."""
    doc = Document(filepath)
    text = ""
    for paragraph in doc.paragraphs:
        text += paragraph.text + "\n"
    return text

def process_csv(filepath):
    """Extract text from CSV files."""
    df = pd.read_csv(filepath)
    return df.to_string()

def process_json(filepath):
    """Extract text from JSON files."""
    with open(filepath, 'r') as file:
        data = json.load(file)
        return json.dumps(data, indent=2)

def process_txt(filepath):
    """Extract text from TXT files."""
    with open(filepath, 'r', encoding='utf-8') as file:
        return file.read() 
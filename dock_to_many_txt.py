import sys
import os
from docx import Document
import textract

def extract_text_from_docx(docx_path):
    document = Document(docx_path)
    text = '\n'.join([paragraph.text for paragraph in document.paragraphs])
    return text

def extract_text_from_doc(doc_path):
    text = textract.process(doc_path).decode('utf-8')
    return text

def save_text_to_txt(text, output_path, max_lines=100):
    lines = text.splitlines()
    file_number = 1

    for i in range(0, len(lines), max_lines):
        current_file = f"{output_path}_{file_number}.txt"
        with open(current_file, 'w', encoding='utf-8') as txt_file:
            txt_file.write('\n'.join(lines[i:i + max_lines]))
        print(f"Text saved to {current_file}")
        file_number += 1

def main(input_path, output_path):
    _, file_extension = os.path.splitext(input_path)
    if file_extension.lower() == ".docx":
        text = extract_text_from_docx(input_path)
    elif file_extension.lower() == ".doc":
        text = extract_text_from_doc(input_path)
    else:
        print("Unsupported file format. Please provide a .doc or .docx file.")
        return

    save_text_to_txt(text, output_path)

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python extract_text.py input.doc(x) output")
    else:
        input_path = sys.argv[1]
        output_path = sys.argv[2]
        main(input_path, output_path)
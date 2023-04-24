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

def save_text_to_txt(text, output_path):
    with open(output_path, 'w', encoding='utf-8') as txt_file:
        txt_file.write(text)

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
    print(f"Text extracted and saved to {output_path}")

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python extract_text.py input.doc(x) output.txt")
    else:
        input_path = sys.argv[1]
        output_path = sys.argv[2]
        main(input_path, output_path)
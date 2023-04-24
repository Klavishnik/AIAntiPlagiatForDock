import sys
import os
import textract
import requests
import json
import time

from docx import Document
from datetime import datetime

def extract_text_from_docx(docx_path):
    document = Document(docx_path)
    text = '\n'.join([paragraph.text for paragraph in document.paragraphs])
    return text

def extract_text_from_doc(doc_path):
    text = textract.process(doc_path).decode('utf-8')
    return text

def save_text_to_txt(text, max_words=300):
    words = text.split()
    file_number = 1
    all_words = []
    for i in range(0, len(words), max_words):
        all_words.append(' '.join(words[i:i + max_words]))
    return all_words


def send_to_api(content, retries=1, delay=1):
    url = 'https://openai-openai-detector.hf.space/'
    headers = {'Content-Type': 'application/json'}
    data = json.dumps({'text': content})

    for attempt in range(retries):
        with requests.Session() as session:
            response = session.post(url, headers=headers, data=data)

        if response.status_code == 200:
            if response.text.strip():
                try:
                    result = response.json()
                    return response, result
                except json.JSONDecodeError:
                    print("Error: The API response is not valid JSON.", file=sys.stderr)
                    print(response.text, file=sys.stderr)
                    break
            else:
                print("Error: The API response is empty.", file=sys.stderr)
        else:
            print(f"Error: {response.status_code} - {response.text}", file=sys.stderr)

        if attempt < retries - 1:
            print(f"Retrying... (attempt {attempt + 2}/{retries})", file=sys.stderr)
            time.sleep(delay)
        

    return None, None

def process_files(my_all_words):
    fake_probabilities = []
    not_loaded_files = 0
    for i in range(len(my_all_words)-1):
        response, result = send_to_api(my_all_words[i])
        if response is not None and result is not None:
            fake_probability = round(result.get('fake_probability', 0) * 100, 1)
            print(f"File: {i}, Fake probability: {fake_probability}%")
            fake_probabilities.append(fake_probability)
        else:
            print(f"File: {i}, NOT LOAD")
            not_loaded_files = not_loaded_files + 1

    if fake_probabilities:
        avg_fake_probability = round(sum(fake_probabilities) / len(fake_probabilities), 1)
        print(f"\nAverage fake probability: {avg_fake_probability}%")
    else:
        print("\nNo valid results were obtained.", file=sys.stderr)
    
    with open("out.txt", "a") as f:
            f.write(f"avg_fake_probability: {avg_fake_probability} \t not_loaded_files: {not_loaded_files} \n")
    return not_loaded_files


def main(input_path):
    _, file_extension = os.path.splitext(input_path)
    if file_extension.lower() == ".docx":
        text = extract_text_from_docx(input_path)
    elif file_extension.lower() == ".doc":
        text = extract_text_from_doc(input_path)
    else:
        print("Unsupported file format. Please provide a .doc or .docx file.")
        return

    return save_text_to_txt(text)


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python extract_text.py input.doc(x)")
        sys.exit(0)

    folder_path=str(sys.argv[1])
    files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
    for file in files:
        name=file.split("_")[-2]
        group=file.split("_")[-4]+" "+ file.split("_")[-3]

        with open("out.txt", "a") as f:
            f.write(f"Name: {name} \t Group: {group} \t ")

        all_words = main(folder_path + "/" + file)
        not_loaded_files = process_files(all_words)
    


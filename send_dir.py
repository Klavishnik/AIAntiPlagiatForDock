import os
import requests
import json
import time
import sys

from datetime import datetime

def read_file_content(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def send_to_api(content, retries=10, delay=1):
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

def process_files(folder_path):
    files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
    fake_probabilities = []

    for file in files:
        file_path = os.path.join(folder_path, file)
        content = read_file_content(file_path)
        response, result = send_to_api(content)

        if response is not None and result is not None:
            fake_probability = round(result.get('fake_probability', 0) * 100, 1)
            print(f"File: {file}, Fake probability: {fake_probability}%")
            fake_probabilities.append(fake_probability)

    if fake_probabilities:
        avg_fake_probability = round(sum(fake_probabilities) / len(fake_probabilities), 1)
        print(f"\nAverage fake probability: {avg_fake_probability}%")
    else:
        print("\nNo valid results were obtained.", file=sys.stderr)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python send_to_api.py folder_path", file=sys.stderr)
    else:
        start_time = datetime.now()
        print("Started at: ", start_time)
        folder_path = sys.argv[1]
        process_files(folder_path)

        end_time = datetime.now()
        print("Started at: ", start_time)
        print("Ended at: ", end_time)
        print("Elapsed time: ", end_time - start_time)

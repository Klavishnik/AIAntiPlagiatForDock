import requests
import json

def read_file_content(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def send_to_api(content):
    url = 'https://openai-openai-detector.hf.space/'
    headers = {'Content-Type': 'application/json'}
    data = json.dumps({'text': content})

    with requests.Session() as session:
        response = session.post(url, headers=headers, data=data)

    return response

def main(input_file):
    content = read_file_content(input_file)
    response = send_to_api(content)

    if response.status_code == 200:
        if response.text:  # Проверяем, что ответ не пустой
            result = response.json()
            print("Response from API:")
            print(json.dumps(result, indent=2))
        else:
            print("Error: Empty response")
    else:
        print(f"Error: {response.status_code} - {response.text}")

if __name__ == '__main__':
    import sys
    if len(sys.argv) != 2:
        print("Usage: python send_to_api.py input.txt")
    else:
        input_file = sys.argv[1]
        main(input_file)

import sys
import os
import textract
import requests
import json
import time
import argparse
import math
import logging
import os

from openai_detector import OpenaiDetector


from docx import Document
from datetime import datetime
from transformers import pipeline
from revChatGPT.V3 import Chatbot


#PUT UOR TOKEN
#HOW?
#https://github.com/promptslab/openai-detector


##Пороги срабатывания у классификатора
mark_detect_ai_possible = 75
mark_detect_ai_generate = 96

#Сколько слов будет в каждом куске файла при разбиении
num_words_split_gpt2  = 300
num_words_split_class = 800
num_words_roberta_base = 20
num_words_roberta_large = 20

def extract_text_from_docx(docx_path):
    document = Document(docx_path)
    text = '\n'.join([paragraph.text for paragraph in document.paragraphs])
    return text

def extract_text_from_doc(doc_path):
    text = textract.process(doc_path).decode('utf-8')
    return text

def save_text_to_txt(text, max_words):
    words = text.split()
    file_number = 1
    all_words = []
    for i in range(0, len(words), max_words):
        all_words.append(' '.join(words[i:i + max_words]))
    return all_words


def send_to_api_gpt2(content, retries=10, delay=1):
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

def process_files_gpt2(my_all_words):
    fake_probabilities = []
    not_loaded_files = 0
    for i in range(len(my_all_words)-1):
        response, result = send_to_api_gpt2(my_all_words[i])
        if response is not None and result is not None:
            fake_probability = round(result.get('fake_probability', 0) * 100, 1)
            print(f"File: {i}, Fake probability: {fake_probability}%")
            with open(f"{args.output}", "a") as f:
                f.write(f"File: {i}, Fake probability: {fake_probability}% \n")
            fake_probabilities.append(fake_probability)
        else:
            print(f"File: {i}, NOT LOAD")
            not_loaded_files = not_loaded_files + 1

    if fake_probabilities:
        avg_fake_probability = round(sum(fake_probabilities) / len(fake_probabilities), 1)
        print(f"\n ---> Average fake probability: {avg_fake_probability}% \n")
    else:
        print("\nNo valid results were obtained.", file=sys.stderr)
    
    with open(f"{args.output}", "a") as f:
            f.write(f"\n ---> avg_fake_probability: {avg_fake_probability} \t not_loaded_files: {not_loaded_files} \n")
    return not_loaded_files



def process_files_class(my_all_words):
    fake_probabilities = []
    od = OpenaiDetector(bearer_token)
    
    for i in range(len(my_all_words)-1):
        response = od.detect(my_all_words[i])
        if response is not None:
            probability = response["AI-Generated Probability"]
            conclusion = response["Class"]
            fake_probabilities.append(probability)
   
            print(f"Pprobability: {probability}")
            print(f"Class: {conclusion}")

    if fake_probabilities:
            avg_fake_probability = round(sum(fake_probabilities) / len(fake_probabilities), 1)
            avg_conclusion = od.get_class_label(avg_fake_probability)

            response_dict = {
            "OpenAI Average Probability":  avg_fake_probability,
            "OpenAI Class": avg_conclusion
            }

            print(f"\n ---> Average fake probability: {avg_fake_probability}%")
            print(f"---> Average fake class: {avg_conclusion}")
                       
            if (avg_fake_probability > mark_detect_ai_generate):
                print(f"\n ---> AI GENERATE!!!!")
                
            elif (avg_fake_probability > mark_detect_ai_possible):
                print(f"\n ---> AI generation possible!")

    return response_dict

def classify_text_roberta_base(text):
    results = detector_base(text)
    return results

def classify_text_roberta_large(text):
    results = detector_large(text)
    return results

def process_files_roberta_base(my_all_words):   
    num_reals = 0 
    num_fakes = 0
    fake_probabilities = []  
    real_probabilities = []
    for i in range(len(my_all_words)-1):
        response = classify_text_roberta_base(my_all_words[i])
        if response is not None:
            for item in response:
                if item['label'] == 'Fake':
                    fake_probabilities.append(item['score'])
                    print(f"[{i}] Fake: {item['score']}")
                    num_fakes = num_fakes + 1
                if item['label'] == 'Real':
                    real_probabilities.append(item['score'])
                    print(f"[{i}] Real: {item['score']}")
                    num_reals = num_reals + 1 
                    
    if fake_probabilities:
        avg_fake_probabilities = sum(fake_probabilities) / len(fake_probabilities)

    if real_probabilities:
        avg_real_probabilities = sum(real_probabilities) / len(real_probabilities)

    print(f"\n ---> Average fake probability: {avg_fake_probabilities}%")
    print(f"---> Average real probability: {avg_real_probabilities}")
    print(f"\n ---> Num fakes: {num_fakes}")
    print(f"---> Num reals: {num_reals}")

    result_dict = {
        "Roberta Base avg FAKE prob": avg_fake_probabilities,
        "Roberta Base avg REAL prob": avg_real_probabilities,
        "Roberta Base Num REALS": num_reals,
        "Roberta Base Num FAKES": num_fakes
    }
    return result_dict


def process_files_roberta_large(my_all_words):   
    num_reals = 0 
    num_fakes = 0
    fake_probabilities = []  
    real_probabilities = []
    for i in range(len(my_all_words)-1):
        response = classify_text_roberta_large(my_all_words[i])
        if response is not None:
            for item in response:
                if item['label'] == 'LABEL_1':
                    fake_probabilities.append(item['score'])
                    print(f"[{i}] Fake: {item['score']}")
                    num_fakes = num_fakes + 1
                if item['label'] == 'LABEL_0':
                    real_probabilities.append(item['score'])
                    print(f"[{i}] Real: {item['score']}")
                    num_reals = num_reals + 1 
                    
    if fake_probabilities:
        avg_fake_probabilities = sum(fake_probabilities) / len(fake_probabilities)

    if real_probabilities:
        avg_real_probabilities = sum(real_probabilities) / len(real_probabilities)

    print(f"\n ---> Average fake probability: {avg_fake_probabilities}%")
    print(f"---> Average real probability: {avg_real_probabilities}")
    print(f"\n ---> Num fakes: {num_fakes}")
    print(f"---> Num reals: {num_reals}")

    result_dict = {
        "Roberta Large avg FAKE prob": avg_fake_probabilities,
        "Roberta Large avg REAL prob": avg_real_probabilities,
        "Roberta Large Num REALS": num_reals,
        "Roberta Large Num FAKES": num_fakes
    }
    return result_dict

def calculate_entropy(text):
    if not text:
        return 0
    char_counts = {}
    for char in text:
        if char in char_counts:
            char_counts[char] += 1
        else:
            char_counts[char] = 1
    char_probs = [count / len(text) for count in char_counts.values()]
    entropy = -sum(p * math.log2(p) for p in char_probs)

    return entropy


        
def main(input_path):
    _, file_extension = os.path.splitext(input_path)
    if file_extension.lower() == ".docx":
        text = extract_text_from_docx(input_path)
    elif file_extension.lower() == ".doc":
        text = extract_text_from_doc(input_path)
    else:
        print("Unsupported file format. Please provide a .doc or .docx file.")
        return

    return (text)


if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(description="Chec AI generated text")
    parser.add_argument("-gpt2", action="store_true", help="Using GPT-2")
    parser.add_argument("-classificator", action="store_true", help="Using classifiacator")
    parser.add_argument("-entropy", action="store_true", help="Calculate entropy of text")
    parser.add_argument("-roberta_base", action="store_true", help="Using roberta base model")
    parser.add_argument("-roberta_large", action="store_true", help="Using roberta large model")
    parser.add_argument("-o", "--output", required=False, type=str, help="output file")
    parser.add_argument("target_dir", type=str, help="target dir with .doc(x) files")
   
    args = parser.parse_args()

    if not args.entropy and not args.gpt2 and not args.classificator and not args.roberta_base and not args.roberta_large:
        print("Check args not set!")
        sys.exit()
            
    files = [f for f in os.listdir(args.target_dir) if os.path.isfile(os.path.join(args.target_dir, f))]
    
    for file in files:
        try:
            all_words = main(args.target_dir + "/" + file)
            json_data = {"Name": file}
                    
            print(f"   Name: {file} ")
            print(f"----------------------------------------------------------------------------")

            if args.roberta_base: 
                try:
                    detector_base = pipeline(
                        "text-classification",
                        model="roberta-base-openai-detector",
                        tokenizer="roberta-base-openai-detector"
                    )   
                    print(f"----- Roberta Base ----- ")
                    splitted_words_roberta_base = save_text_to_txt(all_words, num_words_roberta_base)
                    data_class = process_files_roberta_base(splitted_words_roberta_base)
                    json_data.update(data_class)  
                except:
                    print("Error")

            if args.roberta_large: 
                try:
                    detector_large = pipeline(
                        "text-classification",
                        model="roberta-large-openai-detector",
                        tokenizer="roberta-large-openai-detector"
                    )   
                    print(f"----- Roberta Large ----- ")
                    splitted_words_roberta_large = save_text_to_txt(all_words, num_words_roberta_large)
                    data_class = process_files_roberta_large(splitted_words_roberta_large)
                    json_data.update(data_class)  
                except:
                    print("Error")


            if args.gpt2:
                splitted_words_gpt2 = save_text_to_txt(all_words, num_words_split_gpt2)
                print(f"----- ChatGPT 2.0 ----- ")
                process_files_gpt2(splitted_words_gpt2)
                #json_data.update(data_class)
            if args.entropy:
                print(f"----- Entropy ----- ")
                entropy = calculate_entropy(all_words)
                print(f"Entropy: {entropy}")
                json_data["Entropy"] = entropy
                json_data.update(data_class)

            if args.classificator:
                splitted_words_class = save_text_to_txt(all_words, num_words_split_class)
                print(f"----- AI Text Classifier ----- ")
                data_class = process_files_class(splitted_words_class)
                json_data.update(data_class)
            
            if args.output: 
                with open(args.output, "a") as my_file:
                    json.dump(json_data, my_file, indent=4)
                    my_file.write("\n")

            print("\n\n")
        except:
            print("Error")

            
            
            
            
    
            

        

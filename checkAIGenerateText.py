import base64
import io
import docx2txt
import PyPDF2
import os
import textract
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline, logging
import argparse
import tempfile
import math
from openai_detector import OpenaiDetector
import json
import pandas as pd
import pdfplumber
from docx import Document





def parse_contents_referat(file_path):
    file_extension = os.path.splitext(file_path)[1]
    text = ""

    try:
        if '.docx' in file_extension:
            text = docx2txt.process(file_path)
        elif '.doc' in file_extension:
            text = textract.process(file_path, extension='doc').decode()
    except Exception as e:
        print(f"Error processing file {file_path}: {e}")
        return ""

    # Удаляем первые N и последние M строк
    lines = text.splitlines()
    N = 22  # количество строк для удаления в начале
    M = 22  # количество строк для удаления в конце

    if len(lines) > N + M:
        text = '\n'.join(lines[N:-M])
    
    return text

def parse_contents(file_path):
    file_extension = os.path.splitext(file_path)[1]

    try:
        if '.docx' in file_extension:
            text = docx2txt.process(file_path)
        elif '.doc' in file_extension:
            text = textract.process(file_path, extension='doc').decode()
        elif '.txt' in file_extension:
            with open(file_path, 'r') as f:
                text = f.read()
        elif '.pdf' in file_extension:
            with open(file_path, 'rb') as f:
                with pdfplumber.open(f) as pdf:
                    num_of_pages = len(pdf.pages)
                    text = ''
                    for n_page in range(num_of_pages):
                        page = pdf.pages[n_page]
                        text = text + page.extract_text()
        else:
            print("Unsupported file format.")
            return None
    except Exception as e:
        print(e)
        return None
    
    return text

def classify_text(text, classifier):
    if text:
        res = classifier(text, truncation=True, max_length=510)
        label = res[0]['label']
        score = res[0]['score']

        if label == 'Real':
            real_score = score * 100
            fake_score = 100 - real_score
        else:
            fake_score = score * 100
            real_score = 100 - fake_score

        return real_score, fake_score
    else:
        return None, None



def process_text_with_model(text, model_path):
    logging.set_verbosity_error()
    absolute_path = os.path.dirname(__file__)
    full_path = os.path.join(absolute_path, model_path)
    tokenizer = AutoTokenizer.from_pretrained(full_path, local_files_only=True)
    model = AutoModelForSequenceClassification.from_pretrained(full_path, local_files_only=True)
    classifier = pipeline("sentiment-analysis", model=model, tokenizer=tokenizer)
    real_score, fake_score = classify_text(text, classifier)

    return real_score, fake_score

def save_text_to_txt(text, max_words):
    words = text.split()
    file_number = 1
    all_words = []
    for i in range(0, len(words), max_words):
        all_words.append(' '.join(words[i:i + max_words]))
    return all_words

 
def process_file_open_ai(my_all_words):
    fake_probabilities = []
    od = OpenaiDetector(bearer_token)
    max_retries = 5

    for i in range(len(my_all_words)-1):
        response = od.detect(my_all_words[i])
        retry_count = 0
        while retry_count < max_retries:
            response = od.detect(my_all_words[i])
            if response is not None:
                try:
                    probability = response["AI-Generated Probability"]
                    conclusion = response["Class"]
                    fake_probabilities.append(probability)

                    print(f"[{i}] Probability: {probability}")
                    print(f"[{i}] Class: {conclusion}")
                    break  # Break the retry loop on successful request
                except Exception as e:  # Catch the exception and print it
                    print(f"Error: Open-AI response bad. Exception: {e}")
                    print(f"Retry {retry_count}")
                    retry_count += 1  # Increment the retry count
            else:
                retry_count += 1


    if fake_probabilities:
            avg_fake_probability = round(sum(fake_probabilities) / len(fake_probabilities), 1)
            avg_conclusion = od.get_class_label(avg_fake_probability)

            response_dict = {
            "OpenAI Average Probability":  avg_fake_probability,
            "OpenAI Class": avg_conclusion
            }

            print(f"\n---> Average fake probability: {avg_fake_probability}%")
            print(f"---> Average fake class: {avg_conclusion}")
    return response_dict

def count_words(text):
    words = text.split()
    return len(words)

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

def main(file_path):
    model_base_path = "./roberta-base-openai-detector/"
    model_large_path = "./roberta-large-openai-detector/"

    files = [f for f in os.listdir(args.target_dir) if os.path.isfile(os.path.join(args.target_dir, f))]
    json_data = []

    for i, file in enumerate(files):
       # try:
            file_data = {"Name": file}        
            print(f"   Name: {file} ")
            print(f"----------------------------------------------------------------------------")

            if args.referat: 
                text = parse_contents_referat(args.target_dir + "/" + file)
            else: 
                text = parse_contents(args.target_dir + "/" + file)
            
            if args.roberta_base: 
                try:
                    real_score, fake_score = process_text_with_model(text, model_base_path)
                    result_dict = {
                        'Roberta Base fake': fake_score,
                        'Roberta Base real': real_score
                    }
                    file_data.update(result_dict)

                    print(f"----- Roberta Base ----- ")
                    print(f" Roberta Base fake: {fake_score}")
                    print(f" Roberta Base real: {real_score}")

                except:
                    print("Error BASE")
            
            if args.roberta_large: 
                try:
                    real_score, fake_score = process_text_with_model(text, model_large_path)
                    result_dict = {
                        'Roberta Large fake': fake_score,
                        'Roberta Large real': real_score
                    }
                    file_data.update(result_dict)

                    print(f"----- Roberta Large ----- ")
                    print(f" Roberta Large fake: {fake_score}")
                    print(f" Roberta Large real: {real_score}")

                except:
                    print("Error LARGE")

            if args.entropy:
                print(f"----- Entropy ----- ")
                entropy = calculate_entropy(text)
                print(f"  Entropy: {entropy}")
                file_data["Entropy"] = entropy

            if args.classificator:
                splitted_words_class = save_text_to_txt(text, 300)
                print(f"----- AI Text Classifier ----- ")
                data_class = process_file_open_ai(splitted_words_class)
                file_data.update(data_class)
             
            if args.words:
                print(f"----- Count Words ----- ")
                word_count = count_words(text)
                print(f"  Count Words: {word_count}")
                file_data["Count Words"] = word_count



            json_data.append(file_data)
#        except:
 #           print(f"Error open file: {file}")

            print("\n\n")

    
    if args.output_json: 
        with open(args.output_json, "a") as my_file:
            json.dump(json_data, my_file, indent=4)
            my_file.write("\n")

    if args.output_exel: 
        data = pd.DataFrame(json_data)
        data.to_excel(args.output_exel, index=False)



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process a file.')
    parser.add_argument("-classificator", action="store_true", help="Using classifiacator")
    parser.add_argument("-entropy", action="store_true", help="Calculate entropy of text")
    parser.add_argument("-roberta_base", action="store_true", help="Using roberta base model")
    parser.add_argument("-roberta_large", action="store_true", help="Using roberta large model")
    parser.add_argument("-words", action="store_true", help="Counter words in documnet (with --referat retun less value")
    parser.add_argument("--output_json", required=False, type=str, help="output file to JSON")
    parser.add_argument("--output_exel", required=False, type=str, help="output file to TABLE")
    parser.add_argument("-referat", action="store_true", help="Delete TWO FIRST and TWO LAST pages")
    parser.add_argument("target_dir", type=str, help="target dir with .doc(x) files")

    args = parser.parse_args()
    
    if not args.entropy and not args.classificator and not args.roberta_base and not args.roberta_large and not args.words :
        print("Check args not set!")
        sys.exit()

    main(args.target_dir)


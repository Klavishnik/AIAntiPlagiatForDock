import json
import argparse

def merge_dicts(dict1, dict2):
    merged = dict1.copy()
    for key, value in dict2.items():
        if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
            merged[key] = merge_dicts(merged[key], value)
        else:
            merged[key] = value
    return merged

def combine_json_elements(file1, file2, output_file):
    with open(file1, 'r') as f1, open(file2, 'r') as f2:
        data1 = json.load(f1)
        data2 = json.load(f2)

    if isinstance(data1, list) and isinstance(data2, list):
        combined_data = data2.copy()

        for d1 in data1:
            for index, d2 in enumerate(combined_data):
                if d2["Name"] == d1["Name"]:
                    combined_data[index] = merge_dicts(d2, d1)
                    break
            else:
                combined_data.append(d1)
    else:
        print("Error: Both JSON files should have a list structure.")
        return

    # Save combined data to the output file
    with open(output_file, 'w') as outfile:
        json.dump(combined_data, outfile, indent=2)


def merge_json_files(file1, file2, output_file):
    with open(file1, 'r') as f1, open(file2, 'r') as f2:
        data1 = json.load(f1)
        data2 = json.load(f2)

    if isinstance(data1, list) and isinstance(data2, list):
        combined_data = data1 + data2
    else:
        print("Error: Both JSON files should have a list structure.")
        return
        
      # Save combined data to the output file
    with open(output_file, 'w') as outfile:
        json.dump(combined_data, outfile, indent=2)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Combine elements of two JSON files with a similar structure.')
    parser.add_argument('file1', help='Path to the first JSON file')
    parser.add_argument('file2', help='Path to the second JSON file')
    parser.add_argument('output_file', help='Path to the output JSON file')
    parser.add_argument("-combine", action="store_true", help="Combine json")
    parser.add_argument("-merge", action="store_true", help="Merge json")
    args = parser.parse_args()

    if not args.combine and not args.merge:
        print("Check args not set!")
        sys.exit()

    if args.combine: 
        combine_json_elements(args.file1, args.file2, args.output_file)
    
    if args.merge: 
        merge_json_files(args.file1, args.file2, args.output_file)
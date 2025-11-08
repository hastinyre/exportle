import json
import os

def main():
    # Step 1: Ask for the JSON file name
    file_name = input("Enter the name of the JSON file (with .json extension): ").strip()
    
    # Step 2: Check if file exists
    if not os.path.exists(file_name):
        print("File not found! Please make sure it’s in the same folder.")
        return
    
    # Step 3: Load the JSON data
    with open(file_name, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Ensure it's a dictionary
    if not isinstance(data, dict):
        print("Error: The JSON structure is not a dictionary at the top level.")
        return
    
    # Step 4: Ask for each key (country)
    filtered_data = {}
    for country in data:
        while True:
            choice = input(f"Include {country}? (1 for yes, 0 for no): ").strip()
            if choice in ["1", "0"]:
                break
            print("Invalid input. Please enter 1 or 0.")
        
        if choice == "1":
            filtered_data[country] = data[country]
    
    # Step 5: Save filtered result
    new_file_name = f"filtered_{file_name}"
    with open(new_file_name, 'w', encoding='utf-8') as f:
        json.dump(filtered_data, f, indent=4, ensure_ascii=False)
    
    print(f"\nFiltered JSON saved as: {new_file_name}")

if __name__ == "__main__":
    main()

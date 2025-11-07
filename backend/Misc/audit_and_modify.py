import json
import copy

def audit_and_modify_distances(input_filename, output_filename):
    """
    Reads a JSON distance file, logs all distances being changed from <30km 
    to 0.0, and then saves the modified data to a new file without further prompts.

    Args:
        input_filename (str): The name of the source JSON file.
        output_filename (str): The name for the new, modified JSON file.
    """
    # --- 1. Load the Input File ---
    try:
        with open(input_filename, 'r', encoding='utf-8') as f:
            country_data = json.load(f)
    except FileNotFoundError:
        print(f"Error: The input file '{input_filename}' was not found.")
        print("Please ensure the file is in the same directory as the script. Halting execution.")
        return
    except json.JSONDecodeError:
        print(f"Error: The file '{input_filename}' is not a valid JSON file. Halting execution.")
        return

    # Create a deep copy to modify, preserving the original data for comparison
    modified_data = copy.deepcopy(country_data)
    
    # --- 2. Audit and Log Changes ---
    print("--- Audit Log: Distances to be Overwritten ---")
    print("Starting scan of the distance data...")
    
    changes_to_make = []
    
    # Iterate through the data to find what needs to be changed
    for country, distances in country_data.items():
        for neighbor_country, distance in distances.items():
            # The condition for a change: distance is between 0 (exclusive) and 30 (exclusive)
            if 0.0 < distance < 30.0:
                # Log the change that will be made
                change_record = {
                    "country1": country,
                    "country2": neighbor_country,
                    "original_distance": distance,
                    "new_distance": 0.0
                }
                changes_to_make.append(change_record)
                
                # Apply the change to the copied data
                modified_data[country][neighbor_country] = 0.0

    # --- 3. Print the Serialized Log to CMD ---
    if not changes_to_make:
        print("No distances found that are less than 30 km. No changes will be made.")
    else:
        # Sort the list for a consistent, ordered output.
        # This sorts primarily by the first country, then by the second country.
        changes_to_make.sort(key=lambda x: (x['country1'], x['country2']))
        
        for i, change in enumerate(changes_to_make, 1):
            print(
                f"{i:04d}: Changing distance between '{change['country1']}' and "
                f"'{change['country2']}'. Original: {change['original_distance']} km -> New: 0.0 km"
            )
    
    print("\n--- End of Audit Log ---")
    
    # --- 4. Save the Modified File ---
    try:
        with open(output_filename, 'w', encoding='utf-8') as f:
            json.dump(modified_data, f, indent=4)
        print(f"\nSuccessfully saved all modifications to '{output_filename}'.")
        print(f"Total number of distances overwritten: {len(changes_to_make)}")
    except IOError as e:
        print(f"\nAn error occurred while writing the output file: {e}")

if __name__ == "__main__":
    # Get filenames from the user at the very beginning
    input_file = input("Enter the name of the INPUT JSON file (e.g., distances.json): ")
    output_file = input("Enter the name for the OUTPUT JSON file (e.g., modified_distances.json): ")

    if not input_file or not output_file:
        print("Input and output filenames cannot be empty. Exiting.")
    else:
        # Run the main function
        audit_and_modify_distances(input_file, output_file)
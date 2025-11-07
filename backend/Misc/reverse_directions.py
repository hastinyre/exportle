import json

def reverse_all_directions(data):
    """
    Iterates through the nested dictionary and reverses every direction.

    Args:
        data (dict): The original dictionary with country directions.

    Returns:
        dict: A new dictionary with all directions reversed 180 degrees.
    """
    # Dictionary mapping each direction to its 180-degree opposite
    direction_map = {
        "N": "S",
        "S": "N",
        "E": "W",
        "W": "E",
        "NE": "SW",
        "SW": "NE",
        "NW": "SE",
        "SE": "NW"
    }

    # Create a new dictionary to store the reversed data
    reversed_data = {}

    # Iterate through each primary country in the top level of the JSON
    for primary_country, relations in data.items():
        reversed_relations = {}
        # Iterate through the nested dictionary of secondary countries and their directions
        for secondary_country, direction in relations.items():
            # If the direction is None (json 'null'), it remains None
            if direction is None:
                reversed_relations[secondary_country] = None
            else:
                # Otherwise, look up the opposite direction from the map
                # .get() is used to avoid errors if a direction is not in the map
                reversed_relations[secondary_country] = direction_map.get(direction, direction)
        
        reversed_data[primary_country] = reversed_relations
        
    return reversed_data

def main():
    """
    Main function to run the program. Prompts for filenames,
    reads the data, processes it, and saves the output.
    """
    print("--- Geographic Direction Reverser ---")
    
    # 1. Ask for the input and output filenames at the start
    input_filename = input("Enter the name of the input JSON file: ")
    output_filename = input("Enter the name for the output JSON file: ")

    try:
        # 2. Open and load the data from the input JSON file
        with open(input_filename, 'r', encoding='utf-8') as f:
            original_data = json.load(f)

        print("\nProcessing data...")
        
        # 3. Call the function to reverse the directions
        new_data = reverse_all_directions(original_data)

        # 4. Write the newly processed data to the output JSON file
        # 'indent=2' makes the output JSON file readable (pretty-print)
        with open(output_filename, 'w', encoding='utf-8') as f:
            json.dump(new_data, f, indent=2)

        print(f"\nSuccess! The reversed data has been saved to '{output_filename}'.")

    except FileNotFoundError:
        print(f"\nError: The file '{input_filename}' was not found. Please make sure it's in the same folder as the script.")
    except json.JSONDecodeError:
        print(f"\nError: The file '{input_filename}' is not a valid JSON file. Please check its format.")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")

# This ensures the main() function runs when the script is executed
if __name__ == "__main__":
    main()
import json

def find_close_countries(file_path):
    """
    Reads a JSON file with country distance data and finds pairs of countries
    that are less than 1km apart but do not have a distance of 0.0.

    Args:
        file_path (str): The path to the JSON file.

    Returns:
        list: A list of tuples, where each tuple contains the two country names
              and their distance.
    """
    try:
        with open(file_path, 'r') as f:
            country_data = json.load(f)
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
        print("Please make sure the file is in the same directory as the script.")
        return None
    except json.JSONDecodeError:
        print(f"Error: The file '{file_path}' is not a valid JSON file.")
        return None

    close_pairs = []
    # Use a set to keep track of pairs we've already processed to avoid duplicates
    # e.g., (CountryA, CountryB) is the same as (CountryB, CountryA)
    processed_pairs = set()

    # Iterate through each country in the dataset
    for country1, distances in country_data.items():
        # For each country, check its distance to every other country
        for country2, distance in distances.items():
            # Ensure the distance is less than 1km but not 0 (which often indicates the same country or a shared border)
            if 0.0 < distance < 3.0:
                # Sort the country names to create a unique key for the pair
                sorted_pair = tuple(sorted((country1, country2)))
                # If we haven't processed this pair yet, add it to our results
                if sorted_pair not in processed_pairs:
                    close_pairs.append((country1, country2, distance))
                    processed_pairs.add(sorted_pair)
    
    return close_pairs

if __name__ == "__main__":
    # Get the filename from the user
    n = 0
    filename = input("Please enter the name of the JSON file: ")
    
    # Find the pairs
    result = find_close_countries(filename)
    
    # Print the results
    if result is not None:
        if result:
            print("\nFound the following pairs of countries less than 1km apart:")
            for country1, country2, dist in result:
                n = n + 1 # Corrected placement of the increment
                print(f"{n}- {country1} and {country2}, Distance: {dist} km")
        else:
            print("\nNo pairs of countries found with a distance less than 1km.")
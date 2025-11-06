import os
import pandas as pd
import json

def generate_trade_report():
    """
    Scans the current directory for all .csv files, calculates the top 10
    HS4 codes by trade value for each, and saves the combined results
    into a single JSON file.
    """
    
    # Get the directory where this script is running
    current_directory = os.getcwd()
    
    # This will hold the final data for all countries
    all_country_data = {}
    
    print("Starting report generation...")

    # Loop through every file in the current directory
    for filename in os.listdir(current_directory):
        
        # Check if the file is a CSV
        if filename.endswith(".csv"):
            
            # Get the country name from the filename (e.g., "USA.csv" -> "USA")
            country_name = os.path.splitext(filename)[0]
            file_path = os.path.join(current_directory, filename)
            
            print(f"Processing {filename} for country: {country_name}...")

            try:
                # Read the CSV file. We only need two columns.
                df = pd.read_csv(file_path, usecols=["HS4", "Trade Value"])

                # Group by the 'HS4' column and sum the 'Trade Value'
                # This handles cases where the same HS4 appears on multiple rows
                hs4_grouped = df.groupby("HS4")["Trade Value"].sum()

                # Get the top 10 largest values
                top_10_hs4 = hs4_grouped.nlargest(10)

                # Convert the pandas Series into the list format you wanted
                # e.g., [{"HS4": "Cars", "Total Trade Value": 15000000000}, ...]
                top_10_list = top_10_hs4.reset_index().rename(
                    columns={"Trade Value": "Total Trade Value"}
                ).to_dict('records')

                # Add this country's top 10 list to the main dictionary
                all_country_data[country_name] = top_10_list

            except Exception as e:
                print(f"Could not process {filename}. Error: {e}")
                print("Please check that the file has 'HS4' and 'Trade Value' columns.")

    # After processing all CSVs, write the final dictionary to a JSON file
    output_filename = "trade_report.json"
    try:
        with open(output_filename, "w") as json_file:
            # `indent=2` makes the JSON file human-readable
            json.dump(all_country_data, json_file, indent=2)
            
        print(f"\nSuccessfully generated {output_filename}!")
        print(f"Found and processed {len(all_country_data)} CSV files.")

    except Exception as e:
        print(f"Error writing final JSON file: {e}")

# Run the function
if __name__ == "__main__":
    generate_trade_report()
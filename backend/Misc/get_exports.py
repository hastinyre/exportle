import requests
import json
import time

# The final, corrected list of countries and their OEC IDs
COUNTRIES = [
    {"name": "Albania", "id": "eualb"}, {"name": "Algeria", "id": "afdza"},
    {"name": "Angola", "id": "afago"}, {"name": "Afghanistan", "id": "asafg"},
    {"name": "Armenia", "id": "asarm"}, {"name": "Australia", "id": "ocaus"},
    {"name": "Austria", "id": "euaut"}, {"name": "Azerbaijan", "id": "asaze"},
    {"name": "Bahrain", "id": "asbhr"}, {"name": "Bangladesh", "id": "asbgd"},
    {"name": "Belarus", "id": "eublr"}, {"name": "Belgium", "id": "eubel"},
    {"name": "Benin", "id": "afben"}, {"name": "Bhutan", "id": "asbtn"},
    {"name": "Bolivia", "id": "sabol"}, {"name": "Bosnia and Herzegovina", "id": "eubih"},
    {"name": "Botswana", "id": "afbwa"}, {"name": "Brazil", "id": "sabra"},
    {"name": "Burkina Faso", "id": "afbfa"}, {"name": "Burundi", "id": "afbdi"},
    {"name": "Cambodia", "id": "askhm"}, {"name": "Cameroon", "id": "afcmr"},
    {"name": "Canada", "id": "nacan"}, {"name": "Central African Republic", "id": "afcaf"},
    {"name": "Chad", "id": "aftcd"}, {"name": "Chile", "id": "sachl"},
    {"name": "China", "id": "aschn"}, {"name": "Colombia", "id": "sacol"},
    {"name": "Comoros", "id": "afcom"}, {"name": "Costa Rica", "id": "nacri"},
    {"name": "Croatia", "id": "euhrv"}, {"name": "Cuba", "id": "nacub"},
    {"name": "Cyprus", "id": "eucyp"}, {"name": "Czech Republic (Czechia)", "id": "eucze"},
    {"name": "Denmark", "id": "eudnk"}, {"name": "Djibouti", "id": "afdji"},
    {"name": "Dominican Republic", "id": "nadom"}, {"name": "DR Congo", "id": "afcod"},
    {"name": "Ecuador", "id": "saecu"}, {"name": "Egypt", "id": "afegy"},
    {"name": "El Salvador", "id": "naslv"}, {"name": "Equatorial Guinea", "id": "afgnq"},
    {"name": "Eritrea", "id": "aferi"}, {"name": "Estonia", "id": "euest"},
    {"name": "Eswatini (fmr. \"Swaziland\")", "id": "afswz"}, {"name": "Ethiopia", "id": "afeth"},
    {"name": "Fiji", "id": "ocfji"}, {"name": "Finland", "id": "eufin"},
    {"name": "France", "id": "eufra"}, {"name": "Gabon", "id": "afgab"},
    {"name": "Gambia", "id": "afgmb"}, {"name": "Georgia", "id": "asgeo"},
    {"name": "Germany", "id": "eudeu"}, {"name": "Ghana", "id": "afgha"},
    {"name": "Greece", "id": "eugrc"}, {"name": "Guatemala", "id": "nagtm"},
    {"name": "Guinea", "id": "afgin"}, {"name": "Guinea-Bissau", "id": "afgnb"},
    {"name": "Guyana", "id": "saguy"}, {"name": "Haiti", "id": "nahti"},
    {"name": "Honduras", "id": "nahnd"}, {"name": "Hong Kong", "id": "ashkg"},
    {"name": "Hungary", "id": "euhun"}, {"name": "India", "id": "asind"},
    {"name": "Indonesia", "id": "asidn"}, {"name": "Iran", "id": "asirn"},
    {"name": "Iraq", "id": "asirq"}, {"name": "Ireland", "id": "euirl"},
    {"name": "Israel", "id": "asisr"}, {"name": "Italy", "id": "euita"},
    {"name": "Ivory Coast", "id": "afciv"}, {"name": "Jamaica", "id": "najam"},
    {"name": "Japan", "id": "asjpn"}, {"name": "Jordan", "id": "asjor"},
    {"name": "Kazakhstan", "id": "askaz"}, {"name": "Kenya", "id": "afken"},
    {"name": "Kuwait", "id": "askwt"}, {"name": "Kyrgyzstan", "id": "askgz"},
    {"name": "Laos", "id": "aslao"}, {"name": "Latvia", "id": "eulva"},
    {"name": "Lebanon", "id": "aslbn"}, {"name": "Lesotho", "id": "aflso"},
    {"name": "Liberia", "id": "aflbr"}, {"name": "Libya", "id": "aflby"},
    {"name": "Lithuania", "id": "eultu"}, {"name": "Madagascar", "id": "afmdg"},
    {"name": "Malawi", "id": "afmwi"}, {"name": "Malaysia", "id": "asmys"},
    {"name": "Mali", "id": "afmli"}, {"name": "Mauritania", "id": "afmrt"},
    {"name": "Mauritius", "id": "afmus"}, {"name": "Mexico", "id": "namex"},
    {"name": "Moldova", "id": "eumda"}, {"name": "Mongolia", "id": "asmng"},
    {"name": "Morocco", "id": "afmar"}, {"name": "Mozambique", "id": "afmoz"},
    {"name": "Myanmar", "id": "asmmr"}, {"name": "Namibia", "id": "afnam"},
    {"name": "Nepal", "id": "asnpl"}, {"name": "Netherlands", "id": "eunld"},
    {"name": "New Zealand", "id": "ocnzl"}, {"name": "Nicaragua", "id": "nanic"},
    {"name": "Niger", "id": "afner"}, {"name": "Nigeria", "id": "afnga"},
    {"name": "North Korea", "id": "askpr"}, {"name": "North Macedonia", "id": "eumkd"},
    {"name": "Norway", "id": "eunor"}, {"name": "Oman", "id": "asomn"},
    {"name": "Pakistan", "id": "aspak"}, {"name": "Panama", "id": "napan"},
    {"name": "Papua New Guinea", "id": "ocpng"}, {"name": "Paraguay", "id": "sapry"},
    {"name": "Peru", "id": "saper"}, {"name": "Philippines", "id": "asphl"},
    {"name": "Poland", "id": "eupol"}, {"name": "Portugal", "id": "euprt"},
    {"name": "Puerto Rico", "id": "napri"}, {"name": "Qatar", "id": "asqat"},
    {"name": "Republic of the Congo", "id": "afcog"}, {"name": "Romania", "id": "eurou"},
    {"name": "Russia", "id": "eurus"}, {"name": "Rwanda", "id": "afrwa"},
    {"name": "Saudi Arabia", "id": "assau"}, {"name": "Senegal", "id": "afsen"},
    {"name": "Sierra Leone", "id": "afsle"}, {"name": "Singapore", "id": "assgp"},
    {"name": "Slovenia", "id": "eusvn"}, {"name": "Solomon Islands", "id": "ocslb"},
    {"name": "Somalia", "id": "afsom"}, {"name": "South Africa", "id": "afzaf"},
    {"name": "South Korea", "id": "askor"}, {"name": "South Sudan", "id": "afssd"},
    {"name": "Spain", "id": "euesp"}, {"name": "Sri Lanka", "id": "aslka"},
    {"name": "State of Palestine", "id": "aspse"}, {"name": "Sudan", "id": "afsdn"},
    {"name": "Sweden", "id": "euswe"}, {"name": "Switzerland", "id": "euefta"},
    {"name": "Syria", "id": "assyr"}, {"name": "Taiwan", "id": "astwn"},
    {"name": "Tajikistan", "id": "astjk"}, {"name": "Tanzania", "id": "aftza"},
    {"name": "Thailand", "id": "astha"}, {"name": "Timor-Leste", "id": "astls"},
    {"name": "Togo", "id": "aftgo"}, {"name": "Trinidad and Tobago", "id": "natto"},
    {"name": "Tunisia", "id": "aftun"}, {"name": "Turkey", "id": "astur"},
    {"name": "Turkmenistan", "id": "astkm"}, {"name": "Uganda", "id": "afuga"},
    {"name": "Ukraine", "id": "euukr"}, {"name": "United Arab Emirates", "id": "asare"},
    {"name": "United Kingdom", "id": "eugbr"}, {"name": "United States", "id": "nausa"},
    {"name": "Uruguay", "id": "saury"}, {"name": "Uzbekistan", "id": "asuzb"},
    {"name": "Vietnam", "id": "asvnm"}, {"name": "Yemen", "id": "asyem"},
    {"name": "Zambia", "id": "afzmb"}, {"name": "Zimbabwe", "id": "afzwe"}
]

# This is where we will store the final results
all_countries_exports = {}

# The base URL template with the CORRECT sort parameter
URL_TEMPLATE = "https://api-v2.oec.world/tesseract/data.jsonrecords?cube=trade_i_baci_a_22&drilldowns=HS4,Exporter+Country&measures=Trade+Value&include=Exporter+Country:{}&time=Year.latest&sort=Trade+Value.desc&limit=10"

# Loop through each country in our list
for i, country in enumerate(COUNTRIES):
    country_name = country["name"]
    country_id = country["id"]
    
    # Construct the final URL for this country
    url = URL_TEMPLATE.format(country_id)
    
    print(f"Fetching data for {country_name} ({i+1}/{len(COUNTRIES)})...")
    
    try:
        # Make the API call
        response = requests.get(url)
        response.raise_for_status() 
        
        api_data = response.json()["data"]
        
        # Format the data exactly as requested
        formatted_exports = []
        for item in api_data:
            formatted_exports.append({
                "HS4": item.get("HS4"), 
                "Total Trade Value": item.get("Trade Value")
            })
            
        all_countries_exports[country_name] = formatted_exports
        
        time.sleep(0.5) 

    except requests.exceptions.RequestException as e:
        print(f"  > Could not fetch data for {country_name}: {e}")
    except KeyError:
        print(f"  > Unexpected response format for {country_name}. 'data' key not found.")

# All done, print the final result
print("\n--- COMPLETE ---")
print(json.dumps(all_countries_exports, indent=2))

# Optional: Save the output to a file
with open("top_exports.json", "w") as f:
    json.dump(all_countries_exports, f, indent=2)

print("\nResults also saved to top_exports.json")
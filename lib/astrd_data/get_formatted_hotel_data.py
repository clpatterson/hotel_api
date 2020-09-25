import requests

astrd_dict = {}

def parse_astrd_data_file():
    """Return asteroid ephem data parsed from a txt file as a dictionary."""
    with open("asteroid_ephem_data.txt") as f:
        data = f.read()
        lines = data.splitlines()
        for line in lines:
            if line[0] == '#':
                continue
            else:
                idx = line.find(",")
                asteroid_name = line[:idx]
                astrd_dict[asteroid_name] = {"ephem_data":line}

    return

def insert_jpl_data():
    """Add descriptive data to each asteroid record using JPL Small-Bodies DB API."""
    spectral_types = {"A":"silicaceous",
                      "B":"carbonaceous",
                      "F":"carbonaceous",
                      "C":"carbonaceous",
                      "G":"carbonaceous",
                      "D":"carbonaceous",
                      "E":"enstatite",
                      "M":"metallic",
                      "P":"primitive",
                      "Q":"silicaceous",
                      "R":"silicaceous",
                      "S":"silicaceous",
                      "T":"carbonaceous",
                      "V":"silicaceous"
                      }
    
    for key in astrd_dict.keys():
        # Get data about asteroid from JPL API
        name = key.replace(" ","%20")
        url = f'https://ssd-api.jpl.nasa.gov/sbdb.api?sstr={name}&discovery=True&phys-par=True'
        r = requests.get(url)
        data = r.json()
        
        #Parse data
        proprietor = data['discovery']['who']
        established = data['discovery']['date']
        
        for i in data['phys_par']:
            if i['name'] == "diameter":
                diameter = i['value']
            elif i['name'] == "spec_T":
                if len(i['value']) > 1: # Some astroids are assigned multiple categories
                    i['value'] = i['value'][0] # Use first categorization
                surface_composition = spectral_types.get(i['value'])
        # Insert data
        astrd_dict[key].update({"proprietor": proprietor, 
                                    "established": established,
                                    "astrd_diameter": diameter, 
                                    "astrd_surface_composition": surface_composition
                                })

    return

def get_astrd_data():
    """Return dictionary with asteroid ephem and jpl data."""
    return astrd_dict

def write_to_csv():
    with open("astrd_data.py",mode="w") as f:
        f.write(f"astrd_data = {astrd_dict}")
    return

if __name__ == '__main__':
    parse_astrd_data_file()
    insert_jpl_data()
    write_to_csv()
    print(get_astrd_data())

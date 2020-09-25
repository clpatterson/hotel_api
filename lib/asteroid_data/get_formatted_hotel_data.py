import requests

def parse_astrd_data():
    """Return asteroid ephem data parsed from a txt file as a dictionary."""
    with open("asteroid_data.txt") as f:
        data = f.read()
        lines = data.splitlines()
        asteroids_ephem_data = {}
        for line in lines:
            if line[0] == '#':
                continue
            else:
                idx = line.find(",")
                asteroid_name = line[:idx]
                asteroids_ephem_data[asteroid_name] = {"ephem_data":line}

    return asteroids_ephem_data


def get_jpl_data(astrd_dict):
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
        name = key.replace(" ","%20")
        print("______________________________________")
        print(name)
        url = f'https://ssd-api.jpl.nasa.gov/sbdb.api?sstr={name}&discovery=True&phys-par=True'
        print(url)
        r = requests.get(url)
        data = r.json()
        proprieter = data['discovery']['who']
        print(proprieter)
        established = data['discovery']['date']
        print(established)
        for i in data['phys_par']:
            if i['name'] == "diameter":
                diameter = i['value']
                print(diameter)
            elif i['name'] == "spec_T":
                surface_composition = spectral_types.get(i['value'])
                print(surface_composition)

    return "done job"


if __name__ == '__main__':
    print(get_jpl_data(parse_astrd_data()))

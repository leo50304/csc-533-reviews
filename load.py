from geopy.geocoders import Nominatim
import json

def load_saved_data():
    with open('review_group.json', "r") as file:
        string = file.read()
        review_group = json.loads(string)
    file.close()
    with open('sites.json', 'r') as file:
        string = file.read()
        sites = json.loads(string)
    file.close()
    with open('site_types.json', 'r') as file:
        string = file.read()
        site_types = json.loads(string)
    file.close()
    return review_group, sites, site_types

def read_review_data(name):
    with open(name, 'r') as file:
        data = json.load(file)
    file.close()
    # data = ast.literal_eval(data_string)
    return data

def set_initial_data(review, raw_site_data):
    site_data = {
                'name': review['Location']['Name'],
                'type': raw_site_data['type'],
                'tags': review['Location']['Tags'],
                'coord': (raw_site_data['lat'], raw_site_data['lon']),
                'cost': review['Location']['Cost'],
        }
    review_data = {
            'place_id': raw_site_data['place_id'],
            'type': raw_site_data['type'],
            'rating': review['Rating']
        }
    return site_data, review_data

def store_data(review_group, sites, site_types):
    with open('review_group.json', 'w') as file:
        file.write(json.dumps(review_group))
    file.close()
    with open('sites.json', 'w') as file:
        file.write(json.dumps(sites))
    file.close()
    with open('site_types.json', 'w') as file:
        file.write(json.dumps(site_types))
    file.close()

if __name__ == "__main__":
    reviews = read_review_data('data2.json')
    geolocator = Nominatim(user_agent="CSC533")
    review_group, sites, site_types = load_saved_data()
    hash_address = {}
    count = 0
    print(len(reviews))
    for i, review in enumerate(reviews):
        print(i, count)
        #store site data from reviews
        if review['Location']['Address'] in hash_address:
            raw_site_data = hash_address[review['Location']['Address']]
        elif(geolocator.geocode(review['Location']['Address'])==None):
            count += 1
            continue
        else:
            raw_site_data = geolocator.geocode(review['Location']['Address']).raw
            hash_address[review['Location']['Address']] = raw_site_data
        
        site_data, review_data = set_initial_data(review, raw_site_data)
        sites[raw_site_data['place_id']] = site_data

        #store site categories
        if site_data['type'] not in site_types:
            site_types[site_data['type']] = 0
        site_types[site_data['type']] += 1

        #store user data
        user_id = review['User']
        if user_id not in review_group:
            review_group[user_id] = []
        review_group[user_id].append(review_data)
    store_data(review_group, sites, site_types)

    print(len(review_group), len(sites), len(site_types), count)
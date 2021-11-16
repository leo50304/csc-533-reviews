import ast;
from geopy.geocoders import Nominatim
from geopy.distance import geodesic

# from pprint import pprint
# import requests, json
api_key = 'AIzaSyCEZIhIg5UfjtEC-Fvcn4-oxL1bRoVHVh4'
url = "https://maps.googleapis.com/maps/api/place/textsearch/json?"


def read_review_data():
    with open('reviews.txt', 'r') as file:
        data_string = file.read()
    file.close()
    data = ast.literal_eval(data_string)
    return data

def predict_user_location(reviews):
    return (35.753715, -78.666875)

def predict_user_preferred_cost(reviews):
    pass

def collect_tags(reviews):
    tags = {}
    for review in reviews:
        for tag in review[tags]:
            if tag not in tags:
                tags[tag] = 0
            tags[tag] += 1
    return tags
# count the numbers of same tags
def compute_tag_similarity(reviews):
    user_tags = collect_tags(reviews)
    user_location = predict_user_location(reviews)
    pass

if __name__ == "__main__":
    reviews = read_review_data()

    geolocator = Nominatim(user_agent="CSC533")
    review_group = {}
    for review in reviews:
        user_id = review['User']
        if user_id not in review_group:
            review_group[user_id] = []
        site_data = geolocator.geocode(review['Location']['Address'])
        review_data = {
            'rating':review['Rating'],
            'type': site_data.raw['type'],
            'tags': review['Location']['Tags'],
            'coord': (site_data.latitude, site_data.longitude),
            'cost': review['Location']['Cost']
        }
        review_group[user_id].append(review_data)
    
    site1 = review_group['110540965997813227851'][0]['coord']
    site2 = review_group['110540965997813227851'][1]['coord']
    print(geodesic(site1, site2).miles)
    # compute_tag_similarity(review_group['110540965997813227851'])
    # print(review_group)
    
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import json
from scipy import stats

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

def predict_user_location(reviews):
    x = y = 0
    for r in reviews:
        x += eval(sites[r['place_id']]['coord'][0])
        y += eval(sites[r['place_id']]['coord'][1])
    return x / len(reviews), y / len(reviews)


def predict_location_radius(reviews):
    return 15


def get_user_avg_cost(reviews):
    dollar_signs_sum = count = 0
    for r in reviews:
        if sites[r['place_id']]['cost'] is None:
            continue
        elif sites[r['place_id']]['cost'] == '$':
            dollar_signs_sum += 1
        elif sites[r['place_id']]['cost'] == '$$':
            dollar_signs_sum += 2
        elif sites[r['place_id']]['cost'] == '$$$':
            dollar_signs_sum += 3
        elif sites[r['place_id']]['cost'] == '$$$$':
            dollar_signs_sum += 4
        count += 1
    if count == 0:
        return 0
    return dollar_signs_sum / count

def calculate_distance(site1, site2):
    return geodesic(site1['coord'], site2['coord']).miles

def collect_tags(reviews, sites):
    tags = {}
    for review in reviews:
        site_type = review['type']
        if site_type not in tags:
            tags[site_type] = {}
        for tag in sites[review['place_id']]['tags']:
            if tag not in tags[site_type]:
                tags[site_type][tag] = 0
            tags[site_type][tag] += 1
    return tags

def compute_tag_similarity_score(user_tags, sites):
    result = {}
    count_tag = 0
    for tag in user_tags.values():
        count_tag += tag
    for site in sites.values():
        score = 0
        for tag in site['tags']:
            if tag in user_tags:
                score += user_tags[tag]
        result[site['name']] = score/count_tag
    return result

# count the numbers of same tags
def get_tag_similarity(reviews, sites, site_types):
    user_tags = collect_tags(reviews, sites)
    result = {}
    for site_type in site_types:
        if site_type not in user_tags:
            result[site_type] = None
            continue
        result[site_type] = compute_tag_similarity_score(user_tags[site_type], sites)
        break
    sort_tag_score(result)
    return result

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

def sort_tag_score(tag_scores):
    for type, tag_score in tag_scores.items():
        tag_scores[type] = {k: v for k, v in sorted(tag_score.items(), key=lambda item: item[1], reverse=True)}

def get_top_tag_by_type(tag_scores, type, count):
    result = []
    for i, values in enumerate(tag_scores[type]):
        result.append(values)
        if(i==count-1):
            break
    return result

def wealthness_percentile(user_costs, user):
    return stats.percentileofscore(list(user_costs.values()), user_costs[user])

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
    review_group, sites, site_types = load_saved_data()
    print(sites)
    user_costs = {}
    for user, review in review_group.items():
        user_costs[user] = get_user_avg_cost(review)

    for user in review_group:
        percentile = wealthness_percentile(user_costs, user)
        print(user, percentile)


    #find sites containing tags that most similar to the user, categorized by site types
    tag_scores = get_tag_similarity(review_group['110540965997813227851'], sites, site_types)
    user_location = predict_user_location(review_group['110540965997813227851'])
    top_scores = get_top_tag_by_type(tag_scores, 'house', 2)
    # print(top_scores, user_location)

from geopy.distance import geodesic
import json
from scipy import stats
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score

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
        x += eval(sites[str(r['place_id'])]['coord'][0])
        y += eval(sites[str(r['place_id'])]['coord'][1])
    return x / len(reviews), y / len(reviews)

def transform_dollar_sign(dollar):
    if dollar == '$':
        return 1
    elif dollar == '$$':
        return 2
    elif dollar == '$$$':
        return 3
    elif dollar == '$$$$':
        return 4
    else:
        return 0

def get_user_avg_cost(reviews):
    dollar_signs_sum = count = 0
    for r in reviews:
        cost = transform_dollar_sign(sites[str(r['place_id'])]['cost'])
        if cost is None:
            continue
        else:
            dollar_signs_sum += cost
            count += 1
    if count == 0:
        return 0
    return dollar_signs_sum / count

def calculate_distance(site1, site2):
    return geodesic(site1['coord'], site2['coord']).miles

def collect_tags(reviews, sites, place_id):
    tags = {}
    for review in reviews:
        if review['place_id'] == place_id:
            continue
        if review['type'] not in tags:
            tags[review['type']] = 0
        tags[review['type']] += 1
        for tag in sites[str(review['place_id'])]['tags']:
            if tag not in tags:
                tags[tag] = 0
            tags[tag] += 1
    return tags

def compute_tag_similarity_score(user_tags, site):
    score = 0
    if site['type'] in user_tags:
        score += 1
    for tag in site['tags']:
        if tag in user_tags:
            score += user_tags[tag]
    if len(user_tags) == 0:
        return 0
    return score/len(user_tags)

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
    # arrange data
    review_group, sites, site_types = load_saved_data()
    user_costs = {}
    for user, review in review_group.items():
        user_costs[user] = get_user_avg_cost(review)
    for user in review_group:
        percentile = wealthness_percentile(user_costs, user)
    count_review = 0
    for reviews in review_group.values():
        count_review += len(reviews)
    print("Data arrange complete: {} sites, {} users, {} reviews.".format(len(sites), len(review_group), count_review))

    #training with the first half of our data
    print("Start training")
    x, y = [], []
    i = 0
    for user, reviews in review_group.items():
        i += 1
        if i < len(review_group)/2:
            continue
        user_location = predict_user_location(reviews)
        
        for place_id, site in sites.items():
            user_tags = collect_tags(reviews, sites, place_id)
            tag_score = compute_tag_similarity_score(user_tags, site)
            distance = geodesic(user_location, site['coord']).miles
            cost_diff = transform_dollar_sign(site['cost']) - user_costs[user]
            x.append([tag_score, distance, cost_diff])
            hit = 0
            for review in reviews:
                if str(review['place_id']) == str(place_id):
                    hit = 1
                    break
            y.append(hit)

    model = LogisticRegression(solver='lbfgs')
    model.fit(x, y)
    yhat = model.predict(x)
    acc = accuracy_score(y, yhat)
    print("Finish training")

    #predicting with the second half of our data
    print("Start prediction test")
    i = 0
    count_skip = 0
    count_hit = 0
    count_guess = 0
    count_type = {}
    count_type_success = {}
    for user, reviews in review_group.items():
        i += 1
        if i >= len(review_group)/2:
            break
        user_location = predict_user_location(reviews)
        
        old_count_guess = count_guess
        for place_id, site in sites.items():
            user_tags = collect_tags(reviews, sites, place_id)
            tag_score = compute_tag_similarity_score(user_tags, site)
            distance = geodesic(user_location, site['coord']).miles
            cost_diff = transform_dollar_sign(site['cost']) - user_costs[user]
            x = [[tag_score, distance, cost_diff]]
            hit = 0
            for review in reviews:
                if str(review['place_id']) == str(place_id):
                    hit = 1
                    break
            new_output = model.predict(x)
            if new_output == 1:
                if site['type'] not in count_type:
                    count_type[site['type']] = 0
                count_type[site['type']] += 1
                count_guess += 1
                if new_output == hit:
                    count_hit += 1
                    if site['type'] not in count_type_success:
                        count_type_success[site['type']] = 0
                    count_type_success[site['type']] += 1
        if count_guess == old_count_guess:
            count_skip +=1
            continue

    rate = count_hit/count_guess
    print("{} guesses hit/{} guesses, accuracy: {}%".format(count_hit, count_guess, round(rate*100, 3)))
    print("{} user skipped with no guesses/{} users".format(count_skip, len(review_group)/2))
    print("attemped sites' type:", count_type)
    print("success sites' type:", count_type_success)
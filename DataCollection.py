import requests
import json

# List of "seed" locations
location_ids = ["7443157407086175910"]
page_num = 0
num_reviews = 150

# Grab users who reviewed seed locations
user_ids = []
for location in location_ids:
    url = f"https://www.google.com/maps/preview/review/listentitiesreviews?authuser=0&hl=en&gl=us&pb=!1m2!1y9920574034578334581!2y{location}!2m2!1i{page_num}0!2i{num_reviews}!3e1!4m5!3b1!4b1!5b1!6b1!7b1!5m2!1s6G9DYfPqHKez5NoPoNGTgA0!7e81"
    r = requests.get(url)
    reviews = json.loads(r.text[5:])
    for i in range(len(reviews[2])):
        user_url = reviews[2][i][0][0]
        user_ids.append(user_url[36:57])

# Get all of the users' reviews
for user in user_ids:
    try:
        url = f"https://www.google.com/locationhistory/preview/mas?authuser=0&hl=en&gl=us&pb=!1s{user}!2m5!1soViSYcvVG6iJytMPk6amiA8%3A1!2zMWk6NCx0OjE0MzIzLGU6MCxwOm9WaVNZY3ZWRzZpSnl0TVBrNmFtaUE4OjE!4m1!2i14323!7e81!6m2!4b1!7b1!9m0!10m6!1b1!2b1!5b1!8b1!9m1!1e3!14m69!1m57!1m4!1m3!1e3!1e2!1e4!3m5!2m4!3m3!1m2!1i260!2i365!4m1!3i10!10b1!11m42!1m3!1e1!2b0!3e3!1m3!1e2!2b1!3e2!1m3!1e2!2b0!3e3!1m3!1e8!2b0!3e3!1m3!1e10!2b0!3e3!1m3!1e10!2b1!3e2!1m3!1e9!2b1!3e2!1m3!1e10!2b0!3e3!1m3!1e10!2b1!3e2!1m3!1e10!2b0!3e4!2b1!4b1!2m5!1e1!1e4!1e3!1e5!1e2!3b0!4b1!5m1!1e1!7b1!16m3!1i10!4b1!5b1!17m0!18m9!1m3!1d2567.508024970022!2d-78.667885!3d35.7546725!2m0!3m2!1i537!2i609!4f13.1"
        r = requests.get(url)
        reviews = json.loads(r.text[5:])
        if reviews[24] is None or len(reviews[24]) < 1:
            print(url)
            print(reviews)
            print(reviews[24])
            continue
        review_data = reviews[24][0]
        for i in range(len(review_data)):
            review = review_data[i][0][3]
            rating = review_data[i][0][4]
            location = {"Name": review_data[i][1][2], "Address": review_data[i][1][3], "Tags": review_data[i][1][4]}
            if len(review_data[i][1]) >= 31:
                location["Cost"] = review_data[i][1][31]
            review = {"User": user, "Review": review, "Rating": rating, "Location": location}
            print("Added review")
            agg_reviews.append(review)
    except:
        print("Exception")
        pass

with open("./data.json", "w") as f:
    f.write(json.dumps(agg_reviews))


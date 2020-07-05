from collections import defaultdict

import joblib
from sklearn.model_selection import train_test_split

import csv
from pipeline import full_pipeline

offer_id_tokens = defaultdict(list)
with open("./training/data/to_label-done.csv") as fd:
    reader = csv.reader(fd)
    next(reader)
    for entry in reader:
        offer_id_tokens[int(entry[0])].append(entry[4])

all_offers = []
with open("./training/data/vuelos.csv") as fd:
    reader = csv.reader(fd)
    next(reader)
    for entry in reader:
        all_offers.append(entry[1])

offers = []
labels = []
for offer_id, offer in enumerate(all_offers):
    if offer_id not in offer_id_tokens:
        break
    offers.append(offer)
    labels.append(offer_id_tokens[offer_id])

x_train, x_test, y_train, y_test = train_test_split(offers, labels)


full_pipeline.fit(x_train, y_train)

joblib.dump(full_pipeline, "vuelax.pkl")

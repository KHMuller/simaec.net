# Local backup of all collections in firebase/firestore DB
# Requires firebase admin sdk, service account and credentials
# https://firebase.google.com/docs/admin/setup

import json 

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

try:
    cred = credentials.Certificate("./credentials.json")
    firebase_admin.initialize_app(cred)
    db = firestore.client()
    print('Firestore Connection Created')
except:
    print('Firestore Connection Exists')

# Loops through a list of collections, fetches each document of a collection and stores the document in a dictionary with document id as key
collections = []
for collection in collections:
    documents_ref = db.collection(collection).stream()
    documents = {}
    for item in documents_ref:
        documents[item.id] = item.to_dict()
    with open('firestore/'+collection+'.json', 'w', encoding='utf8') as fp:
       json.dump(documents, fp,  indent=4, ensure_ascii=False)
    with open('backend/public/assets/json/'+collection+'.json', 'w', encoding='utf8') as fp:
        json.dump(documents, fp,  indent=4, ensure_ascii=False)
print('All collections downloaded')

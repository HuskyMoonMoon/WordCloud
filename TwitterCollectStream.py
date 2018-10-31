# Import the necessary package to process data in JSON format
import json
import pymongo
import sys
import yaml

from twitter import OAuth, Twitter, TwitterHTTPError, TwitterStream

with open("config.yml", 'r') as ymlfile:
    cfg = yaml.load(ymlfile)
 
ACCESS_TOKEN = cfg["ACCESS_TOKEN"]
ACCESS_SECRET = cfg["ACCESS_SECRET"]
CONSUMER_KEY = cfg["CONSUMER_KEY"]
CONSUMER_SECRET = cfg["CONSUMER_SECRET"]

mongo = pymongo.MongoClient(cfg["MONGODB_HOST"])
db = mongo[cfg["MONGODB_DB"]]
twcollection = db["tweets"]

oauth = OAuth(ACCESS_TOKEN, ACCESS_SECRET, CONSUMER_KEY, CONSUMER_SECRET)
twitter_stream = TwitterStream(auth=oauth)

keyword = cfg["FILTER_KEYWORD"]
lang = cfg["FILTER_LANG"]

print(f"Target storage : {cfg['MONGODB_HOST']}{cfg['MONGODB_DB']}\nKeyword : {keyword}")

iterator = twitter_stream.statuses.filter(track=keyword, language=lang)

count = twcollection.count()
try:
    for tweet in iterator:
        if "text" in tweet: 
            twcollection.insert_one(tweet)
            count = count + 1
            sys.stdout.write(f"Collected {count} tweets\r")
            sys.stdout.flush()
        else:
            continue
except (KeyboardInterrupt, SystemExit):
    print("\nTerminated")
    mongo.close()

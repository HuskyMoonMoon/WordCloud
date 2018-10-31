import pymongo
import re
import string
import pythainlp
import sys
import yaml
import numpy
from PIL import Image

with open("config.yml", 'r') as ymlfile:
    cfg = yaml.load(ymlfile)

mongo = pymongo.MongoClient(cfg["MONGODB_HOST"])
db = mongo[cfg["MONGODB_DB"]]
twcollection = db["tweets"]

stopwords = pythainlp.corpus.stopwords.words('thai')
stopwords.append("นี้")
wordList = list()

count = cfg["LAST"]
tweets = twcollection.find().sort("_id", -1 ).limit(count)
progress = 0
print(f"Tweets count: {count}")

try:
    for t in tweets:

        content = t["text"]

        # Find all hashtag in text
        hashtag = re.findall(r"#[\w\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF]+", content)

        # Extract only text content by remove all links, RT ref, mention, hashtag
        twitterElementExtracted = re.sub(r"(RT)|:|(@[A-Za-z0-9_]+)|(\\u200b+)|(\n+)|(#[\w\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF]+)|([^A-Za-z0-9\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|( )|(\w+:\/\/\S+)"
          , "", content)

        # Tokenize for Thai words
        tokenizedTweet = pythainlp.tokenize.word_tokenize(twitterElementExtracted, engine="deepcut")

        # Remove all stopwords
        stopwordRemoved = set(tokenizedTweet) - set(stopwords)

        # Combine with hashtags list and add to wordlist
        wordList += list(stopwordRemoved) + hashtag
        progress += 1
        sys.stdout.write(f"({progress} of {count}) {progress/count*100:0.2f} Percent\r")
        sys.stdout.flush()
except (KeyboardInterrupt, SystemExit):
    print("\nTerminated")
    mongo.close()


text = "|".join(wordList)

from wordcloud import WordCloud

fontPath = "./ThSarabun.ttf"
wordcloud = WordCloud(
  background_color="white",
  font_path=fontPath,
  regexp="(#[A-Za-z0-9\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF]+|[A-Za-z0-9\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF]+)",
  width=1920,
  height=1080,
  collocations=False,
  max_words=100
  )
word_freq = wordcloud.process_text(text)
img = wordcloud.generate_from_frequencies(word_freq)

# Display the generated image:
# the matplotlib way:
import matplotlib.pyplot as plt
plt.imshow(img, interpolation='bilinear')
plt.axis("off") 
plt.show()
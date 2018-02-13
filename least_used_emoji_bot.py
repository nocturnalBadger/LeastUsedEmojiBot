import math, json, io
import requests, tweepy
from credentials import *
from datetime import datetime
import os.path


def get_least_used_emoji():
    url = "http://emojitracker.com/api/rankings"

    response = requests.request("GET", url)

    data = json.loads(response.text)

    return data[-1]


def update_profile_image(jsonData):
    name = jsonData['name'].lower().replace(' ', '-')
    id = jsonData['id'].lower()

    url = "https://abs.twimg.com/emoji/v2/72x72/%s.png" % id

    response = requests.get(url)
    if response.status_code == 200:
        with open("icon.png", 'wb') as f:
            f.write(response.content)
    api.update_profile_image("icon.png")


def get_emoji_char(jsonData):
    return chr(int(jsonData['id'], 16))


def get_emoji_name(jsonData):
    return jsonData['name'].capitalize()


def compare_results(emojiName, emojiChar):
    resultsPath = "results.txt"
    if os.path.exists(resultsPath)  :
        with io.open("results.txt", mode="r", encoding="utf-8") as f:
            current, initialTime = f.readline().split(" ")
            initialTime = datetime.fromtimestamp(int(initialTime))
        if current == emojiChar:
            timeStanding = datetime.utcnow() - initialTime
            daysStanding = timeStanding.days
            if daysStanding > 1:
                return "%s (%s) has been the least used emoji for %i days" %(emojiChar, emojiName, daysStanding)
            elif daysStanding == 1:
                return "%s (%s) has been the least used emoji for over a full day" %(emojiChar, emojiName)
            else:
                hoursStanding = math.floor(timeStanding.seconds / 3600)
                if (hoursStanding % 6 == 0):
                    return "%s (%s) has been the least used emoji for over %i hours" %(emojiChar, emojiName, hoursStanding)
                else:
                    return "%s (%s) is still the least used emoji" % (emojiChar, emojiName)
        else:
            with open("results.txt", 'wb') as f:
                resultsText = (emojiChar + " " + str(math.floor(datetime.utcnow().timestamp()))).encode('utf-8')
                f.write(resultsText)
            return "The least used emoji is now: %s (%s)" % (leastUsedEmojiChar, leastUsedEmojiName)

    return "The least used emoji is currently: %s (%s)" % (leastUsedEmojiChar, leastUsedEmojiName)


# Access and authorize our Twitter credentials from credentials.py
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)

leastUsedEmojiData = get_least_used_emoji()
leastUsedEmojiChar = get_emoji_char(leastUsedEmojiData)
leastUsedEmojiName = get_emoji_name(leastUsedEmojiData)


tweetText = compare_results(leastUsedEmojiName, leastUsedEmojiChar)
print(tweetText.encode('utf-8'))


update_profile_image(leastUsedEmojiData)

try:
    api.update_status(tweetText)
except tweepy.TweepError as e:
    print(e.reason)

# try:
#     api.update_status(leastUsedEmojiChar * 140)
# except tweepy.TweepError as e:
#     print(e.reason)

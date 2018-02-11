import requests, json, tweepy, datetime
from credentials import *

def get_least_used_emoji():
    url = "http://emojitracker.com/api/rankings"

    response = requests.request("GET", url)

    data = json.loads(response.text)

    return data[-1]

def update_profile_image(jsonData):
    name = jsonData['name'].lower().replace(' ', '-')
    id = jsonData['id'].lower()

    url = "https://emojipedia-us.s3.amazonaws.com/thumbs/120/mozilla/36/%s_%s.png" % (name, id)

    response = requests.get(url)
    if response.status_code == 200:
        with open("icon.png", 'wb') as f:
            f.write(response.content)
    api.update_profile_image("icon.png")

def get_emoji_char(jsonData):
    return chr(int(jsonData['id'], 16))

def get_emoji_name(jsonData):
    return jsonData['name'].capitalize()


# Access and authorize our Twitter credentials from credentials.py
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)

leastUsedEmojiData = get_least_used_emoji()
leastUsedEmojiChar = get_emoji_char(leastUsedEmojiData)

update_profile_image(leastUsedEmojiData)

try:
    api.update_status("The least used emoji is currently: %s (%s)" % (leastUsedEmojiChar, get_emoji_name(leastUsedEmojiData)))
except tweepy.TweepError as e:
    print(e.reason)

try:
    api.update_status(leastUsedEmojiChar * 140)
except tweepy.TweepError as e:
    print(e.reason)

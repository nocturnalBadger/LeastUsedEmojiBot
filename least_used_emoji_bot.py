import io
import json
import math
import os
import sys
import time
from datetime import datetime, timezone

import ntplib
import requests
import tweepy


def fetch_utc_time():
    ntp = ntplib.NTPClient()
    # Get the time. Retry up to 10 times if there is no response
    retries = 10
    while True:
        try:
            response = ntp.request('time.nist.gov', version=3)
            break  # Exit condition - we got the time and everything's fine
        except ntplib.NTPException as e:
            if retries == 0:
                # Finally give up
                raise e

            print("Exception: %s Retrying." % e)

        time.sleep(15)
        retries -= 1

    return datetime.fromtimestamp(response.tx_time, timezone.utc)


def get_least_used_emoji():
    url = "http://emojitracker.com/api/rankings"

    response = requests.request("GET", url)

    data = json.loads(response.text)

    return data[-1]


def update_profile_image(jsonData):
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


def compare_results(emojiName, emojiChar, currentTime):
    resultsPath = "results.txt"
    if not os.path.exists(resultsPath):
        print("results file missing. skipping update")
        return None

    with io.open(resultsPath, mode="r", encoding="utf-8") as f:
        current, initialTime = f.readline().split(" ")
        initialTime = datetime.fromtimestamp(int(initialTime), timezone.utc)

    if current == emojiChar:
        timeStanding = currentTime - initialTime
        print(timeStanding)
        daysStanding = timeStanding.days
        hoursStanding = math.floor(timeStanding.seconds / 3600)

        # Past one week, always report at noon UTC
        if daysStanding > 7:
            if currentTime.hour == 12:
                return "%s (%s) has been the least used emoji for %i days"\
                        % (emojiChar, emojiName, daysStanding)
            else:
                return None
        # Past one day, report daily at the same hour of the most recent change
        elif daysStanding > 1:
            if hoursStanding == 0:
                return "%s (%s) has been the least used emoji for %i days"\
                        % (emojiChar, emojiName, daysStanding)
            else:
                return None
        # Special case for just one day
        elif daysStanding == 1:
            if hoursStanding == 0:
                return "%s (%s) has been the least used emoji for over a full day"\
                        % (emojiChar, emojiName)
            else:
                return None
        # Past one hour, report every 6 hours
        elif hoursStanding > 1 and hoursStanding % 6 == 0:
            return "%s (%s) has been the least used emoji for over %i hours"\
                    % (emojiChar, emojiName, hoursStanding)
        else:
            return None
    # Report that it just changed and update result file
    else:
        with open(resultsPath, 'wb') as f:
            resultsText = "%s %d" % (emojiChar, math.floor(currentTime.timestamp()))
            f.write(resultsText.encode("utf-8"))
        return "The least used emoji is now: %s (%s)"\
               % (leastUsedEmojiChar, leastUsedEmojiName)

    return "The least used emoji is currently: %s (%s)" % (leastUsedEmojiChar, leastUsedEmojiName)


if __name__ == "__main__":
    # Access and authorize our Twitter credentials
    consumer_key = os.environ.get("CONSUMER_KEY")
    consumer_secret = os.environ.get("CONSUMER_SECRET")
    access_token = os.environ.get("ACCESS_TOKEN")
    access_token_secret = os.environ.get("ACCESS_TOKEN_SECRET")

    dry_run = "--dry-run" in sys.argv
    if not dry_run and None in [consumer_key, consumer_secret, access_token, access_token_secret]:
        print("missing required oauth credentials. running in dry-run mode")
        dry_run = True


    leastUsedEmojiData = get_least_used_emoji()
    leastUsedEmojiChar = get_emoji_char(leastUsedEmojiData)
    leastUsedEmojiName = get_emoji_name(leastUsedEmojiData)

    currentTime = fetch_utc_time()

    tweetText = compare_results(leastUsedEmojiName, leastUsedEmojiChar, currentTime)
    if tweetText is None:
        print("No status update.")
        exit()

    print(tweetText.encode('utf-8'))

    if dry_run:
        print("dry run enabled. skipping tweet")
        exit()

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth)
    update_profile_image(leastUsedEmojiData)

    try:
        api.update_status(tweetText)
    except tweepy.TweepError as e:
        print(e.reason)
        # If status is a duplicate, change it to be ok.
        if e.api_code == 187:
            print("Duplicate status. Adding timestamp.")
            tweetText = "%s (as of %02d:%02d UTC)"\
                        % (tweetText, currentTime.hour, currentTime.minute)
            print(tweetText.encode('utf-8'))
            # Try one more time
            api.update_status(tweetText)

# @LeastUsedEmoji

[https://twitter.com/leastUsedEmoji](https://twitter.com/leastUsedEmoji)

Fetches the least used emoji from [emojitracker.com](http://emojitracker.com) and tweets it.

Requires oauth credentials exported to the environment:
* CONSUMER_KEY
* CONSUMER_SECRET
* "ACCESS_TOKEN"
* ACCESS_TOKEN_SECRET


Example build and usage:
```
docker build . -t lue_bot

docker run -it -v $PWD/results.txt:/opt/lue_bot/results.txt:z -e CONSUMER_KEY=asdf -e CONSUMER_SECRET=123 -e ACCESS_TOKEN=abc123 -e ACCESS_TOKEN_SECRET=def456 lue_bot
```

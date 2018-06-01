# Reddit Instagram Mirror Bot

Scans posts on a given subreddit for links from Instagram then fetches the raw image files from that Instagram post and mirrors them on Imgur for the most consistant viewing experience. 

## Getting Started

The most editing you will have to does is to the auth.ini.example file which I go over in the Installation instructions

### Prerequisites

My script will import all these packages so make sure they are all installed. (Some should be preinstalled on your machine)
```
import os
import json
import random
import urllib.request
import urllib
from imgurpython import ImgurClient
import configparser
import praw
import re
from imgurpython.helpers.error import ImgurClientRateLimitError, ImgurClientError
import logging
from pushbullet import Pushbullet
```

### Installing

A step by step series of examples that tell you how to get a development env running

* Step 1. - Clone the Repo!

* Step 2 - Create Imgur App and Reddit "script"

* Step 3 - Edit the auth.ini.example file in a text editor.

```
[auth]
client_id=Imgur API client ID
client_secret=Imgur API client Secret
imgur_username=Imgur Username
imgur_password=Imgur Password
reddit_client_id=Reddit App Client ID
reddit_client_secret=Reddit App Client Secret
reddit_password=Reddit Account Password
reddit_username=Reddit Account Username
reddit_subreddit=Subreddit you want to scan
reddit_limit=limit the number of posts you want to scan 
pb_key=To be notified if the script fails Pusbullet API key

```
* Step 4 - Save as auth.ini

* Step 5 - Run the script!


## Authors

* **Chat Sumlin** - *Initial work* - [jcsumlin](https://github.com/jcsumlin)

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* thanks to the StarVsTheForcesOfEvil for putting up with my testing!

# -*- coding: utf-8 -*-
"""
Created on Fri May  4 12:21:38 2018

@author: Chat
"""


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
from PIL import Image, ImageTk

config = configparser.ConfigParser()
config.read('auth.ini')


JSON_data = {}
messages = ['By the authority of Alpha and Jeep this post has been mirrored',
            'Mirrored to imgur, ‘cuz ain’t nobody got time fo’ Instagram',
            'Oh look I did a thing, give me karma!',
            'That Sure is a Nice Post You Have There ... Sure Would Be A *Shame* If I... Mirrored It!',
            'Mirrored post from Instagram', 'Hey Listen! ^I mirrored your post']

reddit = praw.Reddit(client_id=config.get('auth', 'reddit_client_id'),
                     client_secret=config.get('auth', 'reddit_client_secret'),
                     password=config.get('auth', 'reddit_password'),
                     user_agent=config.get('auth', 'reddit_user_agent'),
                     username=config.get('auth', 'reddit_username'))


client_id = config.get('auth', 'client_id')
client_secret = config.get('auth', 'client_secret')
client = ImgurClient(client_id, client_secret)
print("Posting as: ", reddit.user.me())
SUBREDDIT = "StarVStheForcesofEvil"
LIMIT = 1000
album_id = ''
if not os.path.isfile("posts_replied_to.txt"):
    posts_replied_to = []
else:
    with open("posts_replied_to.txt", "r") as f:
        posts_replied_to = f.read()
        posts_replied_to = posts_replied_to.split("\n")
        posts_replied_to = list(filter(None, posts_replied_to))

bot_message = "\r\r ^(I am a script. If I did something wrong, ) [^(let me know)](/message/compose/?to=J_C___&subject=mirror_bot)"

def scan_submissions(posts_replied_to):
    """
    Scan the most recent submissions continually.
    """
    subreddit = reddit.subreddit(SUBREDDIT)
    while True:
        for submission in subreddit.stream.submissions():
            if submission.id not in posts_replied_to and "instagram.com" in submission.url:
                print("Instagram Image Found!")
                if instagramPost(submission) is False:
                    print("\tOops ran into a strange error!")
                    continue
                result = "https://imgur.com/a/" + album_id
                print('\t' + result)
                comment = str(messages[random.randrange(0, len(messages)-1)] + "\n    [Imgur]("+ result+ ")" + bot_message)
                submission.reply(comment)
                print('\tSuccess!')
                posts_replied_to.append(submission.id)

def instagramPost(submission):
    upload_list = []
    insta_post_url_id = re.search('[p]\W\w+\S\w+', submission.url).group(0)
    insta_post_url = "https://www.instagram.com/" + insta_post_url_id + "/"
    insta_JSON_url = insta_post_url + '?__a=1'
    print(insta_JSON_url)
    with urllib.request.urlopen(insta_JSON_url) as url:
        data = json.loads(url.read().decode())
        JSON_data[submission.id] = data
    if "edge_sidecar_to_children" in JSON_data[submission.id]['graphql']['shortcode_media'].keys():
        for media in JSON_data[submission.id]['graphql']['shortcode_media']['edge_sidecar_to_children']['edges']:
            if media['node']['__typename'] == "GraphImage":
                raw_image_url = media['node']['display_url']
                upload_list.append(raw_image_url)
            elif media['node']['__typename'] == "GraphVideo":
                video_url = media['node']['video_url']
#                
                upload_list.append(video_url)
    else:
        raw_image = JSON_data[submission.id]['graphql']['shortcode_media']['display_resources'][2]
        raw_image_url = raw_image['src']
        upload_list.append(raw_image_url)
    author = JSON_data[submission.id]['graphql']['shortcode_media']['owner']['username']    
    return upload_to_imgur(upload_list, reddit.user.me(), author, submission.url)


def upload_to_imgur(upload_list, username, author, source):
    global album_id
    uploaded = []
    title="Mirrored Post from r/" + SUBREDDIT
    description='This is a mirror uploaded by /u/%s, originally made by %s, located at %s' % (username, author, source)
    fields =  {"title": title, "description": description}
    album_deletehash = {}
    try:
        album = client.create_album(fields)
    except ImgurClientRateLimitError:
        print('\tRan into imgur rate limit! %s', client.credits)
        return None
    
    album_deletehash['album'] = album['deletehash']
    for image in upload_list:
        try:
            uploaded.append(client.upload_from_url(image, config=album_deletehash, anon=True))
        except ImgurClientRateLimitError:
            print('\tRan into imgur rate limit! %s' % client.credits)
            return False
        except ImgurClientError:
            print("\tRan into an error: %s" % client.credits)
            return False
        except:
            print("\tRan into an unknown error: %s" % client.credits)
            return False
    album_id = album['id']
    return album_id

def update_files(posts_replied_to):
    with open("posts_replied_to.txt", "w") as f:
        for x in posts_replied_to:
            f.write(x + "\n")


try:
    scan_submissions(posts_replied_to)
except KeyboardInterrupt:
    update_files(posts_replied_to)
    print('Interrupted')

# -*- coding: utf-8 -*-
"""
Created on Fri May  4 12:21:38 2018

@author: Chat
"""
import configparser
import json
import logging
import os
import random
import re
import time
import urllib
import urllib.request

import coloredlogs
import praw
from imgurpython import ImgurClient
from imgurpython.helpers.error import ImgurClientRateLimitError, ImgurClientError

coloredlogs.install()
logging.basicConfig(filename='instagram.log',level=logging.DEBUG)
from pushbullet import Pushbullet
__author__ = 'jcsumlin'
__version__ = '0.3'
config = configparser.ConfigParser()
config.read('auth.ini')


JSON_data = {}
messages = ['By the authority of Alpha and Jeep this post has been mirrored',
            'Mirrored to Imgur, ‘cuz ain’t nobody got time fo’ Instagram',
            'Oh look I did a thing, give me karma!',
            'That Sure is a Nice Post You Have There ... Sure Would Be A *Shame* If I... Mirrored It!',
            'Mirrored post from Instagram',
            'Hey Listen! ^(I mirrored your post)',
            'Beep Boop Beep, Mirror Complete!']

reddit = praw.Reddit(client_id=config.get('auth', 'reddit_client_id'),
                     client_secret=config.get('auth', 'reddit_client_secret'),
                     password=config.get('auth', 'reddit_password'),
                     user_agent='Instagram Mirror Bot (Made By u/J_C___)',
                     username=config.get('auth', 'reddit_username'))

pb = Pushbullet(str(config.get('auth', 'pb_key')))
client_id = config.get('auth', 'client_id')
client_secret = config.get('auth', 'client_secret')
logging.info("Logged in and posting as: " + str(reddit.user.me()))
SUBREDDIT = config.get('auth', 'reddit_subreddit')
LIMIT = int(config.get('auth', 'reddit_limit'))

if not os.path.isfile("posts_replied_to.txt"):
    posts_replied_to = []
else:
    with open("posts_replied_to.txt", "r") as f:
        posts_replied_to = f.read()
        posts_replied_to = posts_replied_to.split("\n")
        posts_replied_to = list(filter(None, posts_replied_to))

'''
Static variables for bot.
'''
bot_message = "\r\r ^(I am a script. If I did something wrong, ) [^(let me know)](/message/compose/?to=J_C___&subject=mirror_bot)"
album_id = ''
client = ImgurClient(client_id, client_secret)

def scan_submissions():
    """
    Scan the most recent submissions continually.
    THIS IS THE MAIN DRIVER. REMEMBER TO WEAR A SEAT BELT!
    """
    subreddit = reddit.subreddit(SUBREDDIT)
    while True:
        for submission in subreddit.stream.submissions():
            if submission.id not in posts_replied_to and "instagram.com" in submission.url:
                logging.info("Instagram Image Found!")
                if instagramPost(submission) is False:
                    continue
                result = results['link_display']
                logging.info(result)
                body = random.choice(messages)
                comment = str(body + "\r\r" + result + bot_message)
                logging.info(comment)
                reply = submission.reply(comment)
                reply.mod.distinguish(how='yes', sticky=True)
                #print(comment)
                logging.debug('Successfully uploaded and commented')
                posts_replied_to.append(submission.id)
                update_files(posts_replied_to)
                logging.debug("file updated")


def instagramPost(submission: object) -> object:
    upload_list = []
    logging.info(submission.url)
    insta_post_url = re.search('https?:\/\/w?w?w?\.?instagram\.com\/p\/([a-zA-Z0-9-]+)\/', submission.url).group(0)
    logging.info(insta_post_url)
    insta_JSON_url = insta_post_url + '?__a=1'
    with urllib.request.urlopen(insta_JSON_url) as url:
        data = json.loads(url.read().decode())
        JSON_data[submission.id] = data
    if "edge_sidecar_to_children" in JSON_data[submission.id]['graphql']['shortcode_media'].keys():
        for media in JSON_data[submission.id]['graphql']['shortcode_media']['edge_sidecar_to_children']['edges']:
            if media['node']['__typename'] == "GraphImage":
                raw_image_url = media['node']['display_url']
                upload_list.append(raw_image_url)
            elif media['node']['__typename'] == "GraphVideo":
                # TODO: Add Video functionality
                # video_url = media['node']['video_url']
                # upload_list.append(video_url)
                logging.error("Post Contains a video, skipped")
    else:
        raw_image = JSON_data[submission.id]['graphql']['shortcode_media']['display_resources'][2]
        raw_image_url = raw_image['src']
        upload_list.append(raw_image_url)
    author = JSON_data[submission.id]['graphql']['shortcode_media']['owner']['username']    
    return upload_to_imgur(upload_list, reddit.user.me(), author, submission.url)


def upload_to_imgur(upload_list, username, author, source):
    """
    :param upload_list: List of urls you are uploading
    :param username: Username of the reddit account you're logged in as
    :param author: Author of the Instagram Post
    :param source: Link to the reddit post
    :return:
    """
    global results
    description = 'This is a mirror uploaded by /u/%s, original Instagram post by %s, located at %s' \
                  % (username, author, source)
    fields = {"title": "Mirrored Post from r/" + SUBREDDIT, "description": description}
    config = {}
    results = {}

    # If there are no images
    if len(upload_list) == 0:
        logging.warning('upload_list gave no urls.')
        return False
    # If there is only one image
    elif len(upload_list) == 1:
        logging.debug('A single image will be uploaded.')
        is_album = False
        config['description'] = description
    else:
        logging.debug('An album will be uploaded.')
        try:
            album = client.create_album({'description': description})
        except ImgurClientRateLimitError as e:
            logging.error('Ran into imgur rate limit! %s' % e)
            return False
        except Exception as e:
            logging.critical('Could not create album! %s' % e)
            return False
        config['album'] = album['deletehash']
        is_album = True


    images = []
    for image in upload_list:
        try:
            image = client.upload_from_url(image, config)
            images.append(image)
            logging.debug('Uploaded image: %s', str(image))
            if is_album:
                results['link_display'] = '[Imgur Album](https://imgur.com/a/%s)  \n' % album['id']
            else:
                picture_url = images[0]['link'].replace('http://', 'https://')
                results['link_display'] = '[Imgur](%s)  \n' % picture_url
        except ImgurClientRateLimitError:
            logging.error('Ran into Imgur rate limit! %s' % client.credits)
            return False
        except ImgurClientError:
            logging.error("Ran into an error: %s" % client.credits)
            return False
        except:
            logging.error("Ran into an unknown error: %s" % client.credits)
            return False


def update_files(posts_replied_to):
    with open("posts_replied_to.txt", "w") as f:
        for x in posts_replied_to:
            f.write(x + "\n")


if __name__ == '__main__':
    try:
        logging.info(' --- STARTING J_C___\'s BOT --- ')
        scan_submissions()
    except KeyboardInterrupt:
        logging.info('Interrupted')
    except (AttributeError, praw.exceptions.PRAWException) as e:
        logging.warning("PRAW encountered an error, waiting 30s before trying again. %s" % e)
        time.sleep(30)
        pass
    except praw.exceptions.APIException as e:
        logging.warning("Reddit API encountered an error. %s" % e)
        time.sleep(30)
        pass
    except praw.exceptions.ResponseException as e:
        logging.warning("Reddit encountered a response error. %s" % e)
        time.sleep(30)
        pass
    except Exception as e:
        logging.critical("Uncaught error: %s" % e)
        time.sleep(30)
        pass
    finally:            
        push = pb.push_note("SCRIPT Down", "J_CBot Instagram Script is Down!")
        update_files(posts_replied_to)
        logging.info('files updated')




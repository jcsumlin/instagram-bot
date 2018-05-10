# -*- coding: utf-8 -*-
"""
Created on Tue May  8 21:40:41 2018

@author: Chat
"""

import boto3
from botocore.client import Config
import configparser
config = configparser.ConfigParser()
config.read('auth.ini')
import wget
import re

file_names = []
ACCESS_KEY_ID = config.get('auth', 's3-id')
ACCESS_SECRET_KEY = config.get('auth', 's3-secret')
BUCKET_NAME = config.get('auth', 's3-bucket')


link = 'https://scontent-atl3-1.cdninstagram.com/vp/623211e031099a146417770a5978c408/5B9258D6/t51.2885-15/e35/31236199_2076887779267375_136003708545662976_n.jpg'
file_name = re.search('\/(\d+\D\d+\D\d+\D\w[.]\w+)', link).group(1)
file_names.append(file_name)

SUBREDDIT = "StarVStheForcesofEvil"
title = "Mirrored Post from r/" + SUBREDDIT
desc = 'This is a test'
with open('index.html') as f:
    lines = f.readlines()
for range(0, len(lines)-1) in lines:
    if '{{Title}}' in lines:
        line = line.replace('{{Title}}', title, 1)
    if '{{Description}}' in line:
        lines[line] = line.replace('{{Description}}', desc, 1)
        
0/0
wget.download(link, file_name)
data = open(file_name, 'rb')

# S3 Connect
s3 = boto3.resource(
    's3',
    aws_access_key_id=ACCESS_KEY_ID,
    aws_secret_access_key=ACCESS_SECRET_KEY,
    config=Config(signature_version='s3v4')
)


s3.Bucket(BUCKET_NAME).put_object(Key=file_name, Body=data)

print("Success")
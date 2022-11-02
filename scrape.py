"""
1.1 Collect weather vocabularies

To determine the classes weathers going to be used for training, need to scrape weather vocabulary 
website: Weather Vocabulary (US),
link: https://www.teachstarter.com/au/teaching-resource/weather-word-wall-vocabulary-us/

The function used to scrape vocabularies.
"""

from bs4 import BeautifulSoup
import csv
import os
import pandas as pd
import requests
import time
from tqdm import tqdm
from flickrapi import FlickrAPI

key = ''
secret = ''

# set up url link and use requests and BeautifulSoup to get the vocabularies
URL = "https://www.teachstarter.com/us/teaching-resource/weather-word-wall-vocabulary-us/"
headers = {'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246"}
r = requests.get(URL, headers=headers)
soup = BeautifulSoup(r.content, 'html5lib')

# find the vocabularies sections and save to list
data=[]
words = soup.find('div', attrs={"class":"links"}) 

for row in words.findAll('li', attrs={"data-v-09efc660":""}):
    text = row.text.replace('\n', '')
    if len(text)<15 and not(" " in text) and not(any(ch.isupper() for ch in text)) and (text not in data):
        data.append(text)

# save the scraped vocabularies in csv file for image collection.
fields = ['words'] 
filename = 'weather_vocabulary.csv'
with open(filename, 'w') as f:
    writer = csv.writer(f)
    writer.writerow(fields)
    for voc in data:
        writer.writerow([voc])

# the final classes are rain, cloud, sun, fog, rainbow, snow
# each class has subclasses used for image collected, eg, use the words in each class to collect images from Flickr

data = {
    'rain': ['lightning', 'thunder', 
             'thunderstorm', 'downpour', 
             'storm', 'flood', ], 
    'cloud': ['cloud', 'cloudy',],
    'sun': ['sun', 'sunny',],
    'fog': ['fog', 'mist', 'smog', 
            'sleet', 'dew'],
    'rainbow': ['rainbow',],
    'snow': ['snow', 'icicle', 'snowfall', 
             'hail', 'frost', 'blizzard',],
}

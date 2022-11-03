"""
Collect Sample images
For each scraped weather word, collect some sample images for checking and filter

1.1 Set up for image collection
"""

import csv
from google.colab import drive
import os
import pandas as pd
import requests
import time
from tqdm import tqdm
from flickrapi import FlickrAPI

# please fill in your own key and secret for FlickrAPI
key = ''
secret = ''

"""
1.2 Acquire Image Links

Flickrapi provides a walk function, which can walk through all photos in a set 
specified by a search result
"""

path='/path/to/folder/'
data = []
with open(f'{path}weather_vocabulary.csv', newline='') as f:
    reader = csv.reader(f)
    for voc in reader:
        data.extend(voc)


def fetch_image_link(query):
    flickr = FlickrAPI(key, secret) #initialize python flickr api
    photos = flickr.walk(text=query,
                        tag_mode='all',
                        extras='url_c', #specify meta data to be fetched
                        sort='relevance')   #sort search result based on relevance (high to low by default)

    max_count = 17   #let's just simply fetch 5 images for illustration
    urls = []
    count = 0

    for photo in photos:
        if count < max_count:
            count = count + 1
            #print("Fetching url for image number {}".format(count))
            try:
                url = photo.get('url_c')
                urls.append(url)
            except:
                print("Url for image number {} could not be fetched".format(count))
        else:
            print(f"Done fetching {query} urls, fetched {len(urls)} urls out of {max_count}")
            break
    return urls


# In the initial, classes I've noticed sunny days are not included, but I think it is one of the most important
# weathers, therefore, I've added sun as one of the main classes.
newdata = []
QURIES = data    #specify search query
QURIES.extend(['sun', 'sunny',])
for query in QURIES:
    print('query is ', query)
    urls = fetch_image_link(query)
    if len(urls) > 9:
        newdata.append(query)
        print('example url:', urls[0])
        urls = pd.Series(urls)
        save_path = './Flickr_scrape/'
        if not os.path.exists(save_path):
            os.makedirs(save_path)
        category_path = f'{save_path}/{query}_urls.csv'
        print(f"Writing {query} urls to {category_path}")
        urls.to_csv(category_path)

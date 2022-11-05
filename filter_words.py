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
import ipywidgets as widgets
from glob import glob
import numpy as np
from matplotlib import pyplot as plt
import cv2

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

"""
1.3 Download files using acquired links

Use collected image urls to download the image files.
"""

def fetch_files_with_link(url_path):
    with open(url_path, newline="") as csvfile:
        urls = pd.read_csv(url_path, delimiter=',')
        urls = urls.iloc[:, 1].to_dict().values()
        
    SAVE_PATH = os.path.join(url_path.replace('_urls.csv', ''))
    if not os.path.isdir(SAVE_PATH):
        os.mkdir(SAVE_PATH) #define image storage path

    for idx, url in tqdm(enumerate(urls), total=len(urls)):
        # print("Starting download {} of ".format(url[0] + 1), len(urls))
        try:
            resp = requests.get(url, stream=True)   #request file using url
            path_to_write = os.path.join(SAVE_PATH, url.split("/")[-1])
            outfile = open(path_to_write, 'wb')
            outfile.write(resp.content) #save file content
            outfile.close()
            #print("Done downloading {} of {}".format(idx + 1, len(urls)))
        except:
            print("Failed to download url number {}".format(idx)) 
    print(f"Done with {url_path} download, images are saved in {SAVE_PATH}")

print("Start downloading images...")


CATEGORIES = newdata    #specify search query
save_path = './Flickr_scrape/'
for category in CATEGORIES:
    url_path = f'{save_path}/{category}_urls.csv'
    fetch_files_with_link(url_path)

"""
1.4 Visualize Collected Image 
"""

def plot_samples(category):
    max_count = 10
    paths = sorted(glob(f'./Flickr_scrape/{category}/*.*'))
    # paths = np.random.choice(paths, max_count, replace=False)
    plt.figure(figsize=(12,12))
    for i in range(max_count):
        image = cv2.imread(paths[i])
        image = cv2.resize(image, (512,512), interpolation=cv2.INTER_LINEAR)
        plt.subplot(1, max_count, i+1)
        plt.title(category)
        plt.imshow(image)
        plt.axis('off')
    plt.tight_layout()
    plt.show()


all_categories = newdata
for category in all_categories:
    plot_samples(category)


"""
From the sample images collected above, we can see that some words have high 
errors, which could be due to the fact that some words have other meanings 
which are not relevent to weather, for example shower, pressure, etc. Some 
words are very hard to express in weather image, for example temperature.

There are also other reasons such as users post images with animals, persons, 
and even bands, which happens to have names match the word of weather, and some 
posts are related to their feelings of the weather.

Therefore, the words containing high errors are excluded from the final data 
collection.
"""

# based checking, add the following words in excluded list
words_exclude = ['words', 'weather', 'rain', 'temperature', 'pressure', 'overcast', 'shower', 'sunrise', 'dry', 'tornado', 'sunset', 'humidity',
                 'cold', 'heat', 'wind', 'breeze', 'humid', 'blustery', 'drought', 'tropical', 'temperate', 'moisture', 'drizzle', 'warm',
                 'climate', 'muggy', 'gale', 'atmosphere', 'isobar', 'condensation', 'forecast', 'freeze', 'barometric', 'gust', 'whirlwind',
                 'hurricane', 'cyclone', 'air', 'balmy', 'avalanche', 'ozone', 'outlook', 'sky', 'surge', 'monsoon', 'permafrost.']

final_words = [i for i in newdata if i not in words_exclude]

"""
The final words amount to 20+, which is still a lot for a model to learn. 
Based on the meaning of words, and the images, I have classied them into 6 more 
general classes.
"""

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

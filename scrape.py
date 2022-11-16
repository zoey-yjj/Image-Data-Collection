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
import ipywidgets as widgets
from glob import glob
import numpy as np
from matplotlib import pyplot as plt
import cv2


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

"""
1.2 Checking and filter words

Based on the words collected, I have collected 10 images for each word and 
displayed for checking. I have noticed that images for certain words contains 
a lot errors. This is due to the fact that some words have other meanings which 
are not relevent to weather, for example shower, pressure, etc. Some words are 
very hard to express in weather image, for example temperature.

There are also other reasons such as users would post images with animals, 
persons, and even bands, which happens to have names match the word of weather, 
and some posts are related to their feelings of the weather.

Therefore, the words containing high errors are excluded from the final data collection.

Detailed working is saved in seperate notebook named "filter_words.py", because 
the print out of all words are very long.

To filter out the irrelevant and high error words, I have manually browse through 
the images, save all the excluded words in a list, and excluded them from the final 
collection of images.

After filter, there are stil more than 20 words. Most of words have similar images 
and can be classified to a broader weather class. Therefore, after further 
classification, the words are included in 6 classes, which are used as the classes 
for our model.
"""

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

"""
1.3 Scrape images from Flickr
Full dataset collected amount to 24,000 images. Here I have presented the 
functions for collection and images saved in the dataset for amount of 10 for 
each class as demo. To collect more images, please adjust the amount of urls 
scraped for image collection.

The total dataset I have collect is amount 24,000, so that each class has 4,000 
images. To make sure each has same total amount, each subclass amount is equal to 
4000 / len(class_list). In this way, within each class, the subclasses have equal 
amount of images.

Images collected for each class is saved in their own folder. The path, imageID 
and label are also collected and saved in csv file for training.
"""

def fetch_image_link(query, amount):
    flickr = FlickrAPI(key, secret)         #initialize python flickr api
    photos = flickr.walk(text=query,
                        tag_mode='all',
                        extras='url_c',     #specify meta data to be fetched
                        sort='relevance')   #sort search result based on relevance (high to low by default)
    
    max_count = amount                      #let's just simply fetch 5 images for illustration
    urls = []
    count = 0

    for photo in photos:
        if count >= max_count:
            break
        count = count + 1
        try:
            url = photo.get('url_c')
            urls.append(url)
        except:
            print("Url for image number {} could not be fetched".format(count))
    return urls


# here is a demo to scrap 15 images and save to folder
# scraping 15 because some urls fails to download, need to scrap a more in case
amt_collect = 15
for label, QURIES in data.items():
    l = len(QURIES)
    amount_temp = int(amt_collect / l)
    amount_list = [amount_temp, ] * (l - 1)
    amount_list.append(amt_collect - sum(amount_list)) # for 10 images, the last sub class has more images than others, 
                                                        # but when we collect 4000 total amount for each class, the difference is immaterial
    for query, amount in zip(QURIES, amount_list):
        urls = fetch_image_link(query, amount)
        if len(urls) > amount - 1:
            urls = pd.Series(urls)
            save_path = './Flickr_scrape/'
            if not os.path.exists(save_path):
                os.makedirs(save_path)
            category_path = f'{save_path}/{label}_urls.csv'
            urls.to_csv(category_path, mode='a', header=False, index=False)


def fetch_files_with_link(url_path):
    with open(url_path, newline="") as csvfile:
        urls_df = pd.read_csv(url_path, delimiter=',', index_col=False, header=None, names=["ImageID"])
        urls = urls_df.iloc[:, 0].to_dict().values()
    
    path = []
    id = []
    SAVE_PATH = os.path.join(url_path.replace('_urls.csv', ''))
    if not os.path.isdir(SAVE_PATH):
        os.mkdir(SAVE_PATH)                           #define image storage path

    for idx, url in tqdm(enumerate(urls), total=len(urls)):
        try:
            resp = requests.get(url, stream=True)     #request file using url
            url = url.split("/")[-1]
            path_to_write = os.path.join(SAVE_PATH, url)
            path.append(path_to_write)
            id.append(url)
            outfile = open(path_to_write, 'wb')
            outfile.write(resp.content)               #save file content
            outfile.close()
        except:
            print("Failed to download url number {}".format(idx)) 
    print(f"Done with {url_path} download, images are saved in {SAVE_PATH}")
    return pd.DataFrame(list(zip(path, id)), columns =['path', 'ImageID'])


print("Start downloading images...")

CATEGORIES = data.keys()   #specify search query
save_path = './Flickr_scrape/'
for category in CATEGORIES:
    url_path = f'{save_path}/{category}_urls.csv'
    path_df = fetch_files_with_link(url_path)

"""
1.4 Visualize Collected Image 
"""

def plot_samples(category):
    paths = sorted(glob(f'./Flickr_scrape/{category}/*.*'))
    paths = np.random.choice(paths, 10, replace=False)
    plt.figure(figsize=(12,12))
    for i in range(10):
        image = cv2.imread(paths[i])[...,[2,1,0]]
        image = cv2.resize(image, (512,512), interpolation=cv2.INTER_LINEAR)
        plt.subplot(1, 10, i+1)
        plt.title(category)
        plt.imshow(image)
        plt.axis('off')
    plt.tight_layout()
    plt.show()


for category in CATEGORIES:
    plot_samples(category)

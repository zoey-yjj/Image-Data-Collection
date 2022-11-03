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
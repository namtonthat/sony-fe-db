"""
Scrape the `www.sony.com.au/lenses/gallery` website
and render each lens by their focal length and performance
"""

import requests
from bs4 import BeautifulSoup
import pandas
import json
import os

URL = "https://www.sony.com.au/lenses/gallery"

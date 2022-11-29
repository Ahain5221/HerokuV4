from django.core.management.base import BaseCommand
from polls.models import Game
from django.contrib.auth.models import User
import requests
import os
from time import time
import omdb
import random
from polls.views import *
from polls.models import Movie


class Command(BaseCommand):
    def handle(self, *args, **options):
        type_of_show = 'movies_at_home'
        update = '0'
        start = time()
        months = {"Jan": "01", "Feb": "02", "Mar": "03", "Apr": "04", "May": "05", "Jun": "06", "Jul": "07",
                  "Aug": "08", "Sep": "09", "Oct": "10", "Nov": "11", "Dec": "12"}
        api_key = os.environ.get('API_KEY')
        api = omdb.OMDBClient(apikey=api_key)
        genres = ['action', 'adventure', 'comedy', 'crime', 'drama', 'fantasy', 'horror', 'sci_fi', 'romance', 'war']
        services = ['netflix', 'amc_plus', 'amazon_prime', 'disney_plus', 'hbo_max']
        random.shuffle(genres)
        random.shuffle(services)

        if update == '1':
            update = True
        else:
            update = False

        for service in services:
            for genre in genres:
                url = 'https://www.rottentomatoes.com/browse/' + type_of_show + '/affiliates:' + service + '~genres:' \
                      + genre + '?page=1'
                final_time, end_scraping = scrape_show(url, False, type_of_show, api, update, months, start)
                if end_scraping:
                    exit()
        exit()


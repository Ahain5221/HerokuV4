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
        tweet_save_to_db()
        exit()



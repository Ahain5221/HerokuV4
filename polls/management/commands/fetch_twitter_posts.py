from django.core.management.base import BaseCommand
from polls.views import *


class Command(BaseCommand):
    def handle(self, *args, **options):
        tweet_save_to_db()
        print("Collection of posts from Twitter completed.")
        exit()



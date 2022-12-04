from django.core.management.base import BaseCommand
from polls.models import Game
from django.contrib.auth.models import User
import requests
import os
from time import time
import omdb
import random
from polls.views import *
from django.contrib.auth.models import User
from polls.models import Profile

class Command(BaseCommand):
    def handle(self, *args, **options):
        get_all_profile_users = Profile.objects.all()
        print(get_all_profile_users)

        for userP in get_all_profile_users:
            print(userP)
            print(userP.expired_registration_check())
            if userP.user.is_superuser or userP.user.is_staff:
                continue
            elif userP.expired_registration_check():
                userP.user.delete()
                print("Usunięto kogoś")
            else:
                continue

        exit()


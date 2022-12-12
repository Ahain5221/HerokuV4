from django.core.management.base import BaseCommand
from polls.views import *
from polls.models import *
from django.contrib.auth.models import User
import requests
from time import time, sleep
class Command(BaseCommand):
    def handle(self, *args, **options):
        start = time()
        months_eng = {"Jan,": "01", "Feb,": "02", "Mar,": "03", "Apr,": "04", "May,": "05", "Jun,": "06",
                      "Jul,": "07",
                      "Aug,": "08", "Sep,": "09", "Oct,": "10", "Nov,": "11", "Dec,": "12"}

        added_games = 0
        # error_counter = 0

        for i in range(1, 40):
            steams_ids, end = scrape_steam_ids(i, start)
            if end:
                exit()

            for steam_app_id in steams_ids:
                if time() - start > 25:
                    exit()
                if check_app_id(steam_app_id):
                    # print("To ID jest znane już!")
                    continue
                url2 = "https://store.steampowered.com/api/appdetails?appids=" + str(steam_app_id)
                response2 = requests.get(url2)
                jsoned_data_from_response_app_details = response2.json()
                try:
                    if not jsoned_data_from_response_app_details[str(steam_app_id)]['success']:
                        continue
                except TypeError:
                    print("Type error dla ID:", steam_app_id)
                    # error_counter += 1
                    # if error_counter == 5:
                    break
                    # sleep(1)
                    # continue
                else:
                    type_app = jsoned_data_from_response_app_details[str(steam_app_id)]['data']['type']
                    if type_app == 'game':
                        try:
                            game_date_of_release_check = \
                                jsoned_data_from_response_app_details[str(steam_app_id)]['data'][
                                    'release_date']
                            if game_date_of_release_check['coming_soon']:
                                continue

                            game_name = jsoned_data_from_response_app_details[str(steam_app_id)]['data']['name']
                            game_mode_pk = games_mode_api(
                                jsoned_data_from_response_app_details[str(steam_app_id)]['data']['categories'])
                            game_image = jsoned_data_from_response_app_details[str(steam_app_id)]['data'][
                                'header_image']
                            game_genre_pk = games_genres_api(
                                jsoned_data_from_response_app_details[str(steam_app_id)]['data']['genres'])
                            game_summary = jsoned_data_from_response_app_details[str(steam_app_id)]['data'][
                                'short_description']
                            game_developer_pk = games_developer_api(
                                jsoned_data_from_response_app_details[str(steam_app_id)]['data']['developers'][0])
                        except KeyError:
                            print(steam_app_id)
                            continue
                        words_to_check = ['porn', 'sex', 'gangbang', 'erotic']
                        if any(ext in game_name.lower() for ext in words_to_check):
                            print("Nasty word found in name!!")
                            continue
                        if any(ext in game_summary.lower() for ext in words_to_check):
                            print("Nasty word found in summary!!")
                            continue
                        if not game_date_of_release_check['coming_soon']:
                            game_date_pf_release = game_date_of_release_check['date']
                            split_date = game_date_pf_release.split()
                            if len(split_date) != 3:
                                continue
                            try:
                                correct_date = split_date[2] + '-' + months_eng[split_date[1]] + '-' + split_date[0]
                            except TypeError and KeyError:
                                continue
                        else:
                            correct_date = '1900-01-01'
                        game_object = Game.objects.create(
                            added_by=None,
                            title=game_name,
                            game_image=game_image,
                            date_of_release=correct_date,
                            Verified=True,
                            summary=game_summary,
                        )
                        game_object.mode.set(game_mode_pk)
                        game_object.developer.set(game_developer_pk)
                        game_object.genre.set(game_genre_pk)

                        print(game_name, added_games, time() - start)
                        added_games += 1

        print("Game scraping ended")
        exit()

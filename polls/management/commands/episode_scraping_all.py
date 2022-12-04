from django.core.management.base import BaseCommand
from polls.views import *
from polls.models import *
from time import time
from datetime import datetime

class Command(BaseCommand):
    def handle(self, *args, **options):
        start = time()
        api_key = os.environ.get('API_KEY')
        api = omdb.OMDBClient(apikey=api_key)
        today_date = datetime.strptime(datetime.today().strftime('%Y-%m-%d'), "%Y-%m-%d").date()
        series_pks = []
        series_set = Series.objects.filter(Verified=True)

        for series in series_set.all():
            if series.episodes_update_date:
                days_difference = (today_date - series.episodes_update_date).days
                if days_difference >= 7:
                    series_pks.append(series.pk)
            else:
                series_pks.append(series.pk)
        for series_pk in series_pks:
            print(series_pk)
            episodes_scraping(series_pk, api, start)
            print(time() - start)
            if time() - start > 25:
                print('timeout')
                exit()
        exit()

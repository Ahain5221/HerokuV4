from django.core.management.base import BaseCommand

from polls.models import Profile


class Command(BaseCommand):
    def handle(self, *args, **options):
        get_all_profile_users = Profile.objects.all()
        for userP in get_all_profile_users:
            if userP.user.is_superuser or userP.user.is_staff:
                continue
            elif userP.expired_registration_check():
                userP.user.delete()
            else:
                continue
        exit()


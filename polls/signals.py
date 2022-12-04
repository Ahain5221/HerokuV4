from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib import messages
from django.contrib.auth.signals import user_logged_out, user_logged_in

from .models import Profile


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        get_name = instance
        Profile.objects.create(user=instance,name=get_name.username)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


def logout_notifier(sender, request, user, **kwargs):
    messages.success(request, 'You successfully logged out!')

    get_profile = Profile.objects.get(user_id=user.pk)
    get_profile.name = user.username
    get_profile.save()
    print()


# Czasowy signal, byście nie musieli od razu resetować bazy
def login_set_name(sender, request, user, **kwargs):
    messages.success(request, 'You successfully logged out!')

    get_profile = Profile.objects.get(user_id=user.pk)
    get_profile.name = user.username
    get_profile.save()
    print()


user_logged_out.connect(logout_notifier)
user_logged_in.connect(login_set_name)

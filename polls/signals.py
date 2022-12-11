from django.contrib.auth.models import User
from polls.models import Game
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib import messages
from django.contrib.auth.signals import user_logged_out, user_logged_in
from django.utils.text import slugify

from .models import Profile

from polls.models import *


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        get_name = instance
        Profile.objects.create(user=instance, name=get_name.username)


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

    get_profile = Profile.objects.get(user_id=user.pk)
    get_profile.name = user.username
    get_profile.save()
    print()


@receiver(post_save, sender=Thread)
def add_id_to_thread(sender, instance, created, **kwargs):
    if created:
        instance.slug = slugify(instance.title) + "-" + str(instance.pk)
        get_category_object = ForumCategory.objects.get(pk=instance.category_id)
        instance.slug_category = get_category_object.slug
        instance.save()


user_logged_out.connect(logout_notifier)
user_logged_in.connect(login_set_name)


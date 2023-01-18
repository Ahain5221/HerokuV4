from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib import messages
from django.contrib.auth.signals import user_logged_out, user_logged_in
from polls.models import *


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        get_name = instance
        Profile.objects.create(user=instance, name=get_name.username, profile_image_url="https://cdn-icons-png"
                                                                                        ".flaticon.com/512/3442/3442087.png")


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
        if len(instance.title) >= 40:
            instance.slug = slugify(instance.title[0:40]) + "-" + str(instance.pk)
        else:
            instance.slug = slugify(instance.title) + "-" + str(instance.pk)

        get_category_object = ForumCategory.objects.get(pk=instance.category_id)
        instance.slug_category = get_category_object.slug
        instance.save()


user_logged_out.connect(logout_notifier)
user_logged_in.connect(login_set_name)


from django.test import TestCase
from polls.models import *
from django.contrib.auth import get_user_model
import datetime
from django.utils import timezone

# Tu trzeba dużo sprawdzić


class PermissionRejectandAcceptTestCase(TestCase):
    def setUp(self):

        self.user = User.objects.create(
            username='testuser',
            password='testpass'
        )
        self.profile = Profile.objects.get(name=self.user)
        self.profile.registration_completed = True
        self.userStuff = User.objects.create_user(username='stuffuser', password='password')
        self.userStuff.is_staff = True
        self.userStuff.save()
        login = self.client.login(username='stuffuser', password='password')


    def test_reject_autocomplete_permission_view_post(self):
        # create a RequestPermission object and store it in the database


        request_object = RequestPermission.objects.create(FromUser=self.profile, status="Pending")
        pk = request_object.pk
        # sending a POST request to the view
        response = self.client.post(reverse('reject-autocomplete-permission', kwargs={'pk': pk}))

        # check if the view returned the correct HTTP status (302 - redirect)
        self.assertEqual(response.status_code, 302)

        # check if the RequestPermission object has been changed (status changed to "Rejected").
        request_object.refresh_from_db()
        self.assertEqual(request_object.status, "Rejected")


    def test_succesful_autocomplete_permission_granted_view_post(self):
        from django.contrib.auth.models import Group, Permission

        pk = self.user.pk

        # wysłanie żądania POST do widoku
        response = self.client.post(reverse('get-autocomplete-permission', kwargs={'pk': pk}))

        # sprawdzenie, czy widok zwrócił odpowiedni status HTTP (302 - redirect)
        self.assertEqual(response.status_code, 302)

        # sprawdzenie, czy obiekt User został dodany do grupy 'autocomplete_group'

        autocomplete_group = Group.objects.get(name='autocomplete_group')
        self.assertIn(self.user, autocomplete_group.user_set.all())



from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core import mail
from django.contrib.auth.forms import PasswordResetForm


class PasswordResetRequestViewTests(TestCase):
    def setUp(self):
        self.url = reverse('password_reset_polls')
        self.user = get_user_model().objects.create_user(username='testuser',
            email='user@example.com', password='testpass')

    def test_view_url_exists_at_desired_location(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse('password_reset_polls'))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'registration/password_reset_form.html')

    def test_view_uses_password_reset_form(self):
        response = self.client.get(self.url)
        self.assertIsInstance(response.context['password_reset_form'], PasswordResetForm)

    def test_form_submission_sends_email(self):
        self.client.post(self.url, {'email': self.user.email})
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, [self.user.email])

    def test_form_submission_with_inactive_user(self):
        self.user.is_active = False
        self.user.save()
        response = self.client.post(self.url, {'email': self.user.email})
        self.assertContains(response, "You have not activated your")


from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from polls.token import account_activation_token


class ActivateViewTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='testuserA',
            email='user@example.com', password='testpass')
        self.uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        self.uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        self.token = account_activation_token.make_token(self.user)
        self.url = reverse('activate', kwargs={'uidb64': self.uid, 'token': self.token})

    def test_view_url_exists_at_desired_location(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_view_redirects_on_successful_activation(self):
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse('index'))

    def test_view_sets_user_profile_registration_completed_flag(self):
        self.client.get(self.url)
        user_profile = User.objects.get(username='testuserA').profile
        self.assertTrue(user_profile.registration_completed)

    def test_view_with_invalid_uidb64(self):
        url = reverse('activate', kwargs={'uidb64': 'invalid', 'token': self.token})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Activation link is invalid!')

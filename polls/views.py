import os
import random
from datetime import datetime
from time import time, sleep
from django.contrib.admin.views.decorators import staff_member_required
from .models import RequestPermission
import omdb
# third-party imports
import requests
from bs4 import BeautifulSoup, SoupStrainer
from dal import autocomplete
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.views import PasswordChangeView
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.core.mail import send_mail, BadHeaderError
from django.db.models.query_utils import Q
from django.http import HttpResponse, HttpResponseForbidden, Http404
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.shortcuts import render, redirect
from django.template.loader import render_to_string

from django.http import HttpResponseRedirect, HttpResponse, Http404

from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.urls import reverse_lazy
from django.utils.encoding import force_bytes
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from django.utils.http import urlsafe_base64_encode
from django.views import generic
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormMixin
from polls.models import Author
from .forms import *
from .models import Book
from .models import Game, Developer, Profile, GameGenre, GameMode, KnownSteamAppID
from .models import Movie, Series, Actor, Director, Language, MovieSeriesGenre, Season, Episode, MovieReview, \
    MovieWatchlist, SeriesWatchlist, SeriesReview, GameReview, GameList, BookReview, BookList
from .models import Movie, Series, Actor, Director, Language, MovieSeriesGenre, Season, Episode, MovieReview, \
    MovieWatchlist, SeriesWatchlist, SeriesReview, GameReview, GameList
from .models import Movie, Series, Actor, Director, Language, MovieSeriesGenre

from .models import Post, Thread
from .forms import PostForm, ForumCategory, ThreadCategoryForm, ThreadForm
from django.views.generic.edit import FormMixin
from taggit.models import Tag

# standard library imports
import csv
import datetime as dt
import json
import os
import statistics
# import time

# third-party imports
import requests

from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from .forms import SignUpForm
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from .token import account_activation_token
from django.views import View
# from .models import *
from friendship.models import Friend, Follow, Block, FriendshipRequest
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
import random
from polls.decorators import *
import xlrd
from django.contrib.sessions.models import Session
from django.utils import timezone


def add_books(request):
    link = "polls/static/Books.xls"

    workbook = xlrd.open_workbook(link)
    sheet = workbook.sheet_by_name('Sheet1')

    for row in range(1, sheet.nrows):

        isbn = str(sheet.cell(row, 3).value)
        title = sheet.cell(row, 0).value

        if Book.objects.filter(title=title).exists():
            continue

        authors_pk = []
        genres_pk = []
        languages_pk = []

        authors = sheet.cell(row, 1).value
        summary = sheet.cell(row, 2).value
        genres = sheet.cell(row, 4).value
        languages = sheet.cell(row, 5).value
        img = sheet.cell(row, 6).value

        authors = authors.split(',')
        genres = genres.split(',')
        languages = languages.split(',')

        for author_name in authors:
            author = Author.objects.filter(first_last_name=author_name).first()

            if author:
                authors_pk.append(author.pk)
            else:
                author_object = Author.objects.create(first_last_name=author_name)
                authors_pk.append(author_object.pk)

        for genre_name in genres:
            genre = MovieSeriesGenre.objects.filter(name=genre_name).first()

            if genre:
                genres_pk.append(genre.pk)
            else:
                genre_object = MovieSeriesGenre.objects.create(name=genre_name)
                genres_pk.append(genre_object.pk)

        for language_name in languages:
            language = Language.objects.filter(name=language_name).first()

            if language:
                languages_pk.append(language.pk)
            else:
                language_object = Language.objects.create(name=language_name)
                languages_pk.append(language_object.pk)

        book_object = Book.objects.create(
            title=title,
            summary=summary,
            isbn=isbn,
            Verified=True,
            added_by=request.user,
            book_image=img
        )
        book_object.authors.set(authors_pk)
        book_object.genre.set(genres_pk)
        book_object.languages.set(languages_pk)

    return redirect('index')


def add_categories(request):
    link = "polls/static/category.xls"

    workbook = xlrd.open_workbook(link)
    sheet = workbook.sheet_by_name('Sheet1')

    for row in range(1, sheet.nrows):

        name = str(sheet.cell(row, 0).value)
        summary = sheet.cell(row, 1).value

        ForumCategory.objects.update_or_create(
            title=name,
            defaults=
            {
                'content': summary
            }
        )

    return redirect('index')


class cbv_view(generic.ListView):
    model = Developer
    template_name = 'index.html'


def handler(request, exception):
    context = {'domain': get_current_site(request)}
    return render(request, 'errorrr.html', context=context)


@stuff_or_superuser_required
def get_autocomplete_permission(request, pk):
    new_group, created = Group.objects.get_or_create(name='new_group')
    user_object = User.objects.get(id=pk)
    if created:
        permission_developer = Permission.objects.get(name='Can add developer')
        permission_actor = Permission.objects.get(name='Can add actor')
        permission_director = Permission.objects.get(name='Can add director')
        new_group.permissions.add(permission_developer, permission_actor, permission_director)
    new_group.user_set.add(user_object)
    try:
        checkP = RequestPermission.objects.get(FromUser=pk)
        checkP.status = "Accepted"
        checkP.save(update_fields=['status'])
    except (Exception,):
        return redirect('profile-page', user_object.username)
    return redirect('request-list')
    # return redirect('profile-page',pk)


@stuff_or_superuser_required
def reject_autocomplete_permission(request, pk):
    request_object = RequestPermission.objects.get(FromUser=pk)
    request_object.status = "Rejected"
    request_object.save(update_fields=['status'])
    return redirect('request-list')
    # return redirect('profile-page',pk)


class DeveloperAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Developer.objects.none()

        basic_qs = Developer.objects.all()
        qs1 = basic_qs.filter(Verified=False, added_by=self.request.user.id)
        qs2 = basic_qs.filter(Verified=True)
        qs = qs1 | qs2
        if self.q:
            qs = qs.filter(company_name__istartswith=self.q)

        return qs

    def create_object(self, create_field_from_url):
        """Create an object given a text."""
        return self.get_queryset().get_or_create(added_by=self.request.user,
                                                 company_name=create_field_from_url)[0]


class ActorAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        if not self.request.user.is_authenticated:
            return Actor.objects.none()

        basic_qs = Actor.objects.all()
        qs1 = basic_qs.filter(Verified=False, added_by=self.request.user.id)
        qs2 = basic_qs.filter(Verified=True)
        qs = qs1 | qs2
        if self.q:
            qs = qs.filter(full_name__istartswith=self.q)

        return qs

    def create_object(self, create_field_from_url):
        """Create an object given a text."""
        return self.get_queryset().get_or_create(added_by=self.request.user,
                                                 full_name=create_field_from_url)[0]


class DirectorAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        if not self.request.user.is_authenticated:
            return Director.objects.none()

        basic_qs = Director.objects.all()
        qs1 = basic_qs.filter(Verified=False, added_by=self.request.user.id)
        qs2 = basic_qs.filter(Verified=True)
        qs = qs1 | qs2
        if self.q:
            qs = qs.filter(full_name__istartswith=self.q)

        return qs

    def create_object(self, create_field_from_url):
        """Create an object given a text."""
        return self.get_queryset().get_or_create(added_by=self.request.user,
                                                 full_name=create_field_from_url)[0]


class AuthorAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        if not self.request.user.is_authenticated:
            return Author.objects.none()

        basic_qs = Author.objects.all()
        qs1 = basic_qs.filter(Verified=False, added_by=self.request.user.id)
        qs2 = basic_qs.filter(Verified=True)
        qs = qs1 | qs2
        if self.q:
            qs = qs.filter(first_last_name__istartswith=self.q)

        return qs

    def create_object(self, create_field_from_url):
        """Create an object given a text."""
        return self.get_queryset().get_or_create(added_by=self.request.user,
                                                 first_last_name=create_field_from_url)[0]


def signup(request):
    if request.user.is_authenticated:
        return redirect('index')
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            try:
                to_email = form.cleaned_data.get('email')
                check_username = form.cleaned_data.get('username')
                name_test = User.objects.filter(username__iexact=str(check_username)).exists()
                email_test = User.objects.filter(email__iexact=str(to_email)).exists()
                if name_test or email_test:
                    messages.error(request, 'Your username or email is already taken.')
                    return redirect('form')
                user = form.save(commit=False)
                user.is_active = False
                user.username = user.username.lower()
                user.save()

                # to get the domain of the current site
                current_site = get_current_site(request)
                mail_subject = 'Pop Culture Tracker - Activation link'
                message = render_to_string('registration/Activate_account_with_email.html', {
                    'user': user,
                    'domain': current_site.domain,
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                    'token': account_activation_token.make_token(user),
                })
                email = EmailMessage(
                    mail_subject, message, 'pct-team@outlook.com', to=[to_email]
                )
                email.send()
            except (Exception,):
                messages.error(request, 'Something went wrong, try again')
                user.delete()
                return redirect('form')

            messages.success(request, 'Please confirm your email address to complete the registration!')

            return redirect('index')
            # return HttpResponse('Please confirm your email address to complete the registration')
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})


@anonymous_required
def password_reset_request(request):
    if request.method == "POST":
        password_reset_form = PasswordResetForm(request.POST)
        if password_reset_form.is_valid():
            data = password_reset_form.cleaned_data['email']
            associated_users = User.objects.filter(Q(email__iexact=data))
            if associated_users.exists():
                for user in associated_users:
                    if not user.is_active:
                        return HttpResponse("You have not activated your account.")
                    subject = "Password Reset Requested"
                    email_template_name = "registration/password_reset_email_text.html"
                    c = {
                        "email": user.email,
                        'domain': '127.0.0.1:8000',
                        'site_name': 'Website',
                        "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                        "user": user,
                        'token': default_token_generator.make_token(user),
                        'protocol': 'http',
                    }
                    email = render_to_string(email_template_name, c)
                    try:
                        send_mail(subject, email, 'pct-team@outlook.com', [user.email], fail_silently=False)
                    except BadHeaderError:
                        return HttpResponse('Invalid header found.')
                    return render(request, "registration/password_reset_done.html")
    password_reset_form = PasswordResetForm()
    return render(request=request, template_name="registration/password_reset_form.html",
                  context={"password_reset_form": password_reset_form})


def activate(request, uidb64, token):
    user_model = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = user_model.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, user_model.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user_profile = user.profile
        user_profile.registration_completed = True
        user_profile.save()
        user.save()
        messages.success(request, 'Thank you for your email confirmation. Now you can login into your account!')
        return redirect('index')
        # return HttpResponse('Thank you for your email confirmation. Now you can login your account.')
    else:
        return HttpResponse('Activation link is invalid!')


def sendmail(request):
    send_mail(
        'Weryfikkacja rejestracji na PCT',  # Tytuł maila
        'Link do weryfikacji.',  # Treść maila
        'pct-team@outlook.com',  # Z jakiego maila wysyłamy
        ['pct-team@outlook.com'],  # Na jakiego maila wysyłamy
        fail_silently=False,
    )
    return render(request, 'sendmail.html')


def index(request):
    """View function for home page of site."""
    if request.user.is_authenticated:

        # num_visits = request.session.get('num_visits', 0)
        last_book = Book.objects.filter(Verified=True).last()
        last_game = Game.objects.filter(Verified=True).last()
        last_series = Series.objects.filter(Verified=True).last()
        last_movie = Movie.objects.filter(Verified=True).last()

        # request.session['num_visits'] = num_visits + 1

        index_context = {
            'last_book': last_book,
            'last_game': last_game,
            'last_series': last_series,
            'last_movie': last_movie
        }
        return render(request, 'index.html', context=index_context)

    else:
        num_movies = Movie.objects.all().count()
        num_series = Series.objects.all().count()
        num_games = Game.objects.all().count()
        num_directors = Director.objects.all().count()
        num_actors = Actor.objects.all().count()
        num_users = Profile.objects.all().count()
        num_developers = Developer.objects.all().count()
        num_books = Book.objects.all().count()

        landing_context = {
            'num_movies': num_movies,
            'num_series': num_series,
            'num_games': num_games,
            'num_directors': num_directors,
            'num_actors': num_actors,
            'num_users': num_users,
            'num_developers': num_developers,
            'num_books': num_books

        }

        return render(request, 'landing.html', context=landing_context)


def news_sections(request, num):
    # todo
    if num <= 5:
        return HttpResponse("Book.objects.all()")


class MyFavorites(generic.DetailView):
    model = Profile
    template_name = "polls/Profile/favorites.html"
    slug_field = 'name'
    slug_url_kwarg = 'name'

    def get_context_data(self, *args, **kwargs):
        context = super(MyFavorites, self).get_context_data(*args, **kwargs)
        context['type'] = self.kwargs['type']
        return context


class SignUpView(SuccessMessageMixin, generic.CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy("login")
    success_message = "Profile was created successfully"

    template_name = "registration/signup.html"


def search(request):
    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():
            return HttpResponseRedirect('/thanks/')
    else:
        form = SearchForm()
    return render(request, 'polls/search_form_game.html', {'form': form})


def search_user(request):
    if request.method == 'POST':
        form = SearchForm_User(request.POST)
        if form.is_valid():
            return HttpResponseRedirect('/thanks/')
    else:
        form = SearchForm_User()
    return render(request, 'polls/search_form_user.html', {'form': form})


def search_general(request):
    if request.method == 'POST':
        form = SearchForm_User(request.POST)
        if form.is_valid():
            return HttpResponseRedirect('/thanks/')
    else:
        form = SearchForm_User()
    return render(request, 'polls/search_form_general.html', {'form': form})


def search_movie(request):
    if request.method == 'POST':
        form = SearchForm_Movie(request.POST)
        if form.is_valid():
            return HttpResponseRedirect('/thanks/')
    else:
        form = SearchForm_Movie()
    return render(request, 'polls/search_form_movie.html', {'form': form})


def search_series(request):
    if request.method == 'POST':
        form = SearchForm_Series(request.POST)
        if form.is_valid():
            return HttpResponseRedirect('/thanks/')
    else:
        form = SearchForm_Series()
    return render(request, 'polls/search_form_series.html', {'form': form})


def search_book(request):
    if request.method == 'POST':
        form = SearchForm_Book(request.POST)
        if form.is_valid():
            return HttpResponseRedirect('/thanks/')
    else:
        form = SearchForm_Book()
    return render(request, 'polls/search_form_book.html', {'form': form})


def filter_by_mode(queryset_to_fill, list_of_things, modes2):
    for game in list_of_things:
        qs = game.mode.values("id")
        for queryset_with_id in qs:

            if str(queryset_with_id['id']) in modes2:
                query_to_add = Game.objects.filter(id=game.id)
                queryset_to_fill = queryset_to_fill | query_to_add
    return queryset_to_fill


def filter_by_genre(model, list_of_things, genres):
    queryset_to_fill = model.objects.none()
    for object_model in list_of_things:
        qs = object_model.genre.values("id")
        for queryset_with_id in qs:

            if str(queryset_with_id['id']) in genres:
                query_to_add = model.objects.filter(id=object_model.id)
                queryset_to_fill = queryset_to_fill | query_to_add
    return queryset_to_fill


def filter_by_year(model, list_of_things, year_min, year_max):
    queryset_to_fill = model.objects.none()
    for object_model in list_of_things:

        if year_min and year_max:
            if int(year_min) <= object_model.date_of_release.year <= int(year_max):
                query_to_add = model.objects.filter(id=object_model.id)
                queryset_to_fill = queryset_to_fill | query_to_add
                continue
            continue

        if year_min:
            if object_model.date_of_release.year >= int(year_min):
                query_to_add = model.objects.filter(id=object_model.id)
                queryset_to_fill = queryset_to_fill | query_to_add
                continue
            continue

        if year_max:
            if object_model.date_of_release.year <= int(year_max):
                query_to_add = Game.objects.filter(id=object_model.id)
                queryset_to_fill = queryset_to_fill | query_to_add
                continue
            continue
    return queryset_to_fill


def search_result_game(request):
    if request.method == "POST":
        searched = request.POST['searched']
        genres = request.POST.getlist('genres')
        modes2 = request.POST.getlist('modes')
        year_min = request.POST['fromYear']
        year_max = request.POST['toYear']
        model_type = Game
        searched_games = Game.objects.filter(title__icontains=searched, Verified=True)
        final_queryset = searched_games
        if genres:
            final_queryset = filter_by_genre(model_type, final_queryset, genres)
        if modes2:
            final_queryset = filter_by_mode(Game.objects.none(), final_queryset, modes2)
        if year_min or year_max:
            final_queryset = filter_by_year(model_type, final_queryset, year_min, year_max)

        return render(request, 'polls/Game/game_list.html',
                      {'game_list': final_queryset})
    else:
        return render(request, 'polls/search_result.html')


def search_result_book(request):
    if request.method == "POST":
        searched = request.POST['searched']
        genres = request.POST.getlist('genres')
        isbn = request.POST['isbn']
        model_type = Book
        if isbn:
            final_queryset = Book.objects.filter(isbn__icontains=isbn)
            return render(request, 'polls/Book/book_list.html',
                          {'book_list': final_queryset})
        searched_books = Book.objects.filter(title__icontains=searched, Verified=True)
        final_queryset = searched_books
        if genres:
            final_queryset = filter_by_genre(model_type, final_queryset, genres)

        return render(request, 'polls/Book/book_list.html',
                      {'book_list': final_queryset})
    else:
        return render(request, 'polls/search_result.html')


def filter_by_running_time_movie(list_of_things, running_time):
    queryset_to_fill = Movie.objects.none()
    for movie in list_of_things:

        if running_time:
            if int(movie.running_time) >= int(running_time):
                query_to_add = Movie.objects.filter(id=movie.id)
                queryset_to_fill = queryset_to_fill | query_to_add
                continue
            continue

    return queryset_to_fill


def search_result_movie(request):
    if request.method == "POST":
        model_type = Movie
        searched = request.POST['searched']
        genres = request.POST.getlist('genres')
        year_min = request.POST['fromYear']
        year_max = request.POST['toYear']
        running_time = request.POST['running_time']

        searched_movies = Movie.objects.filter(title__icontains=searched, Verified=True)
        final_queryset = searched_movies
        if genres:
            final_queryset = filter_by_genre(model_type, final_queryset, genres)
        if running_time:
            final_queryset = filter_by_running_time_movie(final_queryset, running_time)
        if year_min or year_max:
            final_queryset = filter_by_year(model_type, final_queryset, year_min, year_max)

        return render(request, 'polls/movie/movie_list.html',
                      {'movie_list': final_queryset})
    else:
        return render(request, 'polls/search_result.html')


def filter_by_in_production_series(model, list_of_things, status):
    queryset_to_fill = Series.objects.none()
    for serie in list_of_things:
        qs = serie.in_production
        if qs == status:
            query_to_add = model.objects.filter(id=serie.id)
            queryset_to_fill = queryset_to_fill | query_to_add
    return queryset_to_fill


def search_result_series(request):
    if request.method == "POST":
        model_type = Series
        searched = request.POST['searched']
        genres = request.POST.getlist('genres')
        year_min = request.POST['fromYear']
        year_max = request.POST['toYear']
        in_production = request.POST['in_production']

        searched_series = Series.objects.filter(title__icontains=searched, Verified=True)
        final_queryset = searched_series
        if genres:
            final_queryset = filter_by_genre(model_type, final_queryset, genres)
        if in_production:
            if in_production == "False":
                in_production = False
            else:
                in_production = True
            final_queryset = filter_by_in_production_series(model_type, final_queryset, in_production)
        if year_min or year_max:
            final_queryset = filter_by_year(model_type, final_queryset, year_min, year_max)

        return render(request, 'polls/movie/series_list.html',
                      {'series_list': final_queryset})
    else:
        return render(request, 'polls/search_result.html')


@stuff_or_superuser_required
def stuff_verification(request):
    # searched = request.POST['searched']
    games_to_verify = Game.objects.filter(Verified=False)
    movies_to_verify = Movie.objects.filter(Verified=False)
    series_to_verify = Series.objects.filter(Verified=False)
    actors_to_verify = Actor.objects.filter(Verified=False)
    directors_to_verify = Director.objects.filter(Verified=False)
    developers_to_verify = Developer.objects.filter(Verified=False)
    books_to_verify = Book.objects.filter(Verified=False)
    authors_to_verify = Author.objects.filter(Verified=False)

    return render(request, 'polls/stuff_verification.html',
                  {'games_to_verify': games_to_verify,
                   'movies_to_verify': movies_to_verify,
                   'series_to_verify': series_to_verify,
                   'actors_to_verify': actors_to_verify,
                   'directors_to_verify': directors_to_verify,
                   'developers_to_verify': developers_to_verify,
                   'books_to_verify': books_to_verify,
                   'authors_to_verify': authors_to_verify

                   }
                  )


@anonymous_required
def login_user(request):
    if request.user.is_authenticated:
        return redirect('index')
    # username = password = ''
    if request.POST:
        username = request.POST['username']
        password = request.POST['password']
        username = username.lower()

        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                messages.success(request, 'You logged in successfully!')
                return redirect('index')
        else:
            messages.error(request, 'Username or password is incorrect!')
    return render(request, 'registration/login.html')


def signup_view(request):
    # form_class = SignUpForm
    form = SignUpForm(request.POST)
    if form.is_valid():
        form.save()
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password1')
        user = authenticate(username=username, password=password)
        login(request, user)
        messages.success(request, 'Your profile is created successfully!')

        return redirect('index')
    return render(request, 'registration/signup2.html', {'form': form})


# @method_decorator(login_required, name='dispatch')
class AuthorListView(generic.ListView):
    model = Author
    template_name = "polls/Book/author_list.html"
    paginate_by = 10


class AuthorDetailView(generic.DetailView):
    model = Author
    template_name = "polls/Book/author_detail.html"


class AuthorCreate(CreateView):
    model = Author
    template_name = "polls/Book/author_form.html"
    # fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death']
    # initial = {'date_of_death': '11/06/2020'}
    form_class = AuthorForm


class AuthorUpdate(UpdateView):
    model = Author
    template_name = "polls/Book/author_form.html"
    form_class = AuthorForm
    # fields = '__all__'


class AuthorDelete(DeleteView):
    model = Author
    template_name = "polls/Book/author_confirm_delete.html"
    success_url = reverse_lazy('authors')


def author_verification(request, pk):
    author_object = get_object_or_404(Author, id=pk)
    if author_object.Verified:
        author_object.Verified = False
        author_object.save(update_fields=['Verified'])
    else:
        author_object.Verified = True
        author_object.save(update_fields=['Verified'])
    return HttpResponseRedirect(reverse('author-detail', args=[str(pk)]))


class BookListView(generic.ListView):
    model = Book
    template_name = "polls/Book/book_list.html"
    paginate_by = 10


class BookDetailView(generic.DetailView):
    model = Book
    template_name = "polls/Book/book_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        if self.request.user.is_authenticated:
            profile_pk = Profile.objects.filter(user=self.request.user.pk).first().pk

            book_in_user_book_list = BookList.objects.filter(
                book__booklist__book__exact=self.object).filter(
                profile__booklist__profile__exact=profile_pk).exists()
            context['book_in_user_book_list'] = book_in_user_book_list

            if book_in_user_book_list:
                context['book_read_reading'] = BookList.objects.filter(
                    book__booklist__book__exact=self.object).filter(
                    profile__booklist__profile__exact=profile_pk).exclude(book_status='want to read').exists()

            context['book_has_user_review'] = BookReview.objects.filter(book_id=self.object).filter(
                author=self.request.user).exists()

            user_review = BookReview.objects.filter(book_id=self.object).filter(author=self.request.user)
            context['user_review'] = user_review.first()

            book_reviews = BookReview.objects.filter(book_id=self.object).exclude(author=self.request.user)
            book_reviews = user_review | book_reviews
            context['book_reviews'] = book_reviews

        else:
            context['book_reviews'] = BookReview.objects.filter(book_id=self.object)
        return context


class BookCreate(UserPassesTestMixin, CreateView):
    model = Book
    template_name = "polls/Book/book_form.html"
    form_class = BookForm

    def test_func(self):
        return self.request.user.is_authenticated

    def handle_no_permission(self):
        return redirect('login')

    def form_valid(self, form):
        messages.success(self.request, "The book has been successfully created!")
        form.instance.added_by = self.request.user
        return super().form_valid(form)


class BookUpdate(UpdateView):
    model = Book
    template_name = "polls/Book/book_form.html"
    form_class = BookForm
    # fields = ['title', 'author', 'summary', 'isbn', 'genre', 'language']


class BookDelete(UserPassesTestMixin, DeleteView):
    model = Book
    template_name = "polls/Book/book_confirm_delete.html"
    success_url = reverse_lazy('books')

    def test_func(self):
        obj = self.get_object()
        if self.request.user.is_superuser:
            return True
        if obj.added_by == self.request.user and obj.Verified is False:
            return True
        return False

    def handle_no_permission(self):
        return redirect('index')

    def form_valid(self, form):
        if self.object.added_by is not None:
            delete_reason_content = form.data['delete_reason']
            basic_message_content = 'Your book was deleted from PTC, title: ' + str(self.object)
            mail_notification(self.get_object(), basic_message_content, delete_reason_content, 'added_by')
        messages.success(self.request, "The book has been deleted!")
        return super().form_valid(form)


def book_verification(request, pk):
    book_object = get_object_or_404(Book, id=pk)
    if book_object.Verified:
        book_object.Verified = False
        book_object.save(update_fields=['Verified'])
    else:
        book_authors = book_object.authors.get_queryset()
        for author in book_authors:
            if not author.Verified:
                author.Verified = True
                author.save(update_fields=['Verified'])
        book_object.Verified = True
        book_object.save(update_fields=['Verified'])
    return HttpResponseRedirect(reverse('book-detail', args=[str(pk)]))




def book_verification_stuff_page(request):
    list_of_books = request.POST.getlist('books-select')
    if not list_of_books:
        return redirect("stuff-verification")
    query_set_of_books = Book.objects.none()
    for id in list_of_books:
        get_book_in_query = Book.objects.filter(pk=id)
        query_set_of_books = query_set_of_books | get_book_in_query
    list_of_books = query_set_of_books
    for book_object in list_of_books:
        if book_object.Verified:
            book_object.Verified = False
            book_object.save(update_fields=['Verified'])
        else:
            book_authors = book_object.authors.get_queryset()
            for author in book_authors:
                if not author.Verified:
                    author.Verified = True
                    author.save(update_fields=['Verified'])
            book_object.Verified = True
            book_object.save(update_fields=['Verified'])
    return redirect("stuff-verification")




class CreateBookReview(UserPassesTestMixin, CreateView):
    model = BookReview
    template_name = "polls/Profile/review_create.html"
    form_class = BookReviewForm

    def test_func(self):
        if not self.request.user.is_authenticated:
            return False

        review_exists = BookReview.objects.filter(
            author_id=self.request.user, book_id=self.kwargs['book_pk']).exists()

        return not review_exists and self.request.user.is_authenticated

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return redirect('login2')
        return redirect('index')

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.book_id = self.kwargs['book_pk']
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('book-detail', kwargs={'pk': self.kwargs['book_pk']})


class UpdateBookReview(UserPassesTestMixin, UpdateView):
    model = BookReview
    template_name = "polls/Profile/review_create.html"
    form_class = BookReviewForm

    def test_func(self):
        author = BookReview.objects.filter(id=self.kwargs['pk']).first().author
        return self.request.user == author and self.request.user.is_authenticated

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return redirect('login2')
        return redirect('index')

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.book_id = self.kwargs['book_pk']
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('book-detail', kwargs={'pk': self.kwargs['book_pk']})


def add_book_to_book_list(request, book_pk, user_pk, book_status):
    profile = Profile.objects.filter(user=user_pk).first()
    book = Book.objects.filter(pk=book_pk).first()

    exists_in_watchlist = BookList.objects.filter(profile=profile).filter(book=book).exists()
    if exists_in_watchlist:
        return HttpResponseRedirect(reverse('book-detail', args=[str(book_pk)]))

    BookList.objects.create(
        book_status=book_status,
        book=book,
        profile=profile
    )

    return HttpResponseRedirect(reverse('book-detail', args=[str(book_pk)]))


def remove_book_from_book_list(request, book_pk, user_pk):
    profile_pk = Profile.objects.filter(user_id=user_pk).first().pk
    review = BookReview.objects.filter(book=book_pk).filter(author=user_pk)
    book_list = BookList.objects.filter(book=book_pk).filter(profile=profile_pk)
    review.delete()
    book_list.delete()

    return HttpResponseRedirect(reverse('book-detail', args=[str(book_pk)]))


class BookReviewDetail(generic.DetailView):
    model = BookReview
    template_name = "polls/Book/book_review_detail.html"


class ProfileBookList(generic.DetailView):
    model = Profile
    template_name = "polls/Profile/book_list.html"
    slug_field = 'name'
    slug_url_kwarg = 'name'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()

        status = self.kwargs['status']

        if status == 'all':
            book_list_all = BookList.objects.filter(profile=self.object)
            book_list_books = BookList.objects.filter(profile=self.object).values_list('book', flat=True)
        else:
            book_list_all = BookList.objects.filter(profile=self.object).filter(book_status=status)
            book_list_books = BookList.objects.filter(
                profile=self.object).filter(book_status=status).values_list('book', flat=True)

        book_reviews_all = []
        book_reviews_books = BookReview.objects.filter(author=self.object.user).values_list('book', flat=True)

        for book in book_list_books:
            if book in book_reviews_books:
                book_reviews_all.append(BookReview.objects.filter(
                    author=self.object.user).filter(book=book).first())
            else:
                book_reviews_all.append(False)

        reviews_and_books = zip(book_list_all, book_reviews_all)
        context['reviews_and_books'] = reviews_and_books

        context['status'] = status

        return context


def change_book_status(request, book_pk, profile_pk, status):
    game_list_object = BookList.objects.filter(book_id=book_pk).filter(profile_id=profile_pk).first()
    game_list_object.book_status = status
    game_list_object.save(update_fields=['book_status'])

    return HttpResponseRedirect(reverse('profile-book-list', args=[request.user, 'all']))


class GameCreate(CreateView):
    model = Game
    form_class = GameForm
    # fields = ['title', 'developer', 'date_of_release', 'genre', 'mode', 'summary',]
    # fields = ['title', 'developer', 'date_of_release', 'genre', 'mode', 'summary']
    template_name = "polls/Game/game_form.html"

    def form_valid(self, form):
        messages.success(self.request, "The game has been successfully crated!")
        form.instance.added_by = self.request.user
        return super(GameCreate, self).form_valid(form)


class GameDetailView(UserPassesTestMixin, generic.DetailView):
    """Generic class-based detail view for a game."""
    model = Game
    template_name = 'polls/Game/game_detail.html'

    def test_func(self):
        get_game_object = Game.objects.get(pk=self.kwargs['pk'])
        if self.request.user.is_superuser or self.request.user.is_staff:
            return True
        elif get_game_object.Verified is False and self.request.user == get_game_object.added_by:
            return True
        elif (self.request.user.is_authenticated or self.request.user.is_anonymous) and get_game_object.Verified:
            return True
        return False

    def handle_no_permission(self):
        return redirect('games')

    def get_context_data(self, *args, **kwargs):
        context = super(GameDetailView, self).get_context_data(*args, **kwargs)

        kont = False

        context["kont"] = kont

        if self.request.user.is_authenticated:
            profile_pk = Profile.objects.filter(user=self.request.user.pk).first().pk

            game_in_user_game_list = GameList.objects.filter(
                game__gamelist__game__exact=self.object).filter(
                profile__gamelist__profile__exact=profile_pk).exists()
            context['game_in_user_game_list'] = game_in_user_game_list

            if game_in_user_game_list:
                context['game_played_playing'] = GameList.objects.filter(
                    game__gamelist__game__exact=self.object).filter(
                    profile__gamelist__profile__exact=profile_pk).exclude(game_status='want to play').exists()

            context['game_has_user_review'] = GameReview.objects.filter(game_id=self.object).filter(
                author=self.request.user).exists()

            user_review = GameReview.objects.filter(game_id=self.object).filter(author=self.request.user)
            context['user_review'] = user_review.first()

            game_reviews = GameReview.objects.filter(game_id=self.object).exclude(author=self.request.user)
            game_reviews = user_review | game_reviews
            context['game_reviews'] = game_reviews

        else:
            context['game_reviews'] = GameReview.objects.filter(game_id=self.object)

        return context


class CreateGameReview(UserPassesTestMixin, CreateView):
    model = GameReview
    template_name = "polls/Profile/review_create.html"
    form_class = GameReviewForm

    def test_func(self):
        if not self.request.user.is_authenticated:
            return False

        review_exists = GameReview.objects.filter(
            author_id=self.request.user, game_id=self.kwargs['game_pk']).exists()

        return not review_exists and self.request.user.is_authenticated

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return redirect('login')
        return redirect('index')

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.game_id = self.kwargs['game_pk']
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('game-detail', kwargs={'pk': self.kwargs['game_pk']})


class UpdateGameReview(UserPassesTestMixin, UpdateView):
    model = GameReview
    template_name = "polls/Profile/review_create.html"
    form_class = GameReviewForm

    def test_func(self):
        author = GameReview.objects.filter(id=self.kwargs['pk']).first().author
        return self.request.user == author and self.request.user.is_authenticated

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return redirect('login')
        return redirect('index')

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.game_id = self.kwargs['game_pk']
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('game-detail', kwargs={'pk': self.kwargs['game_pk']})


class SeriesReviewDelete(UserPassesTestMixin, DeleteView):
    model = SeriesReview

    def test_func(self):
        author = SeriesReview.objects.filter(id=self.kwargs['pk']).first().author
        return self.request.user == author and self.request.user.is_authenticated or self.request.user.is_superuser

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return redirect('login')
        return redirect('index')

    def form_valid(self, form):
        if self.object.author is not None and self.request.user.is_superuser:
            delete_reason_content = form.data['delete_reason']
            basic_message_content = 'Your review was deleted from PTC, title: ' + str(self.object.series)
            mail_notification(self.get_object(), basic_message_content, delete_reason_content, 'author')
        messages.success(self.request, "The review has been deleted!")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('series-detail', kwargs={'pk': self.kwargs['series_pk']})


def mail_notification(thing_object, basic_message_content, additional, filed_name):
    if filed_name == 'author':
        user_email = thing_object.author.email
        superuser_test = thing_object.author.is_superuser
    elif filed_name == 'creator':
        user_email = thing_object.creator.user.email
        superuser_test = thing_object.creator.user.is_superuser
    else:
        user_email = thing_object.added_by.email
        superuser_test = thing_object.added_by.is_superuser

    if additional:
        message_content = basic_message_content + "\n" + "Reason for removal: " + additional
    else:
        message_content = basic_message_content

    if not superuser_test:
        send_mail(
            'Delete notification from PTC ',
            message_content,
            'pct-team@outlook.com',
            [user_email],
            fail_silently=False,
        )


class GameReviewDelete(UserPassesTestMixin, DeleteView):
    model = GameReview

    def test_func(self):
        author = GameReview.objects.filter(id=self.kwargs['pk']).first().author
        return self.request.user == author and self.request.user.is_authenticated or self.request.user.is_superuser

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return redirect('login')
        return redirect('index')

    def form_valid(self, form):
        if self.object.author is not None and self.request.user.is_superuser:
            delete_reason_content = form.data['delete_reason']
            basic_message_content = 'Your review was deleted from PTC, title: ' + str(self.object.game)
            mail_notification(self.get_object(), basic_message_content, delete_reason_content, 'author')
        messages.success(self.request, "The review has been deleted!")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('game-detail', kwargs={'pk': self.kwargs['game_pk']})


class BookReviewDelete(UserPassesTestMixin, DeleteView):
    model = BookReview

    def test_func(self):
        author = BookReview.objects.filter(id=self.kwargs['pk']).first().author
        return self.request.user == author and self.request.user.is_authenticated or self.request.user.is_superuser

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return redirect('login')
        return redirect('index')

    def form_valid(self, form):
        if self.object.author is not None and self.request.user.is_superuser:
            delete_reason_content = form.data['delete_reason']
            basic_message_content = 'Your review was deleted from PTC, title: ' + str(self.object.book)
            mail_notification(self.get_object(), basic_message_content, delete_reason_content, 'author')
        messages.success(self.request, "The review has been deleted!")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('book-detail', kwargs={'pk': self.kwargs['book_pk']})


class MovieReviewDelete(UserPassesTestMixin, DeleteView):
    model = MovieReview

    def test_func(self):
        author = MovieReview.objects.filter(id=self.kwargs['pk']).first().author
        return self.request.user == author and self.request.user.is_authenticated or self.request.user.is_superuser

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return redirect('login')
        return redirect('index')

    def form_valid(self, form):
        if self.object.author is not None and self.request.user.is_superuser:
            delete_reason_content = form.data['delete_reason']
            basic_message_content = 'Your review was deleted from PTC, title: ' + str(self.object.movie)
            mail_notification(self.get_object(), basic_message_content, delete_reason_content, 'author')
        messages.success(self.request, "The review has been deleted!")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('movie-detail', kwargs={'pk': self.kwargs['movie_pk']})


def add_game_to_game_list(request, game_pk, user_pk, game_status):
    profile = Profile.objects.filter(user=user_pk).first()
    game = Game.objects.filter(pk=game_pk).first()

    exists_in_watchlist = GameList.objects.filter(profile=profile).filter(game=game).exists()
    if exists_in_watchlist:
        return HttpResponseRedirect(reverse('game-detail', args=[str(game_pk)]))

    GameList.objects.create(
        game_status=game_status,
        game=game,
        profile=profile
    )

    return HttpResponseRedirect(reverse('game-detail', args=[str(game_pk)]))


def remove_game_from_game_list(request, game_pk, user_pk):
    profile_pk = Profile.objects.filter(user_id=user_pk).first().pk
    review = GameReview.objects.filter(game=game_pk).filter(author=user_pk)
    game_list = GameList.objects.filter(game=game_pk).filter(profile=profile_pk)
    review.delete()
    game_list.delete()

    return HttpResponseRedirect(reverse('game-detail', args=[str(game_pk)]))


class ProfileGameList(generic.DetailView):
    model = Profile
    template_name = "polls/Profile/game_list.html"
    slug_field = 'name'
    slug_url_kwarg = 'name'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()

        status = self.kwargs['status']

        if status == 'all':
            game_list_all = GameList.objects.filter(profile=self.object)
            game_list_games = GameList.objects.filter(profile=self.object).values_list('game', flat=True)
        else:
            game_list_all = GameList.objects.filter(profile=self.object).filter(game_status=status)
            game_list_games = GameList.objects.filter(
                profile=self.object).filter(game_status=status).values_list('game', flat=True)

        game_reviews_all = []
        game_reviews_games = GameReview.objects.filter(author=self.object.user).values_list('game', flat=True)

        for game in game_list_games:
            if game in game_reviews_games:
                game_reviews_all.append(GameReview.objects.filter(
                    author=self.object.user).filter(game=game).first())
            else:
                game_reviews_all.append(False)

        reviews_and_games = zip(game_list_all, game_reviews_all)

        context['reviews_and_games'] = reviews_and_games
        context['status'] = status

        return context


class GameReviewDetail(generic.DetailView):
    model = GameReview
    template_name = "polls/Game/game_review_detail.html"


def change_game_status(request, game_pk, profile_pk, status):
    game_list_object = GameList.objects.filter(game_id=game_pk).filter(profile_id=profile_pk).first()
    game_list_object.game_status = status
    game_list_object.save(update_fields=['game_status'])

    return HttpResponseRedirect(reverse('profile-game-list', args=[request.user, 'all']))


class GameUpdate(UserPassesTestMixin, SuccessMessageMixin, UpdateView):
    model = Game
    template_name = "polls/Game/game_form.html"
    fields = ['title', 'developer', 'date_of_release', 'genre', 'mode', 'summary', 'Verified']
    success_message = 'The game has been successfully updated'

    def test_func(self):
        obj = self.get_object()
        if self.request.user.is_superuser:
            return True
        if obj.added_by == self.request.user and obj.Verified is False:
            return True
        return False

    def handle_no_permission(self):
        return redirect('index')


# success_url = reverse_lazy('games')
#  template_name = "polls/Game/game_confirm_delete.html"


class GameDelete(UserPassesTestMixin, DeleteView):
    model = Game
    success_url = reverse_lazy('games')
    template_name = "polls/Game/game_confirm_delete.html"

    def test_func(self):
        obj = self.get_object()
        if self.request.user.is_superuser:
            return True
        if obj.added_by == self.request.user and obj.Verified is False:
            return True
        return False

    def handle_no_permission(self):
        return redirect('index')

    def form_valid(self, form):
        if self.object.added_by is not None:
            delete_reason_content = form.data['delete_reason']
            basic_message_content = 'Your game was deleted from PTC, title: ' + str(self.object)
            mail_notification(self.get_object(), basic_message_content, delete_reason_content, 'added_by')
        messages.success(self.request, "The game has been deleted!")
        return super().form_valid(form)

"""
def mail_notification(thing_object, basic_message_content, additional):
    user_email = thing_object.added_by.email
    if additional:
        message_content = basic_message_content + "\n" + "Reason for removal: " + additional
    else:
        message_content = basic_message_content

    if not thing_object.added_by.is_superuser:
        print("Wysłano maila")
        print(thing_object.added_by)
        send_mail(
            'Delete notification from PTC ',
            message_content,
            'pct-team@outlook.com',
            [user_email],
            fail_silently=False,
        )
"""

class GameListView(generic.ListView):
    model = Game
    paginate_by = 12
    template_name = "polls/Game/game_list.html"
    ordering = ["title"]


class DeveloperDetailView(generic.DetailView):
    """Generic class-based detail view for a developer."""
    model = Developer
    template_name = 'polls/Game/developer_detail.html'


class DeveloperDelete(UserPassesTestMixin, DeleteView):
    model = Developer
    success_url = reverse_lazy('developers')
    template_name = "polls/Game/developer_confirm_delete.html"

    def test_func(self):
        obj = self.get_object()
        if self.request.user.is_superuser:
            return True
        if obj.added_by == self.request.user and obj.Verified is False:
            return True
        return False

    def handle_no_permission(self):
        return redirect('index')

    def form_valid(self, form):
        if self.object.added_by is not None:
            delete_reason_content = form.data['delete_reason']
            basic_message_content = 'Your developer was deleted from PTC, title: ' + str(self.object)
            mail_notification(self.get_object(), basic_message_content, delete_reason_content, 'added_by')
        messages.success(self.request, "The developer has been deleted!")
        return super().form_valid(form)


class DeveloperCreate(CreateView):
    model = Developer
    fields = ['company_name', 'date_of_foundation']
    template_name = "polls/Game/developer_form.html"


class DeveloperUpdate(UserPassesTestMixin, UpdateView, SuccessMessageMixin):
    model = Developer
    fields = ['company_name', 'date_of_foundation']
    template_name = "polls/Game/developer_form.html"

    def test_func(self):
        return self.request.user.is_superuser

    def handle_no_permission(self):
        return redirect('index')


class DeveloperListView(generic.ListView):
    model = Developer
    paginate_by = 30
    template_name = "polls/Game/developer_list.html"
    ordering = ["company_name"]


class PasswordsChangeView(PasswordChangeView):
    # form_class = PasswordChangeForm #domyślne
    form_class = PasswordChangingForm  # Nowe z forms.py
    template_name = 'polls/Profile/change_password.html'
    success_url = reverse_lazy('password_success')


def password_change_success(request):
    return render(request, 'polls/Profile/password_success.html')


class UserEditView(UserPassesTestMixin, generic.UpdateView):
    form_class = EditUserForm
    success_url = reverse_lazy("index")
    template_name = "polls/Game/edit_user.html"

    def get_object(self):
        return self.request.user

    def test_func(self):
        return self.request.user.is_authenticated


class UserProfileEditView(UserPassesTestMixin, generic.UpdateView):
    model = Profile
    form_class = UserProfileEditForm
    success_url = reverse_lazy("index")
    template_name = "polls/Game/edit_profile.html"

    def get_object(self):
        return self.request.user.profile

    def test_func(self):
        return self.request.user.is_authenticated

    def handle_no_permission(self):
        return redirect('index')


@login_required(login_url='/polls/login/')
def send_friendship_request(request, pk):
    other_user = User.objects.get(id=pk)
    try:
        Friend.objects.add_friend(
            request.user,  # The sender
            other_user,  # The recipient
            message='Hi! I would like to add you')  # This message is optional
        return redirect('profile-page', other_user)
    except (Exception,):
        return redirect('profile-page', other_user)


@login_required(login_url='/polls/login/')
def accept_friendship_request(request, pk):
    try:
        other_user = User.objects.get(id=pk)
        friend_request = FriendshipRequest.objects.get(from_user=other_user, to_user=request.user)
        friend_request.accept()
        return redirect('profile-page', other_user)
    except (Exception,):
        return redirect('profile-page', other_user)


@login_required(login_url='/polls/login/')
def reject_friendship_request(request, pk):
    try:
        other_user = User.objects.get(id=pk)
        friend_request = FriendshipRequest.objects.get(from_user=other_user, to_user=request.user)
        friend_request.reject()
        friend_request.delete()
        return redirect('profile-page', other_user)
    except (Exception,):
        return redirect('profile-page', other_user)


@login_required(login_url='/polls/login/')
def cancel_friendship_request(request, pk):
    try:
        other_user = User.objects.get(id=pk)
        friend_request = FriendshipRequest.objects.get(from_user=request.user, to_user=other_user)
        friend_request.cancel()
        return redirect('profile-page', other_user)
    except FriendshipRequest.DoesNotExist:
        return redirect('profile-page', other_user)


@login_required(login_url='/polls/login/')
def delete_friendship(request, pk):
    try:
        other_user = User.objects.get(id=pk)
        Friend.objects.remove_friend(request.user, other_user)
        return redirect('profile-page', other_user)
    except (Exception,):
        return redirect('profile-page', other_user)


def friend_list(request, pk):
    get_user = User.objects.get(id=pk)
    friends = Friend.objects.friends(get_user)
    avatar = get_user.profile.profile_image_url
    request_list = Friend.objects.unread_requests(get_user)

    context = {
        'friend_list': friends,
        'friend_request_list': request_list,
        'avatar': avatar
    }
    return render(request, 'FriendList.html', context=context)


def friend_request_list(request, pk):
    get_user = User.objects.get(id=pk)
    request_list = Friend.objects.unread_requests(get_user)

    context = {
        'friend_request_list': request_list
    }

    return render(request, 'FriendRequestList.html', context=context)


class ProfilePageView(UserPassesTestMixin, generic.DetailView):
    model = Profile
    template_name = "polls/Profile/user_profile.html"
    slug_field = 'name'
    slug_url_kwarg = 'name'

    def get_object(self, queryset=None):
        """
        Return the object the view is displaying.
        Require `self.queryset` and a `pk` or `slug` argument in the URLconf.
        Subclasses can override this to return any object.
        """
        # Use a custom queryset if provided; this is required for subclasses
        # like DateDetailView
        if queryset is None:
            queryset = self.get_queryset()

        # Next, try looking up by primary key.
        pk = self.kwargs.get(self.pk_url_kwarg)
        slug = self.kwargs.get(self.slug_url_kwarg).lower()
        if pk is not None:
            queryset = queryset.filter(pk=pk)

        # Next, try looking up by slug.
        if slug is not None and (pk is None or self.query_pk_and_slug):
            slug_field = self.get_slug_field()
            queryset = queryset.filter(**{slug_field: slug})

        # If none of those are defined, it's an error.
        if pk is None and slug is None:
            raise AttributeError(
                "Generic detail view %s must be called with either an object "
                "pk or a slug in the URLconf." % self.__class__.__name__
            )

        try:
            # Get the single item from the filtered queryset
            obj = queryset.get()
        except queryset.model.DoesNotExist:
            raise Http404("No Profile found matching the query")
        return obj

    def test_func(self):
        return self.request.user.is_authenticated

    def handle_no_permission(self, **kwargs):
        return redirect('index')

    def get_context_data(self, *args, **kwargs):
        # users = Profile.objects.all()
        context = super(ProfilePageView, self).get_context_data(**kwargs)
        name_lower = self.kwargs['name'].lower()
        get_pk = get_object_or_404(Profile, name=name_lower).pk
        page_user = get_object_or_404(Profile, id=get_pk)
        perm_request = RequestPermission.objects.filter(FromUser=get_pk)
        if perm_request:
            perm_request.first()
        else:
            perm_request = None
        has_perm = self.request.user.groups.filter(name='new_group').exists()
        liked = False
        if page_user.likes.filter(id=self.request.user.id).exists():
            liked = True
        sended = Friend.objects.sent_requests(user=self.request.user)
        received = Friend.objects.unread_requests(user=self.request.user)
        amount_of_pending_friend_request = len(received)
        was_send_friend_request = False
        received_friend_request = False

        for te2 in received:
            if te2.from_user == page_user.user:
                received_friend_request = True

        for te in sended:
            test2 = te.to_user
            if test2 == page_user.user:
                was_send_friend_request = True

        are_we_friends = Friend.objects.are_friends(self.request.user, page_user.user)
        context["are_we_friends"] = are_we_friends

        context["was_send_friend_request"] = was_send_friend_request
        context["received_friend_request"] = received_friend_request
        context["amount_of_pending_friend_request"] = amount_of_pending_friend_request

        context["page_user"] = page_user
        context["liked"] = liked
        context["has_perm"] = has_perm
        context["perm_request"] = perm_request

        return context


@login_required(login_url='/polls/login/')
def like_view(request, pk):
    profile = get_object_or_404(Profile, id=request.POST.get('profile_id'))
    if profile.likes.filter(id=request.user.id).exists():
        profile.likes.remove(request.user)
    else:
        profile.likes.add(request.user)
    return redirect('profile-page', profile.user)


@stuff_or_superuser_required
def game_verification(request, pk):
    game = get_object_or_404(Game, id=pk)
    if game.Verified:
        game.Verified = False
        game.save(update_fields=['Verified'])
    else:
        game_devs = game.developer.get_queryset()
        for dev in game_devs:
            if not dev.Verified:
                dev.Verified = True
                dev.save(update_fields=['Verified'])
        game.Verified = True
        game.save(update_fields=['Verified'])
    return HttpResponseRedirect(reverse('game-detail', args=[str(pk)]))


@stuff_or_superuser_required
def game_verification_stuff_page(request):

    list_of_games = request.POST.getlist('games-select')
    if not list_of_games:
        return redirect("stuff-verification")
    query_set_of_games = Game.objects.none()
    for id in list_of_games:
        get_game_in_query = Game.objects.filter(pk=id)
        query_set_of_games = query_set_of_games | get_game_in_query
    list_of_games = query_set_of_games
    for game in list_of_games:
        if game.Verified:
            game.Verified = False
            game.save(update_fields=['Verified'])
        else:
            game_devs = game.developer.get_queryset()
            for dev in game_devs:
                if not dev.Verified:
                    dev.Verified = True
                    dev.save(update_fields=['Verified'])
            game.Verified = True
            game.save(update_fields=['Verified'])

    return redirect("stuff-verification")


def developer_verification(request, pk):
    developer = get_object_or_404(Developer, id=pk)
    if developer.Verified:
        developer.Verified = False
        developer.save(update_fields=['Verified'])
    else:
        developer.Verified = True
        developer.save(update_fields=['Verified'])
    return HttpResponseRedirect(reverse('developer-detail', args=[str(pk)]))


@login_required(login_url='/polls/login/')
def add_favorite_game(request, pk):
    game = get_object_or_404(Game, id=pk)
    if game in Profile.objects.get(id=request.user.id).favorite_games.filter(id=pk):
        Profile.objects.get(id=request.user.id).favorite_games.remove(game)
    else:
        Profile.objects.get(id=request.user.id).favorite_games.add(game)
    return HttpResponseRedirect(reverse('game-detail', args=[str(pk)]))


def add_favorite_book(request, pk):
    book = get_object_or_404(Book, id=pk)
    if book in Profile.objects.get(id=request.user.id).favorite_books.filter(id=pk):
        Profile.objects.get(id=request.user.id).favorite_books.remove(book)
    else:
        Profile.objects.get(id=request.user.id).favorite_books.add(book)
    return HttpResponseRedirect(reverse('book-detail', args=[str(pk)]))


@login_required(login_url='/polls/login/')
def add_favorite_movie(request, pk):
    movie = get_object_or_404(Movie, id=pk)
    if movie in Profile.objects.get(id=request.user.id).favorite_movies.filter(id=pk):
        Profile.objects.get(id=request.user.id).favorite_movies.remove(movie)
    else:
        Profile.objects.get(id=request.user.id).favorite_movies.add(movie)
    return HttpResponseRedirect(reverse('movie-detail', args=[str(pk)]))


@login_required(login_url='/polls/login/')
def add_favorite_series(request, pk):
    series = get_object_or_404(Series, id=pk)
    if series in Profile.objects.get(id=request.user.id).favorite_series.filter(id=pk):
        Profile.objects.get(id=request.user.id).favorite_series.remove(series)
    else:
        Profile.objects.get(id=request.user.id).favorite_series.add(series)
    return HttpResponseRedirect(reverse('series-detail', args=[str(pk)]))


class MovieListView(generic.ListView):
    template_name = "polls/movie/movie_list.html"
    model = Movie
    paginate_by = 18
    ordering = ["title"]


class MovieDetailView(UserPassesTestMixin, generic.DetailView):
    template_name = "polls/movie/movie_detail.html"
    model = Movie

    def test_func(self):
        get_movie_object = Movie.objects.get(pk=self.kwargs['pk'])
        if self.request.user.is_superuser or self.request.user.is_staff:
            return True
        elif get_movie_object.Verified is False and self.request.user == get_movie_object.added_by:
            return True
        elif (self.request.user.is_authenticated or self.request.user.is_anonymous) and get_movie_object.Verified:
            return True
        return False

    def handle_no_permission(self):
        return redirect('movies')

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        if self.request.user.is_authenticated:
            profile_pk = Profile.objects.filter(user=self.request.user.pk).first().pk

            movie_in_user_watchlist = MovieWatchlist.objects.filter(
                movie__moviewatchlist__movie__exact=self.object).filter(
                profile__moviewatchlist__profile__exact=profile_pk).exists()
            context['movie_in_user_watchlist'] = movie_in_user_watchlist

            if movie_in_user_watchlist:
                context['movie_watched'] = MovieWatchlist.objects.filter(
                    movie__moviewatchlist__movie__exact=self.object).filter(
                    profile__moviewatchlist__profile__exact=profile_pk).filter(movie_status='watched').exists()

            context['movie_has_user_review'] = MovieReview.objects.filter(movie_id=self.object).filter(
                author=self.request.user).exists()

            user_review = MovieReview.objects.filter(movie_id=self.object).filter(author=self.request.user)
            context['user_review'] = user_review.first()

            movie_reviews = MovieReview.objects.filter(movie_id=self.object).exclude(author=self.request.user)
            movie_reviews = user_review | movie_reviews
            context['movie_reviews'] = movie_reviews

        else:
            context['movie_reviews'] = MovieReview.objects.filter(movie_id=self.object)

        return context


class MovieDelete(UserPassesTestMixin, DeleteView):
    model = Movie
    template_name = "polls/movie/movie_delete.html"
    success_url = reverse_lazy('movies')
    login_url = reverse_lazy('index')

    def test_func(self):
        return self.request.user.is_superuser

    def form_valid(self, form):
        if self.object.added_by is not None:
            delete_reason_content = form.data['delete_reason']
            basic_message_content = 'Your movie was deleted from PTC, title: ' + str(self.object)
            mail_notification(self.get_object(), basic_message_content, delete_reason_content, 'added_by')
        messages.success(self.request, "The movie has been deleted!")
        return super().form_valid(form)

    def handle_no_permission(self):
        return redirect('index')


class MovieCreate(UserPassesTestMixin, CreateView):
    model = Movie
    template_name = "polls/movie/movie_create.html"
    form_class = MovieForm

    # fields = ['title', 'actors', 'director', 'date_of_release', 'language', 'genre', 'running_time']

    def test_func(self):
        return self.request.user.is_authenticated

    def handle_no_permission(self):
        return redirect('login')

    def form_valid(self, form):
        messages.success(self.request, "The movie has been successfully created!")
        form.instance.added_by = self.request.user
        form.instance.type_of_show = 'movie'
        return super().form_valid(form)


class MovieUpdate(UserPassesTestMixin, UpdateView):
    model = Movie
    template_name = "polls/movie/movie_create.html"
    form_class = MovieForm

    # fields = ['title', 'actors', 'director', 'date_of_release', 'language', 'genre', 'running_time']

    def form_valid(self, form):
        messages.success(self.request, "The movie has been successfully updated!")
        return super().form_valid(form)

    def test_func(self):
        return self.request.user.is_superuser

    def handle_no_permission(self):
        return redirect('index')


@stuff_or_superuser_required
def movie_verification(request, pk):
    movie_object = get_object_or_404(Movie, id=pk)
    if movie_object.Verified:
        movie_object.Verified = False
        movie_object.save(update_fields=['Verified'])
    else:
        movie_actors = movie_object.actors.get_queryset()
        for actor in movie_actors:
            if not actor.Verified:
                actor.Verified = True
                actor.save(update_fields=['Verified'])

        movie_directors = movie_object.director.get_queryset()
        for director in movie_directors:
            if not director.Verified:
                director.Verified = True
                director.save(update_fields=['Verified'])
        movie_object.Verified = True
        movie_object.save(update_fields=['Verified'])
    return HttpResponseRedirect(reverse('movie-detail', args=[str(pk)]))

@stuff_or_superuser_required
def movie_verification_stuff_page(request):

    list_of_movies = request.POST.getlist('series-select')
    if not list_of_movies:
        return redirect("stuff-verification")
    query_set_of_movies = Game.objects.none()
    for id in list_of_movies:
        get_movie_in_query = Movie.objects.filter(pk=id)
        query_set_of_movies = query_set_of_movies | get_movie_in_query
    list_of_movies = query_set_of_movies
    for movie_object in list_of_movies:
        if movie_object.Verified:
            movie_object.Verified = False
            movie_object.save(update_fields=['Verified'])
        else:
            movie_actors = movie_object.actors.get_queryset()
            for actor in movie_actors:
                if not actor.Verified:
                    actor.Verified = True
                    actor.save(update_fields=['Verified'])

            movie_directors = movie_object.director.get_queryset()
            for director in movie_directors:
                if not director.Verified:
                    director.Verified = True
                    director.save(update_fields=['Verified'])
            movie_object.Verified = True
            movie_object.save(update_fields=['Verified'])
    return redirect('stuff-verification')


class ProfileWatchlist(generic.DetailView):
    model = Profile
    template_name = "polls/Profile/watchlist.html"
    slug_field = 'name'
    slug_url_kwarg = 'name'

    def get_object(self, queryset=None):
        """
        Return the object the view is displaying.
        Require `self.queryset` and a `pk` or `slug` argument in the URLconf.
        Subclasses can override this to return any object.
        """
        # Use a custom queryset if provided; this is required for subclasses
        # like DateDetailView
        if queryset is None:
            queryset = self.get_queryset()

        # Next, try looking up by primary key.
        pk = self.kwargs.get(self.pk_url_kwarg)
        slug = self.kwargs.get(self.slug_url_kwarg).lower()
        if pk is not None:
            queryset = queryset.filter(pk=pk)

        # Next, try looking up by slug.
        if slug is not None and (pk is None or self.query_pk_and_slug):
            slug_field = self.get_slug_field()
            queryset = queryset.filter(**{slug_field: slug})

        # If none of those are defined, it's an error.
        if pk is None and slug is None:
            raise AttributeError(
                "Generic detail view %s must be called with either an object "
                "pk or a slug in the URLconf." % self.__class__.__name__
            )

        try:
            # Get the single item from the filtered queryset
            obj = queryset.get()
        except queryset.model.DoesNotExist:
            raise Http404("No Profile found matching the query")
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data()

        type_of_show = self.kwargs['type_of_show']
        status = self.kwargs['status']

        if type_of_show in ['all', 'movies'] and status != 'watching' and status != 'dropped':
            if status == 'all':
                movie_watchlist_all = MovieWatchlist.objects.filter(profile=self.object)
                movie_watchlist_movies = MovieWatchlist.objects.filter(profile=self.object).values_list('movie',
                                                                                                        flat=True)
            else:
                movie_watchlist_all = MovieWatchlist.objects.filter(profile=self.object).filter(movie_status=status)
                movie_watchlist_movies = MovieWatchlist.objects.filter(
                    profile=self.object).filter(movie_status=status).values_list('movie', flat=True)

            movie_reviews_all = []
            movie_reviews_movies = MovieReview.objects.filter(author=self.object.user).values_list('movie', flat=True)

            for movie in movie_watchlist_movies:
                if movie in movie_reviews_movies:
                    movie_reviews_all.append(MovieReview.objects.filter(
                        author=self.object.user).filter(movie=movie).first())
                else:
                    movie_reviews_all.append(False)

            reviews_and_movies = zip(movie_watchlist_all, movie_reviews_all)
            context['reviews_and_movies'] = reviews_and_movies

        if type_of_show in ['all', 'series']:
            if status == 'all':
                series_watchlist_all = SeriesWatchlist.objects.filter(profile=self.object)
                series_watchlist_series = SeriesWatchlist.objects.filter(profile=self.object).values_list('series',
                                                                                                          flat=True)
            else:
                series_watchlist_all = SeriesWatchlist.objects.filter(profile=self.object).filter(series_status=status)
                series_watchlist_series = SeriesWatchlist.objects.filter(
                    profile=self.object).filter(series_status=status).values_list('series', flat=True)
            series_reviews_all = []
            series_reviews_series = SeriesReview.objects.filter(author=self.object.user).values_list('series',
                                                                                                     flat=True)

            for series in series_watchlist_series:
                if series in series_reviews_series:
                    series_reviews_all.append(SeriesReview.objects.filter(
                        author=self.object.user).filter(series=series).first())
                else:
                    series_reviews_all.append(False)

            reviews_and_series = zip(series_watchlist_all, series_reviews_all)
            context['reviews_and_series'] = reviews_and_series

        context['type_of_show'] = type_of_show
        context['status'] = status

        return context


class MovieReviewDetail(generic.DetailView):
    model = MovieReview
    template_name = "polls/movie/movie_review_detail.html"


def add_movie_to_watchlist(request, movie_pk, user_pk, movie_status):
    profile = Profile.objects.filter(user=user_pk).first()
    movie = Movie.objects.filter(pk=movie_pk).first()

    exists_in_watchlist = MovieWatchlist.objects.filter(profile=profile).filter(movie=movie).exists()
    if exists_in_watchlist:
        return HttpResponseRedirect(reverse('movie-detail', args=[str(movie_pk)]))

    MovieWatchlist.objects.create(
        movie_status=movie_status,
        movie=movie,
        profile=profile
    )

    return HttpResponseRedirect(reverse('movie-detail', args=[str(movie_pk)]))


def movie_watched(request, movie_pk, profile_pk):
    watchlist_object = MovieWatchlist.objects.filter(movie_id=movie_pk).filter(profile_id=profile_pk).first()
    watchlist_object.movie_status = 'watched'
    watchlist_object.save(update_fields=['movie_status'])
    profile = get_object_or_404(Profile, id=profile_pk)
    user = profile.user

    return HttpResponseRedirect(reverse('profile-watchlist', args=[user, 'all', 'all']))


class CreateMovieReview(UserPassesTestMixin, CreateView):
    model = MovieReview
    template_name = "polls/Profile/review_create.html"
    form_class = MovieReviewForm

    def test_func(self):

        if not self.request.user.is_authenticated:
            return False

        review_exists = MovieReview.objects.filter(
            author_id=self.request.user, movie_id=self.kwargs['movie_pk']).exists()

        return not review_exists and self.request.user.is_authenticated

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return redirect('login')
        return redirect('index')

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.movie_id = self.kwargs['movie_pk']
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('movie-detail', kwargs={'pk': self.kwargs['movie_pk']})


class UpdateMovieReview(UserPassesTestMixin, UpdateView):
    model = MovieReview
    template_name = "polls/Profile/review_create.html"
    form_class = MovieReviewForm

    def test_func(self):
        author = MovieReview.objects.filter(id=self.kwargs['pk']).first().author
        return self.request.user == author and self.request.user.is_authenticated

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return redirect('login')
        return redirect('index')

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.movie_id = self.kwargs['movie_pk']
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('movie-detail', kwargs={'pk': self.kwargs['movie_pk']})


def remove_movie_from_watchlist(request, movie_pk, user_pk):
    profile_pk = Profile.objects.filter(user_id=user_pk).first().pk
    review = MovieReview.objects.filter(movie=movie_pk).filter(author=user_pk)
    movie_watchlist = MovieWatchlist.objects.filter(movie=movie_pk).filter(profile=profile_pk)
    review.delete()
    movie_watchlist.delete()

    return HttpResponseRedirect(reverse('movie-detail', args=[str(movie_pk)]))


class MovieWatchlistView(generic.ListView):
    template_name = "polls/Profile/watchlist.html"
    model = MovieWatchlist.objects.filter()
    paginate_by = 18


class SeriesListView(generic.ListView):
    template_name = "polls/movie/series_list.html"
    model = Series
    paginate_by = 18
    ordering = ["title"]


class SeriesDetailView(UserPassesTestMixin, generic.DetailView):
    template_name = "polls/movie/series_detail.html"
    model = Series

    def test_func(self):
        get_series_object = Series.objects.get(pk=self.kwargs['pk'])
        if self.request.user.is_superuser or self.request.user.is_staff:
            return True
        elif get_series_object.Verified is False and self.request.user == get_series_object.added_by:
            return True
        elif (self.request.user.is_authenticated or self.request.user.is_anonymous) and get_series_object.Verified:
            return True
        return False

    def handle_no_permission(self):
        return redirect('series')

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        if self.request.user.is_authenticated:
            profile_pk = Profile.objects.filter(user=self.request.user.pk).first().pk

            series_in_user_watchlist = SeriesWatchlist.objects.filter(
                series__serieswatchlist__series__exact=self.object).filter(
                profile__serieswatchlist__profile__exact=profile_pk).exists()
            context['series_in_user_watchlist'] = series_in_user_watchlist

            if series_in_user_watchlist:
                context['series_watched_watching'] = SeriesWatchlist.objects.filter(
                    series__serieswatchlist__series__exact=self.object).filter(
                    profile__serieswatchlist__profile__exact=profile_pk).exclude(series_status='want to watch').exists()

            context['series_has_user_review'] = SeriesReview.objects.filter(series_id=self.object).filter(
                author=self.request.user).exists()

            user_review = SeriesReview.objects.filter(series_id=self.object).filter(author=self.request.user)
            context['user_review'] = user_review.first()

            series_reviews = SeriesReview.objects.filter(series_id=self.object).exclude(author=self.request.user)
            series_reviews = user_review | series_reviews
            context['series_reviews'] = series_reviews

        else:
            context['series_reviews'] = SeriesReview.objects.filter(series_id=self.object)

        return context


def add_series_to_watchlist(request, series_pk, user_pk, series_status):
    profile = Profile.objects.filter(user=user_pk).first()
    series = Series.objects.filter(pk=series_pk).first()
    exists_in_watchlist = SeriesWatchlist.objects.filter(profile=profile).filter(series=series).exists()
    if exists_in_watchlist:
        return HttpResponseRedirect(reverse('series-detail', args=[str(series_pk)]))

    SeriesWatchlist.objects.create(
        series_status=series_status,
        series=series,
        profile=profile
    )

    return HttpResponseRedirect(reverse('series-detail', args=[str(series_pk)]))


def add_series_to_watched(request, series_pk, profile_pk):
    watchlist_object = SeriesWatchlist.objects.filter(series_id=series_pk).filter(profile_id=profile_pk).first()
    watchlist_object.series_status = 'watched'
    watchlist_object.save(update_fields=['series_status'])

    return HttpResponseRedirect(reverse('profile-watchlist', args=[str(profile_pk)]))


def remove_series_from_watchlist(request, series_pk, user_pk):
    profile_pk = Profile.objects.filter(user_id=user_pk).first().pk
    review = SeriesReview.objects.filter(series=series_pk).filter(author=user_pk)
    series_watchlist = SeriesWatchlist.objects.filter(series=series_pk).filter(profile=profile_pk)
    review.delete()
    series_watchlist.delete()

    return HttpResponseRedirect(reverse('series-detail', args=[str(series_pk)]))


class CreateSeriesReview(UserPassesTestMixin, CreateView):
    model = SeriesReview
    template_name = "polls/Profile/review_create.html"
    form_class = SeriesReviewForm

    def test_func(self):

        if not self.request.user.is_authenticated:
            return False

        review_exists = SeriesReview.objects.filter(
            author_id=self.request.user, series_id=self.kwargs['series_pk']).exists()

        return not review_exists and self.request.user.is_authenticated

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return redirect('login')
        return redirect('index')

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.series_id = self.kwargs['series_pk']
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('series-detail', kwargs={'pk': self.kwargs['series_pk']})


class UpdateSeriesReview(UserPassesTestMixin, UpdateView):
    model = SeriesReview
    template_name = "polls/Profile/review_create.html"
    form_class = SeriesReviewForm

    def test_func(self):
        author = SeriesReview.objects.filter(id=self.kwargs['pk']).first().author
        return self.request.user == author and self.request.user.is_authenticated

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return redirect('login')
        return redirect('index')

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.series_id = self.kwargs['series_pk']
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('series-detail', kwargs={'pk': self.kwargs['series_pk']})


class UpdateSeriesWatchlist(UpdateView):
    model = SeriesWatchlist
    template_name = "polls/movie/series_watchlist_update.html"
    form_class = SeriesProgressStatusForm

    def get_success_url(self):
        profile_pk = Profile.objects.filter(user=self.request.user.pk).first().pk
        profile = get_object_or_404(Profile, id=profile_pk)
        user = profile.user

        return reverse('profile-watchlist', kwargs={'name': user, 'type_of_show': 'all', 'status': 'all'})


class SeriesReviewDetail(generic.DetailView):
    model = SeriesReview
    template_name = "polls/movie/series_review_detail.html"


class SeriesDelete(UserPassesTestMixin, DeleteView):
    model = Series
    template_name = "polls/movie/series_delete.html"
    success_url = reverse_lazy('series')
    login_url = reverse_lazy('index')

    def test_func(self):
        return self.request.user.is_superuser

    def form_valid(self, form):
        if self.object.added_by is not None:
            delete_reason_content = form.data['delete_reason']
            basic_message_content = 'Your series were deleted from PTC, title: ' + str(self.object)
            mail_notification(self.get_object(), basic_message_content, delete_reason_content, 'added_by')
        messages.success(self.request, "The series has been deleted!")
        return super().form_valid(form)

    def handle_no_permission(self):
        return redirect('index')


class SeriesCreate(UserPassesTestMixin, CreateView):
    model = Series
    form_class = SeriesForm
    template_name = "polls/movie/series_create.html"

    # fields = ['title', 'actors', 'director', 'date_of_release', 'language', 'genre', 'number_of_seasons']

    def test_func(self):
        return self.request.user.is_authenticated

    def handle_no_permission(self):
        return redirect('login')

    def form_valid(self, form):
        messages.success(self.request, "The series has been successfully created!")
        form.instance.added_by = self.request.user
        form.instance.type_of_show = 'series'
        return super().form_valid(form)


class SeriesUpdate(UserPassesTestMixin, UpdateView):
    model = Series
    template_name = "polls/movie/series_create.html"
    form_class = SeriesForm

    # fields = ['title', 'actors', 'director', 'date_of_release', 'language', 'genre', 'running_time']

    def test_func(self):
        return self.request.user.is_superuser

    def form_valid(self, form):
        messages.success(self.request, "The series has been successfully updated!")
        return super().form_valid(form)

    def handle_no_permission(self):
        return redirect('index')


@stuff_or_superuser_required
def series_verification(request, pk):
    series_object = get_object_or_404(Series, id=pk)
    if series_object.Verified:
        series_object.Verified = False
        series_object.save(update_fields=['Verified'])
    else:
        series_object.Verified = True
        series_object.save(update_fields=['Verified'])

        series_actors = series_object.actors.get_queryset()
        for actor in series_actors:
            if not actor.Verified:
                actor.Verified = True
                actor.save(update_fields=['Verified'])

        series_actors = series_object.director.get_queryset()
        for director in series_actors:
            if not director.Verified:
                director.Verified = True
                director.save(update_fields=['Verified'])
        series_object.Verified = True
        series_object.save(update_fields=['Verified'])
    return HttpResponseRedirect(reverse('series-detail', args=[str(pk)]))

@stuff_or_superuser_required
def series_verification_stuff_page(request):
    list_of_series = request.POST.getlist('series-select')
    if not list_of_series:
        return redirect("stuff-verification")
    query_set_of_series = Series.objects.none()
    for id in list_of_series:
        get_series_in_query = Series.objects.filter(pk=id)
        query_set_of_series = query_set_of_series | get_series_in_query
    list_of_series = query_set_of_series

    for series_object in list_of_series:
        if series_object.Verified:
            series_object.Verified = False
            series_object.save(update_fields=['Verified'])
        else:
            series_object.Verified = True
            series_object.save(update_fields=['Verified'])
            series_actors = series_object.actors.get_queryset()
            for actor in series_actors:
                if not actor.Verified:
                    actor.Verified = True
                    actor.save(update_fields=['Verified'])

            series_actors = series_object.director.get_queryset()
            for director in series_actors:
                if not director.Verified:
                    director.Verified = True
                    director.save(update_fields=['Verified'])
            series_object.Verified = True
            series_object.save(update_fields=['Verified'])
        return redirect("stuff-verification")



class ActorListView(generic.ListView):
    template_name = "polls/movie/actor_list.html"
    model = Actor
    paginate_by = 30
    ordering = ["full_name"]


class ActorDetailView(generic.DetailView):
    template_name = "polls/movie/actor_detail.html"
    model = Actor

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        # context['movies_list'] = Movie.objects.all
        # context['series_list'] = Series.objects.all
        context['movies_list'] = Movie.objects.filter(actors__full_name__contains=self.object)
        context['series_list'] = Series.objects.filter(actors__full_name__contains=self.object)

        return context


class ActorDelete(UserPassesTestMixin, DeleteView):
    model = Actor
    template_name = "polls/movie/actor_delete.html"
    success_url = reverse_lazy('actors')

    # login_url = reverse_lazy('index')

    def test_func(self):
        return self.request.user.is_superuser

    def handle_no_permission(self):
        return redirect('index')


class ActorCreate(UserPassesTestMixin, CreateView):
    model = Actor
    form_class = ActorForm
    template_name = "polls/movie/actor_create.html"

    # fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death', 'specialisation']

    def test_func(self):
        return self.request.user.is_authenticated

    def handle_no_permission(self):
        return redirect('login')


class ActorUpdate(UserPassesTestMixin, UpdateView):
    model = Actor
    template_name = "polls/movie/actor_create.html"
    form_class = ActorForm

    # fields = ['title', 'actors', 'director', 'date_of_release', 'language', 'genre', 'running_time']

    def test_func(self):
        return self.request.user.is_superuser

    def handle_no_permission(self):
        return redirect('index')


@stuff_or_superuser_required
def actor_verification(request, pk):
    actor_object = get_object_or_404(Actor, id=pk)
    if actor_object.Verified:
        actor_object.Verified = False
        actor_object.save(update_fields=['Verified'])
    else:
        actor_object.Verified = True
        actor_object.save(update_fields=['Verified'])
    return HttpResponseRedirect(reverse('actor-detail', args=[str(pk)]))


class DirectorListView(generic.ListView):
    template_name = "polls/movie/director_list.html"
    model = Director
    paginate_by = 30
    ordering = ["full_name"]


class DirectorDetailView(generic.DetailView):
    template_name = "polls/movie/director_detail.html"
    model = Director


class DirectorDelete(UserPassesTestMixin, DeleteView):
    model = Director
    template_name = "polls/movie/director_delete.html"
    success_url = reverse_lazy('directors')
    login_url = reverse_lazy('index')

    def test_func(self):
        return self.request.user.is_superuser

    def handle_no_permission(self):
        return redirect('index')


class DirectorCreate(UserPassesTestMixin, CreateView):
    model = Director
    form_class = DirectorForm
    template_name = "polls/movie/director_create.html"

    # fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death', 'amount_of_films']

    def test_func(self):
        return self.request.user.is_authenticated

    def handle_no_permission(self):
        return redirect('login')


class DirectorUpdate(UserPassesTestMixin, UpdateView):
    model = Director
    template_name = "polls/movie/director_create.html"
    form_class = DirectorForm

    # fields = ['title', 'actors', 'director', 'date_of_release', 'language', 'genre', 'running_time']

    def test_func(self):
        return self.request.user.is_superuser

    def handle_no_permission(self):
        return redirect('index')


@stuff_or_superuser_required
def director_verification(request, pk):
    director_object = get_object_or_404(Director, id=pk)
    if director_object.Verified:
        director_object.Verified = False
        director_object.save(update_fields=['Verified'])
    else:
        director_object.Verified = True
        director_object.save(update_fields=['Verified'])
    return HttpResponseRedirect(reverse('director-detail', args=[str(pk)]))


class SeasonDetailView(generic.DetailView):
    model = Season
    template_name = "polls/Season/season_detail.html"


class EpisodeDetailView(generic.DetailView):
    model = Episode
    template_name = "polls/Episode/episode_detail.html"


@login_required(login_url='/polls/login/')
@permission_required('catalog.can_mark_returned', raise_exception=True)
def scrape_games_redirect(request):
    random_digit = random.randint(1, 3)
    context = {
        'randomD': random_digit,
    }
    return render(request, 'polls/Game/game_scraping_redirect.html', context=context)


def scrape_steam_ids(page, start):
    steam_ids = []
    url = 'https://store.steampowered.com/search/?page=' + str(page)
    print(page)
    print(url)
    response = requests.get(url)
    only_item_cells = SoupStrainer("div", attrs={'id': 'search_resultsRows'})
    table = BeautifulSoup(response.content, 'lxml', parse_only=only_item_cells)
    games = table.find_all("a")
    for game in games:
        steam_ids.append(game['data-ds-appid'])
        if time() - start > 25:
            return steam_ids, True

    return steam_ids, False


@login_required(login_url='/polls/login/')
@permission_required('catalog.can_mark_returned', raise_exception=True)
def scrape_games(request):
    start = time()
    months_eng = {"Jan,": "01", "Feb,": "02", "Mar,": "03", "Apr,": "04", "May,": "05", "Jun,": "06", "Jul,": "07",
                  "Aug,": "08", "Sep,": "09", "Oct,": "10", "Nov,": "11", "Dec,": "12"}

    added_games = 0
    # error_counter = 0

    for i in range(1, 20):
        steams_ids, end = scrape_steam_ids(i, start)
        if end:
            return render(request, "polls/Game/scrape_games.html", {'addedGames': added_games})

        for steam_app_id in steams_ids:
            if time() - start > 25:
                return render(request, "polls/Game/scrape_games.html", {'addedGames': added_games})
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
                        game_date_of_release_check = jsoned_data_from_response_app_details[str(steam_app_id)]['data'][
                            'release_date']
                        if game_date_of_release_check['coming_soon']:
                            continue

                        game_name = jsoned_data_from_response_app_details[str(steam_app_id)]['data']['name']
                        game_mode_pk = games_mode_api(
                            jsoned_data_from_response_app_details[str(steam_app_id)]['data']['categories'])
                        game_image = jsoned_data_from_response_app_details[str(steam_app_id)]['data']['header_image']
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
                        added_by=User.objects.get(pk=1),
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

    return render(request, "polls/Game/scrape_games.html", {'addedGames': added_games})


def games_genres_api(genres_dic):
    pk_list = []
    for genreDic in genres_dic:
        genre_check = genreDic['description']
        genre = GameGenre.objects.filter(name=genre_check).first()
        if genre:
            pk_list.append(genre.pk)
        else:
            genre_instance = GameGenre.objects.create(name=genre_check, Verified=True)
            pk_list.append(genre_instance.pk)
    return pk_list


def games_mode_api(modes_dic):
    pk_list = []
    for modeDic in modes_dic:
        mode_check = modeDic['description']
        mode = GameMode.objects.filter(name=mode_check).first()
        if mode:
            pk_list.append(mode.pk)
        else:
            mode_instance = GameMode.objects.create(name=mode_check, Verified=True)
            pk_list.append(mode_instance.pk)
    return pk_list


def check_app_id(app_id):
    find_id = KnownSteamAppID.objects.filter(id=app_id).first()
    if find_id:
        return True
    else:
        KnownSteamAppID.objects.create(id=app_id)
        return False


def games_developer_api(developer_name):
    pk_list = []
    developer_check = Developer.objects.filter(company_name=developer_name).first()
    if developer_check:
        pk_list.append(developer_check.pk)
    else:
        developer_instance = Developer.objects.create(company_name=developer_name, Verified=True)
        pk_list.append(developer_instance.pk)
    return pk_list


def compare_titles(shows):
    chars = ['1', '2', '3', '4', '5', '6', '7', '8', '9', 'I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X']
    accepted = []
    primary = shows[0]['title']
    primary_striped = shows[0]['title'].replace(" ", "")
    accepted.append(shows[0])
    for i in range(1, len(shows)):
        if shows[i]['title'] == primary:
            accepted.append(shows[i])
        else:
            title = list(shows[i]['title'].replace(" ", ""))
            for char in primary_striped:
                try:
                    title.remove(char)
                except ValueError:
                    pass
            print(title)
            if "".join(title) in chars:
                accepted.append(shows[i])
    return accepted


def get_imdb_id(shows, multi_search, type_of_show, api):
    imdb_ids = []
    if multi_search:
        # api = omdb.OMDBClient(apikey=apikey)
        for show in shows:
            # counter = 0
            if type_of_show == 'tv_series_browse':
                data = api.search_series(show)
            else:
                data = api.search_movie(show)
            if data:
                data = compare_titles(data)
                for record in data:
                    imdb_ids.append(record['imdb_id'])
    else:
        # api = GetMovie(api_key=apikey)
        for show in shows:
            data = api.get(title=show)
            if data:
                imdb_ids.append(data['imdb_id'])

    return imdb_ids


def compare_actors(api_actors, api_directors, imdb_id, type_of_show):
    new_directors = api_directors.copy()
    new_actors = api_actors.copy()

    if type_of_show == 'movie':
        show = Movie.objects.filter(imdb_id=imdb_id).first()
    else:
        show = Series.objects.filter(imdb_id=imdb_id).first()

    current_actors = show.actors.all()
    current_directors = show.director.all()

    for actor in current_actors:
        name = actor.full_name
        if name not in api_actors:
            new_actors.append(name)

    for director in current_directors:
        name = director.full_name
        if name not in api_directors:
            new_directors.append(name)

    if len(new_directors) == 1 and 'N/A' in new_directors:
        return new_directors, new_actors
    else:
        return [director for director in new_directors if director != 'N/A'], new_actors


def scrape_show(url, multi_search, type_of_show, api, update, months, start):
    created = 0
    updated = 0
    titles = []
    print(url)
    response = requests.get(url)
    only_item_cells = SoupStrainer("div", attrs={'class': 'discovery-tiles__wrap'})
    table = BeautifulSoup(response.content, 'lxml', parse_only=only_item_cells)
    movies_data = table.find_all("span", attrs={'class': 'p--small'})

    for movie in movies_data:
        title = str(movie.text.strip())
        titles.append(title)

    if multi_search:
        shows = get_imdb_id(titles, multi_search, type_of_show, api)
    else:
        shows = titles

    for show in shows:
        print(time() - start)
        if multi_search:
            data = api.imdbid(show)
        else:
            data = api.title(show)

        if not data:
            continue

        imdb_id = data['imdb_id']

        movie_exists = Movie.objects.filter(imdb_id=imdb_id).exists()
        series_exists = Series.objects.filter(imdb_id=imdb_id).exists()

        if movie_exists or series_exists:
            if not update:
                continue
            show_exists = True
        else:
            show_exists = False

        actors_pk_list = []
        directors_pk_list = []
        genres_pk_list = []
        languages_pk_list = []

        released = data['released']
        poster = data['poster']
        imdb_rating = data['imdb_rating']
        type_of_show = data['type']

        if not data or released == 'N/A' or poster == 'N/A' or imdb_rating == 'N/A':
            continue

        imdb_rating = float(imdb_rating)
        title = data['title']

        actors = data['actors'].split(', ')
        directors = data['director'].split(', ')

        if show_exists:
            directors, actors = compare_actors(actors, directors, imdb_id, type_of_show)

        for actor in actors:
            exists_in_db = Actor.objects.filter(full_name=actor).first()
            if exists_in_db:
                actors_pk_list.append(exists_in_db.pk)
            else:
                actor_instance = Actor.objects.create(
                    full_name=actor,
                    Verified=True
                )
                actors_pk_list.append(actor_instance.pk)

        released = released.split(' ')
        release_date = released[2] + '-' + months[released[1]] + '-' + released[0]

        summary = data['plot']

        for director in directors:
            exists_in_db = Director.objects.filter(full_name=director).first()
            if exists_in_db:
                directors_pk_list.append(exists_in_db.pk)
            else:
                director_instance = Director.objects.create(
                    full_name=director,
                    Verified=True
                )
                directors_pk_list.append(director_instance.pk)

        genres = data['genre'].split(', ')
        for genre in genres:
            exists_in_db = MovieSeriesGenre.objects.filter(name=genre).first()
            if exists_in_db:
                genres_pk_list.append(exists_in_db.pk)
            else:
                genre_instance = MovieSeriesGenre.objects.create(
                    name=genre
                )
                genres_pk_list.append(genre_instance.pk)

        languages = data['language'].split(', ')
        for language in languages:
            exists_in_db = Language.objects.filter(name=language).first()
            if exists_in_db:
                languages_pk_list.append(exists_in_db.pk)
            else:
                language_instance = Language.objects.create(
                    name=language
                )
                languages_pk_list.append(language_instance.pk)

        if type_of_show == 'movie':
            try:
                runtime = int(data['runtime'].split(' ')[0])
            except ValueError:
                runtime = 0

            if show_exists:
                movie_object = Movie.objects.get(imdb_id=imdb_id)
                movie_object.title = title
                movie_object.date_of_release = release_date
                movie_object.running_time = int(runtime)
                movie_object.summary = summary
                movie_object.type_of_show = type_of_show
                movie_object.imdb_rating = imdb_rating
                movie_object.Verified = True
                movie_object.director.set(directors_pk_list)
                movie_object.language.set(languages_pk_list)
                movie_object.genre.set(genres_pk_list)
                movie_object.actors.set(actors_pk_list)
                movie_object.save()
                updated += 1
                print(title)

            else:
                movie_object = Movie.objects.create(
                    imdb_id=imdb_id,
                    title=title,
                    date_of_release=release_date,
                    running_time=int(runtime),
                    summary=summary,
                    type_of_show=type_of_show,
                    poster=poster,
                    Verified=True,
                    # 'added_by': User.objects.get(pk=1),
                    imdb_rating=imdb_rating,
                )
                movie_object.director.set(directors_pk_list)
                movie_object.language.set(languages_pk_list)
                movie_object.genre.set(genres_pk_list)
                movie_object.actors.set(actors_pk_list)
                created += 1
                print(title)

        elif type_of_show == 'series':
            in_production = data['year'].split('–')

            if len(in_production) == 1:
                in_production = True
            else:
                if in_production[1] == '' or in_production[1] == '2022':
                    in_production = True
                else:
                    in_production = False

            seasons = data['total_seasons']

            if seasons == 'N/A':
                seasons = None

            if show_exists:
                show = Series.objects.filter(imdb_id=imdb_id).first()
                current_seasons = show.number_of_seasons

                if seasons != 'N/A' and current_seasons:
                    if int(seasons) < int(current_seasons):
                        seasons = current_seasons
                elif seasons == 'N/A' and current_seasons:
                    seasons = current_seasons

            if show_exists:
                series_object = Series.objects.get(imdb_id=imdb_id)
                series_object.in_production = in_production
                series_object.number_of_seasons = seasons
                series_object.title = title
                series_object.date_of_release = release_date
                series_object.summary = summary
                series_object.type_of_show = type_of_show
                series_object.imdb_rating = imdb_rating
                series_object.Verified = True
                series_object.director.set(directors_pk_list)
                series_object.language.set(languages_pk_list)
                series_object.genre.set(genres_pk_list)
                series_object.actors.set(actors_pk_list)
                series_object.save()
                updated += 1
                print(title)

            else:
                series_object = Series.objects.create(
                    imdb_id=imdb_id,
                    number_of_seasons=seasons,
                    in_production=in_production,
                    title=title,
                    date_of_release=release_date,
                    summary=summary,
                    type_of_show=type_of_show,
                    poster=poster,
                    Verified=True,
                    # 'added_by': User.objects.get(pk=1),
                    imdb_rating=imdb_rating,
                )
                series_object.director.set(directors_pk_list)
                series_object.language.set(languages_pk_list)
                series_object.genre.set(genres_pk_list)
                series_object.actors.set(actors_pk_list)
                created += 1
                print(title)

        if time() - start > 25:
            print("Created:", created)
            print("Updated:", updated)
            return time() - start, True
    print("Created:", created)
    print("Updated:", updated)
    return time() - start, False


@login_required(login_url='/polls/login/')
@permission_required('catalog.can_mark_returned', raise_exception=True)
def scraping_shows_script(request, type_of_show, update):
    start = time()
    months = {"Jan": "01", "Feb": "02", "Mar": "03", "Apr": "04", "May": "05", "Jun": "06", "Jul": "07",
              "Aug": "08", "Sep": "09", "Oct": "10", "Nov": "11", "Dec": "12"}
    api_key = os.environ.get('API_KEY')
    api = omdb.OMDBClient(apikey=api_key)
    genres = ['action', 'adventure', 'comedy', 'crime', 'drama', 'fantasy', 'horror', 'sci_fi', 'romance', 'war',
              'history', 'mystery_and_thriller']
    services = ['netflix', 'amc_plus', 'amazon_prime', 'disney_plus', 'hbo_max', 'apple_tv', 'apple_tv_plus', 'hulu',
                'paramount_plus', 'peacock', 'showtime', 'vudu']
    random.shuffle(genres)
    random.shuffle(services)

    if update == '1':
        update = True
    else:
        update = False

    for service in services:
        for genre in genres:
            url = 'https://www.rottentomatoes.com/browse/' + type_of_show + '/affiliates:' + service + '~genres:' \
                  + genre + '?page=1'
            final_time, end_scraping = scrape_show(url, False, type_of_show, api, update, months, start)
            if end_scraping:
                return render(request, 'index.html')
    return render(request, 'index.html')


@login_required(login_url='/polls/login/')
@permission_required('catalog.can_mark_returned', raise_exception=True)
def omdb_api(request, url, multi_search, type_of_show):
    api_key = os.environ.get('API_KEY')
    final_time = time()
    api = omdb.OMDBClient(apikey=api_key)
    months = {"Jan": "01", "Feb": "02", "Mar": "03", "Apr": "04", "May": "05", "Jun": "06", "Jul": "07",
              "Aug": "08", "Sep": "09", "Oct": "10", "Nov": "11", "Dec": "12"}

    if multi_search == 'True':
        multi_search = True
    else:
        multi_search = False

    url = url.replace("\\", "/")

    final_time, end = scrape_show(url, multi_search, type_of_show, api, True, months, final_time)

    context = {
        'scraping_time': final_time,
        'url': url,
    }

    return render(request, "polls/Scraping/scrape_movies.html", context=context)


@login_required(login_url='/polls/login/')
@permission_required('catalog.can_mark_returned', raise_exception=True)
def omdb_api_page(request):
    if request.method == 'POST':
        form = OmdbApiForm(request.POST)
        if form.is_valid():
            multi_search = form.cleaned_data.get('multi_search')
            type_of_show = form.cleaned_data.get('type_of_show')
            vods = form.cleaned_data.get('VOD')
            audience = form.cleaned_data.get('audience')
            critics = form.cleaned_data.get('critics')
            pages = form.cleaned_data.get('pages')
            sort = form.cleaned_data.get('sort')
            url = "https://www.rottentomatoes.com/browse/" + type_of_show

            if len(vods) != 0:
                url += "/affiliates:"
                for vod in vods:
                    url += vod + ','
                url = url[:-1]

            if len(audience) != 0:
                url += "~audience:"
                for score in audience:
                    url += score + ','
                url = url[:-1]

            if len(critics) != 0:
                url += "~critics:"
                for critic in critics:
                    url += critic + ','
                url = url[:-1]

            if sort != 'False':
                url += "~sort:" + sort

            if pages:
                url += "?page=" + str(pages)

            url = url.replace("/", "\\")
            return render(request, 'polls/Scraping/omdb_api_redirect.html', {'url': url, 'multi_search': multi_search,
                                                                             'type_of_show': type_of_show})
    else:
        form = OmdbApiForm

    return render(request, 'polls/Scraping/omdb_api_page.html', {'form': form})


def games_series_movies_by_genre(request, model_name, pk):
    context = {}
    if model_name == MovieSeriesGenre._meta.object_name:
        genre = get_object_or_404(MovieSeriesGenre, id=pk)
        movies = Movie.objects.filter(genre=genre)
        series = Series.objects.filter(genre=genre)

        context = {
            'movies': movies,
            'series': series,
            'genre': genre
        }

    elif model_name == GameGenre._meta.object_name:
        genre = get_object_or_404(GameGenre, id=pk)
        games = Game.objects.filter(genre=genre)

        context = {
            'games': games,
            'genre': genre
        }

    return render(request, "polls/movie/genre_list.html", context=context)


def create_episodes(series, series_imdb_id, start_seasons_number, end_seasons_number, api, months, start):
    episodes_to_create = []
    episodes_to_update = []
    for season in range(start_seasons_number, end_seasons_number + 1):
        url = "https://www.imdb.com/title/" + series_imdb_id + "/episodes?season=" + str(season)

        response = requests.get(url)
        only_item_cells = SoupStrainer("div", attrs={'id': 'episodes_content'})
        table = BeautifulSoup(response.content, 'lxml', parse_only=only_item_cells)
        episodes_data = table.find_all("div", attrs={'class': 'image'})
        episodes_number = len(episodes_data)

        season_object, created = Season.objects.update_or_create(
            series=series,
            season_number=str(season),
            defaults={
                'series': series,
                'season_number': str(season),
                'number_of_episodes': episodes_number
            }
        )

        episode_number = 0
        for episode in episodes_data:
            episode_number += 1
            link = episode.a['href']
            episode_imdb_id = link.split("/")[2]
            if Episode.objects.filter(imdb_id=episode_imdb_id).exists():
                episodes_to_update = episode_scraping(series, episode_imdb_id, season_object, months, api, 'update',
                                                      episodes_to_update, episode_number)
            else:
                episodes_to_create = episode_scraping(series, episode_imdb_id, season_object, months, api, 'create',
                                                      episodes_to_create, episode_number)

            if time() - start > 25:
                print(time() - start)
                if episodes_to_create:
                    Episode.objects.bulk_create(episodes_to_create)
                if episodes_to_update:
                    Episode.objects.bulk_update(episodes_to_update,
                                                ['title', 'release_date', 'episode_number', 'runtime',
                                                 'plot', 'imdb_rating', 'poster', 'imdb_id', 'season'])
                return True
    if episodes_to_create:
        Episode.objects.bulk_create(episodes_to_create)
    if episodes_to_update:
        Episode.objects.bulk_update(episodes_to_update, ['title', 'release_date', 'episode_number', 'runtime',
                                                         'plot', 'imdb_rating', 'poster', 'imdb_id', 'season'])
    return False


def update_episodes(series, seasons_number, api, months, series_in_production, start):
    episodes_list = []
    if series_in_production:
        seasons = Season.objects.filter(series=series.pk).exclude(season_number=seasons_number)
    else:
        seasons = Season.objects.filter(series=series.pk)
    for season in seasons:
        episodes = Episode.objects.filter(season=season.pk)
        for episode in episodes:
            episodes_list = episode_scraping(series, episode.imdb_id, season, months, api, 'update', episodes_list,
                                             episode.episode_number)

    if time() - start > 25:
        print(time() - start)
        if episodes_list:
            Episode.objects.bulk_update(episodes_list,
                                        ['title', 'release_date', 'episode_number', 'runtime',
                                         'plot', 'imdb_rating', 'poster', 'imdb_id', 'season'])
        return True
    if episodes_list:
        Episode.objects.bulk_update(episodes_list, ['title', 'release_date', 'episode_number', 'runtime',
                                                    'plot', 'imdb_rating', 'poster', 'imdb_id', 'season'])
    return False


def scrape_seasons_number(series_imdb_id):
    url = 'https://www.imdb.com/title/' + series_imdb_id + '/episodes'
    response = requests.get(url)
    only_item_cells = SoupStrainer("select", attrs={'id': 'bySeason'})
    html = BeautifulSoup(response.content, 'lxml', parse_only=only_item_cells)
    seasons_number = html.find("option", attrs={'selected': 'selected'}).text.strip()
    return seasons_number


@permission_required('catalog.can_mark_returned', raise_exception=True)
def series_episodes_scraping(request, pk):
    start = time()
    api_key = os.environ.get('API_KEY')
    api = omdb.OMDBClient(apikey=api_key)
    episodes_scraping(pk, api, start)
    return redirect(reverse('series-to-scrape'))


def episodes_scraping(pk, api, start):
    series = get_object_or_404(Series, id=pk)
    series_imdb_id = series.imdb_id
    months = {"Jan": "01", "Feb": "02", "Mar": "03", "Apr": "04", "May": "05", "Jun": "06", "Jul": "07",
              "Aug": "08", "Sep": "09", "Oct": "10", "Nov": "11", "Dec": "12"}

    if series.episodes_update_date:
        if series.in_production:
            # UPDATE EPISODES THEN CREATE EPISODES
            seasons_number = scrape_seasons_number(series_imdb_id)
            Series.objects.filter(id=pk).update(number_of_seasons=seasons_number)
            current_seasons_number = Season.objects.filter(series=pk).count()

            if seasons_number != '1':
                timeout = update_episodes(series, seasons_number, api, months, series.in_production, start)
                if timeout:
                    return
            timeout = create_episodes(series, series_imdb_id, int(current_seasons_number), int(seasons_number), api,
                                      months, start)

        else:
            # UPDATE EPISODES
            seasons_number = series.number_of_seasons
            timeout = update_episodes(series, seasons_number, api, months, series.in_production, start)
    else:
        # CREATE EPISODES
        series_imdb_id = series.imdb_id
        seasons_number = scrape_seasons_number(series_imdb_id)
        Series.objects.filter(id=pk).update(number_of_seasons=seasons_number)
        timeout = create_episodes(series, series_imdb_id, 1, int(seasons_number), api, months, start)

    end = time()
    print(end - start)
    if not timeout:
        Series.objects.filter(id=pk).update(episodes_update_date=datetime.datetime.today().strftime('%Y-%m-%d'))


@stuff_or_superuser_required
def episodes_scraping_script(request):
    print("Start z req")
    start = time()
    api_key = os.environ.get('API_KEY')
    api = omdb.OMDBClient(apikey=api_key)
    today_date = datetime.datetime.strptime(datetime.datetime.today().strftime('%Y-%m-%d'), "%Y-%m-%d").date()
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
            return redirect('index')
    return redirect('index')


def episode_scraping(series, episode_imdb_id, season_object, months, api, action, episodes, episode_number):
    # omdb.set_default('apikey', api_key)
    episode = api.imdbid(episode_imdb_id)
    if episode:
        title = episode['title']
        release_date = episode['released']

        if release_date == 'N/A':
            release_date = None
        else:
            release_date = release_date.split(' ')
            release_date = release_date[2] + '-' + months[release_date[1]] + '-' + release_date[0]

        try:
            runtime = int(episode['runtime'].split(' ')[0])
        except ValueError:
            runtime = None
        plot = episode['plot']

        imdb_rating = episode['imdb_rating']
        if imdb_rating == 'N/A':
            imdb_rating = None
        else:
            imdb_rating = float(episode['imdb_rating'])

        poster = episode['poster']
        imdb_id = episode_imdb_id

    else:
        title = 'Episode not found'
        release_date = None
        episode_number = episode_number
        runtime = None
        plot = None
        imdb_rating = None
        poster = series.poster
        imdb_id = episode_imdb_id
        #

    episode = Episode.objects.filter(imdb_id=imdb_id).first()

    if action == 'update':
        """
        Episode.objects.update_or_create(
            imdb_id=imdb_id,
            defaults={
                'title': title,
                'release_date': release_date,
                'episode_number': int(episode_number),
                'runtime': int(runtime),
                'plot': plot,
                'imdb_rating': imdb_rating,
                'poster': poster,
                'imdb_id': imdb_id,
                'season': season_object
            }
        )
        """
        episode.title = title
        episode.release_date = release_date
        episode.episode_number = episode_number
        episode.runtime = runtime
        episode.plot = plot
        episode.imdb_rating = imdb_rating
        episode.poster = poster
        episode.imdb_id = imdb_id
        episode.season = season_object

        episodes.append(episode)

    elif action == 'create':
        """
        Episode.objects.create(
            imdb_id=imdb_id,
            title=title,
            release_date=release_date,
            episode_number=int(episode_number),
            runtime=int(runtime),
            plot=plot,
            imdb_rating=imdb_rating,
            poster=poster,
            season=season_object
        )
        """
        episode = Episode(
            imdb_id=imdb_id,
            title=title,
            release_date=release_date,
            episode_number=episode_number,
            runtime=runtime,
            plot=plot,
            imdb_rating=imdb_rating,
            poster=poster,
            season=season_object
        )

        episodes.append(episode)

    return episodes


@permission_required('catalog.can_mark_returned', raise_exception=True)
def enter_api_key(request):
    if request.method == 'POST':
        form = EnterApiKey(request.POST)
        if form.is_valid():
            api_key = form.cleaned_data.get('api_key')
            return redirect(reverse('series-to-scrape', kwargs={'api_key': api_key}))
    else:
        form = EnterApiKey

    return render(request, 'polls/Scraping/enter_api_key.html', {'form': form})


@permission_required('catalog.can_mark_returned', raise_exception=True)
def series_to_scrape(request):
    series_set = Series.objects.filter(Verified=True).order_by('episodes_update_date', 'title')

    context = {
        'series_set': series_set,
    }

    return render(request, 'polls/Scraping/series_to_scrape.html', context=context)


@permission_required('catalog.can_mark_returned', raise_exception=True)
def episode_scraping_in_progress(request, pk):
    series = get_object_or_404(Series, id=pk)

    context = {
        'pk': pk,
        'series': series
    }
    return render(request, 'polls/Scraping/episode_scraping_in_progress.html', context=context)


def create_record(request):
    context = {}
    return render(request, 'create_records.html', context=context)


class RequestPermissionCreate(UserPassesTestMixin, CreateView):
    model = RequestPermission
    form_class = RequestPermissionForm
    template_name = "polls/Game/developer_form.html"
    success_url = reverse_lazy('index')

    def test_func(self):
        check_existence = RequestPermission.objects.filter(FromUser=self.request.user.profile)

        if not check_existence and self.request.user.is_authenticated:
            return True
        else:
            return False

    def handle_no_permission(self):
        return redirect('index')

    def form_valid(self, form):
        messages.success(self.request, "Test!")
        form.instance.FromUser = self.request.user.profile
        form.instance.status = 'Sent'

        return super(RequestPermissionCreate, self).form_valid(form)


class RequestPermissionList(UserPassesTestMixin, generic.ListView):
    model = RequestPermission
    template_name = "polls/request_list.html"

    def test_func(self):
        return self.request.user.is_superuser

    def handle_no_permission(self):
        return redirect('index')


@stuff_or_superuser_required
def delete_unverified_users(request):
    get_all_users = User.objects.all()

    for userI in get_all_users:
        if userI.is_superuser or userI.is_staff:
            continue
        elif userI.profile.expired_registration_check():
            userI.delete()
        else:
            continue

    return redirect('index')  # W skryptcie zastąpić jako exit()


class UserPageManagement(UserPassesTestMixin, generic.DetailView):
    model = Profile
    template_name = "polls/Profile/user-management.html"

    def test_func(self):
        return self.request.user.is_superuser or self.request.user.is_staff

    def handle_no_permission(self):
        return redirect('index')


@stuff_or_superuser_required
def delete_unverified_games(request, pk):
    games = Game.objects.filter(added_by=pk, Verified=False)
    for game in games:
        game.delete()
    return redirect('user-page-management', pk)


@stuff_or_superuser_required
def delete_unverified_movies(request, pk):
    movies = Movie.objects.filter(added_by=pk, Verified=False)
    for movie in movies:
        movie.delete()
    return redirect('user-page-management', pk)


@stuff_or_superuser_required
def delete_unverified_series(request, pk):
    series = Series.objects.filter(added_by=pk, Verified=False)
    for series_object in series:
        series_object.delete()
    return redirect('user-page-management', pk)


@stuff_or_superuser_required
def delete_user(request, pk):
    try:
        u = User.objects.get(id=pk)
        u.delete()
        messages.success(request, "The user is deleted")

    except User.DoesNotExist:
        messages.error(request, "User does not exist")
        return redirect('index')

    return redirect('index')


@stuff_or_superuser_required
def delete_unverified_all(request, pk):
    games = Game.objects.filter(added_by=pk, Verified=False)
    movies = Movie.objects.filter(added_by=pk, Verified=False)
    series = Series.objects.filter(added_by=pk, Verified=False)

    for game in games:
        game.delete()

    for movie in movies:
        movie.delete()

    for serie in series:
        serie.delete()

    return redirect('user-page-management', pk)


# TESTING STUF
def test(request):
    authors = []
    start = time()
    update_or_create = []
    bulk_update = []
    for j in range(30):
        for i in range(1, 10):
            author = Author.objects.filter(id=i).first()
            author.first_last_name = 'firstnamev3' + str(i)
            authors.append(author)
        Author.objects.bulk_update(authors, ['first_last_name'])
        bulk_update.append(time() - start)

        start = time()
        for i in range(1, 10):
            Author.objects.update_or_create(
                id=i,
                defaults={
                    'first_last_name': 'firstnamev2' + str(i),
                }
            )
        update_or_create.append(time() - start)
    print('update or create', sum(update_or_create) / len(update_or_create))
    print(update_or_create)
    print('bulk update', sum(bulk_update) / len(bulk_update))
    print(bulk_update)
    return render(request, 'index.html')


# TESTING STUF
def test1(request):
    pk_list = [1]
    movies = []
    for i in range(1, 10):
        movie = Movie(title='title' + str(i), date_of_release='2022-11-21', summary=str(i),
                      poster=str(i), type_of_show='movie', running_time=i)
        movie.actors.through()
        movie.director.set(pk_list)
        movie.language.set(pk_list)
        movie.genre.set(pk_list)
        movies.append(movie)

    Author.objects.bulk_create(movies)

    return render(request, 'index.html')


# TESTING STUF
def bulk_create(request):
    authors = []
    update_or_create = []
    bulk_update = []

    start = time()
    for i in range(1, 100):
        Author.objects.create(

            first_name='firstnamev2' + str(i) + str(random.randint(0, 100000)),
            last_name='lastnamev2' + str(i) + str(random.randint(0, 100000))

        )
    update_or_create.append(time() - start)

    start = time()
    for i in range(1, 100):
        author = Author(first_name='firstnamev3' + str(i) + str(random.randint(0, 100000)),
                        last_name='firstnamev3' + str(i) + str(random.randint(0, 100000)))
        authors.append(author)
    Author.objects.bulk_create(authors)
    bulk_update.append(time() - start)

    print('normal create', sum(update_or_create) / len(update_or_create))
    print(update_or_create)
    print('bulk create', sum(bulk_update) / len(bulk_update))
    print(bulk_update)
    return render(request, 'index.html')


def search_result_user(request):
    if request.method == "POST":
        searched = request.POST['searched']

        searched_profiles = Profile.objects.filter(name__icontains=searched)

        return render(request, 'polls/search_result.html',
                      {'searched_profiles': searched_profiles})
    else:
        return render(request, 'polls/search_result.html')


def search_result_general(request):
    if request.method == "POST":
        searched = request.POST['searched']
        if searched:
            searched_profiles = Profile.objects.filter(name__icontains=searched)
            searched_games = Game.objects.filter(title__icontains=searched, Verified=True)
            searched_movies = Movie.objects.filter(title__icontains=searched, Verified=True)
            searched_series = Series.objects.filter(title__icontains=searched, Verified=True)
            searched_books = Book.objects.filter(title__icontains=searched, Verified=True)
            searched_actors = Actor.objects.filter(full_name__icontains=searched, Verified=True)
        else:
            searched_profiles = Profile.objects.none()
            searched_games = Game.objects.none()
            searched_movies = Movie.objects.none()
            searched_series = Series.objects.none()
            searched_books = Book.objects.none()
            searched_actors = Actor.objects.none()
        return render(request, 'polls/search_result.html',
                      {'searched_profiles': searched_profiles,
                       'searched_games': searched_games,
                       'searched_movies': searched_movies,
                       'searched_series': searched_series,
                       'searched_actors': searched_actors,
                       'searched_books': searched_books})
    else:
        return render(request, 'polls/search_result.html')


class ThreadCreate(UserPassesTestMixin, CreateView):
    model = Thread
    form_class = ThreadForm
    template_name = "polls/Forum/thread_create.html"

    def form_view(self, request, pk):
        if 'category_id' in request == "POST":
            category = get_object_or_404(ForumCategory, id=pk)
            saved_category = Thread(category=category)
            saved_category.save()

        return render(request, 'polls/Forum/thread_create.html', {'form': ThreadCreate()})

    def form_valid(self, form):
        form.instance.creator = self.request.user.profile
        form.instance.category_id = self.kwargs['category_pk']
        return super().form_valid(form)

    def test_func(self):
        return self.request.user.is_authenticated

    def handle_no_permission(self):
        return redirect('login')


class ThreadListView(generic.ListView):
    template_name = "polls/Forum/thread_list.html"
    model = Thread
    paginate_by = 10


class ThreadDetailView(generic.DetailView, FormMixin):
    template_name = "polls/Forum/thread_detail.html"
    model = Thread
    form_class = PostForm
    count_hit = True

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)

        thread = self.get_object()
        thread.views += 1
        thread.save()

        posts_connected = Post.objects.filter(
            thread=self.get_object()).order_by('-date')
        data['posts'] = posts_connected

        if self.request.user.is_authenticated:
            posts_liked = []
            profile = Profile.objects.filter(user_id=self.request.user.pk).first()
            data['post_form'] = PostForm(instance=self.request.user)

            posts = list(posts_connected.values_list('id', flat=True))
            for post_pk in posts:
                # test1111 = profile.post_like.values_list('id', flat=True)
                if profile.post_like.filter(id=post_pk).exists():
                    posts_liked.append(True)
                else:
                    posts_liked.append(False)
            print(posts_liked)
            data['posts'] = zip(posts_liked, posts_connected)

        return data

    def form_view(request):
        return render(request, 'polls/Forum/thread_detail.html', {'form': ThreadDetailView()})

    def get_success_url(self):
        return reverse('thread-detail', kwargs={'slug_category': self.object.slug_category, 'slug': self.object.slug})

    def post(self, request, *args, **kwargs):
        if self.request.method == 'POST':
            self.object = self.get_object()
            form = self.get_form()
            if form.is_valid():
                return self.form_valid(form)
            else:
                return self.form_invalid(form)

    def form_valid(self, form):
        new_post = Post(content=form.data['content'],
                        creator=self.request.user.profile,
                        thread=self.get_object())
        new_post.save()
        return super(ThreadDetailView, self).form_valid(form)


def post_like_view(request, pk, thread_pk):
    post = get_object_or_404(Post, id=pk)
    number_of_likes = post.likes_number
    if post.likes.filter(id=request.user.id).exists():
        post.likes.remove(request.user.profile)
        number_of_likes -= 1
    else:
        post.likes.add(request.user.profile)
        number_of_likes += 1
    post.likes_number = number_of_likes
    post.save()

    get_thread_object_slug = Thread.objects.get(pk=thread_pk).slug
    get_thread_object_slug_category = Thread.objects.get(pk=thread_pk).slug_category

    return HttpResponseRedirect(reverse('thread-detail', args=[get_thread_object_slug_category, get_thread_object_slug]))


class ThreadUpdate(UserPassesTestMixin, UpdateView):
    model = Thread
    template_name = "polls/Forum/thread_update.html"
    fields = ['title']

    def test_func(self):
        return self.request.user.is_superuser

    def handle_no_permission(self):
        return redirect('index')


def ThreadLike(request, pk):
    thread = get_object_or_404(Thread, id=request.POST.get('thread_id'))
    if thread.likes.filter(id=request.user.id).exists():
        thread.likes.remove(request.user.profile)
    else:
        thread.likes.add(request.user.profile)

    return HttpResponseRedirect(reverse('thread-detail', args=[str(thread.slug_category),str(thread.slug)]))


class ThreadCategoryCreate(UserPassesTestMixin, CreateView):
    model = ForumCategory
    form_class = ThreadCategoryForm
    template_name = "polls/Forum/category_create.html"

    def test_func(self):
        return self.request.user.is_authenticated

    def handle_no_permission(self):
        return redirect('login')

    def form_valid(self, form):
        form.instance.creator = self.request.user.profile
        return super(ThreadCategoryCreate, self).form_valid(form)


class ThreadCategoryListView(generic.ListView):
    template_name = "polls/Forum/category.html"
    model = ForumCategory
    paginate_by = 10

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)

        sessions = Session.objects.filter(expire_date__gte=timezone.now())
        users_list = []

        for session in sessions:
            data = session.get_decoded()
            users_list.append(data.get('_auth_user_id', None))

        profile = Profile.objects.filter(user=self.request.user).first()
        data['profile'] = profile

        data['announcements_and_rules'] = ForumCategory.objects.filter(title='announcements & rules').first()
        data['suggestions_and_bugs'] = ForumCategory.objects.filter(title='suggestions & bugs').first()
        data['appeals'] = ForumCategory.objects.filter(title='appeals').first()
        data['books'] = ForumCategory.objects.filter(title='books').first()
        data['games'] = ForumCategory.objects.filter(title='games').first()
        data['movies'] = ForumCategory.objects.filter(title='movies').first()
        data['series'] = ForumCategory.objects.filter(title='series').first()
        data['creative_writing'] = ForumCategory.objects.filter(title='creative writing').first()
        data['questing'] = ForumCategory.objects.filter(title='questing').first()
        data['play_by_post'] = ForumCategory.objects.filter(title='play by post').first()
        data['nswf_creative_writing'] = ForumCategory.objects.filter(title='nswf creative writing').first()
        data['nswf_questing'] = ForumCategory.objects.filter(title='nswf questing').first()
        data['nswf_play_by_post'] = ForumCategory.objects.filter(title='nswf play by post').first()
        data['general'] = ForumCategory.objects.filter(title='general').first()
        data['nswf_general'] = ForumCategory.objects.filter(title='nswf general').first()

        data['logged_users'] = User.objects.filter(id__in=users_list)

        return data


class ThreadCategoryDetailView(generic.DetailView, FormMixin):
    template_name = "polls/Forum/category_detail.html"
    model = ForumCategory
    paginate_by = 20
    form_class = ThreadForm

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        profile = Profile.objects.filter(user=self.request.user).first()
        num_visits = self.request.session.get('num_visits', 0)
        self.request.session['num_visits'] = num_visits + 1

        threads_connected = Thread.objects.filter(
            category=self.get_object()).order_by('-date')
        data['profile'] = profile
        data['threads'] = threads_connected
        data['num_visits'] = num_visits
        if self.request.user.is_authenticated:
            data['thread_form'] = ThreadForm(instance=self.request.user.profile)
        return data

    def get_success_url(self):
        return reverse('thread-category-detail', kwargs={'slug': self.object.slug})


class ThreadCategoryUpdate(UserPassesTestMixin, UpdateView):
    model = ForumCategory
    template_name = "polls/Forum/category_update.html"
    fields = ['title', 'content']

    def test_func(self):
        return self.request.user.is_superuser

    def handle_no_permission(self):
        return redirect('index')


class PostCreate(UserPassesTestMixin, CreateView):
    model = Thread
    form_class = ThreadForm
    template_name = "polls/Forum/post_create.html"

    def form_valid(self, form):
        form.instance.creator = self.request.user.profile
        return super(PostCreate, self).form_valid(form)

    def test_func(self):
        return self.request.user.is_authenticated

    def handle_no_permission(self):
        return redirect('login')


class PostDetailView(generic.DetailView):
    template_name = "polls/Forum/post_detail.html"
    model = Post


class PostListView(generic.ListView):
    template_name = "polls/Forum/category.html"
    model = Post
    paginate_by = 10


class PostUpdate(UserPassesTestMixin, UpdateView):
    model = Post
    template_name = "polls/Forum/post_update.html"
    fields = ['content']

    def test_func(self):
        author = Post.objects.filter(id=self.kwargs['pk']).first().creator.user
        return self.request.user == author and self.request.user.is_authenticated or self.request.user.is_superuser

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return redirect('login')
        return redirect('index')

    def get_success_url(self):
        get_thread_object_slug = Thread.objects.get(pk=self.kwargs['thread_pk']).slug
        get_thread_object_slug_category = Thread.objects.get(pk=self.kwargs['thread_pk']).slug_category

        return reverse('thread-detail', kwargs={'slug_category': get_thread_object_slug_category,'slug': get_thread_object_slug})


class ThreadDelete(UserPassesTestMixin, DeleteView):
    model = Thread
    template_name = "polls/Forum/thread_delete.html"
    success_url = reverse_lazy('thread')
    login_url = reverse_lazy('index')

    def test_func(self):
        return self.request.user.is_superuser

    def handle_no_permission(self):
        return redirect('index')


class ThreadCategoryDelete(UserPassesTestMixin, DeleteView):
    model = ForumCategory
    template_name = "polls/Forum/category_delete.html"
    success_url = reverse_lazy('category')
    login_url = reverse_lazy('index')

    def test_func(self):
        return self.request.user.is_superuser

    def handle_no_permission(self):
        return redirect('index')


class PostDelete(UserPassesTestMixin, DeleteView):
    model = Post
    template_name = "polls/Forum/post_delete.html"
    # success_url = reverse_lazy('post')
    login_url = reverse_lazy('index')

    def test_func(self):
        author = Post.objects.filter(id=self.kwargs['pk']).first().creator.user
        return (self.request.user == author and self.request.user.is_authenticated) or self.request.user.is_superuser

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return redirect('login')
        return redirect('index')

    def form_valid(self, form):
        if self.object.creator is not None and self.request.user.is_superuser:
            delete_reason_content = form.data['delete_reason']
            basic_message_content = 'Your post was deleted from PTC'
            mail_notification(self.get_object(), basic_message_content, delete_reason_content, 'creator')
        messages.success(self.request, "The post has been deleted!")
        return super().form_valid(form)

    def get_success_url(self):
        get_thread_object_slug = Thread.objects.get(pk=self.kwargs['thread_pk']).slug
        get_thread_object_slug_category = Thread.objects.get(pk=self.kwargs['thread_pk']).slug_category
        return reverse('thread-detail',
                       kwargs={'slug_category': get_thread_object_slug_category, 'slug': get_thread_object_slug})


def tagged(request, slug):
    tag = get_object_or_404(Tag, slug=slug)
    # Filter posts by tag name
    threads = Thread.objects.filter(tags=tag)
    context = {
        'tag': tag,
        'threads': threads,
    }
    return render(request, 'index.html', context)
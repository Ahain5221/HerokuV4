import ast
import os
import random
from datetime import datetime
from time import time

import omdb
# third-party imports
import requests
# twitter imports
import tweepy
import xlrd
from bs4 import BeautifulSoup, SoupStrainer
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.models import Group, Permission
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.views import PasswordChangeView
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.sessions.models import Session
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import EmailMessage
from django.core.mail import send_mail, BadHeaderError
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models.query_utils import Q
from django.http import Http404
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.template.loader import render_to_string
from django.urls import reverse
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.views import generic
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.edit import FormMixin
from friendship.models import Friend, FriendshipRequest
from taggit.models import Tag
from polls.prohibited_words import reserved_words_signup

from polls.decorators import *
from .forms import *
from .forms import PostForm, ForumCategory, ThreadCategoryForm, ThreadForm, SignUpForm
from .models import Book, BookReview, BookList
from .models import Game, Developer, Profile, GameGenre, GameMode, KnownSteamAppID, GameReview, GameList
from .models import Movie, Series, Actor, Director, Language, MovieSeriesGenre
from .models import Post, Thread
from .models import Season, Episode, MovieReview, MovieWatchlist, SeriesWatchlist, SeriesReview
from .models import Tweet
from .token import account_activation_token


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


@stuff_or_superuser_required
def add_categories(request):
    link = "polls/static/category.xls"

    workbook = xlrd.open_workbook(link)
    sheet = workbook.sheet_by_name('Sheet1')

    for row in range(1, sheet.nrows):
        name = str(sheet.cell(row, 0).value)
        summary = sheet.cell(row, 1).value

        category_object, created = ForumCategory.objects.update_or_create(
            title=name,
            defaults=
            {
                'content': summary
            })

        category_pk = category_object.pk

        Thread.objects.update_or_create(
            title='Q&A', category_id=category_pk,
            defaults=
            {
                'creator': request.user.profile
            })

    return redirect('index')


class cbv_view(generic.ListView):
    model = Developer
    template_name = 'index.html'


def custom_handler_404(request, exception):
    context = {'domain': get_current_site(request)}
    return render(request, 'error_404.html', context=context)


@stuff_or_superuser_required
def get_autocomplete_permission(request, pk):
    autocomplete_group, created = Group.objects.get_or_create(name='autocomplete_group')
    user_object = User.objects.get(id=pk)
    if created:
        permission_developer = Permission.objects.get(name='Can add developer')
        permission_actor = Permission.objects.get(name='Can add actor')
        permission_director = Permission.objects.get(name='Can add director')
        permission_author = Permission.objects.get(name='Can add author')

        autocomplete_group.permissions.add(permission_developer, permission_actor,
                                           permission_director, permission_author)
    autocomplete_group.user_set.add(user_object)
    try:
        check_permission = RequestPermission.objects.get(FromUser=pk)
        check_permission.status = "Accepted"
        check_permission.save(update_fields=['status'])
    except (Exception,):
        messages.error(request, 'Check if the request still exists')
        return redirect('profile-page', user_object.username)
    return redirect('request-list')


@stuff_or_superuser_required
def reject_autocomplete_permission(request, pk):
    request_object = RequestPermission.objects.get(FromUser=pk)
    request_object.status = "Rejected"
    request_object.save(update_fields=['status'])
    return redirect('request-list')


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


@anonymous_required
def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            try:
                if form.cleaned_data.get('username') in reserved_words_signup:
                    messages.error(request, 'You cannot use such a username.')
                    return redirect('signup')

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
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})


@anonymous_required
def password_reset_request(request):
    if request.method == "POST":
        password_reset_form = PasswordResetForm(request.POST)
        if password_reset_form.is_valid():
            current_site = get_current_site(request)
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
                        'domain': 'my-pct.me',
                        'site_name': 'Website',
                        "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                        "user": user,
                        'token': default_token_generator.make_token(user),
                        'protocol': 'https',
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
    else:
        return HttpResponse('Activation link is invalid!')


def sendmail(request):
    send_mail(
        'Weryfikacja rejestracji na PCT',  # Tytuł maila
        'Link do weryfikacji.',  # Treść maila
        'pct-team@outlook.com',  # Z jakiego maila wysyłamy
        ['pct-team@outlook.com'],  # Na jakiego maila wysyłamy
        fail_silently=False,
    )
    return render(request, 'sendmail.html')

from django.views.decorators.cache import cache_page


@cache_page(123456)
def index(request):
    if request.user.is_authenticated:
        last_book = Book.objects.filter(Verified=True).order_by("pk").last()
        last_game = Game.objects.filter(Verified=True).order_by("pk").last()
        last_series = Series.objects.filter(Verified=True).order_by("pk").last()
        last_movie = Movie.objects.filter(Verified=True).order_by("pk").last()

        tweets = Tweet.objects.order_by('-published_date')[:10]

        index_context = {
            'last_book': last_book,
            'last_game': last_game,
            'last_series': last_series,
            'last_movie': last_movie,
            'tweets': tweets
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
    if request.POST:
        username = request.POST['username'].lower()
        password = request.POST['password']
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
    form_class = AuthorForm


class AuthorUpdate(UpdateView):
    model = Author
    template_name = "polls/Book/author_form.html"
    form_class = AuthorForm


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
            basic_message_content = 'Your book was deleted from PCT, title: ' + str(self.object)
            mail_notification(self.get_object(), basic_message_content, delete_reason_content, 'added_by')
        messages.success(self.request, "The book has been deleted!")
        return super().form_valid(form)


@stuff_or_superuser_required
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


@stuff_or_superuser_required
def book_verification_stuff_page(request):
    list_of_books = request.POST.getlist('books-select')
    if not list_of_books:
        return redirect("stuff-verification")
    query_set_of_books = Book.objects.none()
    for book_id in list_of_books:
        get_book_in_query = Book.objects.filter(pk=book_id)
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


@login_required(login_url='/polls/login/')
def add_book_to_book_list(request, book_pk, user_pk, book_status):
    if request.user.is_superuser or request.user.is_staff or request.user.pk == user_pk:

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
    return redirect('index')


@login_required(login_url='/polls/login/')
def remove_book_from_book_list(request, book_pk, user_pk):
    if request.user.is_superuser or request.user.is_staff or request.user.pk == user_pk:
        profile_pk = Profile.objects.filter(user_id=user_pk).first().pk
        review = BookReview.objects.filter(book=book_pk).filter(author=user_pk)
        book_list = BookList.objects.filter(book=book_pk).filter(profile=profile_pk)
        review.delete()
        book_list.delete()
        return HttpResponseRedirect(reverse('book-detail', args=[str(book_pk)]))
    return redirect('index')


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

        if_book_in_other_user_list = []
        if self.request.user.is_authenticated:
            logged_user_book_list = BookList.objects.filter(profile=self.request.user.profile).values_list(
                'book', flat=True)

        else:
            logged_user_book_list = []

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

            if book in logged_user_book_list:
                if_book_in_other_user_list.append(True)
            else:
                if_book_in_other_user_list.append(False)

            if book in book_reviews_books:
                book_reviews_all.append(BookReview.objects.filter(
                    author=self.object.user).filter(book=book).first())
            else:
                book_reviews_all.append(False)

        reviews_and_books = zip(book_list_all, book_reviews_all, if_book_in_other_user_list)
        context['reviews_and_books'] = reviews_and_books

        context['status'] = status

        return context


@login_required(login_url='/polls/login/')
def change_book_status(request, book_pk, profile_pk, status):
    if request.user.is_superuser or request.user.is_staff or request.user.profile.pk == profile_pk:
        game_list_object = BookList.objects.filter(book_id=book_pk).filter(profile_id=profile_pk).first()
        game_list_object.book_status = status
        game_list_object.save(update_fields=['book_status'])

        return HttpResponseRedirect(reverse('profile-book-list', args=[request.user, 'all']))
    return redirect('index')


class GameCreate(CreateView):
    model = Game
    form_class = GameForm
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
            basic_message_content = 'Your review was deleted from PCT, title: ' + str(self.object.series)
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
            'Delete notification from PCT ',
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
            basic_message_content = 'Your review was deleted from PCT, title: ' + str(self.object.game)
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
            basic_message_content = 'Your review was deleted from PCT, title: ' + str(self.object.book)
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
            basic_message_content = 'Your review was deleted from PCT, title: ' + str(self.object.movie)
            mail_notification(self.get_object(), basic_message_content, delete_reason_content, 'author')
        messages.success(self.request, "The review has been deleted!")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('movie-detail', kwargs={'pk': self.kwargs['movie_pk']})


@login_required(login_url='/polls/login/')
def add_game_to_game_list(request, game_pk, user_pk, game_status):
    if request.user.is_superuser or request.user.is_staff or request.user.pk == user_pk:

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
    return redirect('index')


@login_required(login_url='/polls/login/')
def remove_game_from_game_list(request, game_pk, user_pk):
    if request.user.is_superuser or request.user.is_staff or request.user.pk == user_pk:
        profile_pk = Profile.objects.filter(user_id=user_pk).first().pk
        review = GameReview.objects.filter(game=game_pk).filter(author=user_pk)
        game_list = GameList.objects.filter(game=game_pk).filter(profile=profile_pk)
        review.delete()
        game_list.delete()
        return HttpResponseRedirect(reverse('game-detail', args=[str(game_pk)]))
    return redirect('index')


class ProfileGameList(generic.DetailView):
    model = Profile
    template_name = "polls/Profile/game_list.html"
    slug_field = 'name'
    slug_url_kwarg = 'name'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()

        status = self.kwargs['status']

        if_game_in_other_user_list = []
        if self.request.user.is_authenticated:
            logged_user_game_list = GameList.objects.filter(profile=self.request.user.profile).values_list(
                'game', flat=True)

        else:
            logged_user_game_list = []

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
            if game in logged_user_game_list:
                if_game_in_other_user_list.append(True)
            else:
                if_game_in_other_user_list.append(False)

            if game in game_reviews_games:
                game_reviews_all.append(GameReview.objects.filter(
                    author=self.object.user).filter(game=game).first())
            else:
                game_reviews_all.append(False)

        reviews_and_games = zip(game_list_all, game_reviews_all, if_game_in_other_user_list)

        context['reviews_and_games'] = reviews_and_games
        context['status'] = status

        return context


class GameReviewDetail(generic.DetailView):
    model = GameReview
    template_name = "polls/Game/game_review_detail.html"


@login_required(login_url='/polls/login/')
def change_game_status(request, game_pk, profile_pk, status):
    if request.user.is_superuser or request.user.is_staff or request.user.profile.pk == profile_pk:
        game_list_object = GameList.objects.filter(game_id=game_pk).filter(profile_id=profile_pk).first()
        game_list_object.game_status = status
        game_list_object.save(update_fields=['game_status'])

        return HttpResponseRedirect(reverse('profile-game-list', args=[request.user, 'all']))
    return redirect('index')


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
            basic_message_content = 'Your game was deleted from PCT, title: ' + str(self.object)
            mail_notification(self.get_object(), basic_message_content, delete_reason_content, 'added_by')
        messages.success(self.request, "The game has been deleted!")
        return super().form_valid(form)


class GameListView(generic.ListView):
    model = Game
    paginate_by = 12
    template_name = "polls/Game/game_list.html"
    ordering = ["title"]


class GameGenreList(generic.ListView):
    model = Game
    paginate_by = 12
    template_name = "polls/Game/game_list.html"
    ordering = ["title"]

    def get_queryset(self):
        get_all_games = Game.objects.all()
        try:
            genre_pk = GameGenre.objects.get(name=self.kwargs['selected_genre']).pk
        except ObjectDoesNotExist:
            raise Http404
        filtered_game_list = get_all_games.filter(genre=genre_pk, Verified=True)

        return filtered_game_list

    def get_context_data(self, **kwargs):
        context = super(GameGenreList, self).get_context_data(**kwargs)
        context['genre_name'] = self.kwargs['selected_genre']
        return context


class MovieGenreList(generic.ListView):
    model = Movie
    paginate_by = 12
    template_name = "polls/movie/movie_list.html"
    ordering = ["title"]

    def get_queryset(self):
        get_all_movies = Movie.objects.all()
        try:
            genre_pk = MovieSeriesGenre.objects.get(name=self.kwargs['selected_genre']).pk
        except ObjectDoesNotExist:
            raise Http404
        filtered_movie_list = get_all_movies.filter(genre=genre_pk, Verified=True)

        return filtered_movie_list

    def get_context_data(self, **kwargs):
        context = super(MovieGenreList, self).get_context_data(**kwargs)
        context['genre_name'] = self.kwargs['selected_genre']
        return context


class SeriesGenreList(generic.ListView):
    model = Series
    paginate_by = 12
    template_name = "polls/movie/series_list.html"
    ordering = ["title"]

    def get_queryset(self):
        get_all_series = Series.objects.all()
        try:
            genre_pk = MovieSeriesGenre.objects.get(name=self.kwargs['selected_genre']).pk
        except ObjectDoesNotExist:
            raise Http404
        filtered_series_list = get_all_series.filter(genre=genre_pk, Verified=True)

        return filtered_series_list

    def get_context_data(self, **kwargs):
        context = super(SeriesGenreList, self).get_context_data(**kwargs)
        context['genre_name'] = self.kwargs['selected_genre']
        return context


class BookGenreList(generic.ListView):
    model = Book
    paginate_by = 12
    template_name = "polls/Book/book_list.html"
    ordering = ["title"]

    def get_queryset(self):
        get_all_books = Book.objects.all()
        try:
            genre_pk = MovieSeriesGenre.objects.get(name=self.kwargs['selected_genre']).pk
        except ObjectDoesNotExist:
            raise Http404
        filtered_book_list = get_all_books.filter(genre=genre_pk, Verified=True)

        return filtered_book_list

    def get_context_data(self, **kwargs):
        context = super(BookGenreList, self).get_context_data(**kwargs)
        context['genre_name'] = self.kwargs['selected_genre']
        return context


class DeveloperDetailView(generic.DetailView):
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
            basic_message_content = 'Your developer was deleted from PCT, title: ' + str(self.object)
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
    form_class = PasswordChangingForm
    template_name = 'polls/Profile/change_password.html'
    success_url = reverse_lazy('password_success')


def password_change_success(request):
    return render(request, 'polls/Profile/password_success.html')


class UserProfileEditView(UserPassesTestMixin, generic.UpdateView):
    model = Profile
    form_class = UserProfileEditForm
    template_name = "polls/Profile/edit_profile.html"

    def get_object(self):
        return self.request.user.profile

    def test_func(self):
        return self.request.user.is_authenticated

    def handle_no_permission(self):
        return redirect('index')

    def get_success_url(self):
        return reverse('profile-page', args=[str(self.object.user)])


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


@login_required(login_url='/polls/login/')
def friend_list(request):
    get_user = User.objects.get(id=request.user.pk)
    friends = Friend.objects.friends(get_user)
    avatars = []
    for friend in friends:
        avatars.append(friend.profile.profile_image_url)
    request_list = Friend.objects.unread_requests(get_user)

    context = {
        'friend_list': zip(avatars, friends),
        'friend_request_list': request_list,
        'avatars': avatars
    }
    return render(request, 'FriendList.html', context=context)


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
        context = super(ProfilePageView, self).get_context_data(**kwargs)
        name_lower = self.kwargs['name'].lower()
        get_pk = get_object_or_404(Profile, name=name_lower).pk
        page_user = get_object_or_404(Profile, id=get_pk)
        perm_request = RequestPermission.objects.filter(FromUser=get_pk)
        if perm_request:
            perm_request.first()
        else:
            perm_request = None
        has_perm = self.request.user.groups.filter(name='autocomplete_group').exists()
        liked = False
        if page_user.likes.filter(id=self.request.user.id).exists():
            liked = True
        sent = Friend.objects.sent_requests(user=self.request.user)
        received = Friend.objects.unread_requests(user=self.request.user)
        amount_of_pending_friend_request = len(received)
        was_send_friend_request = False
        received_friend_request = False

        for te2 in received:
            if te2.from_user == page_user.user:
                received_friend_request = True

        for te in sent:
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
    for game_id in list_of_games:
        get_game_in_query = Game.objects.filter(pk=game_id)
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
    paginate_by = 18

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        order_by = self.kwargs['order_by']
        context['order_by'] = order_by
        return context

    def get_queryset(self):
        order_by = self.kwargs['order_by']
        movie_list = Movie.objects.order_by(order_by)

        return movie_list


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
            basic_message_content = 'Your movie was deleted from PCT, title: ' + str(self.object)
            mail_notification(self.get_object(), basic_message_content, delete_reason_content, 'added_by')
        messages.success(self.request, "The movie has been deleted!")
        return super().form_valid(form)

    def handle_no_permission(self):
        return redirect('index')


class MovieCreate(UserPassesTestMixin, CreateView):
    model = Movie
    template_name = "polls/movie/movie_create.html"
    form_class = MovieForm

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
    list_of_movies = request.POST.getlist('movies-select')
    if not list_of_movies:
        return redirect("stuff-verification")
    query_set_of_movies = Game.objects.none()
    for movie_id in list_of_movies:
        get_movie_in_query = Movie.objects.filter(pk=movie_id)
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

        if_movie_in_other_user_list = []
        if_series_in_other_user_list = []
        if self.request.user.is_authenticated:
            logged_user_movie_watchlist = MovieWatchlist.objects.filter(profile=self.request.user.profile).values_list(
                'movie', flat=True)
            logged_user_series_watchlist = SeriesWatchlist.objects.filter(
                profile=self.request.user.profile).values_list('series', flat=True)
        else:
            logged_user_movie_watchlist = []
            logged_user_series_watchlist = []

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
                if movie in logged_user_movie_watchlist:
                    if_movie_in_other_user_list.append(True)
                else:
                    if_movie_in_other_user_list.append(False)

                if movie in movie_reviews_movies:
                    movie_reviews_all.append(MovieReview.objects.filter(
                        author=self.object.user).filter(movie=movie).first())
                else:
                    movie_reviews_all.append(False)

            reviews_and_movies = zip(movie_watchlist_all, movie_reviews_all, if_movie_in_other_user_list)
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

                if series in logged_user_series_watchlist:
                    if_series_in_other_user_list.append(True)
                else:
                    if_series_in_other_user_list.append(False)

                if series in series_reviews_series:
                    series_reviews_all.append(SeriesReview.objects.filter(
                        author=self.object.user).filter(series=series).first())
                else:
                    series_reviews_all.append(False)

            reviews_and_series = zip(series_watchlist_all, series_reviews_all, if_series_in_other_user_list)
            context['reviews_and_series'] = reviews_and_series

        context['type_of_show'] = type_of_show
        context['status'] = status

        return context


class MovieReviewDetail(UserPassesTestMixin, generic.DetailView):
    model = MovieReview
    template_name = "polls/movie/movie_review_detail.html"

    def test_func(self):
        return self.request.user.is_authenticated

    def handle_no_permission(self):
        return redirect('login')


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
    paginate_by = 18

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        order_by = self.kwargs['order_by']
        context['order_by'] = order_by
        return context

    def get_queryset(self):
        order_by = self.kwargs['order_by']
        series_list = Series.objects.order_by(order_by)

        return series_list


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
            basic_message_content = 'Your series were deleted from PCT, title: ' + str(self.object)
            mail_notification(self.get_object(), basic_message_content, delete_reason_content, 'added_by')
        messages.success(self.request, "The series has been deleted!")
        return super().form_valid(form)

    def handle_no_permission(self):
        return redirect('index')


class SeriesCreate(UserPassesTestMixin, CreateView):
    model = Series
    form_class = SeriesForm
    template_name = "polls/movie/series_create.html"

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
    for series_id in list_of_series:
        get_series_in_query = Series.objects.filter(pk=series_id)
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
        context['movies_list'] = Movie.objects.filter(actors__full_name__contains=self.object)
        context['series_list'] = Series.objects.filter(actors__full_name__contains=self.object)

        return context


class ActorDelete(UserPassesTestMixin, DeleteView):
    model = Actor
    template_name = "polls/movie/actor_delete.html"
    success_url = reverse_lazy('actors')

    def test_func(self):
        return self.request.user.is_superuser

    def handle_no_permission(self):
        return redirect('index')


class ActorCreate(UserPassesTestMixin, CreateView):
    model = Actor
    form_class = ActorForm
    template_name = "polls/movie/actor_create.html"

    def test_func(self):
        return self.request.user.is_authenticated

    def handle_no_permission(self):
        return redirect('login')


class ActorUpdate(UserPassesTestMixin, UpdateView):
    model = Actor
    template_name = "polls/movie/actor_create.html"
    form_class = ActorForm

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

    def test_func(self):
        return self.request.user.is_authenticated

    def handle_no_permission(self):
        return redirect('login')


class DirectorUpdate(UserPassesTestMixin, UpdateView):
    model = Director
    template_name = "polls/movie/director_create.html"
    form_class = DirectorForm

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
    print(response)
    only_item_cells = SoupStrainer("div", attrs={'id': 'search_resultsRows'})
    table = BeautifulSoup(response.content, 'lxml', parse_only=only_item_cells)
    print(table.prettify())
    games = table.find_all("a")
    for game in games:
        try:
            steam_ids.append(game['data-ds-appid'])
        except KeyError:
            pass
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

    for i in range(1, 45):
        steams_ids, end = scrape_steam_ids(i, start)
        if end:
            return render(request, "polls/Game/scrape_games.html", {'addedGames': added_games})

        for steam_app_id in steams_ids:
            if time() - start > 25:
                return render(request, "polls/Game/scrape_games.html", {'addedGames': added_games})
            if check_app_id(steam_app_id):
                continue
            url2 = "https://store.steampowered.com/api/appdetails?appids=" + str(steam_app_id)
            response2 = requests.get(url2)
            jsoned_data_from_response_app_details = response2.json()
            try:
                if not jsoned_data_from_response_app_details[str(steam_app_id)]['success']:
                    continue
            except TypeError:
                print("Type error dla ID:", steam_app_id)
                break
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
        for show in shows:
            if type_of_show == 'tv_series_browse':
                data = api.search_series(show)
            else:
                data = api.search_movie(show)
            if data:
                data = compare_titles(data)
                for record in data:
                    imdb_ids.append(record['imdb_id'])
    else:
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
    response = requests.get(url)
    only_item_cells = SoupStrainer("div", attrs={'class': 'discovery-tiles__wrap'})
    table = BeautifulSoup(response.content, 'lxml', parse_only=only_item_cells)
    shows_data = table.find_all("span", attrs={'class': 'p--small'})

    for show in shows_data:
        title = str(show.text.strip())
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
            exists_in_db = MovieSeriesGenre.objects.filter(name=genre.capitalize()).first()
            if exists_in_db:
                genres_pk_list.append(exists_in_db.pk)
            else:
                genre_instance = MovieSeriesGenre.objects.create(
                    name=genre.capitalize()
                )
                genres_pk_list.append(genre_instance.pk)

        languages = data['language'].split(', ')
        for language in languages:
            exists_in_db = Language.objects.filter(name=language.capitalize()).first()
            if exists_in_db:
                languages_pk_list.append(exists_in_db.pk)
            else:
                language_instance = Language.objects.create(
                    name=language.capitalize()
                )
                languages_pk_list.append(language_instance.pk)
        imdb_votes = data['imdb_votes']
        imdb_votes = int(imdb_votes.replace(',', ''))

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
                movie_object.imdb_votes = imdb_votes
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
                    imdb_rating=imdb_rating,
                    imdb_votes=imdb_votes
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
                series_object.imdb_votes = imdb_votes
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
                    imdb_votes=imdb_votes,
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

    update = ast.literal_eval(update)

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

    multi_search = ast.literal_eval(multi_search)
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
            genres = form.cleaned_data.get('genres')
            url = "https://www.rottentomatoes.com/browse/" + type_of_show

            if len(vods) != 0:
                url += "/affiliates:"
                for vod in vods:
                    url += vod + ','
                url = url[:-1]

            if len(genres) != 0:
                url += "~genres:"
                for genre in genres:
                    url += genre + ','
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
        print(url)

        response = requests.get(url)
        only_item_cells = SoupStrainer("div", attrs={'id': 'episodes_content'})
        table = BeautifulSoup(response.content, 'lxml', parse_only=only_item_cells)
        episodes_data = table.find_all("div", attrs={'class': 'image'})
        episodes_number = len(episodes_data)

        season_object, created = Season.objects.update_or_create(
            series=series,
            season_number=season,
            defaults={
                'series': series,
                'season_number': season,
                'number_of_episodes': episodes_number
            }
        )

        episode_number = 0
        for episode in episodes_data:
            episode_number += 1
            link = episode.a['href']
            episode_imdb_id = link.split("/")[2]
            if Episode.objects.filter(imdb_id=episode_imdb_id).exists():
                print(f"update {series} season {season} episode {episode_number}")
                episodes_to_update = episode_scraping(series, episode_imdb_id, season_object, months, api, 'update',
                                                      episodes_to_update, episode_number)
            else:
                print(f"create {series} season {season} episode {episode_number}")
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
        current_seasons_number = int(Season.objects.filter(series=pk).count())
        if current_seasons_number == 0:
            current_seasons_number = 1
        timeout = create_episodes(series, series_imdb_id, int(current_seasons_number), int(seasons_number), api, months,
                                  start)

    end = time()
    print(end - start)
    t = timeout
    e_s = end - start
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
    series_set = Series.objects.filter(Verified=True).order_by('-imdb_votes')

    for series in series_set.all():
        if series.episodes_update_date:
            days_difference = (today_date - series.episodes_update_date).days
            if days_difference >= 7:
                series_pks.append(series.pk)
        else:
            series_pks.append(series.pk)
    for series_pk in series_pks:
        print("Series pk:", series_pk)
        episodes_scraping(series_pk, api, start)
        print(time() - start)
        if time() - start > 25:
            print('timeout')
            return redirect('index')
    return redirect('index')


def episode_scraping(series, episode_imdb_id, season_object, months, api, action, episodes, episode_number):
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
        if poster == 'N/A':
            poster = series.poster
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

    episode = Episode.objects.filter(imdb_id=imdb_id).first()

    if action == 'update':
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

    return redirect('index')


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
                       'searched': searched,
                       'searched_books': searched_books})
    else:
        return render(request, 'polls/search_result.html')


class PostListView(UserPassesTestMixin, FormMixin, generic.ListView):
    template_name = "polls/Forum/post_list.html"
    model = Post
    form_class = PostForm
    paginate_by = 30

    def test_func(self):
        return self.request.user.is_authenticated

    def handle_no_permission(self):
        return redirect('login')

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        page_number = data['page_obj'].number
        pagi_by = PostListView.paginate_by
        category_slug = self.kwargs['slug_category']
        thread_slug = self.kwargs['slug']

        thread = Thread.objects.filter(slug=thread_slug).first()
        category = ForumCategory.objects.filter(slug=category_slug).first()

        thread.views += 1
        thread.save()

        posts = Post.objects.filter(thread=thread).order_by('date')

        posts_id = posts.values_list('id', flat=True)
        data['posts_id'] = posts_id
        data['posts'] = posts
        data['thread'] = thread
        data['category'] = category

        if self.request.user.is_authenticated:
            posts_liked = []
            profile = Profile.objects.filter(user_id=self.request.user.pk).first()
            data['post_form'] = PostForm(instance=self.request.user)

            paginator_posts = Paginator(posts, pagi_by)
            try:
                paginator_posts = paginator_posts.page(page_number)
            except PageNotAnInteger:
                paginator_posts = paginator_posts.page(page_number)
            except EmptyPage:
                paginator_posts = paginator_posts.page(paginator_posts.num_pages)

            for post in paginator_posts.object_list:
                if profile.post_like.filter(id=post.pk).exists():
                    posts_liked.append(True)
                else:
                    posts_liked.append(False)

            paginator_like = Paginator(posts_liked, pagi_by)
            try:
                pagi_like = paginator_like.page(page_number)
            except PageNotAnInteger:
                pagi_like = paginator_like.page(page_number)
            except EmptyPage:
                pagi_like = paginator_like.page(paginator_like.num_pages)

            print(posts_liked)
            data['posts'] = zip(pagi_like.object_list, paginator_posts.object_list)

        return data

    def get_queryset(self, *args, **kwargs):
        thread_slug = self.kwargs['slug']

        thread = Thread.objects.filter(slug=thread_slug).first()
        thread_pk = thread.pk

        return super().get_queryset(*args, **kwargs).filter(thread_id=thread_pk).order_by('-date')

    def form_view(self):
        return render(self.request, 'polls/Forum/post_list.html', {'form': PostListView()})

    def get_success_url(self, **kwargs):
        thread = Thread.objects.filter(slug=self.kwargs['slug']).first()
        posts = Post.objects.filter(thread=thread).order_by('date')
        pagi_num = Paginator(posts, self.paginate_by).num_pages

        return reverse('post-list', kwargs={'slug_category': self.kwargs['slug_category'],
                                            'slug': self.kwargs['slug']}) + '?page=' + str(pagi_num)

    def post(self, request, *args, **kwargs):
        if self.request.method == 'POST':
            form = self.get_form()
            if form.is_valid():
                return self.form_valid(form)
            else:
                return HttpResponseRedirect(reverse('post-list',
                                                    args=[kwargs['slug_category'],
                                                          kwargs['slug']]))

    def form_valid(self, form):
        thread_slug = self.kwargs['slug']
        thread = Thread.objects.filter(slug=thread_slug).first()

        new_post = Post(content=form.data['content'],
                        creator=self.request.user.profile,
                        thread=thread)
        new_post.save()
        thread.number_of_posts += 1
        thread.last_post_date = datetime.datetime.now()
        thread.views -= 1
        thread.save()
        return super(PostListView, self).form_valid(form)


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

    thread = Thread.objects.get(pk=thread_pk)
    thread.views -= 1
    thread.save()
    get_thread_object_slug = thread.slug
    get_thread_object_slug_category = Thread.objects.get(pk=thread_pk).slug_category

    return HttpResponseRedirect(reverse('post-list', args=[get_thread_object_slug_category, get_thread_object_slug]))


class ThreadUpdate(UserPassesTestMixin, UpdateView):
    model = Thread
    template_name = "polls/Forum/thread_update.html"
    fields = ['title']

    def test_func(self):
        return self.request.user.is_superuser

    def handle_no_permission(self):
        return redirect('index')

    def get_success_url(self):
        category_slug = self.kwargs['category_slug']
        thread = Thread.objects.get(pk=self.object.id)
        thread.views -= 1
        thread.save()
        thread_slug = thread.slug

        return reverse('post-list', kwargs={'slug_category': category_slug, 'slug': thread_slug})


def ThreadLike(request, pk):
    thread = get_object_or_404(Thread, id=request.POST.get('thread_id'))
    if thread.likes.filter(id=request.user.id).exists():
        thread.likes.remove(request.user.profile)
    else:
        thread.likes.add(request.user.profile)

    return HttpResponseRedirect(reverse('thread-detail', args=[str(thread.slug_category), str(thread.slug)]))


@stuff_or_superuser_required
def thread_active_unactive(request, pk):
    thread = get_object_or_404(Thread, id=pk)
    t = thread.is_thread_active
    if thread.is_thread_active:
        thread.is_thread_active = False
    else:
        thread.is_thread_active = True
    thread.save()

    return redirect('post-list', thread.slug_category, thread.slug)


class CategoryCreate(UserPassesTestMixin, CreateView):
    model = ForumCategory
    form_class = ThreadCategoryForm
    template_name = "polls/Forum/category_create.html"

    def test_func(self):
        return self.request.user.is_authenticated

    def handle_no_permission(self):
        return redirect('login')

    def form_valid(self, form):
        form.instance.creator = self.request.user.profile
        return super(CategoryCreate, self).form_valid(form)


class CategoryListView(UserPassesTestMixin, generic.ListView):
    template_name = "polls/Forum/category.html"
    model = ForumCategory
    paginate_by = 10

    def test_func(self):
        return self.request.user.is_authenticated

    def handle_no_permission(self):
        return redirect('login')

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)

        sessions = Session.objects.filter(expire_date__gte=timezone.now())
        users_list = []

        for session in sessions:
            data = session.get_decoded()
            users_list.append(data.get('_auth_user_id', None))

        last_posts = Post.objects.order_by('-id')[:3]

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
        data['last_posts'] = last_posts

        return data


class ThreadListView(UserPassesTestMixin, generic.ListView):
    template_name = "polls/Forum/thread_list.html"
    paginate_by = 20
    def test_func(self):
        return self.request.user.is_authenticated

    def handle_no_permission(self):
        return redirect('login')

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        category = ForumCategory.objects.filter(slug=self.kwargs['slug']).first()
        order_by = self.kwargs['order_by']
        context['order_by'] = order_by
        context['category'] = category
        context['sticky'] = Thread.objects.filter(category=category).first()
        return context

    def get_queryset(self):
        order_by = self.kwargs['order_by']
        category = ForumCategory.objects.filter(slug=self.kwargs['slug']).first()
        sticky = Thread.objects.filter(category=category).first()
        queryset = Thread.objects.filter(slug_category=self.kwargs['slug']).exclude(id=sticky.pk).order_by(order_by)
        return queryset


class TaggedThreadListView(generic.ListView):
    model = Thread
    paginate_by = 20
    template_name = "polls/Forum/tag_thread_list.html"
    def get_queryset(self):
        try:
            tag_id = Tag.objects.get(name=self.kwargs['tag']).pk
        except ObjectDoesNotExist:
            raise Http404

        threads_with_tag = Thread.objects.filter(tags=tag_id).order_by(self.kwargs['order_by'])

        return threads_with_tag

    def get_context_data(self, **kwargs):
        context = super(TaggedThreadListView, self).get_context_data(**kwargs)
        context['tag_name'] = Tag.objects.get(name=self.kwargs['tag']).name
        context['order_by'] = self.kwargs['order_by']
        return context


class ThreadCreate(UserPassesTestMixin, CreateView):
    model = Thread
    form_class = ThreadForm
    template_name = "polls/Forum/thread_create.html"

    """"
    def form_view(self, request, pk):
        if 'category_id' in request == "POST":
            category = get_object_or_404(ForumCategory, id=pk)
            saved_category = Thread(category=category)
            saved_category.save()
    
        return render(request, 'polls/Forum/thread_create.html', {'form': ThreadCreate()})
    """

    def form_valid(self, form):
        form.instance.creator = self.request.user.profile
        form.instance.category_id = self.kwargs['category_pk']
        return super().form_valid(form)

    def test_func(self):
        return self.request.user.is_authenticated

    def handle_no_permission(self):
        return redirect('login')

    def get_success_url(self):
        category_slug = ForumCategory.objects.get(pk=self.kwargs['category_pk']).slug
        thread_slug = Thread.objects.get(pk=self.object.id).slug
        return reverse('post-list', kwargs={'slug_category': category_slug, 'slug': thread_slug})


class ThreadCategoryUpdate(UserPassesTestMixin, UpdateView):
    model = ForumCategory
    template_name = "polls/Forum/category_update.html"
    fields = ['title', 'content']

    def test_func(self):
        return self.request.user.is_superuser

    def handle_no_permission(self):
        return redirect('index')


"""
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
"""


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
        thread = Thread.objects.get(pk=self.kwargs['thread_pk'])

        thread.views -= 1
        thread.save()

        get_thread_object_slug = thread.slug
        get_thread_object_slug_category = Thread.objects.get(pk=self.kwargs['thread_pk']).slug_category

        return reverse('post-list', kwargs={'slug_category': get_thread_object_slug_category,
                                            'slug': get_thread_object_slug})


class ThreadDelete(UserPassesTestMixin, DeleteView):
    model = Thread
    template_name = "polls/Forum/thread_delete.html"
    success_url = reverse_lazy('thread')
    login_url = reverse_lazy('index')

    def test_func(self):
        return self.request.user.is_superuser

    def handle_no_permission(self):
        return redirect('index')

    def form_valid(self, form):
        if self.object.creator is not None and self.request.user.is_superuser:
            delete_reason_content = form.data['delete_reason']
            basic_message_content = 'Your post was deleted from PCT'
            mail_notification(self.get_object(), basic_message_content, delete_reason_content, 'creator')
        messages.success(self.request, "The post has been deleted!")

        return super().form_valid(form)

    def get_success_url(self):
        category_slug = Thread.objects.get(id=self.object.pk).category.slug
        return reverse('thread-list', kwargs={'slug': category_slug, 'order_by': '-last_post_date'})


"""
class ThreadCategoryDelete(UserPassesTestMixin, DeleteView):
    model = ForumCategory
    template_name = "polls/Forum/category_delete.html"
    success_url = reverse_lazy('category')
    login_url = reverse_lazy('index')

    def test_func(self):
        return self.request.user.is_superuser

    def handle_no_permission(self):
        return redirect('index')
"""


class PostDelete(UserPassesTestMixin, DeleteView):
    model = Post
    template_name = "polls/Forum/post_delete.html"
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
            basic_message_content = 'Your post was deleted from PCT'
            mail_notification(self.get_object(), basic_message_content, delete_reason_content, 'creator')
        messages.success(self.request, "The post has been deleted!")

        thread = Thread.objects.get(pk=self.kwargs['thread_pk'])
        thread.number_of_posts -= 1
        thread.views -= 1
        thread.save()

        return super().form_valid(form)

    def get_success_url(self):
        get_thread_object_slug = Thread.objects.get(pk=self.kwargs['thread_pk']).slug
        get_thread_object_slug_category = Thread.objects.get(pk=self.kwargs['thread_pk']).slug_category
        return reverse('post-list',
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


def api_user_tweets():
    client = tweepy.Client(bearer_token=os.environ['TWITTER_API'])
    query = 'from:PopCultureTrack'
    tweets = client.search_recent_tweets(query=query, max_results=10, tweet_fields=['created_at', 'author_id'])
    return tweets


def tweet_save_to_db():
    original_tweets = api_user_tweets()
    for original_tweet in original_tweets.data:
        if not Tweet.objects.filter(tweet_id=original_tweet.id):
            new_tweet = Tweet(tweet_id=original_tweet.id,
                              author_id=original_tweet.author_id,
                              tweet_text=original_tweet.text,
                              published_date=original_tweet.created_at)
            new_tweet.save()


def tweet_list(request):
    # expand
    tweet_fetch(request)
    tweets = Tweet.objects.order_by('-published_date')[:10]

    return render(request, 'tweet_list.html', {'tweets': tweets})


def tweet_fetch(request):
    tweet_save_to_db()
    return redirect('tweet_list')


def terms(request):
    return render(request, 'help.html')

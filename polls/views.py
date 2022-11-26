import random
from datetime import datetime
from time import time, sleep

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
from django.http import HttpResponse, HttpResponseForbidden
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
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
from .models import Book, BookInstance
from .models import Game, Developer, Profile, GameGenre, GameMode, KnownSteamAppID
from .models import Movie, Series, Actor, Director, Language, MovieSeriesGenre, Season, Episode, MovieReview, \
    MovieWatchlist, SeriesWatchlist, SeriesReview, GameReview, GameList
from .token import account_activation_token
from django.views import View
# from .models import *
from friendship.models import Friend, Follow, Block, FriendshipRequest


class cbv_view(generic.ListView):
    model = Developer
    template_name = 'index.html'



# import time

from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

def handler(request, exception):
    context = {'domain': get_current_site(request)}
    return render(request, 'errorrr.html', context=context)


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
    except:
        return redirect('profile-page',pk)
    return redirect('request-list')
    #return redirect('profile-page',pk)


def reject_autocomplete_permission(request, pk):
    request_object = RequestPermission.objects.get(FromUser=pk)
    request_object.status = "Rejected"
    request_object.save(update_fields=['status'])
    return redirect('request-list')
    #return redirect('profile-page',pk)


class DeveloperAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        print("ELO")
        #permission_developer = Permission.objects.get(name='Can add developer')
        #permission_actor = Permission.objects.get(name='Can add actor')
        #permission_director = Permission.objects.get(name='Can add director')

       # self.request.user.user_permissions.add(permission)
        #test = self.request.user.has_perm('polls.add_developerr')
       # print(test)

        #new_group, created = Group.objects.get_or_create(name='new_group')
        #if created:
        #    permission_developer = Permission.objects.get(name='Can add developer')
        #    permission_actor = Permission.objects.get(name='Can add actor')
        #    permission_director = Permission.objects.get(name='Can add director')

       # new_group.permissions.add(permission_developer,permission_actor,permission_director)
      # new_group.user_set.add(self.request.user)
        # Don't forget to filter out results depending on the visitor !
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

import os
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


def signup(request):
    if request.user.is_authenticated:
        return redirect('index')
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():

            # save form in the memory not in database
            to_email = form.cleaned_data.get('email')
            check_username = form.cleaned_data.get('username')
            name_test = User.objects.filter(username__iexact=str(check_username)).exists()
            email_test = User.objects.filter(email__iexact=str(to_email)).exists()
            if name_test or email_test:
                messages.error(request, 'Your username or email is already taken.')
                return redirect('form')

            user = form.save(commit=False)
            user.is_active = False
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
            messages.success(request, 'Please confirm your email address to complete the registration!')
            return redirect('index')
            # return HttpResponse('Please confirm your email address to complete the registration')
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})


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
    User = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
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

    # Generate counts of the main objects
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()

    # Available books (status = 'a')
    num_instances_available = BookInstance.objects.filter(status__exact='a').count()

    # The 'all()' is implied by default.
    num_authors = Author.objects.count()

    # Number of visits to this view, as counted in the session variable.
    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits + 1

    context = {
        'num_books': num_books,
        'num_instances': num_instances,
        'num_instances_available': num_instances_available,
        'num_authors': num_authors,
        'num_visits': num_visits,
    }

    # Render the HTML template index.html with the data in the context variable.
    return render(request, 'index.html', context=context)


class BookListView(generic.ListView):
    model = Book
    paginate_by = 10


class BookDetailView(generic.DetailView):
    model = Book


class MyFavorites(generic.DetailView):
    model = Profile
    template_name = "polls/Profile/favorites.html"


# @method_decorator(login_required, name='dispatch')
class AuthorListView(generic.ListView):
    """Generic class-based list view for a list of authors."""
    model = Author
    paginate_by = 10


class AuthorDetailView(generic.DetailView):
    """Generic class-based detail view for an author."""
    model = Author


class LoanedBooksByUserListView(LoginRequiredMixin, generic.ListView):
    """Generic class-based view listing books on loan to current user."""
    model = BookInstance
    template_name = 'polls/bookinstance_list_borrowed_user.html'
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.filter(borrower=self.request.user).filter(status__exact='o').order_by('due_back')


class LoanedBooksAllListView(PermissionRequiredMixin, generic.ListView):
    """Generic class-based view listing all books on loan. Only visible to users with can_mark_returned permission."""
    model = BookInstance
    permission_required = 'catalog.can_mark_returned'
    template_name = 'polls/bookinstance_list_borrowed_all.html'
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.filter(status__exact='o').order_by('due_back')


class SignUpView(SuccessMessageMixin, generic.CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy("login")
    success_message = "Profileee was created successfully"

    template_name = "registration/signup.html"


def search(request):
    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():

            return HttpResponseRedirect('/thanks/')
    else:
        form = SearchForm()
    return render(request, 'polls/search_form_game.html', {'form': form})


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


def filter_by_mode(Queryset_to_fill,list_of_things, modes2):

    for game in list_of_things:
        qs = game.mode.values("id")
        test = game.date_of_release.year
        # print(qs)
        for queryset_with_id in qs:

            if str(queryset_with_id['id']) in modes2:
                query_to_add = Game.objects.filter(id=game.id)
                Queryset_to_fill = Queryset_to_fill | query_to_add
    return Queryset_to_fill


def filter_by_genre(model, list_of_things, genres):
    queryset_to_fill = model.objects.none()
    for object_model in list_of_things:
        qs = object_model.genre.values("id")
        for queryset_with_id in qs:

            if str(queryset_with_id['id']) in genres:
                query_to_add = model.objects.filter(id=object_model.id)
                queryset_to_fill = queryset_to_fill | query_to_add
    return queryset_to_fill


def filter_by_year(model, list_of_things, YearMin, YearMax):
    queryset_to_fill = model.objects.none()
    for object_model in list_of_things:

        if YearMin and YearMax:
            if int(YearMin) <= object_model.date_of_release.year <= int(YearMax):
                query_to_add = model.objects.filter(id=object_model.id)
                queryset_to_fill = queryset_to_fill | query_to_add
                continue
            continue

        if YearMin:
            if object_model.date_of_release.year >= int(YearMin):
                query_to_add = model.objects.filter(id=object_model.id)
                queryset_to_fill = queryset_to_fill | query_to_add
                continue
            continue

        if YearMax:
            if object_model.date_of_release.year <= int(YearMax):
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

def filter_by_in_production_series(model ,list_of_things, status):
    Queryset_to_fill = Series.objects.none()
    for serie in list_of_things:
        qs = serie.in_production
        test = status
        if qs == status:
            query_to_add = model.objects.filter(id=serie.id)
            Queryset_to_fill = Queryset_to_fill | query_to_add
    return Queryset_to_fill


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
            if in_production =="False":
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


def stuff_verification(request):
        #searched = request.POST['searched']
    games_to_verify = Game.objects.filter(Verified=False)
    movies_to_verify = Movie.objects.filter(Verified=False)
    series_to_verify = Series.objects.filter(Verified=False)
    actors_to_verify = Actor.objects.filter(Verified=False)
    directors_to_verify = Director.objects.filter(Verified=False)
    developers_to_verify = Developer.objects.filter(Verified=False)

    return render(request, 'polls/stuff_verification.html',
                      {'games_to_verify': games_to_verify,
                       'movies_to_verify': movies_to_verify,
                       'series_to_verify': series_to_verify,
                       'actors_to_verify': actors_to_verify,
                       'directors_to_verify': directors_to_verify,
                       'developers_to_verify': developers_to_verify})



def login_user(request):
    if request.user.is_authenticated:
        return redirect('index')
    # username = password = ''
    if request.POST:
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                messages.success(request, 'You logged in successfully!')
                return redirect('index')
        else:
            messages.error(request, 'Username or password is incorrect!')
    return render(request, 'registration/login2.html')


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


@login_required
@permission_required('catalog.can_mark_returned', raise_exception=True)
def renew_book_librarian(request, pk):
    """View function for renewing a specific BookInstance by librarian."""
    book_instance = get_object_or_404(BookInstance, pk=pk)

    # If this is a POST request then process the Form data
    if request.method == 'POST':

        # Create a form instance and populate it with data from the request (binding):
        form = RenewBookForm(request.POST)

        # Check if the form is valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required (here we just write it to the model due_back field)
            book_instance.due_back = form.cleaned_data['renewal_date']
            book_instance.save()

            # redirect to a new URL:
            return HttpResponseRedirect(reverse('all-borrowed'))

    # If this is a GET (or any other method) create the default form.
    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewBookForm(initial={'renewal_date': proposed_renewal_date})

    context = {
        'form': form,
        'book_instance': book_instance,
    }

    return render(request, 'polls/book_renew_librarian.html', context)


class AuthorCreate(CreateView):
    model = Author
    fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death']
    initial = {'date_of_death': '11/06/2020'}


class AuthorUpdate(UpdateView):
    model = Author
    fields = '__all__'  # Not recommended (potential security issue if more fields added)


class AuthorDelete(DeleteView):
    model = Author
    success_url = reverse_lazy('authors')


class BookCreate(CreateView):
    model = Book
    fields = ['title', 'author', 'summary', 'isbn', 'genre', 'language']
    template_name = "polls/book_form.html"


class BookUpdate(UpdateView):
    model = Book
    fields = ['title', 'author', 'summary', 'isbn', 'genre', 'language']


class BookDelete(DeleteView):
    model = Book
    success_url = reverse_lazy('books')


class GameCreate(CreateView):
    model = Game
    form_class = GameForm
    # fields = ['title', 'developer', 'date_of_release', 'genre', 'mode', 'summary',]
    # fields = ['title', 'developer', 'date_of_release', 'genre', 'mode', 'summary']
    template_name = "polls/Game/game_form.html"

    def form_valid(self, form):
        messages.success(self.request, "The game has been succesfully crated!")
        form.instance.added_by = self.request.user
        return super(GameCreate, self).form_valid(form)


class GameDetailView(generic.DetailView):
    """Generic class-based detail view for a game."""
    model = Game
    template_name = 'polls/Game/game_detail.html'

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

            context['user_review'] = GameReview.objects.filter(game_id=self.object).filter(
                author=self.request.user).first()
        context['game_reviews'] = GameReview.objects.filter(game_id=self.object)

        return context


class CreateGameReview(UserPassesTestMixin, CreateView):
    model = GameReview
    template_name = "polls/movie/review_create.html"
    form_class = GameReviewForm

    def test_func(self):
        return self.request.user.is_authenticated

    def handle_no_permission(self):
        return redirect('login')

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.game_id = self.kwargs['game_pk']
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('game-detail', kwargs={'pk': self.kwargs['game_pk']})

class UpdateGameReview(UserPassesTestMixin, UpdateView):
    model = GameReview
    template_name = "polls/movie/review_create.html"
    form_class = GameReviewForm

    def test_func(self):
        return self.request.user.is_authenticated

    def handle_no_permission(self):
        return redirect('login')

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.game_id = self.kwargs['game_pk']
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('game-detail', kwargs={'pk': self.kwargs['game_pk']})




def add_game_to_game_list(request, game_pk, user_pk, game_status):
    profile = Profile.objects.filter(user=user_pk).first()
    game = Game.objects.filter(pk=game_pk).first()
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        game_list_all = GameList.objects.filter(profile=self.object)
        game_list_games = GameList.objects.filter(profile=self.object).values_list('game', flat=True)

        game_reviews_all = []
        game_reviews_games = GameReview.objects.filter(author=self.request.user).values_list('game', flat=True)

        for game in game_list_games:
            if game in game_reviews_games:
                game_reviews_all.append(GameReview.objects.filter(
                    author=self.request.user).filter(game=game).first())
            else:
                game_reviews_all.append(False)

        reviews_and_games = zip(game_list_all, game_reviews_all)

        context['reviews_and_games'] = reviews_and_games

        return context


class GameReviewDetail(generic.DetailView):
    model = GameReview
    template_name = "polls/Game/game_review_detail.html"


def change_game_status(request, game_pk, profile_pk, status):
    game_list_object = GameList.objects.filter(game_id=game_pk).filter(profile_id=profile_pk).first()
    game_list_object.game_status = status
    game_list_object.save(update_fields=['game_status'])

    return HttpResponseRedirect(reverse('profile-game-list', args=[str(profile_pk)]))


class GameUpdate(UserPassesTestMixin, SuccessMessageMixin, UpdateView):
    model = Game
    template_name = "polls/Game/game_form.html"
    fields = ['title', 'developer', 'date_of_release', 'genre', 'mode', 'summary', 'Verified']
    success_message = 'The game has been successfully updated'

    def test_func(self):
        obj = self.get_object()
        if self.request.user.is_superuser:
            return True
        if obj.added_by == self.request.user and obj.Verified == False:
            return True
        return False

    def handle_no_permission(self):
        return redirect('index')


# success_url = reverse_lazy('games')
#  template_name = "polls/Game/game_confirm_delete.html"


class GameDelete(DeleteView):
    model = Game
    success_url = reverse_lazy('games')
    template_name = "polls/Game/game_confirm_delete.html"

    def test_func(self):
        obj = self.get_object()
        if self.request.user.is_superuser:
            return True
        if obj.added_by == self.request.user and obj.Verified == False:
            return True
        return False

    def form_valid(self, form):
        if self.object.added_by is not None:
            delete_reason_content = form.data['delete_reason']
            basic_message_content = 'Your game was deleted from PTC, title: ' + str(self.object)
            Mail_Notification(self.get_object(), basic_message_content, delete_reason_content)
        messages.success(self.request, "The game has been deleted!")
        return super().form_valid(form)

    def handle_no_permission(self):
        return redirect('index')


def Mail_Notification(object, basic_message_content, additional):
    user_email = object.added_by.email
    if additional:
        message_content = basic_message_content + "\n" + "Reason for removal: " + additional
    else:
        message_content = basic_message_content

    if not object.added_by.is_superuser:
        print("Wysłano maila")
        print(object.added_by)
        send_mail(
            'Delete notification from PTC ',
            message_content,
            'pct-team@outlook.com',
            [user_email],
            fail_silently=False,
        )


class GameListView(generic.ListView):
    model = Game
    paginate_by = 12
    template_name = "polls/Game/game_list.html"
    ordering = ["title"]


class GameVerify(UserPassesTestMixin, generic.DetailView):
    model = Game
    # login_url = '/polls/error401'
    # redirect_field_name = None

    template_name = "polls/Game/game_verify.html"
    success_url = reverse_lazy('games')

    def test_func(self):
        return self.request.user.is_superuser

    def handle_no_permission(self):
        return redirect('index')


class GameUnverify(UserPassesTestMixin, generic.DetailView):
    model = Game
    template_name = "polls/Game/game_unverify.html"
    success_url = reverse_lazy('games')

    def test_func(self):
        return self.request.user.is_superuser

    def handle_no_permission(self):
        return redirect('index')


class DeveloperDetailView(generic.DetailView):
    """Generic class-based detail view for a developer."""
    model = Developer
    template_name = 'polls/Game/developer_detail.html'


class DeveloperDelete(UserPassesTestMixin, DeleteView):
    model = Developer
    success_url = reverse_lazy('developers')
    template_name = "polls/Game/developer_confirm_delete.html"

    def test_func(self):
        return self.request.user.is_superuser

    def handle_no_permission(self):
        return redirect('index')


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

@login_required
def SendFriendshipRequest(request,pk):
    other_user = User.objects.get(id=pk)
    try:
        test = Friend.objects.sent_requests(user=request.user)
        Friend.objects.add_friend(
        request.user,  # The sender
        other_user,  # The recipient
        message='Hi! I would like to add you')  # This message is optional
        return redirect('profile-page',pk)
    except :
        return redirect('profile-page', pk)

@login_required
def AcceptFriendshipRequest(request,pk):
    try:
        other_user = User.objects.get(id=pk)
        friend_request = FriendshipRequest.objects.get(from_user=other_user, to_user=request.user)
        friend_request.accept()
        return redirect('profile-page', pk)
    except:
        return redirect('profile-page', pk)



@login_required
def RejectFriendshipRequest(request,pk):
    try:
        other_user = User.objects.get(id=pk)
        friend_request = FriendshipRequest.objects.get(from_user=other_user, to_user=request.user)
        friend_request.reject()
        friend_request.delete()
        return redirect('profile-page', pk)
    except:
        return redirect('profile-page', pk)

@login_required
def CancelFriendshipRequest(request,pk):
    try:
        other_user = User.objects.get(id=pk)
        friend_request = FriendshipRequest.objects.get(from_user=request.user, to_user=other_user)
        friend_request.cancel()
        return redirect('profile-page',pk)
    except FriendshipRequest.DoesNotExist:
        return redirect('profile-page', pk)

@login_required
def DeleteFriendship(request,pk):
    try:
        other_user = User.objects.get(id=pk)
        Friend.objects.remove_friend(request.user, other_user)
        return redirect('profile-page', pk)
    except:
        return redirect('profile-page', pk)




def FriendList(request,pk):
    get_user = User.objects.get(id=pk)
    friend_list = Friend.objects.friends(get_user)

    context = {
        'friend_list': friend_list
    }
    return render(request, 'FriendList.html', context=context)


def FriendRequestList(request,pk):
    get_user = User.objects.get(id=pk)
    friend_request_list = Friend.objects.unread_requests(get_user)

    context = {
        'friend_request_list': friend_request_list
    }

    return render(request, 'FriendRequestList.html', context=context)


class ProfilePageView(UserPassesTestMixin, generic.DetailView):
    model = Profile
    template_name = "polls/Profile/user_profile.html"

    def test_func(self):
        return self.request.user.is_authenticated

    def handle_no_permission(self):
        return redirect('index')

    def get_context_data(self, *args, **kwargs):
        # users = Profile.objects.all()
        context = super(ProfilePageView, self).get_context_data(*args, **kwargs)

        page_user = get_object_or_404(Profile, id=self.kwargs['pk'])
        request_status = get_object_or_404(Profile, id=self.kwargs['pk'])
        perm_request = RequestPermission.objects.filter(FromUser=self.kwargs['pk'])
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
            test3 = te2.from_user
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


def LikeView(request, pk):
    profile = get_object_or_404(Profile, id=request.POST.get('profile_id'))
    if profile.likes.filter(id=request.user.id).exists():
        profile.likes.remove(request.user)
    else:
        profile.likes.add(request.user)

    return HttpResponseRedirect(reverse('profile-page', args=[str(pk)]))


def AddVerf(request, pk):
    game = get_object_or_404(Game, id=pk)
    if game.Verified:
        game.Verified = False
        game.save(update_fields=['Verified'])
    else:
        game.Verified = True
        game.save(update_fields=['Verified'])
    return HttpResponseRedirect(reverse('game-detail', args=[str(pk)]))


def add_favorite_game(request, pk):
    game = get_object_or_404(Game, id=pk)
    if game in Profile.objects.get(id=request.user.id).favorite_games.filter(id=pk):
        Profile.objects.get(id=request.user.id).favorite_games.remove(game)
    else:
        Profile.objects.get(id=request.user.id).favorite_games.add(game)
    return HttpResponseRedirect(reverse('game-detail', args=[str(pk)]))


def add_favorite_movie(request, pk):
    movie = get_object_or_404(Movie, id=pk)
    if movie in Profile.objects.get(id=request.user.id).favorite_movies.filter(id=pk):
        Profile.objects.get(id=request.user.id).favorite_movies.remove(movie)
    else:
        Profile.objects.get(id=request.user.id).favorite_movies.add(movie)
    return HttpResponseRedirect(reverse('movie-detail', args=[str(pk)]))


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


class MovieDetailView(generic.DetailView):
    template_name = "polls/movie/movie_detail.html"
    model = Movie

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

            context['user_review'] = MovieReview.objects.filter(movie_id=self.object).filter(
                author=self.request.user).first()
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
            Mail_Notification(self.get_object(), basic_message_content, delete_reason_content)
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
        messages.success(self.request, "The movie has been succesfully created!")
        form.instance.added_by = self.request.user
        return super().form_valid(form)


class MovieUpdate(UserPassesTestMixin, UpdateView):
    model = Movie
    template_name = "polls/movie/movie_create.html"
    form_class = MovieForm

    # fields = ['title', 'actors', 'director', 'date_of_release', 'language', 'genre', 'running_time']

    def form_valid(self, form):
        messages.success(self.request, "The movie has been succesfully updated!")
        return super().form_valid(form)

    def test_func(self):
        return self.request.user.is_superuser

    def handle_no_permission(self):
        return redirect('index')


class MovieVerify(UserPassesTestMixin, generic.DetailView):
    model = Movie
    template_name = "polls/movie/movie_verify.html"

    # success_url = reverse_lazy('movies')

    def test_func(self):
        return self.request.user.is_superuser

    def handle_no_permission(self):
        return redirect('index')


def movie_verification(request, pk):
    movie_object = get_object_or_404(Movie, id=pk)
    if movie_object.Verified:
        movie_object.Verified = False
        movie_object.save(update_fields=['Verified'])
    else:
        movie_object.Verified = True
        movie_object.save(update_fields=['Verified'])
    return HttpResponseRedirect(reverse('movie-detail', args=[str(pk)]))


class MovieUnverify(UserPassesTestMixin, generic.DetailView):
    model = Movie
    template_name = "polls/movie/movie_unverify.html"

    # success_url = reverse_lazy('movies')

    def test_func(self):
        return self.request.user.is_superuser

    def handle_no_permission(self):
        return redirect('index')


class ProfileWatchlist(generic.DetailView):
    model = Profile
    template_name = "polls/Profile/movie_watchlist.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        movie_watchlist_all = MovieWatchlist.objects.filter(profile=self.object)
        movie_watchlist_movies = MovieWatchlist.objects.filter(profile=self.object).values_list('movie', flat=True)

        movie_reviews_all = []
        movie_reviews_movies = MovieReview.objects.filter(author=self.request.user).values_list('movie', flat=True)

        series_watchlist_all = SeriesWatchlist.objects.filter(profile=self.object)
        series_watchlist_series = SeriesWatchlist.objects.filter(profile=self.object).values_list('series', flat=True)

        series_reviews_all = []
        series_reviews_series = SeriesReview.objects.filter(author=self.request.user).values_list('series', flat=True)

        for movie in movie_watchlist_movies:
            if movie in movie_reviews_movies:
                movie_reviews_all.append(MovieReview.objects.filter(
                    author=self.request.user).filter(movie=movie).first())
            else:
                movie_reviews_all.append(False)

        for series in series_watchlist_series:
            if series in series_reviews_series:
                series_reviews_all.append(SeriesReview.objects.filter(
                    author=self.request.user).filter(series=series).first())
            else:
                series_reviews_all.append(False)

        reviews_and_movies = zip(movie_watchlist_all, movie_reviews_all)
        reviews_and_series = zip(series_watchlist_all, series_reviews_all)

        context['reviews_and_movies'] = reviews_and_movies
        context['reviews_and_series'] = reviews_and_series

        return context


class MovieReviewDetail(generic.DetailView):
    model = MovieReview
    template_name = "polls/movie/movie_review_detail.html"


def add_movie_to_watchlist(request, movie_pk, user_pk, movie_status):
    profile = Profile.objects.filter(user=user_pk).first()
    movie = Movie.objects.filter(pk=movie_pk).first()
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

    return HttpResponseRedirect(reverse('profile-watchlist', args=[str(profile_pk)]))


class CreateMovieReview(UserPassesTestMixin, CreateView):
    model = MovieReview
    template_name = "polls/movie/review_create.html"
    form_class = MovieReviewForm

    def test_func(self):
        return self.request.user.is_authenticated

    def handle_no_permission(self):
        return redirect('login')

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.movie_id = self.kwargs['movie_pk']
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('movie-detail', kwargs={'pk': self.kwargs['movie_pk']})


class UpdateMovieReview(UserPassesTestMixin, UpdateView):
    model = MovieReview
    template_name = "polls/movie/review_create.html"
    form_class = MovieReviewForm

    def test_func(self):
        return self.request.user.is_authenticated

    def handle_no_permission(self):
        return redirect('login')

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
    template_name = "polls/Profile/movie_watchlist.html"
    model = MovieWatchlist.objects.filter()
    paginate_by = 18



class SeriesListView(generic.ListView):
    template_name = "polls/movie/series_list.html"
    model = Series
    paginate_by = 18
    ordering = ["title"]


class SeriesDetailView(generic.DetailView):
    template_name = "polls/movie/series_detail.html"
    model = Series

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

            context['user_review'] = SeriesReview.objects.filter(series_id=self.object).filter(
                author=self.request.user).first()
        context['series_reviews'] = SeriesReview.objects.filter(series_id=self.object)

        return context


def add_series_to_watchlist(request, series_pk, user_pk, series_status):
    profile = Profile.objects.filter(user=user_pk).first()
    series = Series.objects.filter(pk=series_pk).first()
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
    template_name = "polls/movie/review_create.html"
    form_class = SeriesReviewForm

    def test_func(self):
        return self.request.user.is_authenticated

    def handle_no_permission(self):
        return redirect('login')

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.series_id = self.kwargs['series_pk']
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('series-detail', kwargs={'pk': self.kwargs['series_pk']})


class UpdateSeriesReview(UserPassesTestMixin, UpdateView):
    model = SeriesReview
    template_name = "polls/movie/review_create.html"
    form_class = SeriesReviewForm

    def test_func(self):
        return self.request.user.is_authenticated

    def handle_no_permission(self):
        return redirect('login')

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.series_id = self.kwargs['series_pk']
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('series-detail', kwargs={'pk': self.kwargs['series_pk']})


class UpdateSeriesProgress(UpdateView):
    model = SeriesWatchlist
    template_name = "polls/movie/series_progress_update.html"
    form_class = SeriesProgressForm

    def get_success_url(self):
        profile_pk = Profile.objects.filter(user=self.request.user.pk).first().pk
        return reverse('profile-watchlist', kwargs={'pk': profile_pk})


class UpdateSeriesStatus(UpdateView):
    model = SeriesWatchlist
    template_name = "polls/movie/series_progress_update.html"
    form_class = SeriesStatusForm

    def get_success_url(self):
        profile_pk = Profile.objects.filter(user=self.request.user.pk).first().pk
        return reverse('profile-watchlist', kwargs={'pk': profile_pk})


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
            basic_message_content = 'Your serie were deleted from PTC, title: ' + str(self.object)
            Mail_Notification(self.get_object(), basic_message_content, delete_reason_content)
        messages.success(self.request, "The serie has been deleted!")
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
        messages.success(self.request, "The serie has been succesfully created!")
        form.instance.added_by = self.request.user
        return super().form_valid(form)


class SeriesUpdate(UserPassesTestMixin, UpdateView):
    model = Series
    template_name = "polls/movie/series_create.html"
    form_class = SeriesForm

    # fields = ['title', 'actors', 'director', 'date_of_release', 'language', 'genre', 'running_time']

    def test_func(self):
        return self.request.user.is_superuser

    def form_valid(self, form):
        messages.success(self.request, "The serie has been succesfully updated!")
        return super().form_valid(form)

    def handle_no_permission(self):
        return redirect('index')


class SeriesVerify(UserPassesTestMixin, generic.DetailView):
    model = Series
    template_name = "polls/movie/series_verify.html"

    # success_url = reverse_lazy('series')

    def test_func(self):
        return self.request.user.is_superuser

    def handle_no_permission(self):
        return redirect('index')


def series_verification(request, pk):
    series_object = get_object_or_404(Series, id=pk)
    if series_object.Verified:
        series_object.Verified = False
        series_object.save(update_fields=['Verified'])
    else:
        series_object.Verified = True
        series_object.save(update_fields=['Verified'])
    return HttpResponseRedirect(reverse('series-detail', args=[str(pk)]))


class SeriesUnverify(UserPassesTestMixin, generic.DetailView):
    model = Series
    template_name = "polls/movie/series_unverify.html"

    # success_url = reverse_lazy('series')

    def test_func(self):
        return self.request.user.is_superuser

    def handle_no_permission(self):
        return redirect('index')


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


class ActorVerify(UserPassesTestMixin, generic.DetailView):
    model = Actor
    template_name = "polls/movie/actor_verify.html"

    # success_url = reverse_lazy('series')

    def test_func(self):
        return self.request.user.is_superuser

    def handle_no_permission(self):
        return redirect('index')


def actor_verification(request, pk):
    actor_object = get_object_or_404(Actor, id=pk)
    if actor_object.Verified:
        actor_object.Verified = False
        actor_object.save(update_fields=['Verified'])
    else:
        actor_object.Verified = True
        actor_object.save(update_fields=['Verified'])
    return HttpResponseRedirect(reverse('actor-detail', args=[str(pk)]))


class ActorUnverify(UserPassesTestMixin, generic.DetailView):
    model = Actor
    template_name = "polls/movie/actor_unverify.html"

    # success_url = reverse_lazy('series')

    def test_func(self):
        return self.request.user.is_superuser

    def handle_no_permission(self):
        return redirect('index')


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


class DirectorVerify(UserPassesTestMixin, generic.DetailView):
    model = Director
    template_name = "polls/movie/director_verify.html"

    # success_url = reverse_lazy('series')

    def test_func(self):
        return self.request.user.is_superuser

    def handle_no_permission(self):
        return redirect('index')


def director_verification(request, pk):
    director_object = get_object_or_404(Director, id=pk)
    if director_object.Verified:
        director_object.Verified = False
        director_object.save(update_fields=['Verified'])
    else:
        director_object.Verified = True
        director_object.save(update_fields=['Verified'])
    return HttpResponseRedirect(reverse('director-detail', args=[str(pk)]))


class DirectorUnverify(UserPassesTestMixin, generic.DetailView):
    model = Director
    template_name = "polls/movie/director_unverify.html"

    # success_url = reverse_lazy('series')

    def test_func(self):
        return self.request.user.is_superuser

    def handle_no_permission(self):
        return redirect('index')


class SeasonDetailView(generic.DetailView):
    model = Season
    template_name = "polls/Season/season_detail.html"


class EpisodeDetailView(generic.DetailView):
    model = Episode
    template_name = "polls/Episode/episode_detail.html"


@login_required
@permission_required('catalog.can_mark_returned', raise_exception=True)
def scrape_games_redirect(request):
    random_digit = random.randint(1, 3)
    context = {
        'randomD': random_digit,
    }
    return render(request, 'polls/Game/game_scraping_redirect.html', context=context)


@login_required
@permission_required('catalog.can_mark_returned', raise_exception=True)
def scrape_games(request):
    # times = []
    # counter = 0
    months_eng = {"Jan,": "01", "Feb,": "02", "Mar,": "03", "Apr,": "04", "May,": "05", "Jun,": "06", "Jul,": "07",
                  "Aug,": "08", "Sep,": "09", "Oct,": "10", "Nov,": "11", "Dec,": "12"}

    # months = {"January": "01", "February": "02", "March": "03", "April": "04", "May": "05", "June": "06",
    # "July": "07", "August": "08", "September": "09", "October": "10", "November": "11", "December": "12"}

    url = "https://api.steampowered.com/ISteamApps/GetAppList/v2/"
    response = requests.get(url)
    jsoned_data_from_response_get_app_list = response.json()
    added_games = 0
    error_counter = 0
    for dataa in jsoned_data_from_response_get_app_list['applist']['apps']:
        if added_games == 5:
            break
        steam_app_id = dataa['appid']
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
            error_counter += 1
            if error_counter == 15:
                break
            sleep(1)

            continue
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
                    game_summary = jsoned_data_from_response_app_details[str(steam_app_id)]['data']['short_description']
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
                    correct_date = split_date[2] + '-' + months_eng[split_date[1]] + '-' + split_date[0]
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

                print("Dodano gre i dane dla: ", game_name, added_games)
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


@login_required
@permission_required('catalog.can_mark_returned', raise_exception=True)
def omdb_api(request, url, multi_search, type_of_show, api_key):
    # omdb.set_default('apikey', apikey)

    api = omdb.OMDBClient(apikey=api_key)

    if multi_search == 'True':
        multi_search = True
    else:
        multi_search = False

    url = url.replace("\\", "/")
    scraping_time = time()
    times1 = []
    times2 = []
    months = {"Jan": "01", "Feb": "02", "Mar": "03", "Apr": "04", "May": "05", "Jun": "06", "Jul": "07",
              "Aug": "08", "Sep": "09", "Oct": "10", "Nov": "11", "Dec": "12"}
    created_shows = []
    updated_shows = []
    titles = []
    response = requests.get(url)
    only_item_cells = SoupStrainer("div", attrs={'class': 'discovery-tiles__wrap'})
    table = BeautifulSoup(response.content, 'lxml', parse_only=only_item_cells)
    movies_data = table.find_all("span", attrs={'class': 'p--small'})

    for movie in movies_data:
        title = str(movie.text.strip())
        titles.append(title)

    test = time()
    if multi_search:
        shows = get_imdb_id(titles, multi_search, type_of_show, api)
    else:
        shows = titles
    end = time()
    test = end - test
    # api = omdb.OMDBClient(apikey=apikey)

    for show in shows:
        start = time()
        actors_pk_list = []
        directors_pk_list = []
        genres_pk_list = []
        languages_pk_list = []
        # api = GetMovie(api_key=apikey)
        # data = api.get_movie(title=movie)
        if multi_search:
            data = api.imdbid(show)
        else:
            data = api.title(show)

        if not data:
            continue

        imdb_id = data['imdb_id']
        released = data['released']
        poster = data['poster']
        imdb_rating = data['imdb_rating']
        type_of_show = data['type']

        if not data or released == 'N/A' or poster == 'N/A' or imdb_rating == 'N/A':
            continue

        # imdb_id = data['imdbid']
        imdb_rating = float(imdb_rating)
        title = data['title']

        actors = data['actors'].split(', ')
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

        directors = data['director'].split(', ')
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
            movie_object, created = Movie.objects.update_or_create(
                imdb_id=imdb_id,
                defaults={
                    'title': title,
                    'date_of_release': release_date,
                    'running_time': int(runtime),
                    'summary': summary,
                    # 'type_of_show': type_of_show,
                    'poster': poster,
                    'Verified': True,
                    # 'added_by': User.objects.get(pk=1),
                    'imdb_rating': imdb_rating,
                    'imdb_id': imdb_id}
            )
            movie_object.director.set(directors_pk_list)
            movie_object.language.set(languages_pk_list)
            movie_object.genre.set(genres_pk_list)
            movie_object.actors.set(actors_pk_list)

            if created:
                created_shows.append(title)
                end = time()
                start = end - start
                times1.append(start)
            else:
                updated_shows.append(title)
                end = time()
                start = end - start
                times2.append(start)

        elif type_of_show == 'series':
            seasons = data['total_seasons']

            in_production = data['year'].split('–')

            if len(in_production) == 1:
                in_production = True
            else:
                if in_production[1] == '' or in_production[1] == '2022':
                    in_production = True
                else:
                    in_production = False

            if seasons == 'N/A':
                seasons = None

            series_object, created = Series.objects.update_or_create(
                imdb_id=imdb_id,
                defaults={
                    'title': title,
                    'date_of_release': release_date,
                    'number_of_seasons': seasons,
                    'summary': summary,
                    # 'type_of_show': type_of_show,
                    'poster': poster,
                    'Verified': True,
                    # 'added_by': User.objects.get(pk=1),
                    'imdb_rating': imdb_rating,
                    'imdb_id': imdb_id,
                    'in_production': in_production}
            )
            series_object.director.set(directors_pk_list)
            series_object.language.set(languages_pk_list)
            series_object.genre.set(genres_pk_list)
            series_object.actors.set(actors_pk_list)

            if created:
                created_shows.append(title)
                end = time()
                start = end - start
                times1.append(start)
            else:
                updated_shows.append(title)
                end = time()
                start = end - start
                times2.append(start)

    end = time()
    scraping_time = end - scraping_time
    created_shows = zip(created_shows, times1)
    updated_shows = zip(updated_shows, times2)

    context = {
        'scraping_time': scraping_time,
        'created_shows': created_shows,
        'updated_shows': updated_shows,
        'url': url,
        'test': test
    }

    return render(request, "polls/Scraping/scrape_movies.html", context=context)


@login_required
@permission_required('catalog.can_mark_returned', raise_exception=True)
def omdb_api_page(request):
    if request.method == 'POST':
        form = OmdbApiForm(request.POST)
        if form.is_valid():
            api_key = form.cleaned_data.get('api_key')
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
                                                                             'type_of_show': type_of_show,
                                                                             'api_key': api_key})
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


def create_episodes(series, series_imdb_id, start_seasons_number, end_seasons_number, api, months):
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

        for episode in episodes_data:
            link = episode.a['href']
            episode_imdb_id = link.split("/")[2]
            if Episode.objects.filter(imdb_id=episode_imdb_id).exists():
                episode_scraping(episode_imdb_id, season_object, months, api, 'update')
            else:
                episode_scraping(episode_imdb_id, season_object, months, api, 'create')


def update_episodes(series, seasons_number, api, months, series_in_production):
    if series_in_production:
        seasons = Season.objects.filter(series=series.pk).exclude(season_number=seasons_number)
    else:
        seasons = Season.objects.filter(series=series.pk)
    for season in seasons:
        episodes = Episode.objects.filter(season=season.pk)
        for episode in episodes:
            episode_scraping(episode.imdb_id, season, months, api, 'update')


def scrape_seasons_number(series_imdb_id):
    url = 'https://www.imdb.com/title/' + series_imdb_id + '/episodes'
    response = requests.get(url)
    only_item_cells = SoupStrainer("select", attrs={'id': 'bySeason'})
    html = BeautifulSoup(response.content, 'lxml', parse_only=only_item_cells)
    seasons_number = html.find("option", attrs={'selected': 'selected'}).text.strip()
    return seasons_number


@login_required
@permission_required('catalog.can_mark_returned', raise_exception=True)
def episode_ids_scraping(request, api_key, how_many_series, pk):
    start = time()
    api = omdb.OMDBClient(apikey=api_key)
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
                update_episodes(series, seasons_number, api, months, series.in_production)
            create_episodes(series, series_imdb_id, int(current_seasons_number), int(seasons_number), api, months)

        else:
            # UPDATE EPISODES
            seasons_number = series.number_of_seasons
            update_episodes(series, seasons_number, api, months, series.in_production)
    else:
        # CREATE EPISODES
        series_imdb_id = series.imdb_id
        seasons_number = scrape_seasons_number(series_imdb_id)
        Series.objects.filter(id=pk).update(number_of_seasons=seasons_number)
        create_episodes(series, series_imdb_id, 1, int(seasons_number), api, months)

    end = time()
    context = {
        'series': series,
        'time': end - start,
        'api_key': api_key
    }
    print(end - start)
    Series.objects.filter(id=pk).update(episodes_update_date=datetime.datetime.today().strftime('%Y-%m-%d'))

    if how_many_series == 'one':
        # return HttpResponseRedirect(reverse('series-detail', args=[str(pk)]))
        return redirect(reverse('series-to-scrape', kwargs={'api_key': api_key}))
    if how_many_series == 'all':
        return render(request, "polls/Scraping/episodes_scraping_redirect.html", context=context)


def episode_scraping(episode_imdb_id, season_object, months, api, action):
    # omdb.set_default('apikey', api_key)
    episode = api.imdbid(episode_imdb_id)
    if episode:
        title = episode['title']
        release_date = episode['released']

        if release_date == 'N/A':
            return 0

        release_date = release_date.split(' ')
        release_date = release_date[2] + '-' + months[release_date[1]] + '-' + release_date[0]

        episode_number = episode['episode']
        try:
            runtime = int(episode['runtime'].split(' ')[0])
        except ValueError:
            runtime = 0
        plot = episode['plot']

        imdb_rating = episode['imdb_rating']
        if imdb_rating == 'N/A':
            imdb_rating = None
        else:
            imdb_rating = float(episode['imdb_rating'])

        poster = episode['poster']
        imdb_id = episode['imdb_id']

        if action == 'update':
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
        elif action == 'create':
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
        # episode_object.series.set(id=season_object.pk)


def enter_api_key(request):
    if request.method == 'POST':
        form = EnterApiKey(request.POST)
        if form.is_valid():
            api_key = form.cleaned_data.get('api_key')
            return redirect(reverse('series-to-scrape', kwargs={'api_key': api_key}))
    else:
        form = EnterApiKey

    return render(request, 'polls/Scraping/enter_api_key.html', {'form': form})


def series_to_scrape(request, api_key):
    series_set = Series.objects.all().order_by('episodes_update_date')

    context = {
        'series_set': series_set,
        'api_key': api_key
    }

    return render(request, 'polls/Scraping/series_to_scrape.html', context=context)


def episode_scraping_in_progress(request, api_key, how_many_series, pk):
    series = get_object_or_404(Series, id=pk)

    context = {
        'api_key': api_key,
        'how_many_series': how_many_series,
        'pk': pk,
        'series': series
    }
    return render(request, 'polls/Scraping/episode_scraping_in_progress.html', context=context)


def create_record(request):
    context = {}
    return render(request, 'create_records.html', context=context)

from .models import RequestPermission


class RequestPermissionCreate(UserPassesTestMixin, CreateView):
    model = RequestPermission
    form_class = RequestPermissionForm
    template_name = "polls/Game/developer_form.html"
    success_url = reverse_lazy('index')

    def test_func(self):
        test = RequestPermission.objects.filter(FromUser=self.request.user.profile)
        print(test)

        if not test and self.request.user.is_authenticated:
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

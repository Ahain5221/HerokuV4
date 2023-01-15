import datetime  # for checking renewal date range.
from django import forms
from django.contrib.auth.forms import UserChangeForm, PasswordChangeForm, UserCreationForm
from django.contrib.auth.models import User
from dal import autocomplete
from captcha.fields import CaptchaField
from .models import RequestPermission
from .models import MovieReview, MovieWatchlist, SeriesWatchlist, SeriesReview, GameReview, Book, Author, BookReview
from .models import Game, Profile
from .models import Movie, Series, Actor, Director
from .models import ForumCategory, Post, Thread


class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=200, help_text='Required')
    captcha = CaptchaField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'captcha']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'custom-form-control'}),
            'password1': forms.TextInput(attrs={'class': 'custom-form-control'}),
            'password2': forms.TextInput(attrs={'class': 'custom-form-control'})
        }


class DateInput(forms.DateInput):
    input_type = 'date'


class SearchForm_User(forms.Form):
    searched = forms.CharField(label='Search for:', max_length=100, required=False)


class SearchForm(forms.Form):
    searched = forms.CharField(label='Game title', max_length=100, required=False)
    genres = forms.MultipleChoiceField(widget=autocomplete.Select2Multiple(url='game_genre-autocomplete'),
                                       required=False)
    modes = forms.MultipleChoiceField(widget=autocomplete.Select2Multiple(url='game_mode-autocomplete'), required=False)
    fromYear = forms.IntegerField(label="Min year", required=False, min_value=1900,
                                  max_value=datetime.datetime.now().year)
    toYear = forms.IntegerField(label="Max year", required=False, min_value=1900,
                                max_value=datetime.datetime.now().year)


class SearchForm_Movie(forms.Form):
    searched = forms.CharField(label='Movie title', max_length=100, required=False)
    genres = forms.MultipleChoiceField(widget=autocomplete.Select2Multiple(url='movie_series_genre-autocomplete'),
                                       required=False)
    fromYear = forms.IntegerField(label="Min year", required=False, min_value=1900,
                                  max_value=datetime.datetime.now().year)
    toYear = forms.IntegerField(label="Max year", required=False, min_value=1900,
                                max_value=datetime.datetime.now().year)
    running_time = forms.IntegerField(label="Minimum running time", required=False, min_value=0, max_value=654321)


class SearchForm_Series(forms.Form):
    searched = forms.CharField(label='Series title', max_length=100, required=False)
    genres = forms.MultipleChoiceField(widget=autocomplete.Select2Multiple(url='movie_series_genre-autocomplete'),
                                       required=False)
    in_production = forms.ChoiceField(label="Series status", choices=(("", ''), (False, 'Finished'), (True, 'Ongoing')),
                                      required=False)
    fromYear = forms.IntegerField(label="Min year", required=False, min_value=1900,
                                  max_value=datetime.datetime.now().year)
    toYear = forms.IntegerField(label="Max year", required=False, min_value=1900,
                                max_value=datetime.datetime.now().year)


class SearchForm_Book(forms.Form):
    searched = forms.CharField(label='Book title', max_length=100, required=False)
    genres = forms.MultipleChoiceField(widget=autocomplete.Select2Multiple(url='movie_series_genre-autocomplete'),
                                       required=False)
    isbn = forms.CharField(label='ISBN', max_length=13, required=False)


class EditUserForm(UserChangeForm):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'custom-form-control'}))
    first_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'custom-form-control'}))
    last_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'custom-form-control'}))
    username = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'custom-form-control'}))
    last_login = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'custom-form-control'}))
    date_joined = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'custom-form-control'}))

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password', 'last_login', 'date_joined')


class UserProfileEditForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('profile_image_url', 'date_of_birth', 'profile_description', 'signature', 'gender')
        widgets = {
            'profile_image_url': forms.TextInput(attrs={'class': 'custom-form-control'}),
            'date_of_birth': DateInput(
                attrs={'min': datetime.datetime.strptime('1 Jan 1900', '%d %b %Y').strftime("%Y-%m-%d"),
                       'max': datetime.datetime.now().strftime("%Y-%m-%d")}),
            'profile_description': forms.Textarea(attrs={'class': 'custom-form-control'}),
            'signature': forms.Textarea(attrs={'class': 'custom-form-control'}),
            'gender': forms.Select(attrs={'class': 'custom-form-control'})
        }


class GameForm(forms.ModelForm):
    class Meta:
        model = Game
        fields = ('title', 'developer', 'date_of_release', 'genre', 'mode', 'summary')
        widgets = {'title': forms.TextInput(attrs={'placeholder': 'Title'}),
                   'developer': autocomplete.ModelSelect2Multiple(url='developer-autocomplete'),
                   'date_of_release': DateInput(),
                   'genre': autocomplete.ModelSelect2Multiple(url='game_genre-autocomplete'),
                   'mode': autocomplete.ModelSelect2Multiple(url='game_mode-autocomplete'),
                   'summary': forms.Textarea(attrs={}),
                   }


class PasswordChangingForm(PasswordChangeForm):
    old_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'custom-form-control', 'type': 'password'}))
    new_password1 = forms.CharField(max_length=100,
                                    widget=forms.PasswordInput(
                                        attrs={'class': 'custom-form-control', 'type': 'password'}))
    new_password2 = forms.CharField(max_length=100,
                                    widget=forms.PasswordInput(
                                        attrs={'class': 'custom-form-control', 'type': 'password'}))

    class Meta:
        model = User
        fields = ('old_password', 'new_password1', 'new_password2')


class MovieForm(forms.ModelForm):
    class Meta:
        model = Movie
        fields = ('title', 'actors', 'director', 'date_of_release', 'language', 'genre', 'running_time', 'summary')
        widgets = {
            'title': forms.TextInput(attrs={'class': 'custom-form-control', 'placeholder': 'title'}),
            'actors': autocomplete.ModelSelect2Multiple(url='actor-autocomplete'),
            'director': autocomplete.ModelSelect2Multiple(url='director-autocomplete'),
            'date_of_release': DateInput(),
            'language': autocomplete.ModelSelect2Multiple(url='language-autocomplete'),
            'genre': autocomplete.ModelSelect2Multiple(url='movie_series_genre-autocomplete'),
            'running_time': forms.NumberInput(
                attrs={'class': 'custom-form-control', 'placeholder': 'Movie length in minutes'}),
            'summary': forms.Textarea(attrs={'class': 'custom-form-control', 'placeholder': 'Description'}),
        }


class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ('title', 'authors', 'summary', 'isbn', 'genre', 'languages')

        widgets = {
            'title': forms.TextInput(attrs={'class': 'custom-form-control', 'placeholder': 'title'}),
            'authors': autocomplete.ModelSelect2Multiple(url='author-autocomplete'),
            'languages': autocomplete.ModelSelect2Multiple(url='language-autocomplete'),
            'genre': autocomplete.ModelSelect2Multiple(url='movie_series_genre-autocomplete'),
            'summary': forms.Textarea(attrs={'class': 'custom-form-control', 'placeholder': 'Description'}),
        }


class AuthorForm(forms.ModelForm):
    class Meta:
        model = Author
        fields = ('first_last_name', 'date_of_birth', 'date_of_death')
        widgets = {
            'first_last_name': forms.TextInput(attrs={'class': 'custom-form-control', 'placeholder': 'first name'}),
            'date_of_birth': DateInput(),
            'date_of_death': DateInput(),
        }


class BookReviewForm(forms.ModelForm):
    class Meta:
        model = BookReview
        fields = ('content', 'rate')
        widgets = {
            'content': forms.Textarea(attrs={'class': 'form-control'}),
            'rate': forms.TextInput(attrs={'type': 'range', 'min': '0', 'max': '10', 'step': '1',
                                           'oninput': 'rangeValue.innerText = this.value'}),
        }


class MovieReviewForm(forms.ModelForm):
    class Meta:
        model = MovieReview
        fields = ('content', 'rate')
        widgets = {
            'content': forms.Textarea(attrs={'class': 'form-control'}),
            'rate': forms.TextInput(attrs={'type': 'range', 'min': '0', 'max': '10', 'step': '1',
                                           'oninput': 'rangeValue.innerText = this.value'}),
        }


class SeriesReviewForm(forms.ModelForm):
    class Meta:
        model = SeriesReview
        fields = ('content', 'rate')
        widgets = {
            'content': forms.Textarea(attrs={'class': 'form-control'}),
            'rate': forms.TextInput(attrs={'type': 'range', 'min': '0', 'max': '10', 'step': '1',
                                           'oninput': 'rangeValue.innerText = this.value'}),
        }


class GameReviewForm(forms.ModelForm):
    class Meta:
        model = GameReview
        fields = ('content', 'rate')
        widgets = {
            'content': forms.Textarea(attrs={'class': 'form-control'}),
            'rate': forms.TextInput(attrs={'type': 'range', 'min': '0', 'max': '10', 'step': '1',
                                           'oninput': 'rangeValue.innerText = this.value'}),
        }


class SeriesProgressStatusForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance', None)
        choices = instance.progress_method
        super(SeriesProgressStatusForm, self).__init__(*args, **kwargs)
        self.fields["progress"] = forms.ChoiceField(choices=choices)

    class Meta:
        model = SeriesWatchlist
        fields = ('progress', 'series_status')

        CHOICES = [
            ('watched', 'watched'),
            ('watching', 'watching'),
            ('want to watch', 'want to watch'),
            ('dropped', 'dropped')
        ]
        widgets = {
            'series_status': forms.Select(choices=CHOICES, attrs={'class': 'custom-form-control'}),
        }


class MovieWatchlistForm(forms.ModelForm):
    class Meta:
        CHOICES = [
            ('watched', 'watched'),
            ('want to watch', 'want to watch')
        ]

        model = MovieWatchlist
        # fields = '__all__'
        fields = ('movie_status',)
        widgets = {
            'movie_status': forms.Select(choices=CHOICES, attrs={'class': 'custom-form-control'}),
        }


class SeriesWatchlistForm(forms.ModelForm):
    class Meta:
        CHOICES = [
            ('watched', 'watched'),
            ('watching', 'watching'),
            ('want to watch', 'want to watch')
        ]

        model = SeriesWatchlist
        fields = ['series_status', ]

        widgets = {
            'series_status': forms.TextInput(attrs={'class': 'custom-form-control'})
        }


class SeriesForm(forms.ModelForm):
    class Meta:
        model = Series
        fields = ('title', 'actors', 'director', 'date_of_release', 'language', 'genre', 'number_of_seasons', 'summary')
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'title'}),
            'actors': autocomplete.ModelSelect2Multiple(url='actor-autocomplete'),
            'director': autocomplete.ModelSelect2Multiple(url='director-autocomplete'),
            'date_of_release': DateInput(),
            'language': autocomplete.ModelSelect2Multiple(url='language-autocomplete'),
            'genre': autocomplete.ModelSelect2Multiple(url='movie_series_genre-autocomplete'),
            'number_of_seasons': forms.NumberInput(
                attrs={'class': 'custom-form-control', 'placeholder': 'number of seasons'}),
            'summary': forms.Textarea(attrs={'class': 'custom-form-control', 'placeholder': 'Description'})
        }


class ActorForm(forms.ModelForm):
    class Meta:
        model = Actor
        fields = ('full_name', 'date_of_birth', 'date_of_death')
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'custom-form-control', 'placeholder': 'full name'}),
            'date_of_birth': DateInput(),
            'date_of_death': DateInput(),
        }


class DirectorForm(forms.ModelForm):
    class Meta:
        model = Director
        fields = ('full_name', 'date_of_birth', 'date_of_death')
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'custom-form-control', 'placeholder': 'full name'}),
            'date_of_birth': DateInput(),
            'date_of_death': DateInput(),
        }


class OmdbApiForm(forms.Form):
    type_CHOICES = (('tv_series_browse', 'Series'),
                    ('movies_at_home', 'Movie'))
    VOD_CHOICES = (('netflix', 'Netflix'),
                   ('amc_plus', 'AMC+'),
                   ('amazon_prime', 'Prime video'),
                   ('disney_plus', 'Disney+'),
                   ('hbo_max', 'HBO Max'),
                   ('apple_tv', 'Apple TV'),
                   ('apple_tv_plus', 'Apple TV+'),
                   ('hulu', 'Hulu'),
                   ('paramount_plus', 'Paramount+'),
                   ('peacock', 'Peacock'),
                   ('showtime', 'Showtime'),
                   ('vudu', 'Vudu'))

    genres_CHOICES = (('action', 'action'),
                      ('adventure', 'adventure'),
                      ('comedy', 'comedy'),
                      ('crime', 'crime'),
                      ('drama', 'drama'),
                      ('fantasy', 'fantasy'),
                      ('horror', 'horror'),
                      ('sci_fi', 'sci_fi'),
                      ('romance', 'romance'),
                      ('war', 'war'))

    critics_CHOICES = (('fresh', 'fresh'),
                       ('rotten', 'rotten'))
    sort_CHOICES = ((False, 'No sort'),
                    ('popular', 'Most popular'),
                    ('newest', 'Newest'),
                    ('a_z', 'Alphabetic'),
                    ('critic_highest', 'Critics highest'),
                    ('critic_lowest', 'Critics lowest'),
                    ('audience_highest', 'Audience highest'),
                    ('audience_lowest', 'Audience lowest'))
    audience_CHOICES = (('upright', 'fresh'),
                        ('spilled', 'rotten'))
    CHOICES = ((False, 'NO'),
               (True, 'YES'))

    type_of_show = forms.ChoiceField(choices=type_CHOICES)
    VOD = forms.MultipleChoiceField(required=False, choices=VOD_CHOICES, widget=forms.CheckboxSelectMultiple())
    genres = forms.MultipleChoiceField(required=False, choices=genres_CHOICES, widget=forms.CheckboxSelectMultiple())
    critics = forms.MultipleChoiceField(required=False, choices=critics_CHOICES, widget=forms.CheckboxSelectMultiple())
    audience = forms.MultipleChoiceField(required=False, choices=audience_CHOICES,
                                         widget=forms.CheckboxSelectMultiple())
    sort = forms.ChoiceField(choices=sort_CHOICES)
    pages = forms.IntegerField(min_value=1, required=False, help_text="One page contains up to 30 movies or series",
                               widget=forms.NumberInput(attrs={'class': 'custom-form-control'}))
    multi_search = forms.ChoiceField(required=True, choices=CHOICES, help_text='Search for similar titles')


class EnterApiKey(forms.Form):
    api_key = forms.CharField(widget=forms.TextInput())


class RequestPermissionForm(forms.ModelForm):
    class Meta:
        model = RequestPermission
        fields = ('Request_Reason',)
        widgets = {
            'Request_Reason': forms.Textarea(attrs={'class': 'custom-form-control'}),
        }


class ThreadForm(forms.ModelForm):
    class Meta:
        model = Thread
        fields = ('title', 'tags')
        widgets = {
            'title': forms.TextInput(attrs={'class': 'custom-form-control', 'placeholder': 'title'}),
        }


class ThreadCategoryForm(forms.ModelForm):
    class Meta:
        model = ForumCategory
        fields = ('title', 'content')
        widgets = {
            'title': forms.TextInput(attrs={'class': 'custom-form-control', 'placeholder': 'title'}),
            'content': forms.TextInput(attrs={'class': 'custom-form-control', 'placeholder': 'content'}),
        }


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['content']

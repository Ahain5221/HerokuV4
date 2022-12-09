import uuid  # Required for unique book instances
from datetime import date
from datetime import datetime, timezone, timedelta
from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse  # Used to generate URLs by reversing the URL patterns
from django.core.validators import MaxValueValidator, MinValueValidator
from isbn_field import ISBNField
# from tinymce.models import HTMLField
from django.shortcuts import get_object_or_404
from ckeditor.fields import RichTextField

# from django.shortcuts import get_object_or_404


# Create your models here.

class Genre(models.Model):
    name = models.CharField(max_length=200, help_text='Enter a book genre (e.g. Science Fiction)')

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Language(models.Model):
    name = models.CharField(max_length=200,
                            help_text="Enter the book's natural language (e.g. English, French, Japanese etc.)")

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class GameGenre(models.Model):
    name = models.CharField(max_length=200, help_text='Enter a game genre (e.g. Adventure)')
    Verified = models.BooleanField(default=False)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def class_name(self):
        return self.__class__.__name__


class GameMode(models.Model):
    name = models.CharField(max_length=200, help_text='Enter a game genre (e.g. SinglePlayer)')
    Verified = models.BooleanField(default=False)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Game(models.Model):
    added_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    title = models.CharField(max_length=200)
    developer = models.ManyToManyField('Developer', blank=True)
    # developer = models.ForeignKey('Developer', on_delete=models.SET_NULL, null=True)
    date_of_release = models.DateField(null=True, blank=True)
    # game_image = models.ImageField(null = True, blank=True, upload_to="images/")
    game_image = models.TextField(max_length=100, null=True, blank=True,
                                  default="https://pbs.twimg.com/profile_images/1510045751803404288/W-AAI2EH_400x400"
                                          ".jpg")
    genre = models.ManyToManyField(GameGenre, help_text='Select a genre for this game')
    mode = models.ManyToManyField(GameMode, help_text='Select which game mode is available')
    # language = models.ForeignKey('Language', on_delete=models.SET_NULL, null=True)
    summary = models.TextField(max_length=1000, help_text='Enter a brief description of the game')
    Verified = models.BooleanField(default=False)

    class Meta:
        ordering = ['title']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('game-detail', args=[str(self.id)])

    @property
    def users_rating(self):
        rate_sum = 0
        counter = 0
        reviews = GameReview.objects.filter(game=self.pk)
        for review in reviews:
            if review.rate:
                rate_sum += review.rate
                counter += 1
        try:
            users_rating = rate_sum / counter
        except ZeroDivisionError:
            users_rating = 'None'
        return users_rating


class Book(models.Model):
    title = models.CharField(max_length=200)
    authors = models.ManyToManyField('Author')

    summary = models.TextField(max_length=1000, help_text='Enter a brief description of the book')
    isbn = ISBNField('ISBN', unique=True,
                     help_text='13 Character <a href="https://www.isbn-international.org/content/what-isbn'
                               '">ISBN number</a>')
    genre = models.ManyToManyField('MovieSeriesGenre', help_text='Select a genre for this book')
    languages = models.ManyToManyField('Language')
    added_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    Verified = models.BooleanField(default=False)

    class Meta:
        ordering = ['title']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('book-detail', args=[str(self.id)])

    def display_genre(self):
        return ', '.join(genr.name for genr in self.genre.all()[:3])

    display_genre.short_description = 'Genre'

    @property
    def users_rating(self):
        rate_sum = 0
        counter = 0
        reviews = BookReview.objects.filter(book=self.pk)
        for review in reviews:
            if review.rate:
                rate_sum += review.rate
                counter += 1
        try:
            users_rating = rate_sum / counter
        except ZeroDivisionError:
            users_rating = 'None'
        return users_rating


class BookReview(models.Model):
    book = models.ForeignKey('Book', on_delete=models.CASCADE)
    content = models.TextField(max_length=1000)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    review_date = models.DateField(default=datetime.today().strftime('%Y-%m-%d'))
    rate = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(10)], null=True)


class BookList(models.Model):
    CHOICES = [
        ('read', 'read'),
        ('reading', 'reading'),
        ('want to read', 'want to read'),
        ('dropped', 'dropped')
    ]

    book = models.ForeignKey('Book', on_delete=models.CASCADE, default=None)
    book_status = models.CharField(max_length=12, choices=CHOICES)
    profile = models.ForeignKey('Profile', on_delete=models.CASCADE, default=None)


class Author(models.Model):
    first_last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField(null=True, blank=True)
    date_of_death = models.DateField('Died', null=True, blank=True)
    added_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    Verified = models.BooleanField(default=False)

    class Meta:
        ordering = ['first_last_name']

    def get_absolute_url(self):
        return reverse('author-detail', args=[str(self.id)])

    def __str__(self):
        return f'{self.first_last_name}'


class Developer(models.Model):
    company_name = models.CharField(max_length=100)
    date_of_foundation = models.DateField(null=True, blank=True)
    Verified = models.BooleanField(default=False)
    added_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    class Meta:
        ordering = ['company_name']

    def get_absolute_url(self):
        return reverse('developer-detail', args=[str(self.id)])

    def __str__(self):
        return f'{self.company_name}'


class Profile(models.Model):
    user = models.OneToOneField(User, null=True, on_delete=models.CASCADE)
    # profile_image = models.ImageField(null = True, blank=True, upload_to="images/")
    profile_image_url = models.TextField(null=True, blank=True, default="https://pbs.twimg.com/profile_images"
                                                                        "/1510045751803404288/W-AAI2EH_400x400.jpg")
    date_of_birth = models.DateField(null=True, blank=True)
    profile_description = models.TextField(null=True, blank=True, max_length=1000)
    signature = models.TextField(null=True, blank=True, max_length=250)
    likes = models.ManyToManyField(User, related_name="blog_posts")
    favorite_games = models.ManyToManyField('Game')
    favorite_movies = models.ManyToManyField('Movie')
    favorite_series = models.ManyToManyField('Series')
    favorite_books = models.ManyToManyField('Book')
    registration_completed = models.BooleanField(default=False)
    name = models.CharField(max_length=200, blank=True)

    # movie_watchlist = models.ForeignKey('MovieWatchlist', on_delete=models.CASCADE, null=True)
    # movie_watchlist = models.ManyToManyField('MovieWatchlist')

    def WhenJoined(self):
        return self.user.date_joined

    def LastSeen(self):
        return self.user.last_login

    def expired_registration_check(self):

        get_joined_date = self.user.date_joined
        elapsed_time = datetime.now(timezone.utc) - get_joined_date
        deadline = timedelta(days=7)
        if elapsed_time > deadline and not self.registration_completed:
            return True
        else:
            return False

    Genders = (
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Undefined', 'Undefined'),
    )

    gender = models.CharField(max_length=10, choices=Genders, default='Undefined')

    def get_absolute_url(self):
        return reverse('profile-page', args=[str(self.user.username)])

    def __str__(self):
        return str(self.user)

    @property
    def number_of_watched_movies(self):
        number = MovieWatchlist.objects.filter(profile=self.pk).filter(movie_status='watched').count()
        return number

    @property
    def number_of_want_to_watch_movies(self):
        number = MovieWatchlist.objects.filter(profile=self.pk).filter(movie_status='want to watch').count()
        return number

    @property
    def number_of_want_to_watch_series(self):
        number = SeriesWatchlist.objects.filter(profile=self.pk).filter(series_status='want to watch').count()
        return number

    @property
    def number_of_watching_series(self):
        number = SeriesWatchlist.objects.filter(profile=self.pk).filter(series_status='watching').count()
        return number

    @property
    def number_of_watched_series(self):
        number = SeriesWatchlist.objects.filter(profile=self.pk).filter(series_status='watched').count()
        return number

    @property
    def number_of_dropped_series(self):
        number = SeriesWatchlist.objects.filter(profile=self.pk).filter(series_status='dropped').count()
        return number

    @property
    def number_of_want_to_play_games(self):
        number = GameList.objects.filter(profile=self.pk).filter(game_status='want to play').count()
        return number

    @property
    def number_of_playing_games(self):
        number = GameList.objects.filter(profile=self.pk).filter(game_status='playing').count()
        return number

    @property
    def number_of_played_games(self):
        number = GameList.objects.filter(profile=self.pk).filter(game_status='played').count()
        return number

    @property
    def number_of_dropped_games(self):
        number = GameList.objects.filter(profile=self.pk).filter(game_status='dropped').count()
        return number

    @property
    def number_of_want_to_read_books(self):
        number = BookList.objects.filter(profile=self.pk).filter(book_status='want to read').count()
        return number

    @property
    def number_of_reading_books(self):
        number = BookList.objects.filter(profile=self.pk).filter(book_status='reading').count()
        return number

    @property
    def number_of_read_books(self):
        number = BookList.objects.filter(profile=self.pk).filter(book_status='read').count()
        return number

    @property
    def number_of_dropped_books(self):
        number = BookList.objects.filter(profile=self.pk).filter(book_status='dropped').count()
        return number


class Person(models.Model):
    full_name = models.CharField(max_length=100)
    date_of_birth = models.DateField(null=True, blank=True)
    date_of_death = models.DateField(null=True, blank=True)
    Verified = models.BooleanField(default=False)
    added_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    class Meta:
        abstract = True


class MovieSeriesBase(models.Model):
    title = models.CharField(max_length=100)
    language = models.ManyToManyField('Language')
    actors = models.ManyToManyField('Actor')
    director = models.ManyToManyField('Director')
    date_of_release = models.DateField()
    genre = models.ManyToManyField('MovieSeriesGenre')
    Verified = models.BooleanField(default=False)
    summary = models.TextField(max_length=1000, default="summary")
    poster = models.TextField(max_length=200,
                              default="https://pbs.twimg.com/profile_images/1510045751803404288/W-AAI2EH_400x400.jpg")
    added_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    imdb_rating = models.FloatField(default=None, null=True, blank=True)
    imdb_id = models.CharField(max_length=10, unique=True, null=True)

    CHOICES = [
        ('movie', 'movie'),
        ('series', 'series')
    ]
    type_of_show = models.CharField(max_length=6, choices=CHOICES)

    class Meta:
        abstract = True

    @property
    def users_rating(self):
        rate_sum = 0
        counter = 0
        reviews = MovieReview.objects.filter(movie=self.pk)
        for review in reviews:
            if review.rate:
                rate_sum += review.rate
                counter += 1
        try:
            users_rating = rate_sum / counter
        except ZeroDivisionError:
            users_rating = 'None'
        return users_rating


class Actor(Person):
    CHOICES = [
        ('actor', 'actor')
    ]
    specialisation = models.CharField(max_length=5, choices=CHOICES, default='actor')

    def get_absolute_url(self):
        return reverse('actor-detail', args=[str(self.id)])

    def __str__(self):
        return self.full_name


class Director(Person):
    CHOICES = [
        ('director', 'director')
    ]
    specialisation = models.CharField(max_length=8, choices=CHOICES, default='director')

    def get_absolute_url(self):
        return reverse('director-detail', args=[str(self.id)])

    def __str__(self):
        return self.full_name


class Movie(MovieSeriesBase):
    running_time = models.IntegerField()

    def get_absolute_url(self):
        return reverse('movie-detail', args=[str(self.id)])

    def __str__(self):
        return f"{self.title} ({self.date_of_release.year})"


class Series(MovieSeriesBase):
    number_of_seasons = models.CharField(max_length=100, null=True)
    episodes_update_date = models.DateField(null=True)
    in_production = models.BooleanField(default=True)

    def get_absolute_url(self):
        return reverse('series-detail', args=[str(self.id)])

    def __str__(self):
        return self.title


class MovieSeriesGenre(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def class_name(self):
        return self.__class__.__name__


class KnownSteamAppID(models.Model):
    id = models.IntegerField(primary_key=True)

    def __str__(self):
        return self.id


# class Favorite(models.Model):

#    user = models.ForeignKey('Profile', related_name='favorites',on_delete=models.SET_NULL, null=True)
#    game = models.ForeignKey('Game', related_name='favorites',on_delete=models.SET_NULL, null=True)


class Season(models.Model):
    series = models.ForeignKey('Series', on_delete=models.CASCADE)
    season_number = models.CharField(max_length=2)
    number_of_episodes = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.series.title} season {self.season_number}"


class Episode(models.Model):
    title = models.CharField(max_length=100)
    season = models.ForeignKey('Season', on_delete=models.CASCADE)
    release_date = models.DateField(null=True)
    episode_number = models.IntegerField(null=True)
    runtime = models.IntegerField(null=True)
    plot = models.TextField(max_length=1000, null=True)
    imdb_rating = models.FloatField(null=True, blank=True)
    poster = models.TextField(max_length=200,
                              default="https://pbs.twimg.com/profile_images/1510045751803404288/W-AAI2EH_400x400.jpg")
    imdb_id = models.CharField(max_length=10, unique=True, null=True)

    def __str__(self):
        return f"{self.title}"

    def get_absolute_url(self):
        return reverse('episode-detail', args=[str(self.id)])


class MovieWatchlist(models.Model):
    CHOICES = [
        ('watched', 'watched'),
        ('want to watch', 'want to watch')
    ]

    movie = models.ForeignKey('Movie', on_delete=models.CASCADE, default=None)
    movie_status = models.CharField(max_length=13, choices=CHOICES)
    profile = models.ForeignKey('Profile', on_delete=models.CASCADE, default=None)


class MovieReview(models.Model):
    movie = models.ForeignKey('Movie', on_delete=models.CASCADE)
    content = models.TextField(max_length=1000)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    review_date = models.DateField(default=datetime.today().strftime('%Y-%m-%d'))
    rate = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(10)], null=True)


class SeriesWatchlist(models.Model):
    CHOICES = [
        ('watched', 'watched'),
        ('watching', 'watching'),
        ('want to watch', 'want to watch'),
        ('dropped', 'dropped')
    ]

    series = models.ForeignKey('Series', on_delete=models.CASCADE, default=None)
    series_status = models.CharField(max_length=13, choices=CHOICES)
    profile = models.ForeignKey('Profile', on_delete=models.CASCADE, default=None)
    progress = models.CharField(max_length=6, blank=True, null=True)

    @property
    def progress_method(self):
        seasons = Season.objects.filter(series_id=self.series.pk)
        choices = []
        for season in seasons:
            season_number = season.season_number
            episodes = season.number_of_episodes
            for episode in range(1, episodes + 1):
                choices.append(
                    ('S' + str(season_number) + 'E' + str(episode), 'S' + str(season_number) + 'E' + str(episode)))

        return choices


class SeriesReview(models.Model):
    series = models.ForeignKey('Series', on_delete=models.CASCADE)
    content = models.TextField(max_length=1000)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    review_date = models.DateField(default=datetime.today().strftime('%Y-%m-%d'))
    rate = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(10)], null=True)


class GameList(models.Model):
    CHOICES = [
        ('played', 'played'),
        ('playing', 'playing'),
        ('want to play', 'want to play'),
        ('dropped', 'dropped')
    ]

    game = models.ForeignKey('Game', on_delete=models.CASCADE, default=None)
    game_status = models.CharField(max_length=12, choices=CHOICES)
    profile = models.ForeignKey('Profile', on_delete=models.CASCADE, default=None)


class GameReview(models.Model):
    game = models.ForeignKey('Game', on_delete=models.CASCADE)
    content = models.TextField(max_length=1000)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    review_date = models.DateField(default=datetime.today().strftime('%Y-%m-%d'))
    rate = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(10)], null=True)


class RequestPermission(models.Model):
    # FromUser = models.ForeignKey(Profile, on_delete=models.CASCADE, unique=True)
    FromUser = models.OneToOneField(Profile, on_delete=models.CASCADE)

    Request_Reason = models.TextField(max_length=1000)
    # status = models.BooleanField(default=False)

    Choice_Status = (
        ('Sent', 'Sent'),
        ('Accepted', 'Accepted'),
        ('Rejected', 'Rejected'),
        ('None', 'None'),
    )
    status = models.CharField(max_length=10, choices=Choice_Status, default='None')


class Forum(models.Model):
    title = models.CharField(max_length=400)
    creator = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True)
    content = models.TextField(blank=False, null=False)
    updated = models.DateTimeField(auto_now=True)
    date = models.DateTimeField(auto_now_add=True)
    Verified = models.BooleanField(default=False)

    def verified(self, *args, **kwargs):
        self.Verified = True
        self.save(update_fields=['Verified'])
        return self.Verified

    def unverified(self, *args, **kwargs):
        self.Verified = False
        self.save(update_fields=['Verified'])
        return self.Verified

    class Meta:
        abstract = True


class ForumCategory(Forum):

    class Meta:
        verbose_name_plural = "category"

    def __str__(self):
        return self.title

    def number_of_threads(self):
        return Thread.objects.filter(category=self).all().count()

    @property
    def number_of_posts(self):
        thread_object = Thread.objects.filter(category_id=self.pk)
        result = 0
        for thread in thread_object:
            pk_thread = thread.pk
            post = Post.objects.filter(thread_id=pk_thread).count()
            result += post
        return result

    def get_absolute_url(self):
        return reverse('thread-category-detail', args=[str(self.id)])


class Thread(Forum):
    category = models.ForeignKey(ForumCategory, on_delete=models.SET_NULL, related_name='categories', null=True)
    likes = models.ManyToManyField(Profile, related_name='thread_like')

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('thread-detail', args=[str(self.id)])

    def number_of_posts(self):
        return Post.objects.filter(thread=self).all().count()

    def number_of_likes(self):
        return self.likes.all().count()


LIKE_CHOICES = (
    ('Like', 'Like'),
    ('Unlike', 'Unlike')
)


class Post(Forum):
    thread = models.ForeignKey(Thread, on_delete=models.SET_NULL, related_name='posts', null=True)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')
    likes = models.ManyToManyField(Profile, related_name='post_like')
    content = RichTextField()

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('post-detail', args=[str(self.id)])

    def number_of_likes(self):
        return self.likes.all().count()


class Like(models.Model):
    creator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    thread = models.ForeignKey(Thread, on_delete=models.SET_NULL, null=True)
    value = models.CharField(choices=LIKE_CHOICES, default='Thread_Like', max_length=10)

    def __str__(self):
        return self.thread

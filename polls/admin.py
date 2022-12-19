from django.contrib import admin

from .models import Author, Genre, Book, Language, Director, Actor, Movie, Series, MovieSeriesGenre
from .models import GameGenre, GameMode, Developer, Game, Profile, KnownSteamAppID, RequestPermission
from .models import Season, Episode, MovieReview, MovieWatchlist, SeriesReview, SeriesWatchlist, GameReview, GameList
from .models import ForumCategory, Post
from .models import *
admin.site.register(MyCacheTable)
# admin.site.register(Author, AuthorAdmin)
admin.site.register(Book)
admin.site.register(Author)
# admin.site.register(BookInstance)
admin.site.register(Genre)
admin.site.register(GameGenre)
admin.site.register(GameMode)
admin.site.register(Developer)
admin.site.register(Language)
admin.site.register(Game)
admin.site.register(Profile)
admin.site.register(KnownSteamAppID)
admin.site.register(RequestPermission)



admin.site.register(Director)
admin.site.register(Actor)
admin.site.register(Movie)
admin.site.register(Series)
admin.site.register(MovieSeriesGenre)
admin.site.register(Season)
admin.site.register(Episode)
admin.site.register(MovieWatchlist)
admin.site.register(MovieReview)
admin.site.register(SeriesWatchlist)
admin.site.register(SeriesReview)
admin.site.register(GameList)
admin.site.register(GameReview)

admin.site.register(Post)
admin.site.register(ForumCategory)

class BooksInline(admin.TabularInline):
    """Defines format of inline book insertion (used in AuthorAdmin)"""
    model = Book



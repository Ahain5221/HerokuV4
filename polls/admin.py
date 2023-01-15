from django.contrib import admin
from .models import *

admin.site.register(MyCacheTable)
admin.site.register(Book)
admin.site.register(Author)
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
admin.site.register(Thread)
admin.site.register(ForumCategory)
admin.site.register(Tweet)


class BooksInline(admin.TabularInline):
    model = Book

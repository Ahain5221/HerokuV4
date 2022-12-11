from django.contrib.auth import views as auth_views
from django.urls import path, re_path
from django.urls import path, include

from . import views

from .views import *
from .models import GameGenre, GameMode, MovieSeriesGenre, Language

urlpatterns = [
    path('', views.index, name='index'),
    path("sections/<int:num>", views.news_sections, name="section"),

    path('sendmail', views.sendmail, name='send'),
    path('form/', views.signup, name='form'),
    path('activate/<slug:uidb64>/<slug:token>/', views.activate, name='activate'),
    path("password_reset", views.password_reset_request, name="password_reset_polls"),
    path('reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(template_name="registration/password_reset_confirm.html"),
         name='password_reset_confirm'),
    path('password_reset/done/',
         auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'),
         name='password_reset_done'),
    path('reset/done/',
         auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'),
         name='password_reset_complete'),
    path('logout', auth_views.LogoutView.as_view(), name='logout'),

    # re_path('activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/',
    #    views.activate, name='activate'),
    # path("sections/<int:num>", views.news_section, name="section"),
    # path("sections/<int:num>", views.newsSections(), name="section"),

    path('sendmail', views.sendmail, name='send'),
    path('activate/<slug:uidb64>/<slug:token>/', views.activate, name='activate'),

    # re_path('activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/',
    #    views.activate, name='activate'),
    path('authors/', views.AuthorListView.as_view(), name='authors'),
    path('author/<int:pk>', views.AuthorDetailView.as_view(), name='author-detail'),
    path('author/create/', views.AuthorCreate.as_view(), name='author-create'),
    path('author/<int:pk>/update/', views.AuthorUpdate.as_view(), name='author-update'),
    path('author/<int:pk>/delete/', views.AuthorDelete.as_view(), name='author-delete'),
    path('author_verification/<int:pk>', views.author_verification, name='author-verification'),

    path('books/', views.BookListView.as_view(), name='books'),
    path('book/<int:pk>', views.BookDetailView.as_view(), name='book-detail'),
    path('book/create/', views.BookCreate.as_view(), name='book-create'),
    path('book/<int:pk>/update/', views.BookUpdate.as_view(), name='book-update'),
    path('book/<int:pk>/delete/', views.BookDelete.as_view(), name='book-delete'),
    path('book_verification/<int:pk>', views.book_verification, name='book-verification'),
    path('book_verification_stuff/', views.book_verification_stuff_page, name='book-verification-stuff'),

    path("add_favorite_book/<int:pk>", add_favorite_book, name="add-favorite-book"),
    path('write_book_review/<int:book_pk>', views.CreateBookReview.as_view(), name='create-book-review'),
    path('book/<int:book_pk>/review/<int:pk>/update', views.UpdateBookReview.as_view(), name='book-review-update'),
    path('book/<book_pk>/review/<int:pk>/delete', views.BookReviewDelete.as_view(), name='book-review-delete'),
    path('add_book_to_book_list/<int:book_pk>/<int:user_pk>/<book_status>', views.add_book_to_book_list,
         name='add-book-to-book-list'),
    path('remove_book_from_book_list/<int:book_pk>/<int:user_pk>', views.remove_book_from_book_list,
         name='remove-book-from-book-list'),
    path('book_review/<int:pk>', views.BookReviewDetail.as_view(), name='book-review-detail'),
    path('change_book_status/<int:book_pk>/<int:profile_pk>/<status>', views.change_book_status,
         name='change-book-status'),

    # re_path(r'^developer-autocomplete/$', autocomplete.Select2QuerySetView.as_view(
    # model = Developer, model_field_name="company_name", create_field='company_name'), name='developer-autocomplete'),
    # re_path(r'^developer-autocomplete/$', autocomplete.Select2QuerySetView.as_view(
    # model = Developer, model_field_name="company_name", create_field='company_name'), name='developer-autocomplete'),

    # re_path(r'^developer-autocomplete/$', autocomplete.Select2QuerySetView.as_view(model = Developer, model_field_name="company_name", create_field='company_name'), name='developer-autocomplete'),

    # re_path(r'^developer-autocomplete/$', autocomplete.Select2QuerySetView.as_view(model = Developer, model_field_name="company_name", create_field='company_name'), name='developer-autocomplete'),
    re_path(r'^developer-autocomplete/$', DeveloperAutocomplete.as_view(create_field='company_name'),
            name='developer-autocomplete'),

    re_path(r'^game_genre-autocomplete/$', autocomplete.Select2QuerySetView.as_view(model=GameGenre,
                                                                                    model_field_name="name"),
            name='game_genre-autocomplete'),
    re_path(r'^game_mode-autocomplete/$',
            autocomplete.Select2QuerySetView.as_view(model=GameMode, model_field_name="name"),
            name='game_mode-autocomplete'),
    re_path(r'^movie_series_genre-autocomplete/$',
            autocomplete.Select2QuerySetView.as_view(model=MovieSeriesGenre, model_field_name="name"),
            name='movie_series_genre-autocomplete'),
    re_path(r'^language-autocomplete/$',
            autocomplete.Select2QuerySetView.as_view(model=Language, model_field_name="name"),
            name='language-autocomplete'),
    re_path(r'^actor-autocomplete/$', ActorAutocomplete.as_view(create_field='full_name'),
            name='actor-autocomplete'),
    re_path(r'^director-autocomplete/$', DirectorAutocomplete.as_view(create_field='full_name'),
            name='director-autocomplete'),
    re_path(r'^author-autocomplete/$', AuthorAutocomplete.as_view(create_field='first_last_name'),
            name='author-autocomplete'),
    path('signup2/', signup_view, name="signup2"),
    path('login/', login_user, name="login"),

    path('search_game/', views.search, name="search-game"),
    path('search_movie/', views.search_movie, name="search-movie"),

    path('search_series/', views.search_series, name="search-series"),
    path('search_user/', views.search_user, name="search-user"),
    path('search_book/', views.search_book, name="search-book"),

    path('search_general/', views.search_general, name="search-general"),

    path('search_result_games/', views.search_result_game, name="search-result-game"),
    path('search_result_movies/', views.search_result_movie, name="search-result-movie"),
    path('search_result_series/', views.search_result_series, name="search-result-series"),
    path('search_result_user/', views.search_result_user, name="search-result-user"),
    path('search_result_book/', views.search_result_book, name="search-result-book"),

    path('search_result_general/', views.search_result_general, name="search-result-general"),

    path('stuff_verification/', views.stuff_verification, name="stuff-verification"),

    path('signup/', views.signup, name='signup'),
    # path("signup/", SignUpView.as_view(), name="signup"), STARA REJESTRACJA. VIEW DO WYWALENIA?
    path("edit_user/", UserEditView.as_view(), name="edit_user"),
    path("testcbv", cbv_view.as_view(), name="cbv-view"),

    path("edit_profile/", UserProfileEditView.as_view(), name="edit_profile"),
    #re_path(r'^profile/username/(?P<slug>[\w.@+-]+)/$', ProfilePageView.as_view(), name="profile-page"),
    #re_path(r'^(?P<name>[\w-]+)/profile/$', ProfilePageView.as_view(), name="profile-page"),
    re_path(r'^profile/(?P<name>[\w-]+)/$(?i)', ProfilePageView.as_view(), name="profile-page"),

    #path("profile/<slug:name>", ProfilePageView.as_view(), name="profile-page"),
    #path("profile/<slug:name>/gosc", ProfilePageView_Gosc.as_view(), name="profile-page-gosc"),

    #path("profile/<slug:name>/my_favorites", MyFavorites.as_view(), name="my-favorites"),
    # re_path(r'^profile/(?P<name>[\w-]+)/my_favorites$(?i)', MyFavorites.as_view(), name="my-favorites"),

    #path("profile/<slug:name>/watchlist", ProfileWatchlist.as_view(), name="profile-watchlist"),
    # re_path(r'^profile/(?P<name>[\w-]+)/watchlist$(?i)',ProfileWatchlist.as_view(), name="profile-watchlist"),


    path("profile/<slug:name>/my_favorites/<type>", MyFavorites.as_view(), name="my-favorites"),
    path("profile/<slug:name>/watchlist/<type_of_show>/<status>", ProfileWatchlist.as_view(), name="profile-watchlist"),
    path("profile/<slug:name>/game_list/<status>", ProfileGameList.as_view(), name="profile-game-list"),
    path("profile/<slug:name>/book_list/<status>", ProfileBookList.as_view(), name="profile-book-list"),
    # path("profile/<slug:name>/game_list", ProfileGameList.as_view(), name="profile-game-list"),
    # re_path(r'^profile/(?P<name>[\w-]+)/game_list$(?i)', ProfileGameList.as_view(), name="profile-game-list"),
    # KOMENTARZ DLA DAWIDA

    path("like/<int:pk>", like_view, name="like_profile"),

    path("add_favorite_game/<int:pk>", add_favorite_game, name="add-favorite-game"),
    path("add_favorite_movie/<int:pk>", add_favorite_movie, name="add-favorite-movie"),
    path("add_favorite_series/<int:pk>", add_favorite_series, name="add-favorite-series"),

    path("profile/give-perm/<int:pk>", get_autocomplete_permission, name="get-autocomplete-permission"),
    path("profile/perm-rejected/<int:pk>", reject_autocomplete_permission, name="reject-autocomplete-permission"),

    path("addverf/<int:pk>", game_verification, name="add_verf"),
    path("addverf-stuff/", game_verification_stuff_page, name="add_verf_stuff"),

    # path('games/', views.GameListView.as_view(), name='games'),
    re_path(r'^games/$(?i)', views.GameListView.as_view(), name='games'),

    # path('game/<int:pk>', views.GameDetailView.as_view(), name='game-detail'),
    re_path(r'^game/(?P<pk>\d+)/$(?i)', views.GameDetailView.as_view(), name='game-detail'),

    #path('game/<int:pk>/update/', views.GameUpdate.as_view(), name='game-update'),
    re_path(r'^game/(?P<pk>\d+)/update/$(?i)', views.GameUpdate.as_view(), name='game-update'),

    #path('game/<int:pk>/delete/', views.GameDelete.as_view(), name='game-delete'),
    re_path(r'^game/(?P<pk>\d+)/delete/$(?i)', views.GameDelete.as_view(), name='game-delete'),

    path('game/create/', views.GameCreate.as_view(), name='game-create'),
    path('write_game_review/<int:game_pk>', views.CreateGameReview.as_view(), name='create-game-review'),
    path('game/<int:game_pk>/review/<int:pk>/update', views.UpdateGameReview.as_view(), name='game-review-update'),
    path('game/<game_pk>/review/<int:pk>/delete', views.GameReviewDelete.as_view(), name='game-review-delete'),
    path('add_game_to_game_list/<int:game_pk>/<int:user_pk>/<game_status>', views.add_game_to_game_list,
         name='add-game-to-game-list'),
    path('remove_game_from_game_list/<int:game_pk>/<int:user_pk>', views.remove_game_from_game_list,
         name='remove-game-from-game-list'),
    path('change_game_status/<int:game_pk>/<int:profile_pk>/<status>', views.change_game_status,
         name='change-game-status'),
    path('game_review/<int:pk>', views.GameReviewDetail.as_view(), name='game-review-detail'),

    path('developers/', views.DeveloperListView.as_view(), name='developers'),

    path('developer/<int:pk>', views.DeveloperDetailView.as_view(), name='developer-detail'),
    path('developer/<int:pk>/update', views.DeveloperUpdate.as_view(), name='developer-update'),

    path('developer/<int:pk>/delete', views.DeveloperDelete.as_view(), name='developer-delete'),
    path('developer/create/', views.DeveloperCreate.as_view(), name='developer-create'),
    path('developer_verification/<int:pk>', views.developer_verification, name='developer-verification'),

    path('password/', PasswordsChangeView.as_view(), name="change-password"),
    path('password_success', views.password_change_success, name="password_success"),

    # MOVIE
    path('movie/', views.MovieListView.as_view(), name='movies'),
    path('movie/<int:pk>', views.MovieDetailView.as_view(), name='movie-detail'),
    path('movie/<int:pk>/delete', views.MovieDelete.as_view(), name='movie-delete'),
    path('movie/create', views.MovieCreate.as_view(), name='movie-create'),
    path('movie/<int:pk>/update', views.MovieUpdate.as_view(), name='movie-update'),
    path('movie_verification/<int:pk>', views.movie_verification, name='movie-verification'),
    path('movie_verification_stuff/', views.movie_verification_stuff_page, name='movie-verification-stuff'),

    path('write_movie_review/<int:movie_pk>', views.CreateMovieReview.as_view(), name='create-movie-review'),
    path('movie/<int:movie_pk>/review/<int:pk>/update', views.UpdateMovieReview.as_view(), name='movie-review-update'),
    path('movie/<movie_pk>/review/<int:pk>/delete', views.MovieReviewDelete.as_view(), name='movie-review-delete'),
    path('add_movie_to_watchlist/<int:movie_pk>/<int:user_pk>/<movie_status>', views.add_movie_to_watchlist,
         name='add-movie-to-watchlist'),
    path('remove_movie_from_watchlist/<int:movie_pk>/<int:user_pk>', views.remove_movie_from_watchlist,
         name='remove-movie-from-watchlist'),
    path('movie_review/<int:pk>', views.MovieReviewDetail.as_view(), name='movie-review-detail'),
    path('movie_watched/<int:movie_pk>/<int:profile_pk>', views.movie_watched, name='movie-watched'),

    # SERIES
    path('series/', views.SeriesListView.as_view(), name='series'),
    path('series/<int:pk>', views.SeriesDetailView.as_view(), name='series-detail'),
    path('series/<int:pk>/delete', views.SeriesDelete.as_view(), name='series-delete'),
    path('series/create', views.SeriesCreate.as_view(), name='series-create'),
    path('series/<int:pk>/update', views.SeriesUpdate.as_view(), name='series-update'),
    path('series_verification/<int:pk>', views.series_verification, name='series-verification'),
    path('series_verification_stuff/', views.series_verification_stuff_page, name='series-verification-stuff'),

    path('add_series_to_watchlist/<int:series_pk>/<int:user_pk>/<series_status>', views.add_series_to_watchlist,
         name='add-series-to-watchlist'),
    path('remove_series_from_watchlist/<int:series_pk>/<int:user_pk>', views.remove_series_from_watchlist,
         name='remove-series-from-watchlist'),
    path('write_series_review/<int:series_pk>', views.CreateSeriesReview.as_view(), name='create-series-review'),
    path('series/<int:series_pk>/review/<int:pk>/update', views.UpdateSeriesReview.as_view(),
         name='series-review-update'),
    path('series_review/<int:pk>', views.SeriesReviewDetail.as_view(), name='series-review-detail'),
    path('series/<series_pk>/review/<int:pk>/delete', views.SeriesReviewDelete.as_view(), name='series-review-delete'),
    path('series_watchlist/<int:pk>/update', views.UpdateSeriesWatchlist.as_view(), name='series-watchlist-update'),
    # path('series/status/<int:pk>/update', views.UpdateSeriesStatus.as_view(), name='series-status-update'),
    path('add_series_to_watched/<int:series_pk>/<int:profile_pk>', views.add_series_to_watched,
         name='add-series-to-watched'),

    # SEASON
    path('season/<int:pk>', views.SeasonDetailView.as_view(), name='season-detail'),

    # EPISODE
    path('episode/<int:pk>', views.EpisodeDetailView.as_view(), name='episode-detail'),

    # SCRAPING Movies and Series
    path('omdb_api/<url>/<multi_search>/<type_of_show>', views.omdb_api, name='omdb-api'),
    path('omdb_api_page', views.omdb_api_page, name='omdb-api-page'),

    # SCRAPING EPISODES
    path('scrape_episodes_of_one_series/<int:pk>', views.series_episodes_scraping,
         name='scrape-episodes'),
    path('episodes_scarping_in_progress/<int:pk>', views.episode_scraping_in_progress,
         name='episodes-scraping-in-progress'),
    # path('scrape_episodes_of_all_series/<api_key>', views.enter_api_key, name='scrape-all-series'),
    path('seriesList', views.series_to_scrape, name='series-to-scrape'),
    # path('scrapeEpisodes', views.enter_api_key, name='enter-api-key'),
    path('scrape_movies/<type_of_show>/<update>', views.scraping_shows_script, name='scrape-shows-script'),
    path('scrape_episodes_script', views.episodes_scraping_script, name='scrape-episodes-script'),

    # ACTOR
    path('actor/', views.ActorListView.as_view(), name='actors'),
    path('actor/<int:pk>', views.ActorDetailView.as_view(), name='actor-detail'),
    path('actor/<int:pk>/delete', views.ActorDelete.as_view(), name='actor-delete'),
    path('actor/create', views.ActorCreate.as_view(), name='actor-create'),
    path('actor/<int:pk>/update', views.ActorUpdate.as_view(), name='actor-update'),
    path('actor_verification/<int:pk>', views.actor_verification, name='actor-verification'),

    # DIRECTOR
    path('director/', views.DirectorListView.as_view(), name='directors'),
    path('director/<int:pk>', views.DirectorDetailView.as_view(), name='director-detail'),
    path('director/<int:pk>/delete', views.DirectorDelete.as_view(), name='director-delete'),
    path('director/create', views.DirectorCreate.as_view(), name='director-create'),
    path('director/<int:pk>/update', views.DirectorUpdate.as_view(), name='director-update'),
    path('director_verification/<int:pk>', views.director_verification, name='director-verification'),

    path('scrapegames/', views.scrape_games, name='scrape-games'),
    path('scrapegames-start/', views.scrape_games_redirect, name='scrape-games-redirect'),

    path('genres/<model_name>/<int:pk>', views.games_series_movies_by_genre, name='genre-list'),

    path('create_records', views.create_record, name='create_record'),
    path('request/create', views.RequestPermissionCreate.as_view(), name='request-create'),
    path('request/list', views.RequestPermissionList.as_view(), name='request-list'),
    path("profile/friendship/add<int:pk>", send_friendship_request, name="add-friend"),
    path("profile/friendship/accept<int:pk>", accept_friendship_request, name="accept-friend"),
    path("profile/friendship/reject<int:pk>", reject_friendship_request, name="reject-friend"),
    path("profile/friendship/cancel<int:pk>", cancel_friendship_request, name="cancel-friend"),

    path("profile/friendship/delete/<int:pk>", delete_friendship, name="delete-friend"),
    path("profile/friendship/my_friends/<int:pk>", friend_list, name="friend-list"),
    path("profile/friendship/friend_requests/<int:pk>", friend_request_list, name="friend-request-list"),

    path("profile/root/management/<int:pk>", UserPageManagement.as_view(), name="user-page-management"),
    path("profile/root/management/delete_games/<int:pk>", delete_unverified_games, name="delete-unverified-games"),
    path("profile/root/management/delete_movies/<int:pk>", delete_unverified_movies, name="delete-unverified-movies"),
    path("profile/root/management/delete_series/<int:pk>", delete_unverified_series, name="delete-unverified-series"),

    path("profile/root/management/delete_all/<int:pk>", delete_unverified_all, name="delete-unverified-everything"),
    path("profile/root/management/delete_user/<int:pk>", delete_user, name="delete-user"),

    path('test/', views.test, name='test'),
    path('test1/', views.bulk_create, name='test1'),
    path('carnage/', delete_unverified_users, name='carnage'),

    path('forum/thread/', views.ThreadListView.as_view(), name='thread'),
    path('forum/thread/create/<int:category_pk>', views.ThreadCreate.as_view(), name='thread-create'),
    path('forum/thread/<int:pk>/delete', views.ThreadDelete.as_view(), name='thread-delete'),
    path('forum/thread/<int:pk>/update', views.ThreadUpdate.as_view(), name='thread-update'),
    path('thread-like/<int:pk>', views.ThreadLike, name="thread_like"),

    path('forum/', views.ThreadCategoryListView.as_view(), name='category'),
    path('forum/category/create', views.ThreadCategoryCreate.as_view(), name='category-create'),
    path('forum/category/<int:pk>/delete', views.ThreadCategoryDelete.as_view(), name='thread-category-delete'),
    path('forum/category/<int:pk>/update', views.ThreadCategoryUpdate.as_view(), name='category-update'),

    # Trzymać je na dole, bo narobią zamętu...
    path('forum/category/<slug:slug>', views.ThreadCategoryDetailView.as_view(), name='thread-category-detail'),
    path('forum/<slug:slug_category>/<slug:slug>', views.ThreadDetailView.as_view(), name='thread-detail'),


    # Ruszę to najwyżej jeśli będzie to miało jakikolwiek sens
    path('post/', views.PostListView.as_view(), name='post'),
    path('post/create', views.PostCreate.as_view(), name='post-create'),
    path('post/<int:pk>', views.PostDetailView.as_view(), name='post-detail'),
    # Te dwa niby trzeba ruszyć, eh.

    path('forum/post/update/<int:pk>/<thread_pk>', views.PostUpdate.as_view(), name='post-update'),
    path('forum/post/delete/<int:pk>/<thread_pk>', views.PostDelete.as_view(), name='post-delete'),

    path('add_books/', add_books, name='add-books'),
    path("postlike/<int:pk>/<int:thread_pk>", post_like_view, name="like_post")
]

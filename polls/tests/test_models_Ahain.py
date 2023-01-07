from django.test import TestCase
from polls.models import *
from django.contrib.auth import get_user_model
import datetime
from django.utils import timezone

# Tu trzeba dużo sprawdzić

class GameModelTestCase(TestCase):
    def setUp(self):
        Developer.objects.create(company_name='Dev1', Verified=True)
        Developer.objects.create(company_name='Dev2', Verified=True)
        GameGenre.objects.create(name='Action', Verified=True)
        GameGenre.objects.create(name='Adventure', Verified=True)
        GameMode.objects.create(name='Single Player', Verified=True)
        GameMode.objects.create(name='Multiplayer', Verified=True)

        self.game = Game.objects.create(
            title='Test Game',
            date_of_release='2022-01-01',
            summary='This is a test game'
        )
        self.game.developer.set(
            [Developer.objects.get(company_name='Dev1'), Developer.objects.get(company_name='Dev2')])
        self.game.genre.set([GameGenre.objects.get(name='Action'), GameGenre.objects.get(name='Adventure')])
        self.game.mode.set([GameMode.objects.get(name='Single Player'), GameMode.objects.get(name='Multiplayer')])

    def test_game_str(self):
        self.assertEqual(str(self.game), self.game.title)

    def test_game_absolute_url(self):
        self.assertEqual(self.game.get_absolute_url(), '/polls/game/' + str(self.game.id) + '/')

    def test_game_users_rating(self):
        self.assertEqual(self.game.users_rating, 'None')

    def test_author_verification_view_redirection(self):
        author = Author.objects.create(first_last_name='John Doe')
        response = self.client.get(reverse('author-verification', args=[str(author.id)]))

        self.assertRedirects(response, reverse('author-detail', args=[str(author.id)]))

    def test_author_verification_view_verified_field(self):
        author = Author.objects.create(first_last_name='John Doe', Verified=False)
        self.client.get(reverse('author-verification', args=[str(author.id)]))
        author.refresh_from_db()
        self.assertTrue(author.Verified)

    # def test_author_verification_view_404_handler(self):
    #    response = self.client.get(reverse('author-verification', args=['999999999']))


#
#    self.assertEqual(response.status_code, 200)

class GenreModelTestCase(TestCase):
    def test_string_representation(self):
        genre = Genre(name='Science Fiction')
        self.assertEqual(str(genre), genre.name)


class LanguageModelTestCase(TestCase):
    def test_string_representation(self):
        language = Language(name='English')
        self.assertEqual(str(language), language.name)


class GameGenreModelTestCase(TestCase):
    def test_string_representation(self):
        game_genre = GameGenre(name='Adventure')
        self.assertEqual(str(game_genre), game_genre.name)

    def test_class_name(self):
        game_genre = GameGenre(name='Adventure')
        self.assertEqual(game_genre.class_name(), 'GameGenre')


class BookReviewModelTestCase(TestCase):
    def setUp(self):
        user = User.objects.create(username='testuser')
        book = Book.objects.create(title='Test Book')
        self.review = BookReview.objects.create(book=book, content='Test review', author=user)

    def test_review_content(self):
        self.assertEqual(self.review.content, 'Test review')

    def test_review_author(self):
        self.assertEqual(self.review.author.username, 'testuser')

    def test_review_date(self):
        today = datetime.datetime.today().strftime('%Y-%m-%d')
        self.assertEqual(self.review.review_date, today)


class AuthorModelTestCase(TestCase):
    def setUp(self):
        user = User.objects.create(username='testuser')
        self.author = Author.objects.create(first_last_name='Test Author', added_by=user)

    def test_string_representation(self):
        self.assertEqual(str(self.author), self.author.first_last_name)

    def test_get_absolute_url(self):
        self.assertIsNotNone(self.author.get_absolute_url())


class DeveloperModelTestCase(TestCase):
    def setUp(self):
        user = User.objects.create(username='testuser')
        self.developer = Developer.objects.create(company_name='Test Developer', added_by=user)

    def test_string_representation(self):
        self.assertEqual(str(self.developer), self.developer.company_name)

    def test_get_absolute_url(self):
        self.assertIsNotNone(self.developer.get_absolute_url())


class ProfileModelTestCase(TestCase):
    def setUp(self):
        self.test_user = User.objects.create_user(
            username='testuser',
            password='testpass'
        )

        self.test_profile = Profile.objects.get(user=self.test_user)
        self.test_profile.date_of_birth = datetime.datetime.strptime('2000-01-01', '%Y-%m-%d').date(),
        self.test_profile.profile_description = 'This is a test profile'
        self.test_profile.signature = 'Test signature'
        self.test_profile.gender = 'Male'

    def test_profile_was_autocreated(self):
        self.assertEqual(str(self.test_profile), 'testuser')

    def test_profile_get_absolute_url(self):
        self.assertEqual(self.test_profile.get_absolute_url(), '/polls/profile/testuser/')

    def test_profile_when_joined(self):
        self.assertIsInstance(self.test_profile.WhenJoined(), datetime.datetime)

    def test_profile_last_seen(self):
        self.assertEqual(self.test_profile.LastSeen(), None)

    def test_profile_expired_registration_check(self):
        self.assertIsInstance(self.test_profile.expired_registration_check(), bool)


class ActorModelTestCase(TestCase):
    def setUp(self):
        self.actor = Actor.objects.create(
            full_name='John Smith',
            date_of_birth='1980-01-01',
            date_of_death='2022-01-01',
            Verified=True,
            specialisation='actor'
        )

    def test_string_representation(self):
        self.assertEqual(str(self.actor), self.actor.full_name)

    def test_verbose_name_plural(self):
        self.assertEqual(str(self.actor._meta.verbose_name_plural), 'actors')

    def test_specialisation_field(self):
        self.assertEqual(self.actor.specialisation, 'actor')

    def test_get_absolute_url(self):
        self.assertEqual(self.actor.get_absolute_url(), '/polls/actor/1')


class DirectorModelTestCase(TestCase):
    def setUp(self):
        self.director = Director.objects.create(
            full_name='John Smith',
            date_of_birth='1980-01-01',
            date_of_death='2022-01-01',
            Verified=True,
            specialisation='director',
        )

    def test_string_representation(self):
        self.assertEqual(str(self.director), self.director.full_name)

    def test_specialisation(self):
        self.assertEqual(self.director.specialisation, 'director')


class MovieModelTestCase(TestCase):
    def setUp(self):

        self.language = Language.objects.create(name='English')
        self.actor = Actor.objects.create(
            full_name='John Smith',
            date_of_birth=datetime.datetime.strptime('1980-01-01', '%Y-%m-%d').date(),
            date_of_death=datetime.datetime.strptime('2022-01-01', '%Y-%m-%d').date(),
            Verified=True,
        )
        self.director = Director.objects.create(
            full_name='Jane Doe',
            date_of_birth=datetime.datetime.strptime('1970-01-01', '%Y-%m-%d').date(),
            date_of_death=datetime.datetime.strptime('2022-01-01', '%Y-%m-%d').date(),
            Verified=True,
        )
        self.genre = MovieSeriesGenre.objects.create(name='Action')
        self.user1 = User.objects.create_user(
            username='user1', password='testpass1'
        )
        self.user2 = User.objects.create_user(
            username='user2', password='testpass2'
        )
        self.movie1 = Movie.objects.create(
            title='Test Movie1',
            date_of_release=datetime.datetime.strptime('2022-01-01', '%Y-%m-%d').date(),
            running_time=120,
            type_of_show='movie',
            added_by=self.user1,
            imdb_rating=8.0
        )

        self.movie2 = Movie.objects.create(
            title='Test Movie2',
            date_of_release=datetime.datetime.strptime('2022-01-01', '%Y-%m-%d').date(),
            running_time=125,
            type_of_show='movie',
            added_by=self.user2,
            imdb_rating=8.0
        )

        self.movie1.language.add(self.language)
        self.movie1.actors.add(self.actor)
        self.movie1.director.add(self.director)
        self.movie1.genre.add(self.genre)
        self.review1 = MovieReview.objects.create(
            movie=self.movie1,
            content='This is a great movie!',
            author=self.user1,
            rate=8
        )
        self.review2 = MovieReview.objects.create(
            movie=self.movie1,
            content='This movie was okay.',
            author=self.user2,
            rate=6
        )

    def test_string_representation(self):
        self.assertEqual(str(self.movie1), f"{self.movie1.title} ({self.movie1.date_of_release.year})")

    def test_users_rating(self):
        self.assertEqual(self.movie1.users_rating, 7.0)
        self.assertEqual(self.movie2.users_rating, 'None')


class SeriesModelTestCase(TestCase):
    def setUp(self):
        self.test_series = Series.objects.create(
            title='Test Series',
            number_of_seasons='1',
            date_of_release='2022-01-01',
            episodes_update_date='2022-01-01',
            in_production=True
        )

        self.test_season = Season.objects.create(
            series=self.test_series,
            season_number='1',
            number_of_episodes=10
        )

        self.test_episode = Episode.objects.create(
            title='Test Episode',
            season=self.test_season,
            release_date='2022-01-01',
            episode_number=1,
            runtime=60,
            plot='This is a test episode',
            imdb_rating=7.5,
            imdb_id='tt1234567'
        )

    def test_series_str(self):
        self.assertEqual(str(self.test_series), 'Test Series')

    def test_series_get_absolute_url(self):
        self.assertEqual(self.test_series.get_absolute_url(), '/polls/series/1')

    def test_season_str(self):
        self.assertEqual(str(self.test_season), 'Test Series season 1')

    def test_episode_str(self):
        self.assertEqual(str(self.test_episode), 'Test Episode')

    def test_episode_get_absolute_url(self):
        self.assertEqual(self.test_episode.get_absolute_url(), '/polls/episode/1')


class ThreadModelTestCase(TestCase):
    def setUp(self):
        self.category = ForumCategory.objects.create(
            title='Test Category'
        )

        self.user = User.objects.create(
            username='testuser',
            password='testpass'
        )
        self.user2 = User.objects.create(
            username='testuser2',
            password='testpass2'
        )
        self.profile = Profile.objects.get(name=self.user)
        self.profile.registration_completed = False
        self.thread = Thread.objects.create(
            title='Test Thread',
            category=self.category,
            slug='test-thread',
            views=0,
            number_of_posts=0,
            slug_category='test-category'
        )
        self.thread.likes.add(self.profile)



    def test_thread_str(self):
        self.assertEqual(str(self.thread), 'Test Thread')

    def test_thread_get_absolute_url(self):
        self.assertEqual(self.thread.get_absolute_url(), '/polls/forum/category/test-category/test-thread-1')

    def test_thread_number_of_likes(self):
        self.assertEqual(self.thread.number_of_likes(), 1)

    def test_thread_get_last_post(self):
        # User never logged in
        self.assertIsNone(self.thread.get_last_post)

    def test_expired_registration_check_with_expired_registration(self):
        # Set the registration date 8 days back
        self.profile.user.date_joined = timezone.now() - datetime.timedelta(days=8)
        self.assertTrue(self.profile.expired_registration_check())

    def test_expired_registration_check_with_non_expired_registration(self):
        # Set the registration date 6 days back
        self.profile.user.date_joined = timezone.now() - datetime.timedelta(days=6)
        self.assertFalse(self.profile.expired_registration_check())

    def test_expired_registration_check_with_completed_registration(self):
        # Set registration date to 8 days back and mark user registration as completed
        self.profile.user.date_joined = timezone.now() - datetime.timedelta(days=8)
        self.profile.registration_completed = True
        self.assertFalse(self.profile.expired_registration_check())

    def test_number_of_threads(self):
        # Earlier another thread was prepared, together checks if there are 2 of them
        Thread.objects.create(title='Test Thread 2', category=self.category)
        self.assertEqual(self.category.number_of_threads(), 2)

    def test_get_last_post(self):
        category = ForumCategory.objects.create(title='Test Category 2')
        thread = Thread.objects.create(title='Test Thread 3', category=category)
        Post.objects.create(thread=thread, date=datetime.datetime.strptime('2022-01-01', '%Y-%m-%d').date())
        last_post = Post.objects.create(thread=thread, date=datetime.datetime.strptime('2022-01-02', '%Y-%m-%d').date())

        self.assertEqual(category.get_last_post, last_post)

    def test_like_increments_post_likes_number(self):
        self.post = Post.objects.create(title='Test Post',
                                        content="Test content",
                                        creator=self.user.profile, thread=self.thread)
        self.post.likes.add(self.profile)
        self.post.likes.add(self.user2.profile)
        self.post.save()
        self.assertEqual(self.post.number_of_likes(), 2)







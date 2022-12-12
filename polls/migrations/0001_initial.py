# Generated by Django 4.1.4 on 2022-12-12 20:41

import ckeditor.fields
from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import isbn_field.fields
import isbn_field.validators
import taggit.managers


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('taggit', '0005_auto_20220424_2025'),
    ]

    operations = [
        migrations.CreateModel(
            name='Actor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('full_name', models.CharField(max_length=100)),
                ('date_of_birth', models.DateField(blank=True, null=True)),
                ('date_of_death', models.DateField(blank=True, null=True)),
                ('Verified', models.BooleanField(default=False)),
                ('specialisation', models.CharField(choices=[('actor', 'actor')], default='actor', max_length=5)),
                ('added_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Author',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_last_name', models.CharField(max_length=100)),
                ('date_of_birth', models.DateField(blank=True, null=True)),
                ('date_of_death', models.DateField(blank=True, null=True, verbose_name='Died')),
                ('Verified', models.BooleanField(default=False)),
                ('added_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['first_last_name'],
            },
        ),
        migrations.CreateModel(
            name='Book',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('book_image', models.TextField(blank=True, default='https://pbs.twimg.com/profile_images/1510045751803404288/W-AAI2EH_400x400.jpg', max_length=100, null=True)),
                ('summary', models.TextField(help_text='Enter a brief description of the book', max_length=2000)),
                ('isbn', isbn_field.fields.ISBNField(help_text='13 Character <a href="https://www.isbn-international.org/content/what-isbn">ISBN number</a>', max_length=28, unique=True, validators=[isbn_field.validators.ISBNValidator], verbose_name='ISBN')),
                ('Verified', models.BooleanField(default=False)),
                ('added_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('authors', models.ManyToManyField(to='polls.author')),
            ],
            options={
                'ordering': ['title'],
            },
        ),
        migrations.CreateModel(
            name='Developer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('company_name', models.CharField(max_length=100)),
                ('date_of_foundation', models.DateField(blank=True, null=True)),
                ('Verified', models.BooleanField(default=False)),
                ('added_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['company_name'],
            },
        ),
        migrations.CreateModel(
            name='Director',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('full_name', models.CharField(max_length=100)),
                ('date_of_birth', models.DateField(blank=True, null=True)),
                ('date_of_death', models.DateField(blank=True, null=True)),
                ('Verified', models.BooleanField(default=False)),
                ('specialisation', models.CharField(choices=[('director', 'director')], default='director', max_length=8)),
                ('added_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ForumCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=400)),
                ('content', models.TextField()),
                ('updated', models.DateTimeField(auto_now=True)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('Verified', models.BooleanField(default=False)),
                ('slug', models.SlugField(null=True, unique=True)),
            ],
            options={
                'verbose_name_plural': 'category',
            },
        ),
        migrations.CreateModel(
            name='Game',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('date_of_release', models.DateField(blank=True, null=True)),
                ('game_image', models.TextField(blank=True, default='https://pbs.twimg.com/profile_images/1510045751803404288/W-AAI2EH_400x400.jpg', max_length=100, null=True)),
                ('summary', models.TextField(help_text='Enter a brief description of the game', max_length=1000)),
                ('Verified', models.BooleanField(default=False)),
                ('added_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('developer', models.ManyToManyField(blank=True, to='polls.developer')),
            ],
            options={
                'ordering': ['title'],
            },
        ),
        migrations.CreateModel(
            name='GameGenre',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Enter a game genre (e.g. Adventure)', max_length=200)),
                ('Verified', models.BooleanField(default=False)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='GameMode',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Enter a game genre (e.g. SinglePlayer)', max_length=200)),
                ('Verified', models.BooleanField(default=False)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Genre',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Enter a book genre (e.g. Science Fiction)', max_length=200)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='KnownSteamAppID',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
            ],
        ),
        migrations.CreateModel(
            name='Language',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text="Enter the book's natural language (e.g. English, French, Japanese etc.)", max_length=200)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Movie',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('date_of_release', models.DateField()),
                ('Verified', models.BooleanField(default=False)),
                ('summary', models.TextField(default='summary', max_length=1000)),
                ('poster', models.TextField(default='https://pbs.twimg.com/profile_images/1510045751803404288/W-AAI2EH_400x400.jpg', max_length=200)),
                ('imdb_rating', models.FloatField(blank=True, default=None, null=True)),
                ('imdb_id', models.CharField(max_length=10, null=True, unique=True)),
                ('type_of_show', models.CharField(choices=[('movie', 'movie'), ('series', 'series')], max_length=6)),
                ('running_time', models.IntegerField()),
                ('actors', models.ManyToManyField(to='polls.actor')),
                ('added_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('director', models.ManyToManyField(to='polls.director')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='MovieSeriesGenre',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('profile_image_url', models.TextField(blank=True, default='https://pbs.twimg.com/profile_images/1510045751803404288/W-AAI2EH_400x400.jpg', null=True)),
                ('date_of_birth', models.DateField(blank=True, null=True)),
                ('profile_description', models.TextField(blank=True, max_length=1000, null=True)),
                ('signature', models.TextField(blank=True, max_length=250, null=True)),
                ('registration_completed', models.BooleanField(default=False)),
                ('name', models.CharField(blank=True, max_length=200)),
                ('gender', models.CharField(choices=[('Male', 'Male'), ('Female', 'Female'), ('Undefined', 'Undefined')], default='Undefined', max_length=10)),
                ('favorite_books', models.ManyToManyField(to='polls.book')),
                ('favorite_games', models.ManyToManyField(to='polls.game')),
                ('favorite_movies', models.ManyToManyField(to='polls.movie')),
            ],
        ),
        migrations.CreateModel(
            name='Series',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('date_of_release', models.DateField()),
                ('Verified', models.BooleanField(default=False)),
                ('summary', models.TextField(default='summary', max_length=1000)),
                ('poster', models.TextField(default='https://pbs.twimg.com/profile_images/1510045751803404288/W-AAI2EH_400x400.jpg', max_length=200)),
                ('imdb_rating', models.FloatField(blank=True, default=None, null=True)),
                ('imdb_id', models.CharField(max_length=10, null=True, unique=True)),
                ('type_of_show', models.CharField(choices=[('movie', 'movie'), ('series', 'series')], max_length=6)),
                ('number_of_seasons', models.CharField(max_length=100, null=True)),
                ('episodes_update_date', models.DateField(null=True)),
                ('in_production', models.BooleanField(default=True)),
                ('actors', models.ManyToManyField(to='polls.actor')),
                ('added_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('director', models.ManyToManyField(to='polls.director')),
                ('genre', models.ManyToManyField(to='polls.movieseriesgenre')),
                ('language', models.ManyToManyField(to='polls.language')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Thread',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=400)),
                ('content', models.TextField()),
                ('updated', models.DateTimeField(auto_now=True)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('Verified', models.BooleanField(default=False)),
                ('slug', models.SlugField(null=True, unique=True)),
                ('slug_category', models.SlugField(null=True)),
                ('views', models.IntegerField(default=0)),
                ('category', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='categories', to='polls.forumcategory')),
                ('creator', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='polls.profile')),
                ('likes', models.ManyToManyField(related_name='thread_like', to='polls.profile')),
                ('tags', taggit.managers.TaggableManager(help_text='A comma-separated list of tags.', through='taggit.TaggedItem', to='taggit.Tag', verbose_name='Tags')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='SeriesWatchlist',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('series_status', models.CharField(choices=[('watched', 'watched'), ('watching', 'watching'), ('want to watch', 'want to watch'), ('dropped', 'dropped')], max_length=13)),
                ('progress', models.CharField(blank=True, max_length=6, null=True)),
                ('profile', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='polls.profile')),
                ('series', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='polls.series')),
            ],
        ),
        migrations.CreateModel(
            name='SeriesReview',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField(max_length=1000)),
                ('review_date', models.DateField(default='2022-12-12')),
                ('rate', models.IntegerField(null=True, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(10)])),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('series', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='polls.series')),
            ],
        ),
        migrations.CreateModel(
            name='Season',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('season_number', models.CharField(max_length=2)),
                ('number_of_episodes', models.IntegerField(default=0)),
                ('series', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='polls.series')),
            ],
        ),
        migrations.CreateModel(
            name='RequestPermission',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Request_Reason', models.TextField(max_length=1000)),
                ('status', models.CharField(choices=[('Sent', 'Sent'), ('Accepted', 'Accepted'), ('Rejected', 'Rejected'), ('None', 'None')], default='None', max_length=10)),
                ('FromUser', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='polls.profile')),
            ],
        ),
        migrations.AddField(
            model_name='profile',
            name='favorite_series',
            field=models.ManyToManyField(to='polls.series'),
        ),
        migrations.AddField(
            model_name='profile',
            name='likes',
            field=models.ManyToManyField(related_name='blog_posts', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='profile',
            name='user',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=400)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('Verified', models.BooleanField(default=False)),
                ('content', ckeditor.fields.RichTextField()),
                ('likes_number', models.IntegerField(default=0)),
                ('creator', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='polls.profile')),
                ('likes', models.ManyToManyField(related_name='post_like', to='polls.profile')),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='replies', to='polls.post')),
                ('thread', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='posts', to='polls.thread')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='MovieWatchlist',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('movie_status', models.CharField(choices=[('watched', 'watched'), ('want to watch', 'want to watch')], max_length=13)),
                ('movie', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='polls.movie')),
                ('profile', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='polls.profile')),
            ],
        ),
        migrations.CreateModel(
            name='MovieReview',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField(max_length=1000)),
                ('review_date', models.DateField(default='2022-12-12')),
                ('rate', models.IntegerField(null=True, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(10)])),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('movie', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='polls.movie')),
            ],
        ),
        migrations.AddField(
            model_name='movie',
            name='genre',
            field=models.ManyToManyField(to='polls.movieseriesgenre'),
        ),
        migrations.AddField(
            model_name='movie',
            name='language',
            field=models.ManyToManyField(to='polls.language'),
        ),
        migrations.CreateModel(
            name='Like',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.CharField(choices=[('Like', 'Like'), ('Unlike', 'Unlike')], default='Post_Like', max_length=10)),
                ('creator', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('post', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='polls.post')),
            ],
        ),
        migrations.CreateModel(
            name='GameReview',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField(max_length=1000)),
                ('review_date', models.DateField(default='2022-12-12')),
                ('rate', models.IntegerField(null=True, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(10)])),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('game', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='polls.game')),
            ],
        ),
        migrations.CreateModel(
            name='GameList',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('game_status', models.CharField(choices=[('played', 'played'), ('playing', 'playing'), ('want to play', 'want to play'), ('dropped', 'dropped')], max_length=12)),
                ('game', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='polls.game')),
                ('profile', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='polls.profile')),
            ],
        ),
        migrations.AddField(
            model_name='game',
            name='genre',
            field=models.ManyToManyField(help_text='Select a genre for this game', to='polls.gamegenre'),
        ),
        migrations.AddField(
            model_name='game',
            name='mode',
            field=models.ManyToManyField(help_text='Select which game mode is available', to='polls.gamemode'),
        ),
        migrations.AddField(
            model_name='forumcategory',
            name='creator',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='polls.profile'),
        ),
        migrations.CreateModel(
            name='Episode',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('release_date', models.DateField(null=True)),
                ('episode_number', models.IntegerField(null=True)),
                ('runtime', models.IntegerField(null=True)),
                ('plot', models.TextField(max_length=1000, null=True)),
                ('imdb_rating', models.FloatField(blank=True, null=True)),
                ('poster', models.TextField(default='https://pbs.twimg.com/profile_images/1510045751803404288/W-AAI2EH_400x400.jpg', max_length=200)),
                ('imdb_id', models.CharField(max_length=10, null=True, unique=True)),
                ('season', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='polls.season')),
            ],
        ),
        migrations.CreateModel(
            name='BookReview',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField(max_length=1000)),
                ('review_date', models.DateField(default='2022-12-12')),
                ('rate', models.IntegerField(null=True, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(10)])),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('book', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='polls.book')),
            ],
        ),
        migrations.CreateModel(
            name='BookList',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('book_status', models.CharField(choices=[('read', 'read'), ('reading', 'reading'), ('want to read', 'want to read'), ('dropped', 'dropped')], max_length=12)),
                ('book', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='polls.book')),
                ('profile', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='polls.profile')),
            ],
        ),
        migrations.AddField(
            model_name='book',
            name='genre',
            field=models.ManyToManyField(help_text='Select a genre for this book', to='polls.movieseriesgenre'),
        ),
        migrations.AddField(
            model_name='book',
            name='languages',
            field=models.ManyToManyField(to='polls.language'),
        ),
    ]

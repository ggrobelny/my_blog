from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.utils import timezone
from taggit.managers import TaggableManager


# tworzę własnego menedżera do pobierania wszystkich postów których stan jest określony jako published
class PublishedManager(models.Manager):
    def get_queryset(self):
        return super(PublishedManager, self).get_queryset().filter(status='published')


class Post(models.Model):

    # menedżer domyślny -> Post.objects.all()
    objects = models.Manager()

    # mój niestandardowy menedżer -> Post.published.all()
    published = PublishedManager()

    # menedżer tagów -umożliwia dodawanie, pobieranie i usuwanie tagów z obiektów Post
    tags = TaggableManager()

    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('published', 'Published'),
    )
    # klucz główny wygeneruje się automatycznie jako pole id
    # aby go nadpisać muszę dodać do któregoś pola: primary_key = True
    title = models.CharField(max_length=250)
    slug = models.SlugField(max_length=250, unique_for_date='publish')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blog_posts')
    body = models.TextField()
    publish = models.DateTimeField(default=timezone.now)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')

    # metadane dla django aby po wysłaniu obiektu do db wyniki sortował malejąco względem pola publish
    class Meta:
        ordering = ('-publish',)
        # w klasie meta mogę też podać własną nazwę tabeli używając db_table

    # metoda str zwraca czytelną reprezentację obiektu
    def __str__(self):
        return self.title

    # metoda get_absolute_url() zwraca kanoniczny adres URL obiektu.
    def get_absolute_url(self):
        return reverse('blog:post_detail',
                       args=[self.publish.year,
                             self.publish.strftime('%m'),
                             self.publish.strftime('%d'),
                             self.slug])


# model komentarzy
class Comment(models.Model):
    post = models.ForeignKey(Post,
                             on_delete=models.CASCADE,
                             related_name='comments')
    name = models.CharField(max_length=80)
    email = models.EmailField()
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ('created',)

    def __str__(self):
        return 'Komentarz dodany przez {} dla posta {}'.format(self.name, self.post)
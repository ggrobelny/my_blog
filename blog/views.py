from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView
from taggit.models import Tag
from .models import Comment, Post
from django.db.models import Count
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from .forms import EmailPostForm, CommentForm, SearchForm
from django.core.mail import send_mail
from django.contrib.postgres.search import TrigramSimilarity


def home_page(request):
    return render(request, 'blog/post/index.html')


def about_page(request):
    return render(request, 'blog/post/about.html')


def contact_page(request):
    return HttpResponse("<h1>Contact: Help Desk Blog</h1>")


def post_search(request):
    form = SearchForm()
    query = None
    results = []
    if 'query' in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            search_vector = SearchVector('title', weight='A') + SearchVector('body', weight='B')
            search_query = SearchQuery(query)
            results = Post.objects.annotate(
                similarity=TrigramSimilarity('title', query),
            ).filter(similarity__gt=0.1).order_by('-similarity')

    return render(request, 'blog/post/search.html', {'form': form,'query': query,'results': results})

def post_share(request, post_id):
# Pobranie posta na podstawie jego identyfikatora.
    post = get_object_or_404(Post, id=post_id, status='published')
    sent = False
    if request.method == 'POST':
# Formularz został wysłany.
        form = EmailPostForm(request.POST)
        if form.is_valid():
# Weryfikacja pól formularza zakończyła się powodzeniem...
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = '{} ({}) zachęca do przeczytania "{}"'.format(cd['name'],cd['email'], post.title)
            message = 'Przeczytaj post "{}" na stronie {}\n\n Komentarz dodany przez {}: {}'.format(post.title, post_url, cd['name'], cd['comments'])
            send_mail(subject, message, 'admin@myblog.com', [cd['to']])
            sent = True
# ... więc można wysłać wiadomość e-mail.
    else:
        form = EmailPostForm()
        return render(request, 'blog/post/share.html', {'post': post,'form': form, 'sent': sent})

def post_list(request, tag_slug=None):
    # posts = Post.published.all()
    object_list = Post.published.all()
    tag = None

    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        object_list = object_list.filter(tags__in=[tag])

    paginator = Paginator(object_list, 3) # Trzy posty na każdej stronie.
    page = request.GET.get('page')
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
    # Jeżeli zmienna page nie jest liczbą całkowitą,
    # wówczas pobierana jest pierwsza strona wyników.
        posts = paginator.page(1)
    except EmptyPage:
    # Jeżeli zmienna page ma wartość większą niż numer ostatniej strony
    # wyników, wtedy pobierana jest ostatnia strona wyników.
        posts = paginator.page(paginator.num_pages)
    return render(request,'blog/post/list.html', {'page': page, 'posts': posts, 'tag': tag})



class PostListView(ListView):
    queryset = Post.published.all()
    context_object_name = 'posts'
    paginate_by = 3
    template_name = 'blog/post/list.html'

def post_detail(request, year, month, day, post):
    # Lista podobnych postów.
    post = get_object_or_404(Post, slug=post, status='published', publish__year=year, publish__month=month, publish__day=day)
    # Lista aktywnych komentarzy dla danego posta.
    comments = post.comments.filter(active=True)

    if request.method == 'POST':
    # Komentarz został opublikowany.
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            # Utworzenie obiektu Comment, ale jeszcze nie zapisujemy go w bazie danych.
            new_comment = comment_form.save(commit=False)
            # Przypisanie komentarza do bieżącego posta.
            new_comment.post = post
            # Zapisanie komentarza w bazie danych.
            new_comment.save()
    else:
        comment_form = CommentForm()

    post_tags_ids = post.tags.values_list('id', flat=True)
    similar_posts = Post.published.filter(tags__in=post_tags_ids).exclude(id=post.id)
    similar_posts = similar_posts.annotate(same_tags=Count('tags')).order_by('-same_tags', '-publish')[:4]

    return render(request, 'blog/post/detail.html', {'post': post, 'comments': comments, 'comment_form': comment_form, 'similar_posts': similar_posts})





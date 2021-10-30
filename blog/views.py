from django.shortcuts import render, redirect, get_object_or_404
from .models import Post, Comment
from .forms import PostCreateForm, EmailPostForm, CommentForm, SearchForm
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.mail import send_mail
from taggit.models import Tag
from django.db.models import Count
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from django.contrib.auth.decorators import login_required


@login_required(login_url='login')
def post_list(request, tag_slug=None):
    object_list = Post.published.all()
    tag = None

    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        object_list = object_list.filter(tags__in=[tag])

    paginator = Paginator(object_list, 4)
    page = request.GET.get('page')
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except  EmptyPage:
        posts = paginator.page(paginator.num_pages)
    context = {'page': page, 'posts': posts, 'tag': tag}
    return render(request, 'post/list.html', context)

@login_required(login_url='login')
def post_detail(request, pk):
    post = Post.objects.get(id=pk)
    comments = post.comments.filter(active=True)
    new_comment = None
    if request.method == "POST":
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.post = post
            new_comment.name = request.user
            new_comment.save()
    else:
        comment_form = CommentForm()

    post_tags_ids = post.tags.values_list('id', flat=True)
    similar_posts = Post.published.filter(tags__in=post_tags_ids).exclude(id=post.id)
    similar_posts = similar_posts.annotate(same_tags=Count('tags')).order_by('-same_tags', '-publish')[:4]

    context = {'post': post, 'comments': comments, 'new_comment': new_comment, 'comment_form': comment_form, 'similar_posts': similar_posts}
    return render(request, 'post/detail.html', context)

@login_required(login_url='login') 
def post_create(request):
    form = PostCreateForm()
    if request.method == "POST":
        form = PostCreateForm(request.POST,request.FILES)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.author = request.user
            form.save()
            return redirect('/')
    context = {'form': form }
    return render(request, 'post/create.html', context)

@login_required(login_url='login')    
def post_edit(request, pk):
    post = get_object_or_404(Post, id=pk, author=request.user)
    form = PostCreateForm(request.POST or None, request.FILES or None, instance=post)
    if form.is_valid():
        form.save()
        return redirect('/')
    context = {'form': form}
    return render(request, 'post/edit.html', context)


@login_required(login_url='login')
def post_delete(request, pk):
    post = get_object_or_404(Post, id=pk, author=request.user)
    if request.method == 'POST':
        post.delete()
        return redirect('/')
    context = {'post': post}
    return render(request, 'post/delete.html', context)

@login_required(login_url='login')
def post_share(request, post_id):
    post = get_object_or_404(Post, id=post_id, status='published')
    sent = False
    if request.method == 'POST':
        form = EmailPostForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(f"/blog/post/{post_id}/")
            subject = f"{cd['name']} recommends you read {post.title}"
            message = f"Read {post.title} at {post_url}\n\n {cd['name']}\'s comments: {cd['comments']}"
            send_mail(subject, message, 'sarvarnematullayev2001@gmail.com', [cd['to']])
            sent = True
    else:
        form = EmailPostForm()
    context = {'post':post, 'form': form, 'sent': sent}
    return render(request, 'post/share.html', context)

@login_required(login_url='login')
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
            results = Post.published.annotate(search=search_vector, rank=SearchRank(search_vector, search_query)).filter(rank__gte=0.3).order_by('-rank')
    context = {'form': form, 'query': query, 'results': results}
    return render(request, 'post/search.html', context)

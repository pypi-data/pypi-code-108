from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

from infscroll.utils import get_pagination
from infscroll.views import more_items

from social_layer.posts.forms import PostForm
from social_layer.posts.models import Post, PostMedia
from social_layer.utils import get_social_profile
from social_layer.mediautils.utils import handle_upload_file


def new_post(request):
    """ manages the creation of new user generated content """
    if not request.user.is_authenticated:
        return redirect(reverse('social_layer:social_login'))
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES,
                        initial={'owner': request.user})
        if form.is_valid():
            post = form.save(commit=False)
            post.owner = get_social_profile(request)
            post.save()
            if (form.allow_media and len(request.FILES) > 0):
                media = handle_upload_file(file_post=request.FILES.get('media'),
                                            quality=1,
                                            Model=PostMedia,
                                            extra_args={'post': post})
            return redirect(reverse('social_layer:posts_feed'))
    else:
        form = PostForm()
    return render(request, 'social_layer/posts/new_post.html', {'form': form,})


def posts_feed(request):
    """ The main list of posts """
    post_list = Post.objects.all().order_by('-id')
    paginated = get_pagination(request, post_list)
    data = {
        'more_posts_url': reverse('social_layer:more_posts'),
        'form': PostForm(),
        }
    data.update(paginated)
    return render(request, 'social_layer/posts/posts_feed.html', data)

def more_posts(request):
    """ dynamic load posts using the django-infinite-scroll module.
    """
    post_list = Post.objects.all().order_by('-id')
    return more_items(request, post_list,
                      template='social_layer/posts/more_posts.html')

def view_post(request, pk, template='social_layer/posts/view_post.html'):
    """ The main list of posts """
    post = get_object_or_404(Post, pk=pk)
    data = {
        'post': post,
        'comment_section': post.comments,
        }
    return render(request, template, data)


def delete_post(request, pk):
    """ The main list of posts """
    post = get_object_or_404(Post, pk=pk, owner__user=request.user)
    post.delete()
    return redirect(reverse('social_layer:posts_feed'))

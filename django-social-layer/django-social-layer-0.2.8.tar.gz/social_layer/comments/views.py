# This file is part of django-social-layer
#
#    django-social-layer is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    django-social-layer is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with django-social-layer. If not, see <http://www.gnu.org/licenses/>.

from django.shortcuts import render, redirect

# Create your views here.
from time import time
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, Http404
from django.utils.translation import gettext as _
from django.urls import reverse
from social_layer.comments.models import CommentSection, Comment, LikeComment, LikePost
from social_layer.notifications.models import Notification
from social_layer.utils import get_social_profile


def comment_section(request, pk=None):
    """ renders a full comment section
    and also stores a new comment
    """
    sprofile = get_social_profile(request)
    if pk:
       section = CommentSection.objects.get(id=pk)
    else:
       section = CommentSection.objects.create(owner=sprofile)
    if request.method == "POST":
        text = request.POST.get("text", '')
        reply_to = request.POST.get("reply_to", None)
        if reply_to:
            reply_to = Comment.objects.filter(pk=reply_to).first()
        comment = Comment.objects.create(author=sprofile,
                                         comment_section=section,
                                         text=text,
                                         reply_to=reply_to)
        parties = []
        if section.owner:
            parties.append(section.owner.user)
        if reply_to:
            jump_to = reply_to.pk
            parties.append(reply_to.author.user)
        else:
            jump_to = comment.pk
            parties.append(comment.author.user)
        if jump_to != None:
            comment_url = section.get_url()+'?show-comments#comment_'+str(jump_to)
            message_list = [sprofile.nick,
                            '<a href="{}" class="alink">'.format(comment_url),
                            _("wrote a comment"),
                            '</a>']
            notif_text = ' '.join(message_list)
            notify_parties(parties, notif_text, do_not=[request.user])
        else:
            comment_url = section.get_url()+'?show-comments'
        return redirect(comment_url)
    data = {
        'comment_section': section,
        }
    return render(request, 'social_layer/comments/comments_view.html', data)


@login_required
def reply_comment(request, pk):
    """ Called when posting a reply to a comment """
    sprofile = get_social_profile(request)
    reply_to = Comment.objects.filter(id=pk).first()
    if not reply_to:
        raise Http404()
    section = reply_to.comment_section
    if request.method == "POST":
        text = request.POST.get("text", '')
        comment = Comment.objects.create(author=sprofile,
                                         comment_section=section,
                                         text=text,
                                         reply_to=reply_to)
        if '?' in section.get_url():
            spacer = '&'
        else:
            spacer = '?'
        comment_url = ''.join([
                            section.get_url(),
                            spacer,
                            'show-comments',
                            '&t='+str(int(time())),
                            '#comment_'+str(reply_to.pk),
                            ])
        message_list = [sprofile.nick,
                        '<a href="{}" class="alink">'.format(comment_url),
                        _("wrote a comment"),
                        '</a>',
                        text[0:10]+'...',]
        notif_text = ' '.join(message_list)
        parties = [reply_to.author.user,]
        if section.owner:
            parties.append(section.owner.user)
        notify_parties(parties, notif_text, do_not=[request.user])
        
        return redirect(comment_url)
    return redirect(section.get_url())

@login_required
def delete_comment(request, pk):
    """ Deletes a comment """
    sprofile = get_social_profile(request)
    comment = Comment.objects.filter(id=pk).first()
    if not comment:
        raise Http404()
    section = comment.comment_section
    if (sprofile == comment.author
        or section.owner_can_delete and sprofile == section.owner
        or request.user.is_superuser):
        comment.delete()
    return redirect(section.get_url())


def notify_parties(parties, text, do_not=[]):
    """ Creates a notification to people interested on it """
    for party in set(parties):
        if (party and party not in do_not):
            Notification.objects.create(to=party,
                                        text=text)

@login_required
def like_comment(request, pk, didlike):
    """ when someone likes a comment """
    comment = Comment.objects.filter(pk=pk).first()
    if not comment:
        raise Http404()
    liked = LikeComment.objects.filter(user=request.user, comment=comment).first()
    if not liked:
        liked = LikeComment.objects.create(user=request.user, comment=comment)
    liked.like = bool(didlike == 'like')
    liked.save()
    comment.updt_counters()
    section = comment.comment_section
    comment.refresh_from_db()
    if 'ajx' in request.GET.keys():
        if liked.like:
            count = comment.count_likes
        else:
            count = comment.count_dislikes
        return HttpResponse(count, content_type='text/txt')
    else:
        return redirect(section.get_url())
    
@login_required
def like_post(request, pk, didlike):
    """ when someone likes a comment_section """
    section = CommentSection.objects.filter(pk=pk).first()
    if not section:
        raise Http404()
    liked = LikePost.objects.filter(user=request.user, comment_section=section).first()
    if not liked:
        liked = LikePost.objects.create(user=request.user, comment_section=section)
    liked.like = bool(didlike == 'like')
    liked.save()
    section.updt_counters()
    if 'ajx' in request.GET.keys():
        if liked.like:
            count = section.count_likes
        else:
            count = section.count_dislikes
        return HttpResponse(count, content_type='text/txt')
    else:
        return redirect(section.get_url())


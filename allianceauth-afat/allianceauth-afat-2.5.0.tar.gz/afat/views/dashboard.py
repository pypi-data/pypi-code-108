"""
Dashboard related views
"""

# Django
from django.contrib.auth.decorators import login_required, permission_required
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.urls import reverse

# Alliance Auth
from allianceauth.eveonline.models import EveCharacter
from allianceauth.services.hooks import get_extension_logger

# Alliance Auth (External Libs)
from app_utils.logging import LoggerAddTag

# Alliance Auth AFAT
from afat import __title__
from afat.helper.views_helper import convert_fatlinks_to_dict, convert_fats_to_dict
from afat.models import AFat, AFatLink

logger = LoggerAddTag(get_extension_logger(__name__), __title__)


@login_required()
@permission_required("afat.basic_access")
def overview(request: WSGIRequest) -> HttpResponse:
    """
    Dashboard view
    :param request:
    :type request:
    :return:
    :rtype:
    """

    characters = (
        EveCharacter.objects.select_related("character_ownership")
        .filter(character_ownership__user=request.user, afats__isnull=False)
        .distinct()
    )

    context = {"characters": characters}

    logger.info(f"Module called by {request.user}")

    return render(request, "afat/view/dashboard/dashboard.html", context)


@login_required
@permission_required("afat.basic_access")
def ajax_recent_get_fats_by_character(
    request: WSGIRequest, charid: int
) -> JsonResponse:
    """
    Ajax call :: get all FATs for a given character
    :param request:
    :type request:
    :param charid:
    :type charid:
    :return:
    :rtype:
    """

    character = EveCharacter.objects.get(character_id=charid)

    fats = (
        AFat.objects.select_related_default()
        .filter(character=character)
        .order_by("afatlink__afattime")
        .reverse()[:10]
    )

    character_fat_rows = [
        convert_fats_to_dict(request=request, fat=fat) for fat in fats
    ]

    return JsonResponse(character_fat_rows, safe=False)


@login_required
@permission_required("afat.basic_access")
def ajax_get_recent_fatlinks(request: WSGIRequest) -> JsonResponse:
    """
    Ajax call :: get recent fat links for the dashboard datatable
    :param request:
    :type request:
    :return:
    :rtype:
    """

    fatlinks = (
        AFatLink.objects.select_related_default()
        .annotate_afats_count()
        .order_by("-afattime")[:10]
    )

    fatlink_rows = [
        convert_fatlinks_to_dict(
            request=request,
            fatlink=fatlink,
            close_esi_redirect=reverse("afat:dashboard"),
        )
        for fatlink in fatlinks
    ]

    return JsonResponse(fatlink_rows, safe=False)

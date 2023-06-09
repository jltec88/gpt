import json
import logging
import re

import unidecode
from administrator.decorators import users_redcalidad
from binnacles.models import SuEventUser
from campaigns.models import QsCampaign
from dashboard.adapters import PrefixedPhraseQuery
from dashboard.django_sites import reverse as sites_reverse
from django.contrib import messages
from django.contrib.postgres.search import SearchVector
from django.db.models import Q
from django.http import Http404, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone, translation
from django.utils.translation import gettext as _
from django.views.decorators.http import require_http_methods
from el_pagination.decorators import page_template
from indicators.models import IndIndicator
from login.login_decorators import active_and_login_required, check_permission
from login.models import (
    QsAppUser,
    QsAppUserAppCompany,
    QsCompany,
    QsHashLogin,
    QsProfile,
)
from sensors.models import QsSensor
from shorturl.models import ShortUrl
from survey.models import SuSurveyReport


logger = logging.getLogger(__name__)


@page_template('qassistant/ajax/all_companies.html')
@active_and_login_required
@users_redcalidad
def index(
        request, template="qassistant/index.html",
        extra_context=None):

    search_term = request.GET.get("s", '')
    search_term = re.sub("\s+", " ", search_term)
    search_term = search_term.strip()
    context = {}

    try:
        assert request.user.redcalidad_user
    except AssertionError as e:
        raise Http404(e)

    all_companies = QsCompany.objects.\
        only('name', 'description', 'creation_datetime').\
        filter(is_active=True).\
        filter(
            Q(expiration_datetime__gte=timezone.now()) |
            Q(expiration_datetime=None)
        ).\
        order_by('name')

    if search_term:

        search_term = unidecode.unidecode(search_term)

        query = PrefixedPhraseQuery(search_term, config='spanish_unaccent')

        all_companies = all_companies.annotate(
            search=SearchVector('name', config='spanish_unaccent')
        ).filter(search=query)

    context.update({
        'body_class': 'box_views',
        'all_companies': all_companies,
        'search': search_term
    })

    if extra_context is not None:
        context.update(extra_context)

    return render(request, template, context)

import json
from django.views.generic import TemplateView
from django.conf import settings
from django.http import Http404

from base import mods

class StatisticsView(TemplateView):
    template_name = 'vot_statistics/statistics.html'
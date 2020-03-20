from decimal import Decimal
from datetime import datetime

from django.views.generic import TemplateView, FormView
from django.db import transaction
from django.urls import reverse_lazy

from .models import VisitedPoint
from . import forms


class HomeView(TemplateView):
    template_name = 'core/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['message'] = 'Hallo, Corona'
        return context


class ReportView(FormView):
    form_class = forms.ReportForm
    template_name = 'core/report_form.html'
    success_url = reverse_lazy('core:home')

    def _process_google_file(self, points_file):
        # TODO: Julius can handle this
        # parse file to json
        # ...

        # return normalized data
        return [{
            'lat': Decimal('52.5256766'),
            'lng': Decimal('13.3415149'),
            'visited_at': datetime.fromtimestamp(1583057626),
        }]

    @transaction.atomic
    def form_valid(self, form):
        # add points to db
        points = self._process_google_file(form.cleaned_data['points_file'])
        VisitedPoint.objects.bulk_create([
            VisitedPoint(
                lat=point['lat'],
                lng=point['lat'],
                visited_at=point['visited_at'],
                is_verified=form.cleaned_data['is_verified'],
            ) for point in points
        ])

        return super().form_valid(form)


class CheckView(FormView):
    form_class = forms.CheckForm
    template_name = 'core/check_form.html'
    success_url = reverse_lazy('core:home')

    def form_valid(self, form):
        # compute risk on the fly

        return super().form_valid(form)

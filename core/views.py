from datetime import datetime, timedelta
import json

from django.views.generic import TemplateView, FormView
from django.db import transaction
from django.urls import reverse_lazy, reverse
from django.http import HttpResponseRedirect
from django.db.models import Q

from .models import VisitedPoint
from . import forms


POINTS_SESSION_KEY = 'points'
RISK_SESSION_KEY = 'risk_points'
MAX_POINTS = 1000


class JsDataMixin:
    def __init__(self):
        self._js_data = {}

    def add_data(self, key, data):
        self._js_data[key] = data

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['js_data'] = json.dumps(self._js_data)
        return context


class HomeView(TemplateView):
    template_name = 'core/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['hide_logo_menu'] = True
        return context


def import_google_coordinate(lat, lng):
    return lat*1e-7, lng*1e-7

def import_timeline_objects(data):
    visited_points = []

    timeline_objects = data['timelineObjects']
    for timeline_object in timeline_objects:
        if 'placeVisit' in timeline_object:
            place_visit = timeline_object['placeVisit']
            # TODO@Glumli: smart way to handle durations
            duration = place_visit['duration']
            start_timestamp = int(duration['startTimestampMs']) / 1000
            end_timestamp = int(duration['endTimestampMs']) / 1000
            visited_at = datetime.fromtimestamp((start_timestamp + end_timestamp) / 2)

            location = place_visit['location']
            lat, lng = import_google_coordinate(location['latitudeE7'], location['longitudeE7'])

            visited_points.append({
                'lat': lat,
                'lng': lng,
                'visited_at': visited_at
            })
        elif 'activitySegment' in timeline_object:
            activity_segment = timeline_object['activitySegment']

            duration = activity_segment['duration']

            start_timestamp = int(duration['startTimestampMs']) / 1000
            end_timestamp = int(duration['endTimestampMs']) / 1000
            if 'waypointPath' in activity_segment:
                visited_at = datetime.fromtimestamp((start_timestamp + end_timestamp) / 2)

                waypoint_path = activity_segment['waypointPath']
                points = waypoint_path.get('waypoints', [])
                for point in points:
                    lat, lng = import_google_coordinate(point['latE7'], point['lngE7'])
                    visited_points.append({
                        'lat': lat,
                        'lng': lng,
                        'visited_at': visited_at
                    })
            elif 'simplifiedRawPath' in activity_segment:
                simplified_path = activity_segment['simplifiedRawPath']
                points = simplified_path.get('points', [])
                for point in points:
                    lat, lng = import_google_coordinate(point['latE7'], point['lngE7'])
                    visited_at = datetime.fromtimestamp(int(point['timestampMs']) / 1000)
                    visited_points.append({
                        'lat': lat,
                        'lng': lng,
                        'visited_at': visited_at
                    })
            elif 'transitPath' in activity_segment:
                visited_at = datetime.fromtimestamp((start_timestamp + end_timestamp) / 2)

                transit_path = activity_segment['transitPath']
                points = transit_path.get('transitStops', [])
                for point in points:
                    lat, lng = import_google_coordinate(point['latitudeE7'], point['longitudeE7'])
                    visited_points.append({
                        'lat': lat,
                        'lng': lng,
                        'visited_at': visited_at
                    })
            else:
                start_point = activity_segment['startLocation']
                lat, lng = import_google_coordinate(start_point['latitudeE7'], start_point['longitudeE7'])
                visited_at = datetime.fromtimestamp(start_timestamp)

                visited_points.append({
                    'lat': lat,
                    'lng': lng,
                    'visited_at': visited_at
                })

                end_point = activity_segment['endLocation']
                lat, lng = import_google_coordinate(end_point['latitudeE7'], end_point['longitudeE7'])
                visited_at = datetime.fromtimestamp(end_timestamp)

                visited_points.append({
                    'lat': lat,
                    'lng': lng,
                    'visited_at': visited_at
                })
    return visited_points


def import_location_history(data, is_check=False):
    visited_points = []
    locations = data['locations']

    for location in locations:
        lat, lng = import_google_coordinate(location['latitudeE7'], location['longitudeE7'])
        visited_point = {
            'lat': lat,
            'lng': lng,
            'visited_at': datetime.fromtimestamp(int(location['timestampMs'])/1000)
        }
        if is_check:
            visited_point['accuracy'] = location['accuracy']
        visited_points.append(visited_point)

    return visited_points


class ReportView(FormView):
    form_class = forms.ReportForm
    template_name = 'core/report_form.html'
    success_url = reverse_lazy('core:home')

    @transaction.atomic
    def form_valid(self, form):
        # add points to db
        raw_data = form.cleaned_data['points_data']
        if not raw_data:
            raw_data = form.cleaned_data['points_file'].read()

        points = import_location_history(json.loads(raw_data))
        VisitedPoint.objects.bulk_create([
            VisitedPoint(
                lat=point['lat'],
                lng=point['lng'],
                visited_at=point['visited_at'],
                is_verified=form.cleaned_data['is_verified'],
            ) for point in points
        ])

        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Report Infected Points'
        return context

class CheckView(FormView):
    form_class = forms.CheckForm
    template_name = 'core/check_form.html'
    success_url = reverse_lazy('core:map')

    def form_valid(self, form):
        # compute risk on the fly
        raw_data = form.cleaned_data['points_data']
        if not raw_data:
            raw_data = form.cleaned_data['points_file'].read()

        points = import_location_history(json.loads(raw_data), is_check=True)
        self.request.session[POINTS_SESSION_KEY] = [{
            'lat': float(point['lat']),
            'lng': float(point['lng']),
            'visited_at': str(point['visited_at']),
        } for point in points]

        filters = None
        radius = 2e-3
        time_window = timedelta(minutes=20)

        for point in points:
            min_date = point['visited_at'] - time_window
            max_date = point['visited_at'] + time_window

            if filters is None:
                filters = Q(
                    lat__gt=point['lat'] - radius,
                    lat__lt=point['lat'] + radius,
                    lng__gt=point['lng'] - radius,
                    lng__lt=point['lng'] + radius,
                    visited_at__gt=min_date,
                    visited_at__lt=max_date
                )
            else:
                filters |= Q(
                    lat__gt=point['lat'] - radius,
                    lat__lt=point['lat'] + radius,
                    lng__gt=point['lng'] - radius,
                    lng__lt=point['lng'] + radius,
                    visited_at__gt=min_date,
                    visited_at__lt=max_date
                )

        risk_points = list(VisitedPoint.objects.filter(filters))
        self.request.session[RISK_SESSION_KEY] = [{
            'lat': float(point.lat),
            'lng': float(point.lng),
            'visited_at': str(point.visited_at),
        } for point in risk_points]

        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Check Your Points'
        return context


class MapView(JsDataMixin, TemplateView):
    template_name = 'core/map.html'

    def dispatch(self, request, *args, **kwargs):
        # map should only show results from check
        self._points = self.request.session.get(POINTS_SESSION_KEY, [])
        if not self._points:
            return HttpResponseRedirect(reverse('core:check'))

        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        self.add_data('points', self._points)
        self.add_data('riskPoints', self.request.session.get(RISK_SESSION_KEY))
        return super().get(request, *args, **kwargs)

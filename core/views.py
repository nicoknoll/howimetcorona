import json
from decimal import Decimal
from datetime import datetime
import json

from django.views.generic import TemplateView, FormView
from django.db import transaction
from django.urls import reverse_lazy

from .models import VisitedPoint
from . import forms


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


def import_location_history(data):
    visited_points = []
    locations = data['locations']

    for location in locations:
        lat, lng = import_google_coordinate(location['latitudeE7'], location['longitudeE7'])

        visited_points.append({
            'lat': lat,
            'lng': lng,
            'visited_at': datetime.fromtimestamp(int(location['timestampMs'])/1000)
        })

    return visited_points


class ReportView(FormView):
    form_class = forms.ReportForm
    template_name = 'core/report_form.html'
    success_url = reverse_lazy('core:map')

    def _process_google_file(self, points_file):
        data = json.loads(points_file.read())

        visited_points = import_location_history(data)

        # return normalized data
        return visited_points

    @transaction.atomic
    def form_valid(self, form):
        # add points to db
        points = self._process_google_file(form.cleaned_data['points_file'])
        VisitedPoint.objects.bulk_create([
            VisitedPoint(
                lat=point['lat'],
                lng=point['lng'],
                visited_at=point['visited_at'],
                is_verified=form.cleaned_data['is_verified'],
            ) for point in points
        ])

        return super().form_valid(form)


class CheckView(FormView):
    form_class = forms.CheckForm
    template_name = 'core/check_form.html'
    success_url = reverse_lazy('core:map')

    def form_valid(self, form):
        # compute risk on the fly

        return super().form_valid(form)


class MapView(JsDataMixin, TemplateView):
    template_name = 'core/map.html'

    def get(self, request, *args, **kwargs):
        self.add_data('points', [{
            'lat': float(point.lat),
            'lng': float(point.lng),
            'visited_at': str(point.visited_at),
        } for point in VisitedPoint.objects.order_by('-created_at')[:MAX_POINTS]])
        return super().get(request, *args, **kwargs)

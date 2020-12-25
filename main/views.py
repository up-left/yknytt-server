from rest_framework import generics
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.db.models import F
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
import json
from main.models import *
from main.serializers import *


class LevelList(generics.ListAPIView):
    serializer_class = LevelSerializer
    queryset = Level.objects.all()

    def get_queryset(self):
        queryset = super().get_queryset()

        text = self.request.query_params.get('text', None)
        if text:
            queryset = queryset.filter(name__icontains=text)

        size = self.request.query_params.get('size', None)
        if size:
            queryset = queryset.filter(size=int(size))

        difficulty = self.request.query_params.get('difficulty', None)
        if difficulty:
            queryset = queryset.filter(difficulty__contains=[int(difficulty)])
            
        category = self.request.query_params.get('category', None)
        if category:
            queryset = queryset.filter(category__contains=[int(category)])

        return queryset


@csrf_exempt
@require_http_methods(["POST"])
def rate(request):
    request_data = json.loads(request.body.decode('utf-8'))
    response_data = {}

    level_id = request_data.get('level_id', None)
    uid = request_data.get('uid', None)
    platform = request_data.get('platform', None)
    action = request_data.get('action', None)

    if level_id is None or uid is None or action is None:
        return JsonResponse({'message': 'missing parameter'}, status=422)

    level_id = int(level_id)
    action = int(action)

    level = Level.objects.filter(id=level_id).first()
    if level is None:
        return JsonResponse({'message': 'level not found'}, status=422)

    rate_field = Rate.ACTION_DICT.get(action, None)
    if rate_field is None:
        return JsonResponse({'message': 'action not found'}, status=422)

    _, created = Rate.objects.get_or_create(level=level, level_hash=level.level_hash, uid=uid, platform=platform, action=action)
    if created:
        LevelRating.objects.filter(pk=level_id).update(**{rate_field: F(rate_field) + 1})

    return JsonResponse({'action': action, 'added': 1 if created else 0}, status=200)


class RatingRetrieve(generics.RetrieveAPIView):
    queryset = LevelRating.objects.all()
    serializer_class = LevelRatingSerializer

    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())
        return get_object_or_404(queryset, level__name=self.request.query_params['name'], level__author=self.request.query_params['author'])

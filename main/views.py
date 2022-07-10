from rest_framework import generics
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.db.models import F, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
import json
import time
from main.models import *
from main.serializers import *


class LevelList(generics.ListAPIView):
    serializer_class = LevelSerializer
    queryset = Level.objects.all()

    ORDER_FIELDS = {3: 'name', 4: 'author', 5: '-levelrating__downloads', 6: '-levelrating__upvotes', 7: '-file_size'}

    def get_queryset(self):
        queryset = super().get_queryset()

        text = self.request.query_params.get('text', None)
        if text:
            queryset = queryset.filter(Q(name__icontains=text) | Q(author__icontains=text))

        size = self.request.query_params.get('size', None)
        if size:
            queryset = queryset.filter(size=int(size))

        difficulty = self.request.query_params.get('difficulty', None)
        if difficulty:
            queryset = queryset.filter(difficulty__contains=[int(difficulty)])
            
        category = self.request.query_params.get('category', None)
        if category:
            queryset = queryset.filter(category__contains=[int(category)])

        order = self.request.query_params.get('order', None)
        if order:
            queryset = queryset.order_by(LevelList.ORDER_FIELDS[int(order)], 'pk')

        return queryset


@csrf_exempt
@require_http_methods(["POST"])
def rate(request):
    request_data = json.loads(request.body.decode('utf-8'))
    response_data = {}

    level_name = request_data.get('name', None)
    level_author = request_data.get('author', None)
    uid = request_data.get('uid', None)
    platform = request_data.get('platform', None)
    action = request_data.get('action', None)
    cutscene = request_data.get('cutscene', None)

    if level_name is None or level_author is None or uid is None or action is None:
        return JsonResponse({'message': 'missing parameter'}, status=422)

    level = get_object_or_404(Level, name=level_name, author=level_author)
    action = int(action)
    cutscene_action = action == 5 or action == 6
    launch_action = action == 7 or action == 8

    rate_field = Rate.ACTION_DICT.get(action, None)
    if rate_field is None and not cutscene_action:
        return JsonResponse({'message': 'action not found'}, status=422)

    if cutscene_action:
        if cutscene is None:
            return JsonResponse({'message': 'missing cutscene parameter'}, status=422)
        cutscene_queryset = Cutscene.objects.filter(level=level, name__iexact=cutscene, ending=action == 6)
        if cutscene_queryset.count() != 1:
            return JsonResponse({'message': 'cutscene not found'}, status=422)

    if launch_action:
        cutscene = str(time.time()) # to provide unique key

    _, created = Rate.objects.get_or_create({'name': level_name, 'author': level_author, 'platform': platform}, level=level, uid=uid, action=action, cutscene=cutscene)
    if created:
        if rate_field is not None:
            LevelRating.objects.filter(level=level).update(**{rate_field: F(rate_field) + 1})
        else:
            cutscene_queryset.update(counter=F("counter") + 1)

            if action == 6 and not level.levelrating.verified:
                if not Cutscene.objects.filter(level=level, ending=True, counter=0).exists():
                    LevelRating.objects.filter(level=level).update(verified=True)

    return JsonResponse({'action': action, 'added': 1 if created else 0}, status=200)


class RatingRetrieve(generics.RetrieveAPIView):
    queryset = LevelRating.objects.all()
    serializer_class = LevelRatingSerializer

    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())
        return get_object_or_404(queryset, level__name=self.request.query_params['name'], level__author=self.request.query_params['author'])

from rest_framework import generics
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.db.models import F, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from ipware import get_client_ip
import json
import time
from main.models import *
from main.serializers import *


class LevelList(generics.ListAPIView):
    serializer_class = LevelSerializer
    queryset = Level.objects.all()

    ORDER_FIELDS = {3: 'name', 4: 'author', 5: '-levelrating__downloads', 6: '-levelrating__upvotes', 7: '-file_size', 8: '-levelrating__score'}

    def get_queryset(self):
        queryset = super().get_queryset()

        text = self.request.query_params.get('text', None)
        if text:
            queryset = queryset.filter(Q(name__icontains=text) | Q(author__icontains=text) | Q(description__icontains=text))

        size = self.request.query_params.get('size', None)
        if size:
            queryset = queryset.filter(size=int(size))

        difficulty = self.request.query_params.get('difficulty', None)
        if difficulty and int(difficulty) > 0:
            queryset = queryset.annotate(filt=F('difficulty').bitand(1 << int(difficulty))).filter(filt__gt=0)
        if difficulty and int(difficulty) == 0:
            queryset = queryset.filter(difficulty=1)

        category = self.request.query_params.get('category', None)
        if category and int(category) > 0:
            queryset = queryset.annotate(filt = F('category').bitand(1 << int(category))).filter(filt__gt=0)
        if category and int(category) == 0:
            queryset = queryset.filter(category=1)

        version = self.request.query_params.get('version', None)
        if version and version == '0.6.9':
            queryset = queryset.exclude(format=9)

        order = self.request.query_params.get('order', None)
        if order:
            queryset = queryset.order_by(LevelList.ORDER_FIELDS[int(order)], '-levelrating__score', '-levelrating__downloads', 'pk')

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
    ip, _ = get_client_ip(request)

    if level_name is None or level_author is None or uid is None or action is None:
        return JsonResponse({'message': 'missing parameter'}, status=422)

    level = get_object_or_404(Level, name=level_name, author=level_author)
    action = int(action)
    cutscene_action = action in (5, 6)
    launch_action = action in (7, 8)
    score_action = action >= 20 and action <= 30
    completion_action = action >= 40 and action <= 46
    power_action = action >= 100

    rate_field = Rate.ACTION_DICT.get(action, None)
    if rate_field is None and not cutscene_action and action != 10 and not score_action:
        return JsonResponse({'message': 'action not found'}, status=422)

    if cutscene_action or power_action or action == 9:
        if Rate.objects.filter(level=level, uid=uid, action=10).exists():
            return JsonResponse({'message': 'previously cheated'}, status=422)

    if cutscene_action:
        if cutscene is None:
            return JsonResponse({'message': 'missing cutscene parameter'}, status=422)
        cutscene_queryset = Cutscene.objects.filter(level=level, name__iexact=cutscene, ending=action == 6)
        if cutscene_queryset.count() != 1:
            return JsonResponse({'message': 'cutscene not found'}, status=422)

    if completion_action:
        prev_rate = Rate.objects.filter(level=level, uid=uid, action__gte=40, action__lte=46).order_by('-time').first()
        if prev_rate:
            prev_rate_field = Rate.ACTION_DICT[prev_rate.action]
            LevelRating.objects.filter(level=level).update(**{prev_rate_field: F(prev_rate_field) - 1})
            prev_rate.delete()

    if launch_action or score_action or completion_action:
        cutscene = str(time.time()) # to provide unique key

    _, created = Rate.objects.get_or_create(
        {'name': level_name, 'author': level_author, 'platform': platform, 'ip': ip}, 
        level=level, uid=uid, action=action, cutscene=cutscene)
    if created:
        if rate_field is not None:
            LevelRating.objects.filter(level=level).update(**{rate_field: F(rate_field) + 1})
        elif cutscene_action:
            cutscene_queryset.update(counter=F("counter") + 1)

        if action in (6, 9) and not level.levelrating.verified:
            if not Cutscene.objects.filter(level=level, ending=True, counter=0).exists():
                LevelRating.objects.filter(level=level).update(verified=True)

    if cutscene_action or action == 9: # autocompletion
        final_cutscene = cutscene_action and cutscene_queryset.first().final
        all_endings = action in (6, 9) and Rate.objects.filter(level=level, uid=uid, action=6).count() >= Cutscene.objects.filter(level=level, ending=True).count()
        if final_cutscene or all_endings:
            prev_rate = Rate.objects.filter(level=level, uid=uid, action__gte=40, action__lte=46).order_by('-time').first()
            if prev_rate:
                prev_rate_field = Rate.ACTION_DICT[prev_rate.action]
                LevelRating.objects.filter(level=level).update(**{prev_rate_field: F(prev_rate_field) - 1})
                prev_rate.delete()

            Rate.objects.get_or_create({'name': level_name, 'author': level_author, 'platform': platform, 'ip': ip},
                level=level, uid=uid, action=41, cutscene=cutscene)
            LevelRating.objects.filter(level=level).update(completions=F('completions') + 1)

    if score_action:
        scores = {r.uid: r.action for r in Rate.objects.filter(level=level, action__gte=20, action__lte=30).order_by('uid', 'time')}.values()
        scores = [s for s in scores if s != 20]
        score = (sum(scores) / len(scores) - 20) / 2 if scores else 0
        LevelRating.objects.filter(level=level).update(score=score, voters=len(scores))

    return JsonResponse({'action': action, 'added': 1 if created else 0}, status=200)


class RatingRetrieve(generics.RetrieveAPIView):
    queryset = LevelRating.objects.all()
    serializer_class = LevelRatingSerializer

    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())
        return get_object_or_404(queryset, level__name=self.request.query_params['name'], level__author=self.request.query_params['author'])

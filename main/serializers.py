from rest_framework import serializers

from main.models import *


class LevelSerializer(serializers.ModelSerializer):
    downloads = serializers.IntegerField(source='levelrating.downloads')
    upvotes = serializers.IntegerField(source='levelrating.upvotes')
    downvotes = serializers.IntegerField(source='levelrating.downvotes')
    complains = serializers.IntegerField(source='levelrating.complains')
    autoverified = serializers.BooleanField(source='levelrating.verified')
    status = serializers.IntegerField(source='levelrating.status')
    score = serializers.FloatField(source='levelrating.score')
    voters = serializers.IntegerField(source='levelrating.voters')

    class Meta:
        model = Level
        fields = ('name', 'author', 'description', 'file_size', 'link', 'icon',
                  'downloads', 'upvotes', 'downvotes', 'complains',
                  'autoverified', 'status', 'score', 'voters', 'size', 'difficulty', 'category')


class CutsceneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cutscene
        fields = ('name', 'ending', 'counter', 'final')


class LevelRatingSerializer(serializers.ModelSerializer):
    cutscenes = CutsceneSerializer(source='level.cutscene_set', many=True)

    class Meta:
        model = LevelRating
        fields = ('downloads', 'upvotes', 'downvotes', 'complains', 'score', 'voters', 'cutscenes', 'winexits',
            'completions', 'backlogged', 'too_hard', 'not_interested', 'cant_progress', 'level_errors',
            'power0', 'power1', 'power2', 'power3', 'power4', 'power5', 'power6', 'power7', 'power8', 'power9', 'power10', 'power11', 'power12')

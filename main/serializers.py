from rest_framework import serializers

from . import models


class LevelSerializer(serializers.ModelSerializer):
    downloads = serializers.IntegerField(source='levelrating.downloads')
    upvotes = serializers.IntegerField(source='levelrating.upvotes')
    downvotes = serializers.IntegerField(source='levelrating.downvotes')

    class Meta:
        model = models.Level
        fields = ('id', 'name', 'author', 'description', 'file_size', 'link', 'icon', 'downloads', 'upvotes', 'downvotes')


class LevelRatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.LevelRating
        fields = ('level', 'downloads', 'upvotes', 'downvotes')

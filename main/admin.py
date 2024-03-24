from django.contrib import admin

from . import models

@admin.register(models.Level)
class LevelAdmin(admin.ModelAdmin):
    ordering = ['author', 'name']

@admin.register(models.LevelRating)
class LevelRatingAdmin(admin.ModelAdmin):
    ordering = ['level.author', 'level.name']

@admin.register(models.Cutscene)
class CutsceneAdmin(admin.ModelAdmin):
    ordering = ['level.author', 'level.name', 'name']

@admin.register(models.Rate)
class RateAdmin(admin.ModelAdmin):
    ordering = ['-time']

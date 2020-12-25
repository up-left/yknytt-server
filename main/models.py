from django.db import models
from django import forms
from django.contrib.postgres.fields import ArrayField


class ChoiceArrayField(ArrayField):
    def formfield(self, **kwargs):
        defaults = {
            'form_class': forms.MultipleChoiceField,
            'choices': self.base_field.choices,
        }
        defaults.update(kwargs)
        return super(ArrayField, self).formfield(**defaults)


class Level(models.Model):
    SIZE_CHOICES = [(0, "Undefined"), (1, "Small"), (2, "Medium"), (3, "Large")]
    DIFFICULTY_CHOICES = [(0, "Undefined"), (1, 'Easy'), (2, 'Normal'), (3, 'Hard'), (4, 'Very Hard'), (5, 'Lunatic')]
    CATEGORY_CHOICES = [(0, "Undefined"), (1, 'Tutorial'), (2, 'Challenge'), (3, 'Puzzle'), (4, 'Maze'), (5, 'Environmental'), (6, 'Playground'), (7, 'Misc')]

    SIZE_DICT = {d: n for n, d in SIZE_CHOICES}
    DIFFICULTY_DICT = {d: n for n, d in DIFFICULTY_CHOICES}
    CATEGORY_DICT = {d: n for n, d in CATEGORY_CHOICES}

    name = models.CharField(max_length=256, db_index=True)
    author = models.CharField(max_length=128, db_index=True)
    description = models.CharField(max_length=512)

    level_hash = models.BinaryField(max_length=64, unique=True)

    size = models.IntegerField(choices=SIZE_CHOICES, db_index=True)
    difficulty = ArrayField(models.IntegerField(choices=DIFFICULTY_CHOICES), size=8, db_index=True)
    category = ArrayField(models.IntegerField(choices=CATEGORY_CHOICES), size=8, db_index=True)

    file_size = models.IntegerField()
    link = models.CharField(max_length=256)
    icon = models.TextField()
    format = models.IntegerField()

    class Meta:
        ordering = ['-levelrating__downloads', 'pk']

    def __str__(self):
        return f'#{self.pk} {self.name} ({self.author})'


class LevelRating(models.Model):
    level = models.OneToOneField(Level, on_delete=models.CASCADE, primary_key=True)
    downloads = models.IntegerField(default=0)
    upvotes = models.IntegerField(default=0)
    downvotes = models.IntegerField(default=0)
    complains = models.IntegerField(default=0)

    def __str__(self):
    	return f'{self.level} +{self.upvotes}/-{self.downvotes} v{self.downloads}'


class Rate(models.Model):
    ACTION_CHOICES = [(0, 'Undefined'), (1, 'Download'), (2, 'Upvote'), (3, 'Downvote'), (4, 'Complain')]
    ACTION_DICT = {1: 'downloads', 2: 'upvotes', 3: 'downvotes', 4: 'complains'}

    level = models.ForeignKey(Level, null=True, on_delete=models.SET_NULL)
    level_hash = models.BinaryField(max_length=64)
    uid = models.UUIDField()
    platform = models.CharField(max_length=16)
    action = models.IntegerField(choices=ACTION_CHOICES)
    time = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=['uid', 'level', 'action'], name='unique_user_rate')]

    def __str__(self):
        return f'{Rate.ACTION_CHOICES[self.action][1]} {self.level} {self.time.strftime("%Y.%m.%d %H:%M:%S %z")}'

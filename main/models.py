from django.db import models
from django import forms
from django.contrib.postgres.fields import ArrayField


class ChoiceArrayField(ArrayField):
    def formfield(self, **kwargs):
        defaults = {
            'form_class': forms.MultipleChoiceField,
            'choices': self.base_field.choices,
            'widget': forms.CheckboxSelectMultiple,
        }
        defaults.update(kwargs)
        return super(ArrayField, self).formfield(**defaults)

    def to_python(self, value):
        res = super().to_python(value)
        if isinstance(res, list):
            value = [self.base_field.to_python(val) for val in res]
        return value


class Level(models.Model):
    SIZE_CHOICES = [(0, "Undefined"), (1, "Small"), (2, "Medium"), (3, "Large")]
    DIFFICULTY_CHOICES = [(0, "Undefined"), (1, 'Easy'), (2, 'Normal'), (3, 'Hard'), (4, 'Very Hard'), (5, 'Lunatic')]
    CATEGORY_CHOICES = [(0, "Undefined"), (1, 'Tutorial'), (2, 'Challenge'), (3, 'Puzzle'), (4, 'Maze'), (5, 'Environmental'), (6, 'Playground'), (7, 'Misc')]

    SIZE_DICT = {d: n for n, d in SIZE_CHOICES}
    DIFFICULTY_DICT = {d: n for n, d in DIFFICULTY_CHOICES}
    CATEGORY_DICT = {d: n for n, d in CATEGORY_CHOICES}

    name = models.CharField(max_length=40, db_index=True)
    author = models.CharField(max_length=40, db_index=True)
    description = models.CharField(max_length=512)

    size = models.IntegerField(choices=SIZE_CHOICES, db_index=True)
    difficulty = ChoiceArrayField(models.IntegerField(choices=DIFFICULTY_CHOICES), size=8, db_index=True)
    category = ChoiceArrayField(models.IntegerField(choices=CATEGORY_CHOICES), size=8, db_index=True)

    file_size = models.IntegerField()
    link = models.CharField(max_length=256)
    icon = models.TextField()
    format = models.IntegerField()

    class Meta:
        constraints = [models.UniqueConstraint(fields=['name', 'author'], name='unique_level')]

    def __str__(self):
        return f'#{self.pk} {self.name} ({self.author})'


class LevelRating(models.Model):
    level = models.OneToOneField(Level, on_delete=models.CASCADE, primary_key=True)
    
    downloads = models.IntegerField(default=0)
    upvotes = models.IntegerField(default=0)
    downvotes = models.IntegerField(default=0)
    complains = models.IntegerField(default=0)
    enters = models.IntegerField(default=0)
    exits = models.IntegerField(default=0)

    power0 = models.IntegerField(default=0)
    power1 = models.IntegerField(default=0)
    power2 = models.IntegerField(default=0)
    power3 = models.IntegerField(default=0)
    power4 = models.IntegerField(default=0)
    power5 = models.IntegerField(default=0)
    power6 = models.IntegerField(default=0)
    power7 = models.IntegerField(default=0)
    power8 = models.IntegerField(default=0)
    power9 = models.IntegerField(default=0)
    power10 = models.IntegerField(default=0)
    power11 = models.IntegerField(default=0)
    power12 = models.IntegerField(default=0)

    verified = models.BooleanField(default=False)
    approved = models.BooleanField(default=False)

    def __str__(self):
    	return f'{"[*]" if self.verified else "[ ]"} {"[+]" if self.approved else "[ ]"} {self.level} +{self.upvotes}/-{self.downvotes} v{self.downloads}'


class Cutscene(models.Model):
    level = models.ForeignKey(Level, null=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=64, db_index=True)
    ending = models.BooleanField()
    counter = models.IntegerField(default=0)

    class Meta:
        constraints = [models.UniqueConstraint(fields=['level', 'name', 'ending'], name='unique_cutscene')]

    def __str__(self):
        return f'{self.level} {self.name} {"*" if self.ending else "+"}{self.counter}'


class Rate(models.Model):
    ACTION_CHOICES = [(0, 'Undefined'), (1, 'Download'), (2, 'Upvote'), (3, 'Downvote'), (4, 'Complain'), (5, 'Cutscene'), (6, 'Ending'), (7, 'Enter'), (8, 'Exit'),
                      (100, 'Run'), (101, 'Climb'), (102, 'Double Jump'), (103, 'High Jump'), (104, 'Eye'), (105, 'Enemy Detector'),
                      (106, 'Umbrella'), (107, 'Hologram'), (108, 'Red Key'), (109, 'Yellow Key'), (110, 'Blue Key'), (111, 'Purple Key'), (112, 'Map')]
    ACTION_CHOICES_DICT = dict(ACTION_CHOICES)

    ACTION_DICT = {1: 'downloads', 2: 'upvotes', 3: 'downvotes', 4: 'complains', 7: 'enters', 8: 'exits',
                   100: 'power0', 101: 'power1', 102: 'power2', 103: 'power3', 104: 'power4', 105: 'power5',
                   106: 'power6', 107: 'power7', 108: 'power8', 109: 'power9', 110: 'power10', 111: 'power11', 112: 'power12'}

    level = models.ForeignKey(Level, null=True, on_delete=models.SET_NULL)
    name = models.CharField(max_length=40, default='')
    author = models.CharField(max_length=40, default='')
    uid = models.UUIDField()
    platform = models.CharField(max_length=16)
    action = models.IntegerField(choices=ACTION_CHOICES)
    cutscene = models.CharField(max_length=64, null=True, default=None)
    time = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=['uid', 'level', 'action', 'cutscene'], name='unique_user_rate')]

    def __str__(self):
        return f'{Rate.ACTION_CHOICES_DICT[self.action]} {self.cutscene if action == 5 or action == 6 else ""} #{self.level_id} {self.name} ({self.author}) {self.time.strftime("%Y.%m.%d %H:%M:%S")}'

from django.db import models
from django import forms


class MyChoiceField(forms.MultipleChoiceField):
    def __init__(self, **kwargs):
        del kwargs['coerce']
        super().__init__(**kwargs)


class ChoiceBitField(models.IntegerField):
    def formfield(self, **kwargs):
        defaults = {
            'choices_form_class': MyChoiceField,
            'choices': self.choices,
            'required': False,
            'widget': forms.CheckboxSelectMultiple,
        }
        defaults.update(kwargs)
        return super().formfield(**defaults)

    def from_db_value(self, value, expression, connection):
        return [i for i, _ in self.choices if (1 << i) & value]

    def validate(self, value, model_instance):
        int_choices = [c for c, _ in self.choices]
        return all(i in int_choices for i in value)

    validators = []

    def get_db_prep_value(self, value, connection, prepared=False):
        return value if isinstance(value, int) else sum(1 << int(i) for i in value)

    def to_python(self, value):
        return self.from_db_value(value, None, None) if isinstance(value, int) else \
                [int(v) for v in value[1:-1].split(', ')] if isinstance(value, str) else [int(i) for i in value]


class Level(models.Model):
    SIZE_CHOICES = [(0, "Undefined"), (1, "Small"), (2, "Medium"), (3, "Large")]
    DIFFICULTY_CHOICES = [(0, "Undefined"), (1, 'Easy'), (2, 'Normal'), (3, 'Hard'), (4, 'Very Hard'), (5, 'Lunatic')]
    CATEGORY_CHOICES = [(0, "Undefined"), (1, 'Tutorial'), (2, 'Challenge'), (3, 'Puzzle'), (4, 'Maze'), (5, 'Environmental'), (6, 'Playground'), (7, 'Misc')]

    SIZE_DICT = {d: n for n, d in SIZE_CHOICES}
    DIFFICULTY_DICT = {d: n for n, d in DIFFICULTY_CHOICES}
    CATEGORY_DICT = {d: n for n, d in CATEGORY_CHOICES}

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=40, db_index=True)
    author = models.CharField(max_length=40, db_index=True)
    description = models.CharField(max_length=512, blank=True, db_index=True)

    size = models.IntegerField(choices=SIZE_CHOICES, db_index=True)
    difficulty = ChoiceBitField(choices=DIFFICULTY_CHOICES, db_index=True)
    category = ChoiceBitField(choices=CATEGORY_CHOICES, db_index=True)

    file_size = models.IntegerField()
    link = models.CharField(max_length=256)
    icon = models.TextField()
    format = models.IntegerField()

    class Meta:
        constraints = [models.UniqueConstraint(fields=['name', 'author'], name='unique_level')]

    def __str__(self):
        return f'#{self.pk} {self.name} ({self.author})'


class LevelRating(models.Model):
    STATUS_CHOICES = [(0, 'Not Verified'), (1, 'Unfinished'), (2, 'Broken'), (3, 'Almost Broken'), (4, 'Partially Playable'), (5, 'Almost Playable'), (6, 'Playable')]
    STATUS_CHOICES_DICT = dict(STATUS_CHOICES)

    level = models.OneToOneField(Level, on_delete=models.CASCADE, primary_key=True)
    
    downloads = models.IntegerField(default=0)
    upvotes = models.IntegerField(default=0)
    downvotes = models.IntegerField(default=0)
    complains = models.IntegerField(default=0)
    enters = models.IntegerField(default=0)
    exits = models.IntegerField(default=0)
    winexits = models.IntegerField(default=0)

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

    in_progress = models.IntegerField(default=0)
    completions = models.IntegerField(default=0)
    backlogged = models.IntegerField(default=0)
    too_hard = models.IntegerField(default=0)
    not_interested = models.IntegerField(default=0)
    cant_progress = models.IntegerField(default=0)
    level_errors = models.IntegerField(default=0)

    score = models.FloatField(default=0)
    voters = models.IntegerField(default=0)
    status = models.IntegerField(default=0, choices=STATUS_CHOICES)
    verified = models.BooleanField(default=False)

    def __str__(self):
    	return f'{"[+]" if self.verified else "[ ]"}[{self.winexits}] {LevelRating.STATUS_CHOICES_DICT[self.status]} {self.level} {self.score:0.2}[{self.voters}] v{self.downloads}'


class Cutscene(models.Model):
    id = models.AutoField(primary_key=True)
    level = models.ForeignKey(Level, null=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=64, db_index=True)
    ending = models.BooleanField()
    counter = models.IntegerField(default=0)

    class Meta:
        constraints = [models.UniqueConstraint(fields=['level', 'name', 'ending'], name='unique_cutscene')]

    def __str__(self):
        return f'{self.level} {self.name} {"*" if self.ending else "+"}{self.counter}'


class Rate(models.Model):
    ACTION_CHOICES = [(0, 'Undefined'), (1, 'Download'), (2, 'Upvote'), (3, 'Downvote'), (4, 'Complain'), 
                      (5, 'Cutscene'), (6, 'Ending'), (7, 'Enter'), (8, 'Exit'), (9, 'Win Exit'), (10, 'Cheat'), (11, 'Complete'),
                      (20, 'Clear rating'), (21, '0.5 star'), (22, 'One star'), (23, '1.5 stars'), (24, 'Two stars'), (25, '2.5 star'),
                      (26, 'Three stars'), (27, '3.5 stars'), (28, 'Four stars'), (29, '4.5 stars'), (30, 'Five stars'),
                      (40, 'In progress'), (41, 'Completed'), (42, 'Backlog'), (43, 'Too hard'), (44, 'Not intereseted'), (45, "Can't progress"), (46, 'Level errors'),
                      (100, 'Run'), (101, 'Climb'), (102, 'Double Jump'), (103, 'High Jump'), (104, 'Eye'), (105, 'Enemy Detector'),
                      (106, 'Umbrella'), (107, 'Hologram'), (108, 'Red Key'), (109, 'Yellow Key'), (110, 'Blue Key'), (111, 'Purple Key'), (112, 'Map')]
    ACTION_CHOICES_DICT = dict(ACTION_CHOICES)

    ACTION_DICT = {1: 'downloads', 2: 'upvotes', 3: 'downvotes', 4: 'complains', 7: 'enters', 8: 'exits', 9: 'winexits', 11: 'completions',
                   40: 'in_progress', 41: 'completions', 42: 'backlogged', 43: 'too_hard', 44: 'not_interested', 45: 'cant_progress', 46: 'level_errors',
                   100: 'power0', 101: 'power1', 102: 'power2', 103: 'power3', 104: 'power4', 105: 'power5',
                   106: 'power6', 107: 'power7', 108: 'power8', 109: 'power9', 110: 'power10', 111: 'power11', 112: 'power12'}

    id = models.AutoField(primary_key=True)
    level = models.ForeignKey(Level, null=True, on_delete=models.SET_NULL)
    name = models.CharField(max_length=40, default='')
    author = models.CharField(max_length=40, default='')
    uid = models.UUIDField()
    platform = models.CharField(max_length=16)
    action = models.IntegerField(choices=ACTION_CHOICES)
    cutscene = models.CharField(max_length=64, null=True, default=None)
    time = models.DateTimeField(auto_now=True)
    ip = models.CharField(max_length=48, null=True, default=None)

    class Meta:
        constraints = [models.UniqueConstraint(fields=['uid', 'level', 'action', 'cutscene'], name='unique_user_rate')]

    def __str__(self):
        return f'{Rate.ACTION_CHOICES_DICT[self.action]} {self.cutscene if self.action in (5, 6) else ""} #{self.level_id} {self.name} ({self.author}) {self.time.strftime("%Y.%m.%d %H:%M:%S")} {{{self.uid}}}'

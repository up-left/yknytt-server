# Generated by Django 4.2.2 on 2024-04-18 06:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0005_levelrating_score_alter_levelrating_status_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='levelrating',
            name='voters',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='rate',
            name='action',
            field=models.IntegerField(choices=[(0, 'Undefined'), (1, 'Download'), (2, 'Upvote'), (3, 'Downvote'), (4, 'Complain'), (5, 'Cutscene'), (6, 'Ending'), (7, 'Enter'), (8, 'Exit'), (9, 'Win Exit'), (10, 'Cheat'), (11, 'Complete'), (20, 'Clear rating'), (21, '0.5 star'), (22, 'One star'), (23, '1.5 stars'), (24, 'Two stars'), (25, '2.5 star'), (26, 'Three stars'), (27, '3.5 stars'), (28, 'Four stars'), (29, '4.5 stars'), (30, 'Five stars'), (100, 'Run'), (101, 'Climb'), (102, 'Double Jump'), (103, 'High Jump'), (104, 'Eye'), (105, 'Enemy Detector'), (106, 'Umbrella'), (107, 'Hologram'), (108, 'Red Key'), (109, 'Yellow Key'), (110, 'Blue Key'), (111, 'Purple Key'), (112, 'Map')]),
        ),
    ]

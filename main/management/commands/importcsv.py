from django.core.management.base import BaseCommand, CommandError
import csv
import urllib.parse
from main.models import *

class Command(BaseCommand):
    help = 'Import CSV extracted from parsed KS levels'

    def add_arguments(self, parser):
        parser.add_argument('filename', type=str)
        parser.add_argument('--update', dest='update', action='store_true')
        parser.set_defaults(update=False)

    def handle(self, *args, **options):
        new_counter = 0
        total_counter = 0

        with open(options['filename'], 'rt') as f:
            reader = csv.reader(f)
            for row in reader:
                level = {
                    'name': row[1],
                    'author': row[2],
                    'description': row[8], 
                    'size': Level.SIZE_DICT.get(row[3], 0), 
                    'difficulty': sum(1 << Level.DIFFICULTY_DICT.get(d, 0) for d in row[4].split(';')), 
                    'category': sum(1 << Level.CATEGORY_DICT.get(d, 0) for d in row[5].split(';')),
                    'file_size': row[7],
                    'link': row[0],
                    'icon': row[11],
                    'format': row[6]
                }
                if options['update']:
                    level, created = Level.objects.update_or_create(level, name=row[1], author=row[2])
                else:
                    level, created = Level.objects.get_or_create(level, name=row[1], author=row[2])

                if created:
                    new_counter += 1
                    LevelRating.objects.create(level=level)

                if created or options['update']:
                    cutscenes = row[9].split(';') if row[9] else []
                    Cutscene.objects.filter(level=level, ending=True).exclude(name__in=cutscenes).delete()
                    for cutscene in cutscenes:
                        Cutscene.objects.get_or_create(level=level, name=cutscene, ending=True)

                if created or options['update']:
                    cutscenes = row[10].split(';') if row[10] else []
                    Cutscene.objects.filter(level=level, ending=False).exclude(name__in=cutscenes).delete()
                    for cutscene in cutscenes:
                        Cutscene.objects.get_or_create(level=level, name=cutscene, ending=False)

                total_counter += 1

        self.stdout.write(self.style.SUCCESS(f'Finished ({total_counter} rows total, {new_counter} rows new)'))

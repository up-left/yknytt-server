from django.core.management.base import BaseCommand, CommandError
import csv
import hashlib
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
                m = hashlib.sha256()
                m.update((row[1] + row[2]).encode())
                level_hash = m.digest()

                level = {
                    'name': row[1],
                    'author': row[2],
                    'description': row[8], 
                    'level_hash': level_hash,
                    'size': Level.SIZE_DICT.get(row[3], 0), 
                    'difficulty': [Level.DIFFICULTY_DICT.get(d, 0) for d in row[4].split(';')], 
                    'category': [Level.CATEGORY_DICT.get(d, 0) for d in row[5].split(';')],
                    'file_size': row[7],
                    'link': row[0],
                    'icon': row[11],
                    'format': row[6]
                }
                if options['update']:
                    level, created = Level.objects.update_or_create(level, level_hash=level_hash)
                else:
                    level, created = Level.objects.get_or_create(level, level_hash=level_hash)

                if created:
                    new_counter += 1
                    LevelRating.objects.create(level=level)

                if (created or options['update']) and row[9]:
                    Cutscene.objects.filter(level=level, ending=True).exclude(name__in=row[9].split(';')).delete()
                    for cutscene in row[9].split(';'):
                        Cutscene.objects.get_or_create(level=level, name=cutscene, ending=True)
                if (created or options['update']) and row[10]:
                    Cutscene.objects.filter(level=level, ending=False).exclude(name__in=row[10].split(';')).delete()
                    for cutscene in row[10].split(';'):
                        Cutscene.objects.get_or_create(level=level, name=cutscene, ending=False)

                total_counter += 1

        self.stdout.write(self.style.SUCCESS(f'Finished ({total_counter} rows total, {new_counter} rows new)'))

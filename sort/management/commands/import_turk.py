from django.core.management.base import BaseCommand
from sort.models import Object
from sort.models import Ranking
import csv

class Command(BaseCommand):
    args = "none"
    help = "Loads a turk.csv file into the database. Should be called after an import command."

    def handle(self, *args, **options):
        Object.objects.all().delete()
        
        img_root = "images/"

        with open('turk_results.csv') as f:
            reader = csv.reader(f, delimiter=',')
            key = {}
            for row in reader:
                if not key:
                    for i,v in enumerate(row):
                        key[v] = i
                    continue

                n1 = row[key['Input.image1url']].split('/')[-1]
                n2 = row[key['Input.image2url']].split('/')[-1]
                image1 = Object.objects.filter(name=n1)
                if not image1:
                    image1 = Object(name=n1, image = img_root + n1, rank=0.0)
                    image1.save()
                else:
                    image1 = image1[0]

                image2 = Object.objects.filter(name=n2)
                if not image2:
                    image2 = Object(name=n2, image = img_root + n2, rank=0.0)
                    image2.save()
                else:
                    image2 = image2[0]

                r = Ranking(user=row[key['WorkerId']], first=image1,
                            second=image2,
                            value=float(row[key['Answer.Rating']]))
                r.save()

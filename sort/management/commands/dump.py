from django.core.management.base import BaseCommand
from sort.models import Object
from sort.models import Ranking

class Command(BaseCommand):
    args = "none"
    help = "prints db contents"

    def handle(self, *args, **options):
        for o in Object.objects.all():
            print(o)
        for r in Ranking.objects.all():
            print(r)
        #self.stdout.write(str(onlyfiles))



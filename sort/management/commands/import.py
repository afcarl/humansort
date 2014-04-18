from django.core.management.base import BaseCommand, CommandError
from os.path import isfile, join
from sort.models import Object
from os import listdir

class Command(BaseCommand):
    args = "none"
    help = "creates objects for all the images in the image dir"

    def handle(self, *args, **options):
        images_path = 'images'
        onlyfiles = [f for f in listdir(images_path) if isfile(join(images_path, f))]

        self.stdout.write(str(onlyfiles))


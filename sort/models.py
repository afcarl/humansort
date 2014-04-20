from django.db import models

# Create your models here.
class Object(models.Model):
    name = models.CharField(max_length=200)
    image = models.ImageField(upload_to='images')
    rank = models.FloatField(default=0.0)
    confidence = models.FloatField(default=0.0)

    def __str__(self):
        return str((self.name, self.rank))

class Ranking(models.Model):
    user = models.CharField(max_length=200)
    first = models.ForeignKey(Object, related_name='ranking_first')
    second = models.ForeignKey(Object, related_name='ranking_second')
    value = models.IntegerField()

    def __str__(self):
        return str((self.user, self.first, self.second, self.value))

#class Queue(models.Model):
#    first = models.ForeignKey(Object, related_name='queue_first')
#    second = models.ForeignKey(Object, related_name='queue_second')
#
#    def __str__(self):
#        return str((self.first, self.second))



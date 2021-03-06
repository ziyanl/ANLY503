from django.db import models

# Create your models here.
class Sonnet(models.Model):
    text = models.CharField(max_length=1400)

    @property	
    def score(self):
        upvotes = Score.objects.filter(sonnet=self, value=1).count()
        downvotes = Score.objects.filter(sonnet=self, value=0).count()
        return upvotes - downvotes


class Score(models.Model):
    sonnet = models.ForeignKey(Sonnet)
    ip = models.CharField(max_length=40)
    value = models.IntegerField()

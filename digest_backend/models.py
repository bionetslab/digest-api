from django.db import models


class Example(models.Model):
    name = models.CharField(max_length=128, default='empty', unique=False)
    count = models.IntegerField()

    def __str__(self):
        return f'{self.name}-{self.count}'

    class Example:
        unique_together = ('name', 'count')
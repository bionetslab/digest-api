from django.db import models

class Task(models.Model):
    uid = models.CharField(max_length=36, unique=True, primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)

    mode = models.CharField(max_length=32, choices=[('set','set'),('network','network'),('cluster','cluster'),('id-set','id-set'),('set-set','set-set')])
    parameters = models.TextField()
    request = models.TextField()

    started_at = models.DateTimeField(null=True)
    finished_at = models.DateTimeField(null=True)
    worker_id = models.CharField(max_length=128, null=True)
    job_id = models.CharField(max_length=128, null=True)
    done = models.BooleanField(default=False)
    failed = models.BooleanField(default=False)
    status = models.CharField(max_length=255, null=True)
    version = models.CharField(max_length=10, null=False, default="2022-01-01")

    progress = models.FloatField(default=0.0)
    result = models.TextField(null=True)


class Attachment(models.Model):
    uid = models.CharField(max_length=36)
    type = models.CharField(max_length=4, choices=[('png','png'),('csv','csv')])
    name = models.CharField(max_length=128, unique=True, primary_key=True)
    content = models.TextField(null=False)
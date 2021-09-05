from django.db import models
import uuid

# Create your models here.

role_enum = [('student', 'student'), ('teacher', 'teacher'), ('admin', 'admin'), ('undefined', 'undefined')]


class User(models.Model):
    uid = models.UUIDField(primary_key=True, default=uuid.uuid1, editable=False)
    name = models.CharField(max_length=128, unique=True)
    role = models.CharField(max_length=10, choices=role_enum)
    password = models.CharField(max_length=256, blank=False)
    email = models.EmailField(max_length=128, unique=True, blank=False)
    logup_time = models.DateTimeField(auto_now_add=True)    # first time create
    login_time = models.DateTimeField(auto_now=True)        # every time Model.save()
    login_count = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["logup_time"]

from django.db import models
import uuid

# Create your models here.
from Login.models import User

state_enum = [('Open', 'Open'), ('Closed', 'Closed'), ('Helpless', 'Helpless')]


class Suggestions(models.Model):
    uid = models.UUIDField(primary_key=True, default=uuid.uuid1, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    advise = models.CharField(max_length=512)
    detail = models.TextField()
    state = models.CharField(max_length=10, choices=state_enum, default="Open")
    anonymity = models.BooleanField(default=True)
    create_time = models.DateTimeField(auto_now_add=True)
    deal_time = models.DateTimeField(auto_now=True)

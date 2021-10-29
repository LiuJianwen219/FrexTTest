import uuid

from django.db import models

# Create your models here.
from Home.models import TestList
from Login.models import User


state_success = "success"
state_fail = "fail"
state_enum = [
    (state_success, state_success),
    (state_fail, state_fail),
]

type_save = "save"
type_sim = "sim"
type_enum = [
    (type_save, type_save),
    (type_sim, type_sim),
]


class SimulateRecord(models.Model):
    uid = models.UUIDField(primary_key=True, default=uuid.uuid1, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    test = models.ForeignKey(TestList, on_delete=models.CASCADE)
    code = models.TextField()
    sim_code = models.TextField()
    type = models.CharField(max_length=8, choices=type_enum, default=type_save)
    state = models.CharField(max_length=8, choices=state_enum, default=state_fail)
    create_time = models.DateTimeField(auto_now_add=True)
    sim_result = models.TextField()
    sim_result_url = models.TextField()

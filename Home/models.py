from django.db import models
from Login.models import User
import uuid


# Create your models here.

type_enum = [
    ('combination', 'combination'),
    ('time_sequence', 'time_sequence'),
    ('system_all', 'system_all'),
    ('undefined', 'undefined'),
]


class TestList(models.Model):
    uid = models.UUIDField(primary_key=True, default=uuid.uuid1, editable=False)
    title = models.CharField(max_length=256)
    file_path = models.CharField(max_length=256)
    content = models.TextField()
    type = models.CharField(max_length=16, choices=type_enum)
    grade = models.DecimalField(max_digits=5, decimal_places=2)  # max 999.99
    submit_number = models.PositiveIntegerField(default=0)
    pass_number = models.PositiveIntegerField(default=0)
    topic = models.CharField(max_length=128, unique=True)
    top_module_name = models.CharField(max_length=256)
    author = models.CharField(max_length=128, default="admin")
    email = models.CharField(max_length=128, default="21921088@zju.edu.cn")
    company = models.CharField(max_length=128, default="ARClab")
    visibility = models.BooleanField(default=False)
    create_time = models.DateTimeField(auto_now_add=True)


class TestFile(models.Model):
    uid = models.UUIDField(primary_key=True, default=uuid.uuid1, editable=False)
    test = models.ForeignKey(TestList, on_delete=models.CASCADE)
    file_path = models.CharField(max_length=512)
    content = models.TextField()


state_enum = [
    ('pass', 'pass'),
    ('try', 'try'),
    ('unknown', "unknown")
]


class SubmitList(models.Model):
    uid = models.UUIDField(primary_key=True, default=uuid.uuid1, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    test = models.ForeignKey(TestList, on_delete=models.CASCADE)
    score = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)     # max 999.99
    state = models.CharField(max_length=8, choices=state_enum)      # whether pass
    submit_time = models.DateTimeField(auto_now_add=True)    # first time create
    code = models.TextField()
    status = models.CharField(max_length=256)   # testing flow status, refresh in process
    message = models.TextField()                # testing flow message, refresh/append in process
    result = models.TextField()
    cycle = models.IntegerField(default=-1)
    compile_start_time = models.DateTimeField()     # start compile time
    compile_end_time = models.DateTimeField()       # end compile time
    test_start_time = models.DateTimeField()        # start test time
    test_end_time = models.DateTimeField()          # end test time


class ValidSubmitList(models.Model):
    uid = models.UUIDField(primary_key=True, default=uuid.uuid1, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    test = models.ForeignKey(TestList, on_delete=models.CASCADE)
    submit = models.ForeignKey(SubmitList, on_delete=models.CASCADE)


class BestSubmitList(models.Model):
    uid = models.UUIDField(primary_key=True, default=uuid.uuid1, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    test = models.ForeignKey(TestList, on_delete=models.CASCADE)
    submit = models.ForeignKey(SubmitList, on_delete=models.CASCADE)





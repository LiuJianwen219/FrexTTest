from django.db import models
import uuid

# Create your models here.

role_student = 'student'
role_teacher = 'teacher'
role_admin = 'admin'
role_undefined = 'undefined'
role_sub_student = "student_0"
role_enum = [('student', 'student'),
             ('teacher', 'teacher'),
             ('admin', 'admin'),
             ('undefined', 'undefined'),
             (role_sub_student, role_sub_student)]


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


class LoginRecord(models.Model):
    uid = models.UUIDField(primary_key=True, default=uuid.uuid1, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    host = models.CharField(max_length=64)
    port = models.CharField(max_length=32)
    login_index = models.PositiveIntegerField(default=0)
    login_time = models.DateTimeField(auto_now_add=True)
    logout_time = models.DateTimeField(auto_now=True)

from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    name = models.CharField(verbose_name="用户昵称")
    mobile = models.CharField(max_length=15, unique=True, verbose_name="手机号码")
    avatar = models.ImageField(upload_to="avatar", null=True, blank=True, verbose_name="头像")

    class Meta:
        db_table = 'res_users'
        verbose_name = '用户'
        verbose_name_plural = verbose_name


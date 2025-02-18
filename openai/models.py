from django.db import models
from users.models import User


class OpenAiToken(models.Model):
    class Meta:
        db_table = 'openai_token'
        verbose_name = 'Openai Token'
        verbose_name_plural = verbose_name

    active = models.BooleanField(default=True, verbose_name="状态")
    code = models.CharField(unique=True, verbose_name="API TOKEN")
    api_type = models.CharField(verbose_name="API类型")
    quota = models.FloatField(verbose_name="总额度", default=0)
    used_quota = models.FloatField(verbose_name="已使用额度", default=0)
    remain_quota = models.FloatField(verbose_name="剩余额度", editable=False, default=0)
    create_date = models.DateTimeField(auto_now_add=True, verbose_name="创建日期")
    write_date = models.DateTimeField(auto_now=True, verbose_name="修改日期")

    def save(self, *args, **kwargs):
        # 在保存之前计算剩余额度
        # 确保 quota 和 used_quota 都是浮点数
        quota_value = self.quota if self.quota is not None else 0.0
        used_quota_value = self.used_quota if self.used_quota is not None else 0.0
        self.remain_quota = quota_value - used_quota_value
        if self.remain_quota <= 0:
            self.active = False
        self.active = True
        # 调用父类的 save 方法
        super().save(*args, **kwargs)

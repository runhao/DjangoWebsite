from django.db import models


class OpenAiKey(models.Model):
    class Meta:
        db_table = 'openai_key'
        verbose_name = 'Openai Key'
        verbose_name_plural = verbose_name

    active = models.BooleanField(default=True, verbose_name="状态")
    code = models.CharField(unique=True, verbose_name="API KEY")
    api_type = models.CharField(verbose_name="API类型")
    quota = models.FloatField(verbose_name="总额度", default=0)
    usage = models.FloatField(verbose_name="已使用额度", default=0)
    remaining_balance = models.FloatField(verbose_name="剩余额度", editable=False, default=0)  # 新增字段

    def save(self, *args, **kwargs):
        # 在保存之前计算剩余额度
        # 确保 quota 和 usage 都是浮点数
        quota_value = self.quota if self.quota is not None else 0.0
        usage_value = self.usage if self.usage is not None else 0.0
        self.remaining_balance = quota_value - usage_value
        if self.remaining_balance <= 0:
            self.active = False
        # 调用父类的 save 方法
        super().save(*args, **kwargs)

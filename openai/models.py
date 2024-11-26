from django.db import models


class OpenAiKey(models.Model):
    code = models.CharField(unique=True, verbose_name="API KEY")
    active = models.BooleanField(default=True, verbose_name="状态")

    class Meta:
        db_table = 'openai.key'
        verbose_name = 'Openai Key'
        verbose_name_plural = verbose_name

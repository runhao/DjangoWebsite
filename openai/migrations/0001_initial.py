# Generated by Django 4.2 on 2024-11-26 07:39

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='OpenAiKey',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(unique=True, verbose_name='API KEY')),
                ('active', models.BooleanField(default=True, verbose_name='状态')),
            ],
            options={
                'verbose_name': 'Openai Key',
                'verbose_name_plural': 'Openai Key',
                'db_table': 'openai.key',
            },
        ),
    ]
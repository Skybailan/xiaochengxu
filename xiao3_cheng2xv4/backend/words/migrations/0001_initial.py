# Generated manually for local setup
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='DailyWord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_openid', models.CharField(db_index=True, max_length=64, verbose_name='用户 OpenID')),
                ('word', models.CharField(db_index=True, max_length=128, verbose_name='英文单词')),
                ('translation', models.CharField(max_length=255, verbose_name='中文翻译')),
                ('daily_sentence', models.TextField(verbose_name='日常句式')),
                ('daily_sentence_translation', models.TextField(blank=True, default='null', verbose_name='日常句中文')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
            ],
            options={
                'verbose_name': '日常单词',
                'verbose_name_plural': '日常单词',
                'ordering': ['id'],
                'unique_together': {('user_openid', 'word')},
            },
        ),
        migrations.CreateModel(
            name='ProWord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_openid', models.CharField(db_index=True, max_length=64, verbose_name='用户 OpenID')),
                ('word', models.CharField(db_index=True, max_length=128, verbose_name='英文单词')),
                ('translation_with_pos', models.CharField(max_length=255, verbose_name='中文翻译（含词性）')),
                ('memory_method', models.TextField(verbose_name='特殊记忆方法')),
                ('daily_sentence', models.TextField(verbose_name='日常句式')),
                ('daily_sentence_translation', models.TextField(blank=True, default='null', verbose_name='日常句中文')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
            ],
            options={
                'verbose_name': '专业单词',
                'verbose_name_plural': '专业单词',
                'ordering': ['id'],
                'unique_together': {('user_openid', 'word')},
            },
        ),
    ]

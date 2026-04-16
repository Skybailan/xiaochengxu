from django.db import models


class DailyWord(models.Model):
    user_openid = models.CharField('用户 OpenID', max_length=64, db_index=True)
    word = models.CharField('英文单词', max_length=128, db_index=True)
    translation = models.CharField('中文翻译', max_length=255)
    daily_sentence = models.TextField('日常句式')
    daily_sentence_translation = models.TextField('日常句中文', default='null', blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '日常单词'
        verbose_name_plural = '日常单词'
        ordering = ['id']
        unique_together = ('user_openid', 'word')

    def __str__(self):
        return f'{self.word} - {self.translation}'


class ProWord(models.Model):
    user_openid = models.CharField('用户 OpenID', max_length=64, db_index=True)
    word = models.CharField('英文单词', max_length=128, db_index=True)
    translation_with_pos = models.CharField('中文翻译（含词性）', max_length=255)
    memory_method = models.TextField('特殊记忆方法')
    daily_sentence = models.TextField('日常句式')
    daily_sentence_translation = models.TextField('日常句中文', default='null', blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '专业单词'
        verbose_name_plural = '专业单词'
        ordering = ['id']
        unique_together = ('user_openid', 'word')

    def __str__(self):
        return f'{self.word} - {self.translation_with_pos}'

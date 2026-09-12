from django.db import models


class CreatedModel(models.Model):
    created_at = models.DateTimeField("Создан", auto_now_add=True)

    class Meta:
        abstract = True


class TimestampedModel(CreatedModel):
    updated_at = models.DateTimeField("Изменён", auto_now=True)

    class Meta:
        abstract = True

from django.db import models
import pytz


class Host(models.Model):
    TIMEZONES = tuple(zip(pytz.all_timezones, pytz.all_timezones))
    hostname = models.CharField(max_length=100, unique=True)
    is_active = models.BooleanField(default=True)
    timezone = models.CharField(max_length=32, choices=TIMEZONES,
                                default='Europe/Moscow')

    def __str__(self):
        return self.hostname
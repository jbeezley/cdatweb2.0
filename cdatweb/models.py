from __future__ import unicode_literals

from django.db import models

class User(models.Model):
    open_id = models.CharField(max_length=512)

# class Settings(models.Model):
#    user = models.ForeignKey(User, on_delete=models.CASCADE)

# class Saved_State(models.Model):


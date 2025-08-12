# core/models.py
from django.db import models
from django.contrib.auth.models import User
from django.db.models import JSONField 


class SearchResult(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    query = models.CharField(max_length=255)
    results = JSONField()  # Django 3.1+ supports native JSONField
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.query

from django.db import models
from django.conf import settings

class ChatMessage(models.Model):
    """Stores chat history between user and chatbot."""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    query = models.TextField()
    response = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


class Product(models.Model):
    """Stores product data extracted from catalogue."""
    
    part_no = models.CharField(max_length=100, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    price = models.FloatField(null=True, blank = True)
    raw_data = models.JSONField()

    source = models.CharField(max_length=50, default="source_1")
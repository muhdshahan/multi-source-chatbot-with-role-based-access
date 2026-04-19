from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.

class User(AbstractUser):
    ROLE_CHOICES = (
        ("user1", "User 1"),
        ("user2", "User 2"),
        ("user3", "User 3"),
    )

    role = models.CharField(max_length=10, choices=ROLE_CHOICES)

    def get_allowed_sources(self):
        if self.role == "user1":
            return ["source_1", "source_2"]
        elif self.role == "user2":
            return ["source_1", "source_3"]
        elif self.role == "user3":
            return ["source_2", "source_3"]
        return []
    
    

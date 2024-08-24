
from django.utils import timezone
from datetime import timedelta
from django.db import models

class TemporaryUser(models.Model):
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True, blank=False, null=False)
    password = models.CharField(max_length=128)
    verification_code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username


    @classmethod
    def cleanup_expired(cls):
        """Delete TemporaryUser entries older than 5 minutes."""
        cutoff_time = timezone.now() - timedelta(minutes=5)
        cls.objects.filter(created_at__lt=cutoff_time).delete()
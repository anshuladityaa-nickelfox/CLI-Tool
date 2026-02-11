from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Email(models.Model):
    subject = models.CharField(max_length=255)
    body = models.TextField()
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_emails')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.subject

    class Meta:
        ordering = ['-created_at']
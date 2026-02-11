from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class ErrorLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='error_logs')
    error_message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Error Log for {self.user.username}'

    class Meta:
        ordering = ['-created_at']
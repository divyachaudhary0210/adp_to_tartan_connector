from django.db import models
from django.utils import timezone

class SourceEmployee(models.Model):
    source_id = models.CharField(max_length=128, unique=True)
    raw_json = models.JSONField()
    fetched_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"SourceEmployee {self.source_id}"

class UnifiedEmployee(models.Model):
    employee_number = models.CharField(max_length=64, unique=True)
    unified_json = models.JSONField()
    transformed_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"UnifiedEmployee {self.employee_number}"

class FieldMapping(models.Model):
    source_path = models.CharField(max_length=255, help_text="e.g. adp.employeeId")
    unified_path = models.CharField(max_length=255, help_text="e.g. employee_number")
    description = models.TextField(blank=True, default="")

    def __str__(self):
        return f"{self.source_path} -> {self.unified_path}"

class OAuthClient(models.Model):
    client_id = models.CharField(max_length=128, unique=True)
    client_secret = models.CharField(max_length=256)
    name = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"OAuthClient {self.client_id}"

class AccessToken(models.Model):
    token = models.CharField(max_length=256, unique=True)
    client = models.ForeignKey(OAuthClient, on_delete=models.CASCADE)
    expires_at = models.DateTimeField()

    def __str__(self):
        return f"Token {self.token} (client={self.client.client_id})"

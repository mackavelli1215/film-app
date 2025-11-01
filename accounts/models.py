import uuid
from django.db import models
from django.contrib.auth.models import User


class Company(models.Model):
    COMPANY_SIZES = [
        ('startup', 'Startup (1-10 people)'),
        ('small', 'Small (11-50 people)'),
        ('medium', 'Medium (51-200 people)'),
        ('large', 'Large (200+ people)'),
    ]
    
    TIER_CHOICES = [
        ('free', 'Free'),
        ('pro', 'Pro'),
        ('enterprise', 'Enterprise'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    size = models.CharField(max_length=20, choices=COMPANY_SIZES, default='startup')
    tier = models.CharField(max_length=20, choices=TIER_CHOICES, default='free')
    settings = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Companies"
    
    def __str__(self):
        return self.name


class Profile(models.Model):
    ROLE_CHOICES = [
        ('owner', 'Owner'),
        ('admin', 'Admin'),
        ('producer', 'Producer'),
        ('coordinator', 'Coordinator'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='members')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='coordinator')
    
    def __str__(self):
        return f"{self.user.username} - {self.company.name}"
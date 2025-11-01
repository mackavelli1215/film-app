import uuid
from decimal import Decimal
from django.db import models
from projects.models import Project


class Grant(models.Model):
    GRANT_TYPES = [
        ('development', 'Development'),
        ('production', 'Production'),
        ('post_production', 'Post Production'),
        ('distribution', 'Distribution'),
        ('general', 'General'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    organization = models.CharField(max_length=200)
    url = models.URLField()
    deadline = models.DateField()
    amount_min = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    amount_max = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    currency = models.CharField(max_length=3, default='USD')
    grant_type = models.CharField(max_length=20, choices=GRANT_TYPES, default='general')
    eligibility_criteria = models.JSONField(default=dict)
    application_requirements = models.JSONField(default=dict)
    location_restrictions = models.JSONField(default=dict)
    project_types = models.JSONField(default=list)  # Array of supported project types
    scraped_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    source = models.CharField(max_length=100, default='manual')
    
    class Meta:
        ordering = ['deadline']
    
    def __str__(self):
        return f"{self.title} - {self.organization}"


class GrantMatch(models.Model):
    MATCH_STATUS_CHOICES = [
        ('suggested', 'Suggested'),
        ('applied', 'Applied'),
        ('awarded', 'Awarded'),
        ('rejected', 'Rejected'),
    ]

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='grant_matches')
    grant = models.ForeignKey(Grant, on_delete=models.CASCADE, related_name='matches')
    match_score = models.IntegerField(default=0)  # 0-100 score
    match_reasoning = models.TextField()
    status = models.CharField(max_length=20, choices=MATCH_STATUS_CHOICES, default='suggested')
    applied_at = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['project', 'grant']
        ordering = ['-match_score', 'grant__deadline']
    
    def __str__(self):
        return f"{self.project.name} -> {self.grant.title} ({self.match_score}%)"
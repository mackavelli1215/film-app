import uuid
from decimal import Decimal
from django.db import models
from projects.models import Project


class Festival(models.Model):
    TIER_CHOICES = [
        ('a_list', 'A-List'),
        ('regional', 'Regional'),
        ('genre', 'Genre-Specific'),
        ('online', 'Online'),
        ('student', 'Student'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    website_url = models.URLField()
    submission_url = models.URLField(blank=True)
    dates = models.JSONField(default=dict)  # Start date, end date, key events
    deadline_early = models.DateField(null=True, blank=True)
    deadline_regular = models.DateField(null=True, blank=True)
    deadline_late = models.DateField(null=True, blank=True)
    fee_early = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    fee_regular = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    fee_late = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    currency = models.CharField(max_length=3, default='USD')
    tier = models.CharField(max_length=20, choices=TIER_CHOICES, default='regional')
    genres = models.JSONField(default=list)  # Accepted genres
    eligibility_criteria = models.JSONField(default=dict)
    awards = models.JSONField(default=list)  # List of awards offered
    prestige_score = models.IntegerField(default=50)  # 0-100 prestige rating
    scraped_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-prestige_score', 'deadline_regular']
    
    def __str__(self):
        return f"{self.name} ({self.location})"


class FestivalMatch(models.Model):
    MATCH_STATUS_CHOICES = [
        ('considering', 'Considering'),
        ('submitted', 'Submitted'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='festival_matches')
    festival = models.ForeignKey(Festival, on_delete=models.CASCADE, related_name='matches')
    match_score = models.IntegerField(default=0)  # 0-100 score
    strategy_notes = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=MATCH_STATUS_CHOICES, default='considering')
    submitted_at = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['project', 'festival']
        ordering = ['-match_score', 'festival__deadline_regular']
    
    def __str__(self):
        return f"{self.project.name} -> {self.festival.name} ({self.match_score}%)"
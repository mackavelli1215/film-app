import uuid
from decimal import Decimal
from django.db import models
from projects.models import Project


class ScriptBreakdown(models.Model):
    project = models.OneToOneField(Project, on_delete=models.CASCADE, related_name='breakdown')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Breakdown for {self.project.name}"


class Scene(models.Model):
    INT_EXT_CHOICES = [
        ('INT', 'Interior'),
        ('EXT', 'Exterior'),
    ]
    
    DAY_NIGHT_CHOICES = [
        ('DAY', 'Day'),
        ('NIGHT', 'Night'),
        ('DAWN', 'Dawn'),
        ('DUSK', 'Dusk'),
    ]
    
    COMPLEXITY_CHOICES = [
        ('simple', 'Simple'),
        ('medium', 'Medium'),
        ('complex', 'Complex'),
        ('very_complex', 'Very Complex'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    breakdown = models.ForeignKey(ScriptBreakdown, on_delete=models.CASCADE, related_name='scenes')
    number = models.IntegerField()
    slug = models.CharField(max_length=100)  # Short identifier like "INT. COFFEE SHOP - DAY"
    header = models.CharField(max_length=200)  # Full scene header
    int_ext = models.CharField(max_length=3, choices=INT_EXT_CHOICES)
    day_night = models.CharField(max_length=5, choices=DAY_NIGHT_CHOICES)
    location = models.CharField(max_length=200)
    characters = models.JSONField(default=list)  # List of character names
    est_shoot_hours = models.DecimalField(max_digits=4, decimal_places=2, default=Decimal('1.0'))
    complexity = models.CharField(max_length=20, choices=COMPLEXITY_CHOICES, default='simple')
    special = models.JSONField(default=dict, blank=True)  # Special requirements, equipment, etc.
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['number']
        unique_together = ['breakdown', 'number']
    
    def __str__(self):
        return f"Scene {self.number}: {self.slug}"


class Character(models.Model):
    breakdown = models.ForeignKey(ScriptBreakdown, on_delete=models.CASCADE, related_name='characters')
    name = models.CharField(max_length=100)
    meta = models.JSONField(default=dict, blank=True)  # Age, description, casting notes
    
    class Meta:
        unique_together = ['breakdown', 'name']
    
    def __str__(self):
        return self.name


class Location(models.Model):
    LOCATION_TYPES = [
        ('studio', 'Studio'),
        ('practical', 'Practical Location'),
        ('outdoor', 'Outdoor'),
        ('green_screen', 'Green Screen'),
    ]
    
    breakdown = models.ForeignKey(ScriptBreakdown, on_delete=models.CASCADE, related_name='locations')
    name = models.CharField(max_length=200)
    type = models.CharField(max_length=20, choices=LOCATION_TYPES, default='practical')
    meta = models.JSONField(default=dict, blank=True)  # Address, contact, requirements
    
    class Meta:
        unique_together = ['breakdown', 'name']
    
    def __str__(self):
        return self.name
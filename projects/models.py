import uuid
from django.db import models
from accounts.models import Company


class Project(models.Model):
    PROJECT_TYPES = [
        ('feature', 'Feature Film'),
        ('short', 'Short Film'),
        ('documentary', 'Documentary'),
        ('series', 'TV Series'),
        ('commercial', 'Commercial'),
        ('music_video', 'Music Video'),
    ]
    
    STATUS_CHOICES = [
        ('development', 'Development'),
        ('pre_production', 'Pre-Production'),
        ('production', 'Production'),
        ('post_production', 'Post-Production'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    GENRE_CHOICES = [
        ('action', 'Action'),
        ('adventure', 'Adventure'),
        ('comedy', 'Comedy'),
        ('drama', 'Drama'),
        ('horror', 'Horror'),
        ('romance', 'Romance'),
        ('thriller', 'Thriller'),
        ('sci_fi', 'Science Fiction'),
        ('fantasy', 'Fantasy'),
        ('documentary', 'Documentary'),
        ('animation', 'Animation'),
    ]
    
    BUDGET_RANGES = [
        ('micro', 'Micro ($0-50K)'),
        ('low', 'Low Budget ($50K-1M)'),
        ('medium', 'Medium Budget ($1M-20M)'),
        ('high', 'High Budget ($20M+)'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='projects')
    name = models.CharField(max_length=200)
    type = models.CharField(max_length=20, choices=PROJECT_TYPES, default='feature')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='development')
    genre = models.CharField(max_length=20, choices=GENRE_CHOICES, default='drama')
    logline = models.TextField(blank=True)
    budget_range = models.CharField(max_length=20, choices=BUDGET_RANGES, default='micro')
    timeline = models.JSONField(default=dict, blank=True)  # Start date, end date, milestones
    script_file_url = models.URLField(blank=True, null=True)
    metadata = models.JSONField(default=dict, blank=True)  # Additional project info
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name


class ProjectStatus(models.Model):
    project = models.OneToOneField(Project, on_delete=models.CASCADE, related_name='project_status')
    script_analyzed = models.BooleanField(default=False)
    budget_generated = models.BooleanField(default=False)
    schedule_generated = models.BooleanField(default=False)
    grants_scraped = models.BooleanField(default=False)
    festivals_researched = models.BooleanField(default=False)
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Project Statuses"
    
    def __str__(self):
        return f"Status for {self.project.name}"
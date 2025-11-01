import uuid
from django.db import models
from accounts.models import Company


class Project(models.Model):
    PROJECT_TYPES = [
        ('feature', 'Feature Film'),
        ('short', 'Short Film'),
        ('documentary', 'Documentary'),
        ('series', 'TV Series'),
        ('web_series', 'Web Series'),
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
        ('low', 'Low Budget ($50K-250K)'),
        ('medium', 'Medium Budget ($250K-1M)'),
        ('high', 'High Budget ($1M-5M)'),
        ('major', 'Major Budget ($5M+)'),
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
    
    # Core project data for grant feature (NEW)
    genres = models.JSONField(default=list, blank=True)  # Multiple genres
    synopsis = models.TextField(blank=True)
    themes = models.JSONField(default=list, blank=True)  # Social themes
    production_location = models.JSONField(default=dict, blank=True)  # {country, state, city}
    additional_locations = models.JSONField(default=list, blank=True)  # Array of locations
    languages = models.JSONField(default=list, blank=True)  # Array of languages
    estimated_budget = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    currency = models.CharField(max_length=3, default='USD')
    project_stage = models.CharField(max_length=20, choices=STATUS_CHOICES, default='development')
    company_info = models.JSONField(default=dict, blank=True)
    team_members = models.JSONField(default=list, blank=True)  # Array of team member objects
    diversity_flags = models.JSONField(default=list, blank=True)  # Array of diversity flags
    
    # Feature enablement (NEW)
    features_enabled = models.JSONField(default=list, blank=True)  # ['grants', 'budget', 'schedule']
    
    # Setup status (NEW)
    core_setup_completed = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name


class ProjectFeature(models.Model):
    """Track feature-specific setup and status for each project"""
    FEATURE_CHOICES = [
        ('grants', 'Grant Discovery & Tracking'),
        ('budget', 'Budget Builder'),
        ('schedule', 'Production Schedule'),
        ('festivals', 'Festival Research & Submissions'),
        ('script', 'Script Analysis & Breakdown'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='project_features')
    feature = models.CharField(max_length=20, choices=FEATURE_CHOICES)
    setup_completed = models.BooleanField(default=False)
    setup_data = models.JSONField(default=dict, blank=True)  # Feature-specific setup data
    last_run_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['project', 'feature']
    
    def __str__(self):
        return f"{self.project.name} - {dict(self.FEATURE_CHOICES)[self.feature]}"


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
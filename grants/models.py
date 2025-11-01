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

    FUNDING_TYPES = [
        ('grant', 'Grant'),
        ('tax_credit', 'Tax Credit'),
        ('rebate', 'Rebate'),
        ('loan', 'Loan'),
        ('equity', 'Equity'),
        ('mixed', 'Mixed'),
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
    funding_type = models.CharField(max_length=20, choices=FUNDING_TYPES, default='grant')
    eligibility_criteria = models.JSONField(default=dict)
    application_requirements = models.JSONField(default=dict)
    location_restrictions = models.JSONField(default=dict)
    project_types = models.JSONField(default=list)  # Array of supported project types
    
    # Enhanced grant data (NEW)
    description = models.TextField(blank=True)
    selection_criteria = models.JSONField(default=list, blank=True)  # Array of criteria
    application_process = models.TextField(blank=True)
    contact_info = models.JSONField(default=dict, blank=True)  # Contact details
    annual_cycle = models.BooleanField(default=False)  # Recurring annually
    tags = models.JSONField(default=list, blank=True)  # Array of tags for filtering
    matched_projects_count = models.IntegerField(default=0)  # Track popularity
    success_rate = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)  # % success rate
    
    scraped_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    source = models.CharField(max_length=100, default='manual')
    
    class Meta:
        ordering = ['deadline']
    
    def __str__(self):
        return f"{self.title} - {self.organization}"


class GrantPreferences(models.Model):
    """Grant-specific preferences and filters for a project"""
    
    FUNDING_PRIORITIES = [
        ('development', 'Development Funding'),
        ('production', 'Production Funding'),
        ('post_production', 'Post-Production Funding'),
        ('distribution', 'Distribution Funding'),
        ('marketing', 'Marketing Funding'),
        ('festival', 'Festival Funding'),
        ('equipment', 'Equipment Funding'),
        ('travel', 'Travel Funding'),
    ]

    project = models.OneToOneField(Project, on_delete=models.CASCADE, related_name='grant_preferences')
    
    # Grant filtering preferences
    preferred_funding_types = models.JSONField(default=list, blank=True)  # grant, tax_credit, etc.
    funding_priorities = models.JSONField(default=list, blank=True)  # development, production, etc.
    min_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    max_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    preferred_regions = models.JSONField(default=list, blank=True)  # Geographic preferences
    excluded_regions = models.JSONField(default=list, blank=True)  # Regions to exclude
    
    # Application preferences
    max_application_complexity = models.IntegerField(default=5)  # 1-5 scale
    lead_time_preference = models.IntegerField(default=30)  # Days before deadline
    recurring_grants_only = models.BooleanField(default=False)
    
    # Content preferences
    genre_requirements = models.JSONField(default=list, blank=True)  # Required genres
    theme_requirements = models.JSONField(default=list, blank=True)  # Required themes
    diversity_requirements = models.JSONField(default=list, blank=True)  # Diversity criteria
    
    # Company/team requirements
    company_age_minimum = models.IntegerField(null=True, blank=True)  # Years in business
    track_record_required = models.BooleanField(default=False)
    collaboration_required = models.BooleanField(default=False)
    
    # Auto-application settings
    auto_apply_enabled = models.BooleanField(default=False)
    auto_apply_threshold = models.IntegerField(default=80)  # Match score threshold
    notification_preferences = models.JSONField(default=dict, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Grant Preferences for {self.project.name}"


class GrantMatch(models.Model):
    MATCH_STATUS_CHOICES = [
        ('suggested', 'Suggested'),
        ('interested', 'Interested'),
        ('applied', 'Applied'),
        ('under_review', 'Under Review'),
        ('awarded', 'Awarded'),
        ('rejected', 'Rejected'),
        ('withdrawn', 'Withdrawn'),
    ]

    MATCH_QUALITY = [
        ('perfect', 'Perfect Match (90-100%)'),
        ('excellent', 'Excellent Match (80-89%)'),
        ('good', 'Good Match (70-79%)'),
        ('fair', 'Fair Match (60-69%)'),
        ('poor', 'Poor Match (50-59%)'),
    ]

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='grant_matches')
    grant = models.ForeignKey(Grant, on_delete=models.CASCADE, related_name='matches')
    match_score = models.IntegerField(default=0)  # 0-100 score
    match_quality = models.CharField(max_length=20, choices=MATCH_QUALITY, blank=True)
    match_reasoning = models.TextField()
    match_details = models.JSONField(default=dict, blank=True)  # Detailed match breakdown
    
    status = models.CharField(max_length=20, choices=MATCH_STATUS_CHOICES, default='suggested')
    applied_at = models.DateField(null=True, blank=True)
    deadline_reminder_sent = models.BooleanField(default=False)
    
    # Application tracking
    application_notes = models.TextField(blank=True)
    application_documents = models.JSONField(default=list, blank=True)  # Document URLs/paths
    follow_up_date = models.DateField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['project', 'grant']
        ordering = ['-match_score', 'grant__deadline']
    
    def save(self, *args, **kwargs):
        # Auto-set match quality based on score
        if self.match_score >= 90:
            self.match_quality = 'perfect'
        elif self.match_score >= 80:
            self.match_quality = 'excellent'
        elif self.match_score >= 70:
            self.match_quality = 'good'
        elif self.match_score >= 60:
            self.match_quality = 'fair'
        else:
            self.match_quality = 'poor'
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.project.name} -> {self.grant.title} ({self.match_score}%)"


class GrantApplication(models.Model):
    """Track detailed application progress and requirements"""
    
    APPLICATION_STATUS = [
        ('draft', 'Draft'),
        ('in_progress', 'In Progress'),
        ('review', 'Internal Review'),
        ('submitted', 'Submitted'),
        ('under_review', 'Under Review'),
        ('awarded', 'Awarded'),
        ('rejected', 'Rejected'),
        ('withdrawn', 'Withdrawn'),
    ]

    grant_match = models.OneToOneField(GrantMatch, on_delete=models.CASCADE, related_name='application')
    
    # Application details
    application_id = models.CharField(max_length=100, blank=True)  # External application ID
    submission_date = models.DateTimeField(null=True, blank=True)
    confirmation_number = models.CharField(max_length=100, blank=True)
    
    # Requirements checklist
    requirements_checklist = models.JSONField(default=list, blank=True)  # Array of requirement objects
    completed_requirements = models.JSONField(default=list, blank=True)  # Array of completed IDs
    completion_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'))
    
    # Documents and materials
    submitted_documents = models.JSONField(default=dict, blank=True)  # Document type -> file info
    additional_materials = models.JSONField(default=list, blank=True)  # Additional submitted items
    
    # Communication log
    communication_log = models.JSONField(default=list, blank=True)  # Array of communication objects
    
    # Results
    decision_date = models.DateField(null=True, blank=True)
    award_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    rejection_reason = models.TextField(blank=True)
    feedback_received = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Application: {self.grant_match.project.name} -> {self.grant_match.grant.title}"
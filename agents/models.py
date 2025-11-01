import uuid
from django.db import models
from projects.models import Project


class AgentJob(models.Model):
    AGENT_TYPES = [
        ('script', 'Script Analysis'),
        ('budget', 'Budget Generation'),
        ('schedule', 'Schedule Generation'),
        ('grant_scrape', 'Grant Scraping'),
        ('grant_match', 'Grant Matching'),
        ('festival_scrape', 'Festival Scraping'),
        ('festival_match', 'Festival Matching'),
    ]
    
    STATUS_CHOICES = [
        ('queued', 'Queued'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='agent_jobs')
    agent_type = models.CharField(max_length=20, choices=AGENT_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='queued')
    input_params = models.JSONField(default=dict)
    output_data = models.JSONField(default=dict, blank=True)
    error_message = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.get_agent_type_display()} for {self.project.name} ({self.status})"
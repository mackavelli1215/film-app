import uuid
from django.db import models
from django.contrib.auth.models import User
from projects.models import Project


class Comment(models.Model):
    SECTION_CHOICES = [
        ('script', 'Script'),
        ('budget', 'Budget'),
        ('schedule', 'Schedule'),
        ('grant', 'Grant'),
        ('festival', 'Festival'),
        ('general', 'General'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='comments')
    section = models.CharField(max_length=20, choices=SECTION_CHOICES, default='general')
    item_id = models.CharField(max_length=100, blank=True)  # ID of specific item being commented on
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment_text = models.TextField()
    mentions = models.JSONField(default=list)  # List of mentioned user IDs
    resolved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Comment by {self.user.username} on {self.project.name}"


class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('comment', 'Comment'),
        ('mention', 'Mention'),
        ('project_update', 'Project Update'),
        ('grant_deadline', 'Grant Deadline'),
        ('festival_deadline', 'Festival Deadline'),
        ('agent_complete', 'Agent Complete'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    link = models.CharField(max_length=200, blank=True)  # URL to relevant page
    read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Notification for {self.user.username}: {self.title}"


class ActivityLog(models.Model):
    ACTION_TYPES = [
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete'),
        ('upload', 'Upload'),
        ('generate', 'Generate'),
        ('submit', 'Submit'),
    ]
    
    SECTION_CHOICES = [
        ('project', 'Project'),
        ('script', 'Script'),
        ('budget', 'Budget'),
        ('schedule', 'Schedule'),
        ('grant', 'Grant'),
        ('festival', 'Festival'),
    ]

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='activity_logs')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    action_type = models.CharField(max_length=20, choices=ACTION_TYPES)
    section = models.CharField(max_length=20, choices=SECTION_CHOICES)
    description = models.CharField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        user_name = self.user.username if self.user else 'System'
        return f"{user_name} {self.action_type}d {self.section} in {self.project.name}"
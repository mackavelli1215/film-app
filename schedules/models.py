import uuid
from django.db import models
from django.contrib.auth.models import User
from projects.models import Project


class Schedule(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('approved', 'Approved'),
        ('locked', 'Locked'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='schedules')
    version = models.IntegerField(default=1)
    total_days = models.IntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['project', 'version']
    
    def __str__(self):
        return f"Schedule v{self.version} for {self.project.name}"


class ShootDay(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE, related_name='shoot_days')
    day_number = models.IntegerField()
    date = models.DateField(null=True, blank=True)
    location = models.CharField(max_length=200)
    scenes = models.JSONField(default=list)  # List of scene numbers/IDs
    call_time = models.TimeField(null=True, blank=True)
    wrap_time = models.TimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    order_index = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order_index', 'day_number']
        unique_together = ['schedule', 'day_number']
    
    def __str__(self):
        return f"Day {self.day_number}: {self.location}"
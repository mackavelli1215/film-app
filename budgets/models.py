import uuid
from decimal import Decimal
from django.db import models
from django.contrib.auth.models import User
from projects.models import Project


class Budget(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('approved', 'Approved'),
        ('locked', 'Locked'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='budgets')
    version = models.IntegerField(default=1)
    total_budget = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    contingency_percent = models.IntegerField(default=10)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['project', 'version']
    
    def __str__(self):
        return f"Budget v{self.version} for {self.project.name}"


class BudgetItem(models.Model):
    BUDGET_CATEGORIES = [
        ('above_line', 'Above the Line'),
        ('below_line', 'Below the Line'),
        ('post_production', 'Post Production'),
        ('other', 'Other'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    budget = models.ForeignKey(Budget, on_delete=models.CASCADE, related_name='items')
    category = models.CharField(max_length=50, choices=BUDGET_CATEGORIES)
    subcategory = models.CharField(max_length=100)
    description = models.CharField(max_length=200)
    quantity = models.DecimalField(max_digits=8, decimal_places=2, default=Decimal('1.00'))
    unit = models.CharField(max_length=50, default='item')  # day, week, item, etc.
    rate = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    total = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    notes = models.TextField(blank=True)
    order_index = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['category', 'order_index']
    
    def save(self, *args, **kwargs):
        # Calculate total automatically
        self.total = self.quantity * self.rate
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.category}: {self.description}"
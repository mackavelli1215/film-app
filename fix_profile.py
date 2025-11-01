#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'filmapp.settings')
django.setup()

from django.contrib.auth.models import User
from accounts.models import Company, Profile

# Get the superuser
try:
    user = User.objects.get(username='frankieadmin')
    print(f"Found user: {user.username}")
    
    # Create a default company if it doesn't exist
    company, created = Company.objects.get_or_create(
        name="Default Production Company",
        defaults={
            'size': 'startup',
            'tier': 'free'
        }
    )
    
    if created:
        print(f"Created company: {company.name}")
    else:
        print(f"Using existing company: {company.name}")
    
    # Create or update user profile
    profile, created = Profile.objects.get_or_create(
        user=user,
        defaults={
            'company': company,
            'role': 'owner'
        }
    )
    
    if created:
        print(f"Created profile for {user.username}")
    else:
        print(f"Profile already exists for {user.username}")
        # Update the company if needed
        if profile.company != company:
            profile.company = company
            profile.save()
            print(f"Updated profile company")
    
    print("Profile setup complete!")
    
except User.DoesNotExist:
    print("User 'frankieadmin' not found")
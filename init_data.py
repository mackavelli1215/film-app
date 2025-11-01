#!/usr/bin/env python
"""
Initialization script for FilmApp.
Run this after setting up the environment to create initial data.
"""

import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'filmapp.settings')
django.setup()

from django.contrib.auth.models import User
from accounts.models import Company, Profile
from grants.models import Grant
from festivals.models import Festival
from django.utils import timezone


def create_initial_data():
    """Create initial sample data for the application."""
    
    print("Creating initial data...")
    
    # Create sample company
    company, created = Company.objects.get_or_create(
        name="Demo Production Company",
        defaults={
            'size': 'startup',
            'tier': 'free',
            'settings': {}
        }
    )
    if created:
        print(f"✓ Created company: {company.name}")
    
    # Create sample grants
    sample_grants = [
        {
            'title': 'National Film Board Production Grant',
            'organization': 'National Film Board',
            'url': 'https://example.com/nfb-grant',
            'deadline': timezone.now().date().replace(month=12, day=31),
            'amount_min': 10000,
            'amount_max': 50000,
            'grant_type': 'production',
            'eligibility_criteria': {'citizenship': 'US/Canada', 'experience': 'emerging'},
            'project_types': ['feature', 'documentary', 'short']
        },
        {
            'title': 'Independent Film Development Fund',
            'organization': 'Film Development Corporation',
            'url': 'https://example.com/dev-fund',
            'deadline': timezone.now().date().replace(month=6, day=15),
            'amount_min': 5000,
            'amount_max': 25000,
            'grant_type': 'development',
            'eligibility_criteria': {'budget_max': 1000000, 'first_time': True},
            'project_types': ['feature', 'short']
        }
    ]
    
    grants_created = 0
    for grant_data in sample_grants:
        grant, created = Grant.objects.get_or_create(
            title=grant_data['title'],
            organization=grant_data['organization'],
            defaults=grant_data
        )
        if created:
            grants_created += 1
    
    print(f"✓ Created {grants_created} sample grants")
    
    # Create sample festivals
    sample_festivals = [
        {
            'name': 'Sundance Film Festival',
            'location': 'Park City, UT',
            'website_url': 'https://festival.sundance.org',
            'deadline_early': timezone.now().date().replace(month=8, day=15),
            'deadline_regular': timezone.now().date().replace(month=9, day=15),
            'deadline_late': timezone.now().date().replace(month=10, day=1),
            'fee_early': 40,
            'fee_regular': 65,
            'fee_late': 85,
            'tier': 'a_list',
            'genres': ['drama', 'documentary', 'comedy'],
            'prestige_score': 95
        },
        {
            'name': 'Regional Film Showcase',
            'location': 'Various Cities',
            'website_url': 'https://regionalfilmfest.com',
            'deadline_regular': timezone.now().date().replace(month=5, day=30),
            'fee_regular': 15,
            'tier': 'regional',
            'genres': ['drama', 'documentary', 'short'],
            'prestige_score': 50
        }
    ]
    
    festivals_created = 0
    for festival_data in sample_festivals:
        festival, created = Festival.objects.get_or_create(
            name=festival_data['name'],
            location=festival_data['location'],
            defaults=festival_data
        )
        if created:
            festivals_created += 1
    
    print(f"✓ Created {festivals_created} sample festivals")
    
    print("\nInitial data creation complete!")
    print("\nNext steps:")
    print("1. Create a superuser: python manage.py createsuperuser")
    print("2. Run the development server: python manage.py runserver")
    print("3. In another terminal, run agents: python manage.py run_agents --once")


if __name__ == '__main__':
    create_initial_data()
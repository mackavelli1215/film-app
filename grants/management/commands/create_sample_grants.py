from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal
from grants.models import Grant


class Command(BaseCommand):
    help = 'Create sample grant data for testing'

    def handle(self, *args, **options):
        # Clear existing grants
        Grant.objects.all().delete()
        
        grants_data = [
            {
                'title': 'Independent Film Development Grant',
                'organization': 'National Endowment for the Arts',
                'url': 'https://www.arts.gov/grants/independent-film',
                'deadline': timezone.now().date() + timedelta(days=45),
                'amount_min': Decimal('10000'),
                'amount_max': Decimal('50000'),
                'grant_type': 'development',
                'funding_type': 'grant',
                'description': 'Supports the development of independent narrative, documentary, and experimental films with strong artistic merit.',
                'eligibility_criteria': {
                    'location': 'United States',
                    'experience': 'Emerging to mid-career filmmakers',
                    'project_stage': 'Development',
                    'budget_max': 250000
                },
                'application_requirements': {
                    'treatment': 'Required',
                    'budget': 'Detailed budget breakdown',
                    'director_statement': 'Required',
                    'sample_work': 'Previous film samples'
                },
                'tags': ['independent', 'development', 'emerging_filmmakers', 'arts_council']
            },
            {
                'title': 'Documentary Production Fund',
                'organization': 'Sundance Institute',
                'url': 'https://www.sundance.org/programs/documentary-fund',
                'deadline': timezone.now().date() + timedelta(days=60),
                'amount_min': Decimal('25000'),
                'amount_max': Decimal('100000'),
                'grant_type': 'production',
                'funding_type': 'grant',
                'description': 'Provides funding for feature-length documentaries that address contemporary social issues.',
                'eligibility_criteria': {
                    'location': 'International',
                    'genre': 'Documentary',
                    'project_stage': 'Production',
                    'social_impact': 'Required'
                },
                'application_requirements': {
                    'treatment': 'Required',
                    'work_in_progress': 'Rough cut or footage',
                    'impact_statement': 'Social impact plan',
                    'budget': 'Complete production budget'
                },
                'tags': ['documentary', 'production', 'social_impact', 'sundance']
            },
            {
                'title': 'Diversity in Film Initiative',
                'organization': 'Ford Foundation',
                'url': 'https://www.fordfoundation.org/work/challenging-inequality/creativity-and-free-expression/',
                'deadline': timezone.now().date() + timedelta(days=30),
                'amount_min': Decimal('15000'),
                'amount_max': Decimal('75000'),
                'grant_type': 'general',
                'funding_type': 'grant',
                'description': 'Supports films by and about underrepresented communities, focusing on stories that challenge inequality.',
                'eligibility_criteria': {
                    'location': 'United States',
                    'diversity_requirement': 'POC or female director',
                    'theme': 'Social justice or diversity',
                    'budget_max': 500000
                },
                'application_requirements': {
                    'script': 'Complete screenplay',
                    'director_bio': 'Detailed biography',
                    'diversity_statement': 'Commitment to diversity',
                    'community_impact': 'Community engagement plan'
                },
                'tags': ['diversity', 'social_justice', 'underrepresented', 'ford_foundation']
            },
            {
                'title': 'Regional Arts Council Grant',
                'organization': 'California Arts Council',
                'url': 'https://www.arts.ca.gov/grants/',
                'deadline': timezone.now().date() + timedelta(days=90),
                'amount_min': Decimal('5000'),
                'amount_max': Decimal('25000'),
                'grant_type': 'general',
                'funding_type': 'grant',
                'description': 'General arts funding for California-based filmmakers and media artists.',
                'eligibility_criteria': {
                    'location': 'California residents only',
                    'experience': 'All levels welcome',
                    'project_stage': 'Any stage',
                    'arts_focus': 'Required'
                },
                'application_requirements': {
                    'artist_statement': 'Required',
                    'project_description': 'Detailed description',
                    'budget': 'Simple budget outline',
                    'samples': 'Work samples'
                },
                'location_restrictions': {
                    'state': 'California',
                    'residency_required': True
                },
                'tags': ['regional', 'california', 'general_arts', 'state_funding']
            },
            {
                'title': 'Innovation in Media Grant',
                'organization': 'Knight Foundation',
                'url': 'https://knightfoundation.org/programs/arts/',
                'deadline': timezone.now().date() + timedelta(days=75),
                'amount_min': Decimal('20000'),
                'amount_max': Decimal('150000'),
                'grant_type': 'general',
                'funding_type': 'grant',
                'description': 'Supports innovative approaches to media and storytelling, particularly projects that engage communities.',
                'eligibility_criteria': {
                    'location': 'United States',
                    'innovation_focus': 'Required',
                    'community_engagement': 'Required',
                    'technology_component': 'Preferred'
                },
                'application_requirements': {
                    'innovation_statement': 'How project is innovative',
                    'community_plan': 'Community engagement strategy',
                    'technical_plan': 'Technical implementation',
                    'budget': 'Detailed budget'
                },
                'tags': ['innovation', 'technology', 'community_engagement', 'knight_foundation']
            }
        ]
        
        created_grants = []
        for grant_data in grants_data:
            grant = Grant.objects.create(**grant_data)
            created_grants.append(grant)
            self.stdout.write(
                self.style.SUCCESS(f'Created grant: {grant.title}')
            )
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {len(created_grants)} sample grants')
        )
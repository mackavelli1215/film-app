"""
Agent processors for handling different types of background jobs.
"""
import random
from decimal import Decimal
from typing import Dict, Any
from django.utils import timezone
from projects.models import Project
from breakdown.models import ScriptBreakdown, Scene
from budgets.models import Budget, BudgetItem
from schedules.models import Schedule, ShootDay
from grants.models import Grant, GrantMatch
from festivals.models import Festival, FestivalMatch


class AgentProcessor:
    """Main processor for routing agent jobs to specific handlers."""
    
    def process_job(self, job) -> Dict[str, Any]:
        """
        Process a job based on its agent_type.
        
        Args:
            job: AgentJob instance
            
        Returns:
            Dict with 'success' bool and 'data' or 'error'
        """
        try:
            handler_map = {
                'script': self._process_script_analysis,
                'budget': self._process_budget_generation,
                'schedule': self._process_schedule_generation,
                'grant_scrape': self._process_grant_scraping,
                'grant_match': self._process_grant_matching,
                'festival_scrape': self._process_festival_scraping,
                'festival_match': self._process_festival_matching,
            }
            
            handler = handler_map.get(job.agent_type)
            if not handler:
                return {
                    'success': False,
                    'error': f'Unknown agent type: {job.agent_type}'
                }
            
            return handler(job)
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Processing error: {str(e)}'
            }
    
    def _process_script_analysis(self, job) -> Dict[str, Any]:
        """
        Analyze a script and create scene breakdown.
        For MVP: Creates fake but coherent scene data.
        """
        try:
            project = job.project
            
            # Create or get breakdown
            breakdown, created = ScriptBreakdown.objects.get_or_create(project=project)
            
            # Generate fake scenes for demonstration
            fake_scenes = [
                {
                    'number': 1,
                    'slug': 'INT. COFFEE SHOP - DAY',
                    'header': 'INT. COFFEE SHOP - DAY',
                    'int_ext': 'INT',
                    'day_night': 'DAY',
                    'location': 'Coffee Shop',
                    'characters': ['SARAH', 'MIKE'],
                    'est_shoot_hours': 2.5,
                    'complexity': 'simple',
                    'notes': 'Dialogue-heavy scene with two characters'
                },
                {
                    'number': 2,
                    'slug': 'EXT. CITY STREET - DAY',
                    'header': 'EXT. CITY STREET - DAY',
                    'int_ext': 'EXT',
                    'day_night': 'DAY',
                    'location': 'City Street',
                    'characters': ['SARAH'],
                    'est_shoot_hours': 1.0,
                    'complexity': 'medium',
                    'notes': 'Walking scene with background action'
                },
                {
                    'number': 3,
                    'slug': 'INT. SARAH\'S APARTMENT - NIGHT',
                    'header': 'INT. SARAH\'S APARTMENT - NIGHT',
                    'int_ext': 'INT',
                    'day_night': 'NIGHT',
                    'location': 'Sarah\'s Apartment',
                    'characters': ['SARAH', 'ROOMMATE'],
                    'est_shoot_hours': 3.0,
                    'complexity': 'complex',
                    'notes': 'Emotional scene with special lighting'
                }
            ]
            
            # Clear existing scenes and create new ones
            Scene.objects.filter(breakdown=breakdown).delete()
            
            created_scenes = []
            for scene_data in fake_scenes:
                scene = Scene.objects.create(
                    breakdown=breakdown,
                    **scene_data
                )
                created_scenes.append(scene.id)
            
            # Update project status
            project.project_status.script_analyzed = True
            project.project_status.save()
            
            return {
                'success': True,
                'data': {
                    'scenes_created': len(created_scenes),
                    'scene_ids': [str(sid) for sid in created_scenes],
                    'total_scenes': len(fake_scenes)
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Script analysis failed: {str(e)}'
            }
    
    def _process_budget_generation(self, job) -> Dict[str, Any]:
        """
        Generate budget based on script breakdown.
        For MVP: Creates realistic budget categories and items.
        """
        try:
            project = job.project
            
            # Create new budget version
            existing_budgets = Budget.objects.filter(project=project).count()
            budget = Budget.objects.create(
                project=project,
                version=existing_budgets + 1,
                created_by=None  # System generated
            )
            
            # Generate budget items based on project type and scope
            budget_items_data = [
                # Above the Line
                ('above_line', 'Producer', 'Producer Fee', 1, 'project', 5000),
                ('above_line', 'Director', 'Director Fee', 1, 'project', 8000),
                ('above_line', 'Writer', 'Script Development', 1, 'project', 2500),
                
                # Below the Line
                ('below_line', 'Cast', 'Lead Actor #1', 5, 'day', 500),
                ('below_line', 'Cast', 'Lead Actor #2', 5, 'day', 400),
                ('below_line', 'Cast', 'Supporting Cast', 3, 'day', 200),
                ('below_line', 'Crew', 'Director of Photography', 5, 'day', 600),
                ('below_line', 'Crew', 'Sound Recordist', 5, 'day', 300),
                ('below_line', 'Crew', 'Gaffer', 5, 'day', 400),
                ('below_line', 'Equipment', 'Camera Package', 5, 'day', 400),
                ('below_line', 'Equipment', 'Lighting Package', 5, 'day', 300),
                ('below_line', 'Equipment', 'Sound Package', 5, 'day', 150),
                ('below_line', 'Locations', 'Location Fees', 3, 'day', 200),
                ('below_line', 'Catering', 'Meals and Craft Services', 5, 'day', 100),
                
                # Post Production
                ('post_production', 'Editing', 'Editor Fee', 2, 'week', 1500),
                ('post_production', 'Color', 'Color Correction', 1, 'project', 2000),
                ('post_production', 'Sound', 'Sound Design & Mix', 1, 'project', 3000),
                ('post_production', 'Music', 'Original Score', 1, 'project', 2500),
            ]
            
            total_budget = 0
            created_items = []
            
            for idx, (category, subcategory, description, quantity, unit, rate) in enumerate(budget_items_data):
                item = BudgetItem.objects.create(
                    budget=budget,
                    category=category,
                    subcategory=subcategory,
                    description=description,
                    quantity=quantity,
                    unit=unit,
                    rate=rate,
                    order_index=idx
                )
                total_budget += item.total
                created_items.append(item.id)
            
            # Add contingency
            contingency_amount = total_budget * Decimal(str(budget.contingency_percent / 100))
            contingency_item = BudgetItem.objects.create(
                budget=budget,
                category='other',
                subcategory='Contingency',
                description=f'Contingency ({budget.contingency_percent}%)',
                quantity=1,
                unit='project',
                rate=contingency_amount,
                order_index=len(budget_items_data)
            )
            
            total_budget += contingency_amount
            budget.total_budget = total_budget
            budget.save()
            
            # Update project status
            project.project_status.budget_generated = True
            project.project_status.save()
            
            return {
                'success': True,
                'data': {
                    'budget_id': str(budget.id),
                    'total_budget': float(total_budget),
                    'items_created': len(created_items) + 1,  # +1 for contingency
                    'contingency_amount': float(contingency_amount)
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Budget generation failed: {str(e)}'
            }
    
    def _process_schedule_generation(self, job) -> Dict[str, Any]:
        """
        Generate shooting schedule based on script breakdown.
        For MVP: Groups scenes by location and creates logical shooting days.
        """
        try:
            project = job.project
            
            # Create new schedule version
            existing_schedules = Schedule.objects.filter(project=project).count()
            schedule = Schedule.objects.create(
                project=project,
                version=existing_schedules + 1,
                created_by=None  # System generated
            )
            
            # Get scenes from breakdown (if available)
            try:
                breakdown = project.breakdown
                scenes = breakdown.scenes.all().order_by('number')
            except:
                # No breakdown available, create sample days
                scenes = []
            
            if scenes:
                # Group scenes by location
                location_groups = {}
                for scene in scenes:
                    location = scene.location
                    if location not in location_groups:
                        location_groups[location] = []
                    location_groups[location].append(scene)
                
                # Create shoot days
                day_number = 1
                created_days = []
                
                for location, location_scenes in location_groups.items():
                    # Calculate total hours for this location
                    total_hours = sum(float(scene.est_shoot_hours) for scene in location_scenes)
                    
                    # Split into multiple days if needed (max 10 hours per day)
                    current_hours = 0
                    current_scenes = []
                    
                    for scene in location_scenes:
                        scene_hours = float(scene.est_shoot_hours)
                        
                        if current_hours + scene_hours > 10 and current_scenes:
                            # Create a day with current scenes
                            shoot_day = ShootDay.objects.create(
                                schedule=schedule,
                                day_number=day_number,
                                location=location,
                                scenes=[scene.number for scene in current_scenes],
                                call_time=timezone.now().time().replace(hour=8, minute=0),
                                notes=f'Scenes {min(s.number for s in current_scenes)}-{max(s.number for s in current_scenes)}',
                                order_index=day_number - 1
                            )
                            created_days.append(shoot_day.id)
                            day_number += 1
                            current_scenes = []
                            current_hours = 0
                        
                        current_scenes.append(scene)
                        current_hours += scene_hours
                    
                    # Create final day for remaining scenes
                    if current_scenes:
                        shoot_day = ShootDay.objects.create(
                            schedule=schedule,
                            day_number=day_number,
                            location=location,
                            scenes=[scene.number for scene in current_scenes],
                            call_time=timezone.now().time().replace(hour=8, minute=0),
                            notes=f'Scenes {min(s.number for s in current_scenes)}-{max(s.number for s in current_scenes)}',
                            order_index=day_number - 1
                        )
                        created_days.append(shoot_day.id)
                        day_number += 1
                
            else:
                # Create sample shoot days
                sample_days = [
                    ('Coffee Shop', [1], 'Interior dialogue scenes'),
                    ('City Street', [2], 'Exterior walking sequences'),
                    ('Sarah\'s Apartment', [3], 'Interior night scenes'),
                ]
                
                created_days = []
                for idx, (location, scene_numbers, notes) in enumerate(sample_days):
                    shoot_day = ShootDay.objects.create(
                        schedule=schedule,
                        day_number=idx + 1,
                        location=location,
                        scenes=scene_numbers,
                        call_time=timezone.now().time().replace(hour=8, minute=0),
                        notes=notes,
                        order_index=idx
                    )
                    created_days.append(shoot_day.id)
                    day_number = idx + 2
            
            schedule.total_days = day_number - 1
            schedule.save()
            
            # Update project status
            project.project_status.schedule_generated = True
            project.project_status.save()
            
            return {
                'success': True,
                'data': {
                    'schedule_id': str(schedule.id),
                    'total_days': schedule.total_days,
                    'shoot_days_created': len(created_days)
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Schedule generation failed: {str(e)}'
            }
    
    def _process_grant_scraping(self, job) -> Dict[str, Any]:
        """
        Scrape grant opportunities from various sources.
        For MVP: Creates sample grant data.
        """
        try:
            # Sample grant data for demonstration
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
                },
                {
                    'title': 'Documentary Impact Grant',
                    'organization': 'Documentary Alliance',
                    'url': 'https://example.com/doc-impact',
                    'deadline': timezone.now().date().replace(month=9, day=30),
                    'amount_min': 15000,
                    'amount_max': 75000,
                    'grant_type': 'production',
                    'eligibility_criteria': {'genre': 'documentary', 'social_impact': True},
                    'project_types': ['documentary']
                }
            ]
            
            created_grants = []
            for grant_data in sample_grants:
                grant, created = Grant.objects.get_or_create(
                    title=grant_data['title'],
                    organization=grant_data['organization'],
                    defaults=grant_data
                )
                if created:
                    created_grants.append(grant.id)
            
            return {
                'success': True,
                'data': {
                    'grants_scraped': len(created_grants),
                    'total_grants': Grant.objects.count()
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Grant scraping failed: {str(e)}'
            }
    
    def _process_grant_matching(self, job) -> Dict[str, Any]:
        """
        Match project with relevant grants.
        For MVP: Simple matching based on project type and budget.
        """
        try:
            project = job.project
            
            # Get all grants
            grants = Grant.objects.all()
            created_matches = []
            
            for grant in grants:
                # Simple matching logic
                score = 0
                reasoning_parts = []
                
                # Match project type
                if project.type in grant.project_types:
                    score += 40
                    reasoning_parts.append(f"Project type ({project.get_type_display()}) matches grant requirements")
                
                # Match budget range (if available)
                if project.budget_range in ['micro', 'low'] and grant.amount_max and grant.amount_max <= 100000:
                    score += 30
                    reasoning_parts.append("Budget range aligns with grant maximum")
                
                # Match genre for documentaries
                if project.genre == 'documentary' and grant.grant_type == 'production':
                    score += 20
                    reasoning_parts.append("Documentary project matches production grant")
                
                # Random factor for variety
                score += random.randint(0, 10)
                
                # Only create matches above threshold
                if score >= 30:
                    match, created = GrantMatch.objects.get_or_create(
                        project=project,
                        grant=grant,
                        defaults={
                            'match_score': score,
                            'match_reasoning': '; '.join(reasoning_parts) if reasoning_parts else 'General compatibility'
                        }
                    )
                    if created:
                        created_matches.append(match.id)
            
            # Update project status
            project.project_status.grants_scraped = True
            project.project_status.save()
            
            return {
                'success': True,
                'data': {
                    'matches_created': len(created_matches),
                    'total_matches': GrantMatch.objects.filter(project=project).count()
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Grant matching failed: {str(e)}'
            }
    
    def _process_festival_scraping(self, job) -> Dict[str, Any]:
        """
        Scrape festival opportunities.
        For MVP: Creates sample festival data.
        """
        try:
            # Sample festival data
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
                    'name': 'SXSW Film Festival',
                    'location': 'Austin, TX',
                    'website_url': 'https://www.sxsw.com',
                    'deadline_early': timezone.now().date().replace(month=10, day=15),
                    'deadline_regular': timezone.now().date().replace(month=11, day=15),
                    'deadline_late': timezone.now().date().replace(month=12, day=1),
                    'fee_early': 25,
                    'fee_regular': 40,
                    'fee_late': 55,
                    'tier': 'a_list',
                    'genres': ['comedy', 'drama', 'thriller'],
                    'prestige_score': 85
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
            
            created_festivals = []
            for festival_data in sample_festivals:
                festival, created = Festival.objects.get_or_create(
                    name=festival_data['name'],
                    location=festival_data['location'],
                    defaults=festival_data
                )
                if created:
                    created_festivals.append(festival.id)
            
            return {
                'success': True,
                'data': {
                    'festivals_scraped': len(created_festivals),
                    'total_festivals': Festival.objects.count()
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Festival scraping failed: {str(e)}'
            }
    
    def _process_festival_matching(self, job) -> Dict[str, Any]:
        """
        Match project with relevant festivals.
        For MVP: Matching based on genre, tier, and project characteristics.
        """
        try:
            project = job.project
            
            # Get all festivals
            festivals = Festival.objects.all()
            created_matches = []
            
            for festival in festivals:
                # Simple matching logic
                score = 0
                strategy_notes = []
                
                # Match genre
                if project.genre in festival.genres:
                    score += 50
                    strategy_notes.append(f"Genre ({project.get_genre_display()}) matches festival focus")
                
                # Match project type and tier
                if project.type == 'feature' and festival.tier == 'a_list':
                    score += 30
                    strategy_notes.append("Feature film suitable for A-list festival")
                elif project.type == 'short' and festival.tier in ['regional', 'genre']:
                    score += 40
                    strategy_notes.append("Short film well-suited for regional/genre festival")
                elif project.type == 'documentary' and 'documentary' in festival.genres:
                    score += 45
                    strategy_notes.append("Documentary matches festival programming")
                
                # Budget consideration
                if project.budget_range in ['micro', 'low'] and festival.tier == 'regional':
                    score += 15
                    strategy_notes.append("Budget-friendly festival for independent production")
                
                # Random factor
                score += random.randint(0, 15)
                
                # Only create matches above threshold
                if score >= 40:
                    match, created = FestivalMatch.objects.get_or_create(
                        project=project,
                        festival=festival,
                        defaults={
                            'match_score': score,
                            'strategy_notes': '; '.join(strategy_notes) if strategy_notes else 'General festival compatibility'
                        }
                    )
                    if created:
                        created_matches.append(match.id)
            
            # Update project status
            project.project_status.festivals_researched = True
            project.project_status.save()
            
            return {
                'success': True,
                'data': {
                    'matches_created': len(created_matches),
                    'total_matches': FestivalMatch.objects.filter(project=project).count()
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Festival matching failed: {str(e)}'
            }
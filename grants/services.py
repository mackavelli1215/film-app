"""
Grant discovery and matching algorithm
"""
from django.db.models import Q
from datetime import datetime, timedelta
from grants.models import Grant, GrantMatch, GrantPreferences


class GrantMatcher:
    """Main class for grant discovery and matching"""
    
    def __init__(self, project):
        self.project = project
        
    def discover_grants(self):
        """
        Main discovery method that finds and scores grant matches
        """
        # Get project's grant preferences
        try:
            preferences = self.project.grant_preferences
        except:
            preferences = None
            
        # Get available grants (not expired)
        available_grants = Grant.objects.filter(
            deadline__gte=datetime.now().date()
        )
        
        # Apply preference filters if they exist
        if preferences:
            available_grants = self._apply_preference_filters(available_grants, preferences)
        
        matches_created = 0
        for grant in available_grants:
            # Check if match already exists
            if not GrantMatch.objects.filter(project=self.project, grant=grant).exists():
                score, reasoning, details = self._calculate_match_score(grant, preferences)
                
                if score >= 50:  # Only create matches with decent scores
                    GrantMatch.objects.create(
                        project=self.project,
                        grant=grant,
                        match_score=score,
                        match_reasoning=reasoning,
                        match_details=details
                    )
                    matches_created += 1
        
        return matches_created
    
    def _apply_preference_filters(self, grants, preferences):
        """Apply grant preferences to filter available grants"""
        
        # Filter by funding types
        if preferences.preferred_funding_types:
            grants = grants.filter(funding_type__in=preferences.preferred_funding_types)
        
        # Filter by amount range
        if preferences.min_amount:
            grants = grants.filter(
                Q(amount_max__gte=preferences.min_amount) | Q(amount_max__isnull=True)
            )
        if preferences.max_amount:
            grants = grants.filter(
                Q(amount_min__lte=preferences.max_amount) | Q(amount_min__isnull=True)
            )
        
        # Filter by lead time preference
        if preferences.lead_time_preference:
            min_deadline = datetime.now().date() + timedelta(days=preferences.lead_time_preference)
            grants = grants.filter(deadline__gte=min_deadline)
        
        return grants
    
    def _calculate_match_score(self, grant, preferences):
        """Calculate match score between project and grant"""
        score = 0
        reasoning_parts = []
        details = {}
        
        # Base score for all grants
        score += 20
        
        # Project type matching
        if grant.project_types and self.project.type in grant.project_types:
            score += 15
            reasoning_parts.append(f"Project type '{self.project.type}' is supported")
            details['project_type_match'] = True
        
        # Genre matching
        project_genres = getattr(self.project, 'genres', [])
        if project_genres:
            # Check for genre overlap in grant eligibility
            genre_keywords = ['genre', 'type', 'category']
            for key, value in grant.eligibility_criteria.items():
                if any(keyword in key.lower() for keyword in genre_keywords):
                    if any(genre in str(value).lower() for genre in project_genres):
                        score += 10
                        reasoning_parts.append("Genre alignment found in eligibility criteria")
                        details['genre_match'] = True
                        break
        
        # Budget alignment
        project_budget = getattr(self.project, 'estimated_budget', None)
        if project_budget and grant.amount_min and grant.amount_max:
            if grant.amount_min <= project_budget <= grant.amount_max:
                score += 15
                reasoning_parts.append("Budget aligns with grant amount range")
                details['budget_match'] = True
            elif grant.amount_min <= project_budget * 0.5:  # Grant covers at least 50% of budget
                score += 10
                reasoning_parts.append("Grant could cover significant portion of budget")
                details['partial_budget_match'] = True
        
        # Theme and diversity matching
        project_themes = getattr(self.project, 'themes', [])
        project_diversity = getattr(self.project, 'diversity_flags', [])
        
        # Check for social impact themes
        social_themes = ['social_justice', 'environmental', 'diversity', 'community', 'education']
        if any(theme in project_themes for theme in social_themes):
            # Check if grant supports social impact
            if any(keyword in grant.description.lower() for keyword in ['social', 'community', 'diversity', 'impact']):
                score += 10
                reasoning_parts.append("Project themes align with grant's social impact focus")
                details['theme_match'] = True
        
        # Diversity alignment
        if project_diversity:
            diversity_keywords = ['diversity', 'inclusion', 'underrepresented', 'emerging', 'female', 'poc']
            if any(keyword in grant.description.lower() for keyword in diversity_keywords):
                score += 10
                reasoning_parts.append("Project diversity elements match grant priorities")
                details['diversity_match'] = True
        
        # Location matching
        project_location = getattr(self.project, 'production_location', {})
        if project_location:
            grant_location = grant.location_restrictions
            if grant_location:
                # Check state/country alignment
                if grant_location.get('state') and project_location.get('state'):
                    if grant_location['state'].lower() == project_location['state'].lower():
                        score += 15
                        reasoning_parts.append("Perfect location match")
                        details['location_match'] = True
                elif grant_location.get('country', '').lower() == 'united states' and project_location.get('country', '').lower() in ['usa', 'united states', 'us']:
                    score += 8
                    reasoning_parts.append("Country eligibility confirmed")
                    details['country_match'] = True
        
        # Grant type alignment with project stage
        project_stage = getattr(self.project, 'project_stage', self.project.status)
        if grant.grant_type == 'development' and project_stage in ['development']:
            score += 12
            reasoning_parts.append("Grant type aligns with project development stage")
            details['stage_match'] = True
        elif grant.grant_type == 'production' and project_stage in ['pre_production', 'production']:
            score += 12
            reasoning_parts.append("Grant type aligns with project production stage")
            details['stage_match'] = True
        elif grant.grant_type == 'post_production' and project_stage in ['post_production']:
            score += 12
            reasoning_parts.append("Grant type aligns with project post-production stage")
            details['stage_match'] = True
        
        # Preference-based scoring
        if preferences:
            # Funding priority alignment
            if preferences.funding_priorities and grant.grant_type in preferences.funding_priorities:
                score += 8
                reasoning_parts.append("Matches your funding priorities")
                details['priority_match'] = True
            
            # Region preference
            if preferences.preferred_regions:
                # This is a simplified check - in real implementation, you'd have more sophisticated region matching
                score += 5
                details['region_preference'] = True
        
        # Cap the score at 100
        score = min(score, 100)
        
        # Create reasoning string
        if reasoning_parts:
            reasoning = "Strong match because: " + "; ".join(reasoning_parts[:3])  # Limit to first 3 reasons
        else:
            reasoning = "Basic eligibility match - review grant details for specific requirements"
        
        return score, reasoning, details
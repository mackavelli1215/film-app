from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.views import View
from django.db.models import Q, Count, Avg
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal
import json

from .models import Grant, GrantMatch, GrantPreferences
from projects.models import Project


class GrantListView(LoginRequiredMixin, ListView):
    """Main grants page showing all available grants with filtering"""
    model = Grant
    template_name = 'grants/list.html'
    context_object_name = 'grants'
    paginate_by = 20

    def get_queryset(self):
        queryset = Grant.objects.filter(
            deadline__gte=timezone.now().date()
        ).annotate(
            matches_count=Count('matches')
        ).order_by('deadline')

        # Apply search filter
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(organization__icontains=search) |
                Q(description__icontains=search)
            )

        # Apply filters
        grant_type = self.request.GET.get('grant_type')
        if grant_type:
            queryset = queryset.filter(grant_type=grant_type)

        funding_type = self.request.GET.get('funding_type')
        if funding_type:
            queryset = queryset.filter(funding_type=funding_type)

        min_amount = self.request.GET.get('min_amount')
        if min_amount:
            try:
                min_amount = Decimal(min_amount)
                queryset = queryset.filter(
                    Q(amount_min__gte=min_amount) | Q(amount_min__isnull=True)
                )
            except:
                pass

        max_amount = self.request.GET.get('max_amount')
        if max_amount:
            try:
                max_amount = Decimal(max_amount)
                queryset = queryset.filter(
                    Q(amount_max__lte=max_amount) | Q(amount_max__isnull=True)
                )
            except:
                pass

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get user's projects for quick apply functionality
        user_projects = Project.objects.filter(
            company__members__user=self.request.user
        ).filter(features_enabled__icontains='grants')
        
        context['user_projects'] = user_projects
        
        # Grant statistics
        total_grants = Grant.objects.filter(deadline__gte=timezone.now().date()).count()
        closing_soon = Grant.objects.filter(
            deadline__gte=timezone.now().date(),
            deadline__lte=timezone.now().date() + timedelta(days=30)
        ).count()
        
        context.update({
            'total_grants': total_grants,
            'closing_soon': closing_soon,
            'grant_types': Grant.GRANT_TYPES,
            'funding_types': Grant.FUNDING_TYPES,
            'current_filters': {
                'search': self.request.GET.get('search', ''),
                'grant_type': self.request.GET.get('grant_type', ''),
                'funding_type': self.request.GET.get('funding_type', ''),
                'min_amount': self.request.GET.get('min_amount', ''),
                'max_amount': self.request.GET.get('max_amount', ''),
            }
        })
        
        return context


class GrantDetailView(LoginRequiredMixin, DetailView):
    """Detailed view of a specific grant"""
    model = Grant
    template_name = 'grants/detail.html'
    pk_url_kwarg = 'grant_id'
    context_object_name = 'grant'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        grant = self.object
        
        # Get user's projects that have grants enabled
        user_projects = Project.objects.filter(
            company__members__user=self.request.user,
            features_enabled__icontains='grants'
        )
        
        # Check which projects already have matches with this grant
        existing_matches = GrantMatch.objects.filter(
            grant=grant,
            project__in=user_projects
        ).select_related('project')
        
        matched_project_ids = [match.project.id for match in existing_matches]
        available_projects = user_projects.exclude(id__in=matched_project_ids)
        
        context.update({
            'user_projects': available_projects,
            'existing_matches': existing_matches,
            'days_until_deadline': (grant.deadline - timezone.now().date()).days,
        })
        
        return context


class GrantFilterView(LoginRequiredMixin, View):
    """HTMX endpoint for filtering grants"""
    
    def get(self, request):
        # This will use the same logic as GrantListView but return only the grants list partial
        view = GrantListView()
        view.request = request
        queryset = view.get_queryset()
        
        context = {
            'grants': queryset[:20],  # Limit to first 20 for performance
            'user_projects': Project.objects.filter(
                company__members__user=request.user,
                features_enabled__icontains='grants'
            )
        }
        
        return render(request, 'grants/partials/grant_list.html', context)


class GrantSearchView(LoginRequiredMixin, View):
    """HTMX endpoint for search suggestions"""
    
    def get(self, request):
        query = request.GET.get('q', '')
        
        if len(query) < 2:
            return JsonResponse({'results': []})
        
        grants = Grant.objects.filter(
            Q(title__icontains=query) |
            Q(organization__icontains=query),
            deadline__gte=timezone.now().date()
        )[:10]
        
        results = []
        for grant in grants:
            results.append({
                'id': str(grant.id),
                'title': grant.title,
                'organization': grant.organization,
                'deadline': grant.deadline.strftime('%b %d, %Y'),
                'amount_range': f"${grant.amount_min:,.0f} - ${grant.amount_max:,.0f}" if grant.amount_min and grant.amount_max else "Amount varies"
            })
        
        return JsonResponse({'results': results})


class GrantBookmarkView(LoginRequiredMixin, View):
    """Bookmark/unbookmark a grant for later review"""
    
    def post(self, request, grant_id):
        grant = get_object_or_404(Grant, id=grant_id)
        
        # For now, we'll use a simple session-based bookmarking
        # In a real app, you might want a proper bookmark model
        bookmarks = request.session.get('grant_bookmarks', [])
        
        if str(grant_id) in bookmarks:
            bookmarks.remove(str(grant_id))
            bookmarked = False
        else:
            bookmarks.append(str(grant_id))
            bookmarked = True
        
        request.session['grant_bookmarks'] = bookmarks
        
        return JsonResponse({
            'status': 'success',
            'bookmarked': bookmarked,
            'message': 'Grant bookmarked!' if bookmarked else 'Bookmark removed'
        })


class GrantApplyView(LoginRequiredMixin, View):
    """Quick apply for a grant (creates a grant match)"""
    
    def post(self, request, grant_id):
        grant = get_object_or_404(Grant, id=grant_id)
        project_id = request.POST.get('project_id')
        
        if not project_id:
            return JsonResponse({
                'status': 'error',
                'message': 'Please select a project'
            })
        
        try:
            project = Project.objects.get(
                id=project_id,
                company__members__user=request.user
            )
        except Project.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': 'Project not found'
            })
        
        # Check if match already exists
        existing_match = GrantMatch.objects.filter(
            project=project,
            grant=grant
        ).first()
        
        if existing_match:
            return JsonResponse({
                'status': 'error',
                'message': 'This grant is already in your project matches'
            })
        
        # Create a new grant match
        from grants.services import GrantMatcher
        matcher = GrantMatcher(project)
        score, reasoning, details = matcher._calculate_match_score(grant, None)
        
        grant_match = GrantMatch.objects.create(
            project=project,
            grant=grant,
            match_score=score,
            match_reasoning=reasoning,
            match_details=details,
            status='interested'
        )
        
        return JsonResponse({
            'status': 'success',
            'message': f'Grant added to {project.name} with {score}% match score',
            'match_id': str(grant_match.id),
            'match_score': score
        })
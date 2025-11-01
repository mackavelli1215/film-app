from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.views import View
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.db import transaction
from django.utils import timezone
from .models import Project, ProjectFeature
from .forms import ProjectSetupForm, ProjectCoreDataForm, GrantPreferencesForm, ProjectFeatureSetupForm
from grants.models import GrantPreferences, Grant, GrantMatch


class ProjectListView(LoginRequiredMixin, ListView):
    model = Project
    template_name = 'projects/list.html'
    context_object_name = 'projects'


class ProjectCreateView(LoginRequiredMixin, CreateView):
    model = Project
    form_class = ProjectSetupForm
    template_name = 'projects/create.html'
    success_url = reverse_lazy('projects:list')
    
    def form_valid(self, form):
        # Set the company from user's profile
        try:
            from accounts.models import Profile
            profile = Profile.objects.get(user=self.request.user)
            form.instance.company = profile.company
        except Profile.DoesNotExist:
            # Fallback: get or create a default company
            from accounts.models import Company
            company, created = Company.objects.get_or_create(
                name="Default Production Company",
                defaults={'size': 'startup', 'tier': 'free'}
            )
            form.instance.company = company
        
        # Mark core setup as completed
        form.instance.core_setup_completed = True
        
        response = super().form_valid(form)
        
        # Create project status
        from projects.models import ProjectStatus
        ProjectStatus.objects.create(project=form.instance)
        
        # Redirect to feature setup
        return redirect('projects:feature_setup', project_id=form.instance.id)


class ProjectDetailView(LoginRequiredMixin, DetailView):
    model = Project
    template_name = 'projects/detail.html'
    pk_url_kwarg = 'project_id'
    context_object_name = 'project'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project = self.get_object()
        
        # Add feature setup status
        context['features_enabled'] = project.features_enabled
        context['grants_enabled'] = 'grants' in project.features_enabled
        
        # Add grant preferences if grants are enabled
        if context['grants_enabled']:
            try:
                context['grant_preferences'] = project.grant_preferences
            except GrantPreferences.DoesNotExist:
                context['grant_preferences'] = None
                context['grants_setup_needed'] = True
        
        return context


class ProjectFeatureSetupView(LoginRequiredMixin, View):
    """Setup project features after initial project creation"""
    
    def get(self, request, project_id):
        project = get_object_or_404(Project, id=project_id)
        form = ProjectFeatureSetupForm(project=project)
        
        context = {
            'project': project,
            'form': form,
            'step': 'features'
        }
        return render(request, 'projects/setup/features.html', context)
    
    def post(self, request, project_id):
        project = get_object_or_404(Project, id=project_id)
        form = ProjectFeatureSetupForm(project=project, data=request.POST)
        
        if form.is_valid():
            selected_features = form.cleaned_data['features']
            project.features_enabled = selected_features
            project.save()
            
            # Create ProjectFeature entries for enabled features
            for feature in selected_features:
                ProjectFeature.objects.get_or_create(
                    project=project,
                    feature=feature,
                    defaults={'setup_completed': False}
                )
            
            # If grants is enabled, redirect to grant setup
            if 'grants' in selected_features:
                return redirect('projects:grant_setup', project_id=project.id)
            else:
                messages.success(request, 'Project features configured successfully!')
                return redirect('projects:detail', project_id=project.id)
        
        context = {
            'project': project,
            'form': form,
            'step': 'features'
        }
        return render(request, 'projects/setup/features.html', context)


class ProjectGrantSetupView(LoginRequiredMixin, View):
    """Setup grant preferences and additional project data for grant discovery"""
    
    def get(self, request, project_id):
        project = get_object_or_404(Project, id=project_id)
        
        # Check if grants feature is enabled
        if 'grants' not in project.features_enabled:
            messages.error(request, 'Grants feature must be enabled first.')
            return redirect('projects:feature_setup', project_id=project.id)
        
        # Get or create grant preferences
        grant_preferences, created = GrantPreferences.objects.get_or_create(project=project)
        
        core_data_form = ProjectCoreDataForm(instance=project)
        grant_prefs_form = GrantPreferencesForm(instance=grant_preferences)
        
        context = {
            'project': project,
            'core_data_form': core_data_form,
            'grant_prefs_form': grant_prefs_form,
            'step': 'grant_setup'
        }
        return render(request, 'projects/setup/grant_setup.html', context)
    
    def post(self, request, project_id):
        project = get_object_or_404(Project, id=project_id)
        grant_preferences, created = GrantPreferences.objects.get_or_create(project=project)
        
        core_data_form = ProjectCoreDataForm(instance=project, data=request.POST)
        grant_prefs_form = GrantPreferencesForm(instance=grant_preferences, data=request.POST)
        
        if core_data_form.is_valid() and grant_prefs_form.is_valid():
            with transaction.atomic():
                core_data_form.save()
                grant_prefs_form.save()
                
                # Mark grant feature as setup completed
                try:
                    grant_feature = ProjectFeature.objects.get(project=project, feature='grants')
                    grant_feature.setup_completed = True
                    grant_feature.save()
                except ProjectFeature.DoesNotExist:
                    ProjectFeature.objects.create(
                        project=project,
                        feature='grants',
                        setup_completed=True
                    )
                
                messages.success(request, 'Grant setup completed successfully!')
                return redirect('projects:grants', project_id=project.id)
        
        context = {
            'project': project,
            'core_data_form': core_data_form,
            'grant_prefs_form': grant_prefs_form,
            'step': 'grant_setup'
        }
        return render(request, 'projects/setup/grant_setup.html', context)


class ProjectOverviewView(LoginRequiredMixin, DetailView):
    model = Project
    template_name = 'projects/tabs/overview.html'
    pk_url_kwarg = 'project_id'


class ProjectScriptView(LoginRequiredMixin, DetailView):
    model = Project
    template_name = 'projects/tabs/script.html'
    pk_url_kwarg = 'project_id'


class ProjectBudgetView(LoginRequiredMixin, DetailView):
    model = Project
    template_name = 'projects/tabs/budget.html'
    pk_url_kwarg = 'project_id'


class ProjectScheduleView(LoginRequiredMixin, DetailView):
    model = Project
    template_name = 'projects/tabs/schedule.html'
    pk_url_kwarg = 'project_id'


class ProjectGrantsView(LoginRequiredMixin, DetailView):
    model = Project
    template_name = 'projects/tabs/grants.html'
    pk_url_kwarg = 'project_id'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project = self.get_object()
        
        # Check if grants feature is enabled and setup
        grants_enabled = 'grants' in project.features_enabled
        context['grants_enabled'] = grants_enabled
        
        if grants_enabled:
            try:
                grant_feature = ProjectFeature.objects.get(project=project, feature='grants')
                context['grants_setup_completed'] = grant_feature.setup_completed
            except ProjectFeature.DoesNotExist:
                context['grants_setup_completed'] = False
            
            if context['grants_setup_completed']:
                # Get grant matches
                grant_matches = GrantMatch.objects.filter(project=project).select_related('grant')
                context['grant_matches'] = grant_matches
                context['total_matches'] = grant_matches.count()
                context['perfect_matches'] = grant_matches.filter(match_quality='perfect').count()
                context['excellent_matches'] = grant_matches.filter(match_quality='excellent').count()
                
                # Get grant preferences
                try:
                    context['grant_preferences'] = project.grant_preferences
                except GrantPreferences.DoesNotExist:
                    context['grant_preferences'] = None
            else:
                context['setup_needed'] = True
        else:
            context['feature_not_enabled'] = True
        
        return context


class ProjectFestivalsView(LoginRequiredMixin, DetailView):
    model = Project
    template_name = 'projects/tabs/festivals.html'
    pk_url_kwarg = 'project_id'


class ProjectCommentsView(LoginRequiredMixin, DetailView):
    model = Project
    template_name = 'projects/tabs/comments.html'
    pk_url_kwarg = 'project_id'


class ScriptUploadView(LoginRequiredMixin, View):
    def post(self, request, project_id):
        # Placeholder for script upload functionality
        return JsonResponse({'status': 'success'})


class AddCommentView(LoginRequiredMixin, View):
    def post(self, request, project_id):
        # Placeholder for adding comments
        return JsonResponse({'status': 'success'})


class GrantDiscoveryView(LoginRequiredMixin, View):
    """Trigger grant discovery for a project"""
    
    def post(self, request, project_id):
        project = get_object_or_404(Project, id=project_id)
        
        # Check if grants feature is enabled and setup
        if 'grants' not in project.features_enabled:
            return JsonResponse({'status': 'error', 'message': 'Grants feature not enabled'})
        
        try:
            grant_feature = ProjectFeature.objects.get(project=project, feature='grants')
            if not grant_feature.setup_completed:
                return JsonResponse({'status': 'error', 'message': 'Grant setup not completed'})
        except ProjectFeature.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Grant feature not found'})
        
        # Run grant discovery
        try:
            from grants.services import GrantMatcher
            matcher = GrantMatcher(project)
            matches_found = matcher.discover_grants()
            
            # Update last run time
            grant_feature.last_run_at = timezone.now()
            grant_feature.save()
            
            return JsonResponse({
                'status': 'success',
                'message': f'Grant discovery completed. Found {matches_found} new matches.',
                'matches_found': matches_found
            })
            
        except Exception as e:
            return JsonResponse({
                'status': 'error', 
                'message': f'Error during grant discovery: {str(e)}'
            })


class GrantMatchDetailView(LoginRequiredMixin, View):
    """Get detailed information about a grant match"""
    
    def get(self, request, project_id, match_id):
        project = get_object_or_404(Project, id=project_id)
        grant_match = get_object_or_404(GrantMatch, id=match_id, project=project)
        
        context = {
            'project': project,
            'grant_match': grant_match,
            'grant': grant_match.grant
        }
        
        return render(request, 'projects/modals/grant_detail.html', context)
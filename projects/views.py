from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.views import View
from django.urls import reverse_lazy
from .models import Project


class ProjectListView(LoginRequiredMixin, ListView):
    model = Project
    template_name = 'projects/list.html'
    context_object_name = 'projects'


class ProjectCreateView(LoginRequiredMixin, CreateView):
    model = Project
    template_name = 'projects/create.html'
    fields = ['name', 'type', 'genre', 'logline', 'budget_range']
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
        
        response = super().form_valid(form)
        
        # Create project status
        from projects.models import ProjectStatus
        ProjectStatus.objects.create(project=self.object)
        
        return response


class ProjectDetailView(LoginRequiredMixin, DetailView):
    model = Project
    template_name = 'projects/detail.html'
    pk_url_kwarg = 'project_id'
    context_object_name = 'project'


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
from django.shortcuts import render
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'core/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get project data for the dashboard
        try:
            from projects.models import Project
            
            # Get project count and recent projects
            context['project_count'] = Project.objects.count()
            context['projects'] = Project.objects.all()[:5]  # Show last 5 projects
            
        except Exception as e:
            context['error'] = f"Unable to load project data: {str(e)}"
            context['projects'] = []
            context['project_count'] = 0
        
        return context
    
    def get(self, request, *args, **kwargs):
        try:
            return super().get(request, *args, **kwargs)
        except Exception as e:
            return HttpResponse(f"Template error: {e}", status=500)
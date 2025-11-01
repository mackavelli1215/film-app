from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.views import View
from agents.models import AgentJob
from projects.models import Project


class AgentJobListView(LoginRequiredMixin, ListView):
    model = AgentJob
    template_name = 'agents/job_list.html'
    context_object_name = 'jobs'


class AgentJobDetailView(LoginRequiredMixin, DetailView):
    model = AgentJob
    template_name = 'agents/job_detail.html'
    pk_url_kwarg = 'job_id'


class EnqueueAgentView(LoginRequiredMixin, View):
    def post(self, request, agent_type):
        project_id = request.POST.get('project_id')
        project = get_object_or_404(Project, id=project_id)
        
        # Create new agent job
        job = AgentJob.objects.create(
            project=project,
            agent_type=agent_type,
            input_params=request.POST.dict()
        )
        
        return JsonResponse({
            'status': 'success',
            'job_id': str(job.id),
            'message': f'{agent_type} job queued successfully'
        })


class AgentJobStatusView(LoginRequiredMixin, DetailView):
    model = AgentJob
    pk_url_kwarg = 'job_id'
    
    def get(self, request, *args, **kwargs):
        job = self.get_object()
        return JsonResponse({
            'status': job.status,
            'created_at': job.created_at.isoformat(),
            'started_at': job.started_at.isoformat() if job.started_at else None,
            'completed_at': job.completed_at.isoformat() if job.completed_at else None,
            'error_message': job.error_message,
        })
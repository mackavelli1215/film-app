from django.urls import path
from . import views

app_name = 'agents'

urlpatterns = [
    # Agent job management
    path('jobs/', views.AgentJobListView.as_view(), name='job_list'),
    path('jobs/<uuid:job_id>/', views.AgentJobDetailView.as_view(), name='job_detail'),
    
    # Agent execution endpoints
    path('run/<str:agent_type>/', views.EnqueueAgentView.as_view(), name='enqueue'),
    path('status/<uuid:job_id>/', views.AgentJobStatusView.as_view(), name='job_status'),
]
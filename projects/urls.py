from django.urls import path, include
from . import views

app_name = 'projects'

urlpatterns = [
    # Project list and creation
    path('', views.ProjectListView.as_view(), name='list'),
    path('create/', views.ProjectCreateView.as_view(), name='create'),
    
    # Project setup flows
    path('<uuid:project_id>/setup/features/', views.ProjectFeatureSetupView.as_view(), name='feature_setup'),
    path('<uuid:project_id>/setup/grants/', views.ProjectGrantSetupView.as_view(), name='grant_setup'),
    
    # Project detail with tabs
    path('<uuid:project_id>/', views.ProjectDetailView.as_view(), name='detail'),
    path('<uuid:project_id>/overview/', views.ProjectOverviewView.as_view(), name='overview'),
    path('<uuid:project_id>/script/', views.ProjectScriptView.as_view(), name='script'),
    path('<uuid:project_id>/budget/', views.ProjectBudgetView.as_view(), name='budget'),
    path('<uuid:project_id>/schedule/', views.ProjectScheduleView.as_view(), name='schedule'),
    path('<uuid:project_id>/grants/', views.ProjectGrantsView.as_view(), name='grants'),
    path('<uuid:project_id>/festivals/', views.ProjectFestivalsView.as_view(), name='festivals'),
    path('<uuid:project_id>/comments/', views.ProjectCommentsView.as_view(), name='comments'),
    
    # Grant-specific endpoints
    path('<uuid:project_id>/grants/discover/', views.GrantDiscoveryView.as_view(), name='grant_discovery'),
    path('<uuid:project_id>/grants/<uuid:match_id>/', views.GrantMatchDetailView.as_view(), name='grant_match_detail'),
    
    # HTMX endpoints
    path('<uuid:project_id>/script/upload/', views.ScriptUploadView.as_view(), name='script_upload'),
    path('<uuid:project_id>/comments/add/', views.AddCommentView.as_view(), name='add_comment'),
]
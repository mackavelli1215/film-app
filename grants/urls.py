from django.urls import path
from . import views

app_name = 'grants'

urlpatterns = [
    # Main grants page
    path('', views.GrantListView.as_view(), name='list'),
    
    # Grant detail view
    path('<uuid:grant_id>/', views.GrantDetailView.as_view(), name='detail'),
    
    # HTMX endpoints for filtering and search
    path('filter/', views.GrantFilterView.as_view(), name='filter'),
    path('search/', views.GrantSearchView.as_view(), name='search'),
    
    # Grant management
    path('bookmark/<uuid:grant_id>/', views.GrantBookmarkView.as_view(), name='bookmark'),
    path('apply/<uuid:grant_id>/', views.GrantApplyView.as_view(), name='apply'),
]
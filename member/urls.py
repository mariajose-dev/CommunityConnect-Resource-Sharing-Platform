from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing_page, name='landing'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    path('dashboard/', views.dashboard_view, name='dashboard'),
    
    path('explore/', views.explore_view, name='explore'),
    path('item/<int:item_id>/', views.item_detail, name='item_detail'),
    path('item/<int:item_id>/request/', views.request_item, name='request_item'),
    path('item/<int:item_id>/report/', views.report_item, name='report_item'),
    
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path('profile/<str:username>/', views.user_profile, name='user_profile'),
    
    path('leaderboard/', views.leaderboard_view, name='leaderboard'),
    
    # Member specific
    path('my-items/', views.my_items, name='my_items'),
    path('my-items/add/', views.add_item, name='add_item'),
    path('my-items/edit/<int:item_id>/', views.edit_item, name='edit_item'),
    path('my-requests/', views.my_requests, name='my_requests'),
    path('incoming-requests/', views.incoming_requests, name='incoming_requests'),
    path('request/<int:req_id>/approve/', views.approve_request, name='approve_request'),
    path('request/<int:req_id>/reject/', views.reject_request, name='reject_request'),
    path('request/<int:req_id>/collect/', views.mark_collected, name='mark_collected'),
    path('request/<int:req_id>/review/', views.review_item, name='review_item'),
    
    # Admin specific
    path('admin-dashboard/categories/', views.manage_categories, name='manage_categories'),
    path('admin-dashboard/categories/add/', views.add_category, name='add_category'),
    path('admin-dashboard/users/', views.manage_users, name='manage_users'),
    path('admin-dashboard/users/<int:user_id>/toggle-block/', views.toggle_block_user, name='toggle_block_user'),
    path('admin-dashboard/items/', views.all_items, name='all_items'),
    path('admin-dashboard/items/<int:item_id>/toggle-active/', views.toggle_item_active, name='toggle_item_active'),
    path('admin-dashboard/borrow-records/', views.all_borrow_records, name='all_borrow_records'),
    path('admin-dashboard/reviews/', views.monitor_reviews, name='monitor_reviews'),
]

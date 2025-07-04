from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home, name='home'),  
    path('login/', views.login_view, name='login'),  
    path('register/', views.register, name='register'),  
    path('mainhome/', views.mainhome, name='mainhome'),  
    path('items/', views.items, name='items'),  
    path('reports/', views.reports, name='reports'),  
    path('sales/', views.sales, name='sales'),  
    path('item_list/', views.item_list, name='item_list'),  
    path('item_list_maker/', views.item_list_maker, name='item_list_maker'),  
    path('item_list_checker/', views.item_list_checker, name='item_list_checker'),  
    path('stockin/', views.stockin, name='stockin'),  
    path('stockout/', views.create_stockout_request, name='stockout'),  
    path('stockin_history/', views.stockin_history, name='stockin_history'),  
    path('maker_stockout_request/', views.maker_stockout_request, name='maker_stockout_request'),  
    path('checker_stockout_list/', views.checker_stockout_list, name='checker_stockout_list'),  
    path('logout_view/', views.logout_view, name='logout'),  
    path('add_items_checker/', views.add_items_checker, name='add_items_checker'),  
    
    path('dashboard_maker/', views.dashboard_maker, name='dashboard_maker'),
    path('dashboard_checker/', views.dashboard_checker, name='dashboard_checker'),
    path('allusers/', views.allusers, name='allusers'),
    path('stockout_requests/', views.stockout_requests, name='stockout_requests'),
    path('my_requests/', views.myrequests, name='my_requests'),
    path('checker_request/', views.checker_request, name='checker_requests'),
    path('viewitems/<int:id>', views.viewitems, name='viewitems'),
    path('approve_request/<int:id>', views.approve_request, name='approve_request'),
    path('reject_request/<int:id>', views.reject_request, name='reject_request'),
    path('view_approved/<int:id>', views.view_approved, name='view_approved'),
    path('view_rejected/<int:id>', views.view_rejected, name='view_rejected'),
    path('deleteitem_admin/<int:id>', views.deleteitem_admin, name='deleteitem_admin'),
    path('delete_users/<int:id>', views.delete_users, name='delete_users'),
    path('view_items/<int:id>', views.view_items, name='view_items'),
    path('edit_items/<int:id>', views.edit_item, name='edit_items'),
    path('accounts/login/', auth_views.LoginView.as_view(template_name='temp/login.html'), name='login'),

    
    path('categories/', views.categories, name='categories'),
    path('add_category/', views.add_category, name='add_category'),
    path('access_denied/', views.access_denied, name='access_denied'),
    path('add_item_checker/', views.add_item_checker, name='add_item_checker'),  
    path('stockin_checker/', views.stockin_checker, name='stockin_checker'),  
    
    path('send_email/', views.send_test_email, name='send_email'),
    path('check_stock/', views.check_and_notify_low_stock, name='check_stock'),
    

    
    path('contact/', views.contact, name='contact'),
    
    
]
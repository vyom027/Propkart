# Propkart/app/urls.py

from django.urls import path
from . import views
from django.conf.urls.static import static


urlpatterns = [


    path('', views.index, name='index'),
    path('login', views.login_view, name='login'),
    path('logout', views.logOutUser, name='logout'),
    path('register', views.register, name='register'),
    path('forget-password', views.forget_password, name='forget_password'),
    path('verify-password-reset-otp/<int:token_id>/', views.verify_password_reset_otp, name='verify_password_reset_otp'),
    path('reset-password', views.reset_password, name='reset_password'),
    path('verify-otp/', views.verify_otp, name='verify_otp'), 
    path('about',views.about,name='aboutUs'),
    path('contact',views.contact,name='contactUs'),
    path('profile',views.profile,name='profile'),
    path('profile/edit', views.edit_profile, name='edit_profile'),
    path('properties', views.property_list, name='property_list'),
    path('property/<int:property_id>/', views.property_detail, name='property_detail'),
    path('property/<int:property_id>/increment-view/', views.increment_property_view, name='increment_property_view'),
    path('property/<int:property_id>/message/', views.property_message, name='property_message'),
    path('property/<int:property_id>/brochure.pdf', views.property_brochure_pdf, name='property_brochure_pdf'),
    

    path('seller',views.become_seller_request, name='become_seller'),
    path("verify-seller/<uuid:token>/", views.verify_seller, name="verify_seller"),
    path('seller/dashboard', views.seller_dashboard, name='seller_dashboard'),

    path('seller/property_create/', views.property_create, name='property_create'),
    path('seller/property/<int:property_id>/edit/', views.property_update, name='property_update'),
    path('seller/property/<int:property_id>/delete/', views.property_delete, name='property_delete'),
    path('seller/property/<int:property_id>/toggle-visibility/', views.toggle_property_visibility, name='toggle_property_visibility'),
    path('seller/properties/bulk-delete', views.properties_bulk_delete, name='properties_bulk_delete'),
    path('seller/import', views.seller_import_properties, name='seller_import_properties'),

    path('seller/messages', views.seller_messages, name='seller_messages'),
    path('seller/properties', views.my_properties, name='my_properties'),
    path('seller/enquiries', views.seller_enquiries, name='seller_enquiries'),
    path('seller/analytics', views.seller_analytics, name='seller_analytics'),
    path('seller/support', views.seller_support, name='seller_support'),
    
    # Enquiry URLs
    path('property/<int:property_id>/enquiry/', views.submit_enquiry, name='submit_enquiry'),
    path('seller/enquiry/<int:enquiry_id>/delete/', views.delete_enquiry, name='delete_enquiry'),
    path('seller/enquiry/<int:enquiry_id>/mark-replied/', views.mark_enquiry_replied, name='mark_enquiry_replied'),
    
    # Visit Request URLs
    path('property/<int:property_id>/request-visit/', views.request_visit, name='request_visit'),
    path('seller/visit-requests/', views.seller_visit_requests, name='seller_visit_requests'),
    path('seller/visit-request/<int:request_id>/update/', views.update_visit_request, name='update_visit_request'),
    path('buyer/visit-requests/', views.buyer_visit_requests, name='buyer_visit_requests'),
    path('buyer/visit-request/<int:request_id>/cancel/', views.cancel_visit_request, name='cancel_visit_request'),
    
    # Wishlist
    path('wishlist/toggle/', views.wishlist_toggle, name='wishlist_toggle'),
    path('wishlist/', views.wishlist_list, name='wishlist_list'),
    
    # Chat API endpoints
    path('api/chat/ask/', views.chat_ask, name='chat_ask'),
    path('api/chat/history/', views.chat_history, name='chat_history'),
    path('api/chat/new-session/', views.chat_new_session, name='chat_new_session'),
    path('api/chat/clear/', views.chat_clear, name='chat_clear'),
    path('api/chat/conversation/', views.chat_conversation, name='chat_conversation'),
    path('api/chat/delete/', views.chat_delete_messages, name='chat_delete_messages'),
    path('api/chat/clear-conversation/', views.chat_clear_conversation, name='chat_clear_conversation'),
    
    path('buyer/messages', views.buyer_messages, name='buyer_messages'),
    path('messages/reply', views.message_reply, name='message_reply'),
    path('api/notifications/', views.notifications_list, name='notifications_list'),
    path('api/notifications/mark-read', views.notifications_mark_read, name='notifications_mark_read'),
    path('api/notifications/mark-all-read', views.notifications_mark_all_read, name='notifications_mark_all_read'),
]
from django.urls import path
from . import views
from .views import EventListAPI, TicketBookingAPI

urlpatterns = [
    path('', views.event_list_view, name='event_list'),
    path('<int:pk>/', views.event_detail_view, name='event_detail'),
    path('api/events/', EventListAPI.as_view(), name='api_event_list'),
    path('api/events/<int:pk>/tickets/', TicketBookingAPI.as_view(), name='api_ticket_booking'),
    path('book-ticket/', views.api_booking_form_view, name='api_booking_form'),
    path('upcoming/', views.upcoming_events, name='upcoming_events'),
]

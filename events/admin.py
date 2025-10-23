from django.contrib import admin
from .models import Event, TicketType, Booking
# Register your models here.

class TicketTypeInline(admin.TabularInline):
    model = TicketType
    extra = 1

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title','description','date_time','location','is_published','max_capacity')
    list_filter = ('is_published','date_time')
    search_field = ('title','location')
    inlines = [TicketTypeInline]


@admin.register(TicketType)
class TicketTypeAdmin(admin.ModelAdmin):
    list_display = ('event', 'name', 'price', 'quantity_available')
    list_filter = ('event',)

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('user', 'event', 'ticket_type', 'quantity', 'booking_date')
    list_filter = ('event', 'booking_date')
    search_fields = ('user__username', 'event__title')
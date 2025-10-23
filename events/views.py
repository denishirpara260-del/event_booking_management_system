from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError

from .models import Event, Booking
from .forms import BookingForm

def upcoming_events(request):
    events = Event.objects.filter(is_published=True).order_by('date_time')
    return render(request, 'events/upcoming_events.html', {'events': events})
    
def event_list_view(request):
    query = request.GET.get('q', '').strip()
    date_filter = request.GET.get('date', '').strip()

    if query or date_filter:
        events = Event.objects.published_upcoming()
    else:
        events = Event.objects.published_upcoming()

    if query:
        events = events.filter(Q(title__icontains=query) | Q(location__icontains=query))
    if date_filter: 
        events = events.filter(date_time__date=date_filter)

    events = events.order_by('date_time')
    return render(request, 'events/event_list.html', {
        'events': events,
        'query': query,
        'date_filter': date_filter,
    })


@login_required
def event_detail_view(request, pk):
    event = get_object_or_404(Event, pk=pk, is_published=True)
    ticket_types = event.ticket_types.all()

    if request.method == "POST":
        form = BookingForm(request.POST, user=request.user, event=event)
        if form.is_valid():
            try:
                booking = form.save()
                messages.success(
                    request,
                    f"✅ Booked {booking.quantity} {booking.ticket_type.name} ticket(s) successfully!"
                )
                return redirect("profile")
            except ValidationError as e:
                messages.error(request, e.message)
            except Exception as e:
                messages.error(request, f"❌ Booking failed: {e}")
    else:
        form = BookingForm(user=request.user, event=event)

    return render(request, "events/event_detail.html", {
        "event": event,
        "ticket_types": ticket_types,
        "form": form,
    })


from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from .models import Event
from .serializers import EventSerializer, TicketBookingSerializer
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError


class EventListAPI(generics.ListAPIView):
    queryset = Event.objects.filter(is_published=True)
    serializer_class = EventSerializer
    permission_classes = [AllowAny]


class TicketBookingAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        event = get_object_or_404(Event, pk=pk, is_published=True)
        serializer = TicketBookingSerializer(data=request.data, context={'request': request})

        if serializer.is_valid():
            try:
                booking = serializer.save()
                return Response({
                    "message": "Booking successful!",
                    "event": event.title,
                    "ticket_type": booking.ticket_type.name,
                    "quantity": booking.quantity,
                }, status=status.HTTP_201_CREATED)
            except ValidationError as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

import requests
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import APIBookingForm

API_BASE_URL = "http://127.0.0.1:8000/events/api"  

@login_required
def api_booking_form_view(request):
    event_id = request.GET.get('event_id')
    form = APIBookingForm(request.POST or None, event_id=event_id)

    if request.method == "POST" and form.is_valid():
        event = form.cleaned_data['event']
        ticket_type = form.cleaned_data['ticket_type']
        quantity = form.cleaned_data['quantity']

        token = request.user.auth_token.key  # user must have a token
        headers = {"Authorization": f"Token {token}"}
        data = {"ticket_type_id": ticket_type.id, "quantity": quantity}

        url = f"{API_BASE_URL}/events/{event.id}/tickets/"
        response = requests.post(url, json=data, headers=headers)

        if response.status_code == 201:
            messages.success(request, "✅ Booking successful!")
        else:
            messages.error(request, f"❌ Booking failed: {response.json().get('error', 'Unknown error')}")

    return render(request, "events/api_booking_form.html", {"form": form})


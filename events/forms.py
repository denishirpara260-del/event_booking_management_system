from django import forms
from django.core.exceptions import ValidationError
from .models import TicketType, Booking, Event


class BookingForm(forms.Form):
    ticket_type = forms.ModelChoiceField(
        queryset=TicketType.objects.none(),
        label="Select Ticket Type"
    )
    quantity = forms.IntegerField(min_value=1, label="Number of Tickets")

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        event = kwargs.pop("event", None)
        super().__init__(*args, **kwargs)
        if event:
            self.fields["ticket_type"].queryset = TicketType.objects.filter(event=event)
        else:
            self.fields["ticket_type"].queryset = TicketType.objects.none()

    def clean(self):
        cleaned_data = super().clean()
        ticket_type = cleaned_data.get("ticket_type")
        quantity = cleaned_data.get("quantity")
        if ticket_type and quantity:
            if ticket_type.quantity_available < quantity:
                raise ValidationError(
                    f"Only {ticket_type.quantity_available} tickets available for {ticket_type.name}."
                )
        return cleaned_data

    def save(self):
        ticket_type = self.cleaned_data["ticket_type"]
        quantity = self.cleaned_data["quantity"]
        return Booking.create_booking(self.user, ticket_type, quantity)


class APIBookingForm(forms.Form):
    event = forms.ModelChoiceField(
        queryset=Event.objects.filter(is_published=True),
        label="Select Event",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    ticket_type = forms.ModelChoiceField(
        queryset=TicketType.objects.none(),
        label="Select Ticket Type",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    quantity = forms.IntegerField(
        min_value=1,
        label="Number of Tickets",
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )

    def __init__(self, *args, **kwargs):
        event_id = kwargs.pop('event_id', None)
        super().__init__(*args, **kwargs)
        if event_id:
            self.fields['ticket_type'].queryset = TicketType.objects.filter(event_id=event_id, event__is_published=True)
        else:
            self.fields['ticket_type'].queryset = TicketType.objects.filter(event__is_published=True)
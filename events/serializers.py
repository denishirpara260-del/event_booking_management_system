from rest_framework import serializers
from .models import Event, TicketType, Booking
from django.core.exceptions import ValidationError

class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ['id', 'title', 'description', 'date_time', 'location', 'max_capacity']


class TicketBookingSerializer(serializers.Serializer):
    ticket_type_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)

    def validate(self, data):
        try:
            ticket_type = TicketType.objects.get(pk=data['ticket_type_id'])
        except TicketType.DoesNotExist:
            raise serializers.ValidationError("Invalid ticket type.")

        if ticket_type.quantity_available < data['quantity']:
            raise serializers.ValidationError("Not enough tickets available.")

        data['ticket_type'] = ticket_type
        return data

    def create(self, validated_data):
        user = self.context['request'].user
        ticket_type = validated_data['ticket_type']
        quantity = validated_data['quantity']
        return Booking.create_booking(user, ticket_type, quantity)

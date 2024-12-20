from rest_framework import serializers

from .models import Booking, Hotel


class HotelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hotel
        fields = ['id', 'name', ]


class BookingSerializer(serializers.ModelSerializer):
    hotel = serializers.CharField(write_only=True)
    room = serializers.CharField(source='room.room_number', read_only=True)
    hotel_name = serializers.CharField(source='room.hotel.name', read_only=True)

    class Meta:
        model = Booking
        fields = ['id', 'hotel', 'hotel_name', 'room', 'start_date', 'end_date', ]

    def validate(self, attrs):
        if attrs['start_date'] > attrs['end_date']:
            raise serializers.ValidationError("end date can't be before start date")
        return attrs

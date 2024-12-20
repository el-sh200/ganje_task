from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from drf_spectacular.utils import extend_schema
from rest_framework import generics, status
from rest_framework.response import Response

from .models import Room, Booking, Hotel
from .serializers import BookingSerializer, HotelSerializer


@extend_schema(tags=['booking'])
class HotelList(generics.ListAPIView):
    queryset = Hotel.objects.all()
    serializer_class = HotelSerializer


@extend_schema(tags=['booking'])
class BookingCreate(generics.CreateAPIView):
    serializer_class = BookingSerializer

    def create(self, request, *args, **kwargs):
        booking_srz = BookingSerializer(data=request.data)
        booking_srz.is_valid(raise_exception=True)
        data = booking_srz.validated_data

        try:
            with transaction.atomic():
                available_rooms = self.get_available_rooms(data)
                if not available_rooms.exists():
                    return Response({"error": "No available rooms."}, status=status.HTTP_400_BAD_REQUEST)

                booking = Booking.objects.create(
                    user=request.user,
                    room=available_rooms.first(),
                    start_date=data['start_date'],
                    end_date=data['end_date']
                )

            return Response({
                'message': 'Booked successfully',
                'data': BookingSerializer(booking).data,
            }, status=status.HTTP_201_CREATED)

        except ObjectDoesNotExist:
            return Response({"error": "Room not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get_available_rooms(self, data):
        booked_rooms = Booking.objects.filter(
            room__hotel_id=data['hotel'],
            start_date__lte=data['end_date'],
            end_date__gte=data['start_date'],
        ).values_list('room_id', flat=True)

        return Room.objects.filter(hotel_id=data['hotel']).exclude(id__in=booked_rooms)

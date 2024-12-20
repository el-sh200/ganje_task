from django.contrib.auth.models import User
from django.test import TransactionTestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Room, Booking, Hotel


class BookingTests(TransactionTestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='password')
        self.hotel = Hotel.objects.create(name='testhotel')
        self.room = Room.objects.create(room_number='101', hotel_id=self.hotel.id)
        self.url = reverse('booking_create')
        self.token = RefreshToken.for_user(self.user)
        self.auth_headers = {
            'HTTP_AUTHORIZATION': f'Bearer {str(self.token.access_token)}'
        }

    def test_booking_creation(self):
        response = self.client.post(self.url, {
            'hotel': self.hotel.id,
            'start_date': '2024-01-01',
            'end_date': '2024-01-05'
        }, **self.auth_headers)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Booking.objects.count(), 1)

    def test_race_condition(self):
        booking_data = {
            'hotel': self.hotel.id,
            'start_date': '2024-01-01',
            'end_date': '2024-01-05'
        }

        # Simulate two concurrent bookings
        from threading import Thread

        def attempt_booking():
            response = self.client.post(self.url, booking_data, **self.auth_headers)
            return response

        thread1 = Thread(target=attempt_booking)
        thread2 = Thread(target=attempt_booking)

        thread1.start()
        thread2.start()

        thread1.join()
        thread2.join()
        # must create just one booking instance
        self.assertEqual(Booking.objects.count(), 1)

    def test_booking_overlap(self):
        # Create an initial booking
        self.client.post(self.url, {
            'hotel': self.hotel.id,
            'start_date': '2024-01-01',
            'end_date': '2024-01-05'
        }, **self.auth_headers)

        response = self.client.post(self.url, {
            'hotel': self.hotel.id,
            'start_date': '2024-01-03',
            'end_date': '2024-01-07'
        }, **self.auth_headers)

        # Check for validation error
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("No available rooms.", response.data['error'])

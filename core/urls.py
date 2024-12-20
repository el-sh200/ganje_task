from django.urls import path

from . import views

urlpatterns = [
    path('hotels/', views.HotelList.as_view(), name='hotels_list'),
    path('book/', views.BookingCreate.as_view(), name='booking_create'),
]

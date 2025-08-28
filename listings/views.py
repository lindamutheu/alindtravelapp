from django.shortcuts import render
from rest_framework import viewsets, permissions
from rest_framework.exceptions import ValidationError
from django.utils import timezone

from .models import Listing, Booking, Review
from .serializers import ListingSerializer, BookingSerializer, ReviewSerializer


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit/delete it.
    """

    def has_object_permission(self, request, view, obj):
        # Read-only permissions for safe methods (GET, HEAD, OPTIONS)
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.host == request.user or obj.user == request.user


class ListingViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing Listings.
    """
    queryset = Listing.objects.all().order_by("-created_at")
    serializer_class = ListingSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(host=self.request.user)


class BookingViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing Bookings.
    """
    queryset = Booking.objects.all().order_by("-created_at")
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

    def perform_create(self, serializer):
        # Ensure the booking is tied to the logged-in user
        check_in = serializer.validated_data["check_in"]
        check_out = serializer.validated_data["check_out"]

        if check_out <= check_in:
            raise ValidationError("Check-out date must be after check-in date.")

        # Prevent overlapping confirmed bookings for the same listing
        listing = serializer.validated_data["listing"]
        overlapping = Booking.objects.filter(
            listing=listing,
            check_in__lt=check_out,
            check_out__gt=check_in,
            status="CONFIRMED"
        )
        if overlapping.exists():
            raise ValidationError("This listing is already booked for the selected dates.")

        serializer.save(user=self.request.user)


class ReviewViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing Reviews.
    """
    queryset = Review.objects.all().order_by("-created_at")
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

# Create your views here.

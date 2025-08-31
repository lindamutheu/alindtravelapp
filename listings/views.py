from django.shortcuts import render
from rest_framework import viewsets, permissions
from rest_framework.exceptions import ValidationError
from django.utils import timezone

from .models import Listing, Booking, Review
from .serializers import ListingSerializer, BookingSerializer, ReviewSerializer

from rest_framework import generics, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Payment
from .serializers import PaymentSerializer
from .services import initiate_chapa_payment, verify_chapa_payment
import uuid
from .tasks import send_booking_confirmation_email  # import the task


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

    booking = serializer.save(user=self.request.user)

  #✅ Trigger Celery email task here
    send_booking_confirmation_email.delay(
        booking.user.email,
        booking.listing.title,
        str(booking.check_in),
        str(booking.check_out),
    )


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

class InitiatePaymentView(generics.GenericAPIView):
    serializer_class = PaymentSerializer

    def post(self, request, booking_id):
        booking = get_object_or_404(Booking, id=booking_id)

        payment = Payment.objects.create(
            booking=booking,
            user=request.user,
            amount=booking.listing.price_per_night,  # or total calculation
            chapa_tx_ref=str(uuid.uuid4())
        )

        callback_url = "https://yourdomain.com/api/payments/verify/"
        response = initiate_chapa_payment(payment, callback_url)

        if response.get("status") == "success":
            return Response({"checkout_url": response["data"]["checkout_url"]}, status=200)

        return Response(response, status=400)


class VerifyPaymentView(generics.GenericAPIView):
    def get(self, request, tx_ref):
        payment = get_object_or_404(Payment, chapa_tx_ref=tx_ref)
        response = verify_chapa_payment(tx_ref)

        if response.get("status") == "success" and response["data"]["status"] == "success":
            payment.status = "SUCCESS"
            payment.save()
            
            # trigger background email here
            send_booking_confirmation_email.delay(
                payment.user.email,
                payment.booking.listing.title,
                str(payment.booking.check_in),
                str(payment.booking.check_out),
            )
            return Response({"message": "Payment verified successfully"}, status=200)

        payment.status = "FAILED"
        payment.save()
        return Response({"message": "Payment verification failed"}, status=400)


from rest_framework import serializers
from .models import Listing, Booking


class ListingSerializer(serializers.ModelSerializer):
    host = serializers.ReadOnlyField(source="host.username")  # show username instead of id

    class Meta:
        model = Listing
        fields = [
            "id",
            "title",
            "description",
            "price_per_night",
            "location",
            "host",
            "created_at",
        ]


class BookingSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source="user.username")   # show username
    listing_title = serializers.ReadOnlyField(source="listing.title")  # include listing title for clarity

    class Meta:
        model = Booking
        fields = [
            "id",
            "listing",
            "listing_title",
            "user",
            "check_in",
            "check_out",
            "status",
            "created_at",
        ]

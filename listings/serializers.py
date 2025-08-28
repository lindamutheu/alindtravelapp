from rest_framework import serializers
from .models import Listing, Booking, Review


class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source="user.username")  # show username only

    class Meta:
        model = Review
        fields = ["id", "user", "rating", "comment", "created_at"]
        read_only_fields = ["user", "created_at"]


class ListingSerializer(serializers.ModelSerializer):
    host = serializers.ReadOnlyField(source="host.username")
    # ✅ show reviews but not re-embed Listing to avoid recursion
    reviews = ReviewSerializer(many=True, read_only=True)

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
            "reviews",
        ]


class BookingSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source="user.username")
    listing_title = serializers.ReadOnlyField(source="listing.title")

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
        read_only_fields = ["user", "status", "created_at"]

    def create(self, validated_data):
        # ✅ ensure booking is tied to logged-in user
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)

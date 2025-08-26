from django.db import models
from django.contrib.auth.models import User   # assuming you use Django's built-in User model


class Listing(models.Model):
    """Represents a property/travel package available for booking."""
    title = models.CharField(max_length=255)
    description = models.TextField()
    price_per_night = models.DecimalField(max_digits=8, decimal_places=2)
    location = models.CharField(max_length=255)
    host = models.ForeignKey(User, on_delete=models.CASCADE, related_name="listings")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.location}"


class Booking(models.Model):
    """Represents a booking made by a user for a specific listing."""
    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("CONFIRMED", "Confirmed"),
        ("CANCELLED", "Cancelled"),
    ]

    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="bookings")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bookings")
    check_in = models.DateField()
    check_out = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="PENDING")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=models.Q(check_out__gt=models.F("check_in")),
                name="check_out_after_check_in"
            ),
            models.UniqueConstraint(
                fields=["listing", "user", "check_in", "check_out"],
                name="unique_booking_per_user"
            ),
        ]

    def __str__(self):
        return f"Booking by {self.user.username} for {self.listing.title} ({self.status})"


class Review(models.Model):
    """Represents a customer review for a listing after a booking."""
    RATING_CHOICES = [(i, str(i)) for i in range(1, 6)]  # 1–5 stars

    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="reviews")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reviews")
    rating = models.IntegerField(choices=RATING_CHOICES)
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["listing", "user"], name="unique_review_per_user")
        ]

    def __str__(self):
        return f"Review {self.rating}/5 by {self.user.username} for {self.listing.title}"

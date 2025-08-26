from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from listings.models import Listing
from faker import Faker
import random

class Command(BaseCommand):
    help = "Seed the database with sample listings data"

    def handle(self, *args, **kwargs):
        fake = Faker()

        self.stdout.write("Seeding listings data...")

        # Clear existing data (optional — helps avoid duplicates during testing)
        Listing.objects.all().delete()

        # Ensure at least one host exists
        if not User.objects.exists():
            host = User.objects.create_user(username="host1", email="host1@example.com", password="password123")
        else:
            host = User.objects.first()

        # Create sample listings
        for i in range(10):
            Listing.objects.create(
                title=fake.sentence(nb_words=4),
                description=fake.paragraph(nb_sentences=5),
                price_per_night=random.randint(50, 500),
                location=fake.city(),
                host=host
            )

        self.stdout.write(self.style.SUCCESS("✅ Database seeded with sample listings!"))

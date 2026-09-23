"""
Create or update the category tree (top-level categories and their
sub-categories). Idempotent: matched by name, ordering preserved.

    python manage.py seed_categories
"""

from django.core.management.base import BaseCommand

from core.models import Category

# (name, description, [sub-category names])
CATEGORY_TREE = [
    ("Data Science & AI", "Data analytics, machine learning and AI engineering programmes", [
        "Data Analytics", "Machine Learning", "AI Engineering & MLOps", "Business Intelligence",
    ]),
    ("Marketing", "Digital marketing, advertising, social media and content platforms", [
        "Digital Marketing", "Search Engine Optimization (SEO)", "Social Media Marketing",
        "Google Ads (Adwords)", "Facebook Ads", "Marketing Strategy", "Social Media Management",
        "YouTube Marketing", "Instagram Marketing", "WordPress",
    ]),
]


class Command(BaseCommand):
    help = "Create or update the top-level categories and their sub-categories"

    def handle(self, *args, **options):
        created = updated = 0
        for order, (name, description, children) in enumerate(CATEGORY_TREE):
            parent, was_created = Category.objects.get_or_create(
                name=name, defaults={'description': description, 'order': order, 'is_active': True}
            )
            if not was_created:
                parent.description = description
                parent.order = order
                parent.parent = None
                parent.is_active = True
                parent.save()
            created += was_created
            updated += not was_created
            for child_order, child_name in enumerate(children):
                child, child_created = Category.objects.get_or_create(
                    name=child_name,
                    defaults={'parent': parent, 'order': child_order, 'is_active': True},
                )
                if not child_created:
                    child.parent = parent
                    child.order = child_order
                    child.is_active = True
                    child.save()
                created += child_created
                updated += not child_created
        self.stdout.write(self.style.SUCCESS(
            f"Categories: {created} created, {updated} updated, "
            f"{Category.objects.filter(parent__isnull=True).count()} top-level, "
            f"{Category.objects.filter(parent__isnull=False).count()} sub-categories"
        ))

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.apps import apps


class Profile(models.Model):
    """
    Stores additional information for each user.

    Extends Django's built-in User model using a one-to-one relationship.
    """

    user = models.OneToOneField(User, on_delete=models.CASCADE)

    full_name = models.CharField(
        max_length=150,
        blank=True,
        help_text="Your full name.",
    )

    phone_number = models.CharField(
        max_length=20,
        blank=True,
        help_text="Your phone number.",
    )

    def __str__(self):
        return f"Profile of {self.user.username}"


# ---------- SIGNAL: ensure Profile exists ----------

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, **kwargs):
    """
    Ensure every User has an associated Profile.
    """
    # get_or_create is safe here because Profile has a one-to-one field to User
    # and we never query by non-unique fields.
    Profile.objects.get_or_create(user=instance)


# ---------- SIGNAL: ensure Person exists for this user ----------

@receiver(post_save, sender=User)
def ensure_person_for_user(sender, instance, **kwargs):
    """
    Ensure there is at least one Person entry in the expenses app
    representing this user. If one already exists, do nothing.

    This lets the logged-in user appear in 'Paid by' and 'Participants'
    lists as 'Me (username)'.
    """
    Person = apps.get_model("expenses", "Person")

    # Check if any Person already matches (owner=user, name=username)
    existing_qs = Person.objects.filter(owner=instance, name=instance.username)
    if existing_qs.exists():
        # At least one record already exists: do nothing (avoid MultipleObjectsReturned)
        return

    # Otherwise create a new Person entry linked to this user
    Person.objects.create(
        owner=instance,
        name=instance.username,
        email=instance.email or "",
    )
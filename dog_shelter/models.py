from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


# Create your models here.
class Organization(models.Model):
    name = models.CharField(max_length=50, help_text='Enter organization name')
    description = models.TextField(help_text='Enter description for organization')
    address = models.CharField(max_length=50, help_text='Enter address of your organization')
    phone_number = models.CharField(max_length=13, help_text='Enter phone number')
    email = models.EmailField(max_length=30, help_text='Enter email')
    logo = models.ImageField(upload_to='media', null=True, blank=True)


class OrganizationAdmin(models.Model):
    user = models.OneToOneField(User, null=True, on_delete=models.CASCADE, related_name='users')
    bio = models.TextField(max_length=500, blank=True)
    personal_phone_number = models.CharField(max_length=13, help_text='Enter your personal phone number')
    organization = models.ForeignKey(Organization, null=True, on_delete=models.CASCADE)

    class Meta:
        permissions = [
            ('can_add_dog', 'can add dog'),
            ('can_change_dog', 'can change dog'),
            ('can_delete_dog', 'can delete dog'),
            ('can_view_dog', 'can view dog'),
            ('can_add_dog_images', 'can add dog images'),
            ('can_change_dog_images', 'can change dog images'),
            ('can_delete_dog_images', 'can delete dog images'),
            ('can_view_dog_images', 'can view dog images'),
            ('can_change_organization', 'can change organization'),
            ('can_view_organization', 'can view organization'),
            ('can_view_profile', 'can view profile'),
            ('can_change_profile', 'can change profile'),
        ]


# @receiver(post_save, sender=User)
# def create_user_profile(sender, instance, created, **kwargs):
#     if created:
#         OrganizationAdmin.objects.create(user=instance)
#
#
# @receiver(post_save, sender=User)
# def save_user_profile(sender, instance, **kwargs):
#     instance.profile.save()


class Dog(models.Model):
    SIZE = (
        ("s", 'Small'),
        ("m", 'Medium'),
        ("l", 'Large'),
    )

    name = models.CharField(max_length=20, help_text='Enter dogs name')
    description = models.TextField(help_text='Enter description for dog')
    breed = models.CharField(max_length=50, help_text='Enter the breed of dog')
    age = models.IntegerField(
        validators=[
            MaxValueValidator(100),
            MinValueValidator(1)
        ]
    )
    size = models.CharField(
        max_length=1,
        choices=SIZE,
        default='m',
        blank=True,
        null=True
    )
    disease_info = models.TextField(null=True, blank=True,
                                    help_text='Enter description for dog disease if there are some')
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    user_liked = models.ManyToManyField(User)


class DogImages(models.Model):
    image = models.BinaryField()
    dog = models.ForeignKey(Dog, on_delete=models.CASCADE)

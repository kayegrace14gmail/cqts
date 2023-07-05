from django.db import models


# from django.contrib.auth.models import Permission

from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.contrib.auth.models import Group, AbstractUser, Permission, BaseUserManager


# Create your models here.

from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import gettext_lazy as _


class CustomUserManager(BaseUserManager):
    """
    Custom user model manager where email is the unique identifiers
    for authentication instead of usernames.
    """

    def create_user(self, email, password, **extra_fields):
        """
        Create and save a user with the given email and password.
        """
        if not email:
            raise ValueError(_("The Email must be set"))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must have is_staff=True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must have is_superuser=True."))
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):

    email = models.EmailField(_("email address"), unique=True)
    name = models.CharField(max_length=200, null=True)
    username = None
    phone = models.CharField(max_length=200, null=True)
    about = models.TextField(null=True, blank=True)
    location = models.CharField(max_length=200, null=True)
    group = models.ForeignKey(
        Group, on_delete=models.CASCADE, null=True, blank=True, related_name='group_user')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-updated_at', '-created_at')

    def __str__(self):
        return self.email
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    objects = CustomUserManager()


class Farmer(models.Model):
    name = models.CharField(max_length=200, null=False)
    phone = models.CharField(max_length=200, null=False)
    location = models.CharField(max_length=200, null=True)
    operation_scale = models.CharField(max_length=200, null=True, blank=True)
    cooperative = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'group__name': 'Cooperative'}, related_name='cooperative_farmers'
                                    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-updated_at', '-created_at')

    def __str__(self):
        return self.name

# exporter


class Exporter(models.Model):
    license = models.CharField(max_length=200, null=False)
    exporter = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={
        'group__name': 'Exporter'}, related_name='exporter_details', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-updated_at', '-created_at')

    def __str__(self):
        return self.exporter + ' - ' + self.license

# cooperatives
class Cooperative(models.Model):
    cooperative_head = models.CharField(max_length=200, null=False)
    cooperative = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={
        'group__name': 'Cooperative'}, related_name='cooperative_details', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-updated_at', '-created_at')

    def __str__(self):
        return self.cooperative.name + ' - ' + self.cooperative_head

class Batch(models.Model):
    type = models.CharField(max_length=200, null=False,
                            default='Not Specified')
    grade = models.CharField(max_length=200, null=False)
    moisture_content = models.FloatField(null=False, default=0.0)
    color = models.CharField(max_length=200, null=False, blank=True)
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={
                              'group__name': 'Buyer'}, related_name='buyer_batches', null=True, blank=True)
    cooperative = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={
                                    'group__name': 'Cooperative'}, related_name='cooperative_batches', null=True, blank=True)
    exporter = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={
                                 'group__name': 'Exporter'}, related_name='exporter_batches', null=True, blank=True)

    # flags for batch status
    is_approved = models.BooleanField(default=False)
    sold_to_exporter = models.BooleanField(default=False)
    date_sold_to_exporter = models.DateField(null=True, blank=True)
    sold_to_buyer = models.BooleanField(default=False)
    date_sold_to_buyer = models.DateField(null=True, blank=True)
    date_sold_to_exporter = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    batch_string = models.CharField(max_length=200, null=True, blank=True)
    def __str__(self):
        return 'CQTS-Batch ' + str(self.id)
    class Meta:
        ordering = ('-updated_at', '-created_at')

# create or get the user groups and assign them permissions
# @receiver(post_migrate)
# def insert_auth_groups(sender, **kwargs):
#     if sender.name == 'auth' and kwargs['created']:
#         # Insert data into auth_group table
#         group_data = [
#             {'name': 'CQTSadmin'},
#             {'name': 'Cooperative'},
#             {'name': 'Exporter'},
#             {'name': 'Buyer'},
#         ]

#         permission_data = {
#             'add_user_permission': 'add_user',
#             'delete_user_permission': 'delete_user',
#             'change_user_permission': 'change_user',
#             'view_user_permission': 'view_user',
#             'add_farmer_permission': 'add_farmer',
#             'delete_farmer_permission': 'delete_farmer',
#             'change_farmer_permission': 'change_farmer',
#             'view_farmer_permission': 'view_farmer',
#             'add_batch_permission': 'add_batch',
#             'change_batch_permission': 'change_batch',
#             'view_batch_permission': 'view_batch',
#         }

#         for data in group_data:
#             group, _ = Group.objects.get_or_create(**data)
#             group.save()

#             if data['name'] == 'CQTSadmin':
#                 # Permissions for admin group
#                 for permission_name in permission_data.values():
#                     permission = Permission.objects.get(codename=permission_name)
#                     group.permissions.add(permission)

#             elif data['name'] == 'Cooperative':
#                 # Permissions for cooperative group
#                 group.permissions.add(
#                     Permission.objects.get(codename='add_farmer'),
#                     Permission.objects.get(codename='delete_farmer'),
#                     Permission.objects.get(codename='change_farmer'),
#                     Permission.objects.get(codename='view_farmer'),
#                     Permission.objects.get(codename='add_batch'),
#                     Permission.objects.get(codename='view_batch')
#                 )

#             elif data['name'] == 'Exporter':
#                 # Permissions for exporter group
#                 group.permissions.add(
#                     Permission.objects.get(codename='view_batch'),
#                     Permission.objects.get(codename='change_batch')
#                 )

#             elif data['name'] == 'Buyer':
#                 # Permissions for buyer group
#                 group.permissions.add(
#                     Permission.objects.get(codename='view_batch'),
#                     Permission.objects.get(codename='change_batch')
#                 )

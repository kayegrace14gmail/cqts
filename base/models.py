from django.db import models


# from django.contrib.auth.models import Permission
from django.contrib.auth.models import Permission
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import Group

# Create your models here.


class User(AbstractUser):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=200, null=True)
    phone = models.CharField(max_length=200, null=True)
    about = models.TextField(null=True, blank=True)
    username = models.CharField(max_length=150, unique=False,null=True, blank=True)
    location = models.CharField(max_length=200, null=True)
    group = models.ForeignKey(
        Group, on_delete=models.CASCADE, null=True, related_name='group_user')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-updated_at', '-created_at')
    def __str__(self):
        return self.name
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []


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

#exporter 
class Exporter(models.Model):
    license = models.CharField(max_length=200, null=False)
    exporter = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={
        'group__name': 'Exporter'}, related_name='exporter_details',null=True, blank=True ) 
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ('-updated_at', '-created_at')
    def __str__(self):
        return self.exporter + ' - ' + self.license
    
#cooperatives
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
    grade = models.CharField(max_length=200, null=False)
    moisture_content = models.FloatField( null=False, default=0.0)
    color = models.CharField(max_length=200, null=False)
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={
                              'group__name': 'Buyer'}, related_name='buyer_batches', null=True, blank=True)
    cooperative = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={
                                    'group__name': 'Cooperative'}, related_name='cooperative_batches')
    exporter = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={
                                 'group__name': 'Exporter'}, related_name='exporter_batches', null=True, blank=True)

    # flags for batch status
    is_approved = models.BooleanField(default=False)
    sold_to_exporter = models.BooleanField(default=False)
    sold_to_buyer = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return 'CQTS-Batch ' + str(self.id) 


# create or get the user groups
admin_group, _ = Group.objects.get_or_create(name='CQTSadmin')
cooperative_group, _ = Group.objects.get_or_create(name='Cooperative')
exporter_group, _ = Group.objects.get_or_create(name='Exporter')
buyer_group, _ = Group.objects.get_or_create(name='Buyer')

#permissions for user
add_user_permission = Permission.objects.get(codename='add_user')
delete_user_permission = Permission.objects.get(codename='delete_user')
change_user_permission = Permission.objects.get(codename='change_user')
view_user_permission = Permission.objects.get(codename='view_user')

# getting the permissions by codename
add_farmer_permission = Permission.objects.get(codename='add_farmer')
delete_farmer_permission = Permission.objects.get(codename='delete_farmer')
change_farmer_permission = Permission.objects.get(codename='change_farmer')
view_farmer_permission = Permission.objects.get(codename='view_farmer')

# permissions for batch
add_batch_permission = Permission.objects.get(codename='add_batch')
change_batch_permision = Permission.objects.get(codename='change_batch')
view_batch_permission = Permission.objects.get(codename='view_batch')


# Assign the permissions to the groups
# cooperative group adds, deletes, changes and views farmers and adds, views batches
cooperative_group.permissions.add(add_farmer_permission, delete_farmer_permission,
                                  change_farmer_permission, view_farmer_permission, add_batch_permission, view_batch_permission)

# exporter group views batches
exporter_group.permissions.add(view_batch_permission, change_batch_permision)

# buyer group views batches
buyer_group.permissions.add(view_batch_permission, change_batch_permision )

#group admin has all permissions
admin_group.permissions.add( 
                             view_farmer_permission,  
                             view_batch_permission,
                             add_user_permission, delete_user_permission,
                             change_user_permission, view_user_permission,
                             )





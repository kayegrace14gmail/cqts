from django.contrib import admin
from .models import User, Farmer, Batch, Cooperative, Exporter

# Register your models here.
admin.site.register(User)
admin.site.register(Farmer)
admin.site.register(Batch)
admin.site.register(Cooperative)
admin.site.register(Exporter)

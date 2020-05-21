from django.contrib import admin
from .models import Dog, Organization, OrganizationAdmin

# Register your models here.


admin.site.register(Dog)
admin.site.register(Organization)
admin.site.register(OrganizationAdmin)
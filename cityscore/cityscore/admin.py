from django.contrib import admin

from .models import Metric, Value, City

admin.site.register(Metric)
admin.site.register(Value)
admin.site.register(City)

def has_add_permission(self, request, obj=None):
    return True
def has_change_permission(self, request, obj=None):
    return True
def has_delete_permission(self, request, obj=None):
    return True
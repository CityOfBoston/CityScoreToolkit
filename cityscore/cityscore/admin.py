from django.contrib import admin
from .models import Metric, Value, City
from import_export import resources
from import_export.admin import ImportExportModelAdmin

class MetricAdmin(ImportExportModelAdmin):
    pass

class ValueResource(resources.ModelResource):
    class Meta:
        model = Value
        exclude = ('metric', )
        export_order = ('id', 'val', 'entry_date')
        skip_unchanged = True
        report_skipped = False
        widgets = {
            'published': {'format': '%m.%d.%Y'},
        }

admin.site.register(Metric)
admin.site.register(Value)
admin.site.register(City)

def has_add_permission(self, request, obj=None):
    return True
def has_change_permission(self, request, obj=Metric):
    return True
def has_delete_permission(self, request, obj=None):
    return True
    

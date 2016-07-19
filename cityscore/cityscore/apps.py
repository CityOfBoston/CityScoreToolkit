from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _

class CityscoreConfig(AppConfig): # Our app config class
    name = 'cityscorewebapp.apps.cityscore'
    verbose_name = "cityscorewebapp"
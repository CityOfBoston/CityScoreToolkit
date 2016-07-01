from django.forms import ModelForm, Textarea
from .models import Value, City, Metric, User
import django.forms
from django.contrib.auth.forms import UserCreationForm

class MetricForm(ModelForm):
    class Meta:
        model = Metric
        exclude = ['city']
        widgets = {
            'definition': Textarea(attrs={'cols': 20, 'rows': 5})
        }

class ValueForm(ModelForm):
    class Meta:
        model = Value
        metric_select = django.forms.ModelMultipleChoiceField(
                                                queryset=Metric.objects.all(), 
                                                to_field_name = "metric"
                                                             )
        exclude = ['city']
        
class CityForm(ModelForm):
    class Meta:
        model = City
        exclude = ['user']
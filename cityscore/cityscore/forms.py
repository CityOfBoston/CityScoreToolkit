from django.forms import ModelForm, Textarea, Form, HiddenInput
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
                                                queryset=Metric.objects.filter(), 
                                                to_field_name = "metric"
                                                             )
        exclude = ['city']
    # def __init__(self, *args, **kwargs):
    #     mycity = args[0]
    #     super(ValueForm, self).__init__(**kwargs)
    #     if mycity:
    #         self.fields['metric'].queryset = Metric.objects.filter(city = mycity)
        
class CityForm(ModelForm):
    class Meta:
        model = City
        exclude = ['user']
        
class DownloadForm(Form):
    value = django.forms.FloatField(widget=HiddenInput)
    entry_date = django.forms.DateField(widget=HiddenInput)
    metric = django.forms.CharField(widget=HiddenInput)
    
class SQLForm(Form):
    engine = django.forms.CharField()
    host = django.forms.CharField()
    user = django.forms.CharField()
    password = django.forms.CharField()
    name = django.forms.CharField()
    
class UploadFileForm(Form):
    file = django.forms.FileField()
    metric =  django.forms.ModelMultipleChoiceField(
                                                queryset=Metric.objects.all()
                                                             )
                                                             
class UploadMetricForm(Form):
    file = django.forms.FileField()

    # def __init__(self, *args, **kwargs):
    #     if args is not None:
    #         mycity = args[0]
    #     super(UploadFileForm, self).__init__(**kwargs)
    #     if mycity:
    #         self.fields['metric'].queryset = Metric.objects.filter(city = mycity)    
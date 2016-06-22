import date
import numpy as np
import datetime
import simplejson 

from django.http import HttpResponseRedirect, HttpResponse, Http404, HttpResponseBadRequest
from django.template import loader
from django.shortcuts import render, get_object_or_404, render_to_response
from .models import Value, Metric, City
from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .forms import UploadFileForm

## ADDS A VALUE OBJECT TO THE SET HELD BY METRICS.    
@login_required
def enter_val(request, city_id):
    city = get_object_or_404(City, id = city_id)
    template = loader.get_template('cityscore/enter_val.html')  
    if request.method == 'POST':
        metric = get_object_or_404(Metric, id = request.POST.get('metric'))
        try:
            newVal = Value(
                        val = request.GET['today_val'], 
                        entry_date = request.GET['set_date'] if request.GET['set_date'] else date.today,
                        metric =  metric.name
                           )
        except(KeyError, ValueError):
            return render(request, 'cityscore/enter_val.html', {
                'metric': metric,
                'error_message': "Your value was invalid.",
            })
        else:
            if(metric.historic == 1):
                metric.set_historic_target #Refresh the target value as a new value is entered.
            if(metric.value_set.get(entry_date = newVal.entry_date) is not None):
                metric.value_set.get(entry_date = newVal.entry_date).val = newVal.val
            else:
                new_set = metric.value_set.add(newVal)
            return HttpResponseRedirect(reverse('cityscore:enter_val'))

@login_required        
## ADDS A METRIC OBJECT TO THE SET HELD BY CITY. 
def new_metric(request, city_id):
    city = get_object_or_404(Metric, id = city_id)
    template = loader.get_template('cityscore/new_metric.html')
    try:
        newMetric = Metric(
                        name = request.GET['name'],
                        definition = request.GET['def'],
                        direction = 1 if request.GET['dir'] == 'UP' else 0,
                        historic = 1 if request.GET['hist'] == 'Yes' else 0,
                        target = 1 if request.GET['hist'] == 'Yes' else request.GET['target']
                       )
    except(KeyError):
            return render(request, 'cityscore/new_metric.html', {
                'city': city,
                'error_message': "There was an error processing your request for a new metric."
            })
    else:
        new_set = city.metric_set.add(newMetric)
        return HttpResponseRedirect(reverse('cityscore:today_view'))
    
##SCREEN FOR A NEW CITY TO SIGN UP WITH CITY SCORE        
def welcome_city(request):
    template = loader.get_template('cityscore/welcome_city.html')
    try:
        newCity = City(
                    cityname = request.GET['username'],
                    input_spec = request.GET['input_type']
                      )
        user = User(
                                    request.GET['username'],
                                    request.GET['pw']
                                    )
    except(KeyError):
        return  render(request, 'cityscore/welcome_city.html', {
            'error_message': "Please re-check the information you entered."
        })
    else:
        new_user = User.objects.create_user(user)
        new_set = City.objects.add(newCity)
        return HttpResponseRedirect(reverse('cityscore:today_view'))

##SCREEN FOR A CITY TO LOG INTO CITY SCORE        
def login_pls(request):
    template = loader.get_template('cityscore/login_pls.html')
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(username=username, password=password)
    if user is not None:
        if user.is_active:
            login(request, user)
            return HttpResponseRedirect(reverse('cityscore:today_view'))
        else:
            return  render(request, 'cityscore/welcome_city.html', {
            'error_message': "disabled_account"
            })
    else:
        return  render(request, 'cityscore/login_pls.html', {
            'error_message': "bad_details"
            })

@login_required         
def today_view(request, city_id):
    template = loader.get_template('cityscore/today_view.html')
    city = get_object_or_404(City, id = city_id)
    if request.method == 'POST':
        metric = get_object_or_404(Metric, id = request.POST.get('metric'))
        if request.POST.get('new_metric'):
            return HttpResponseRedirect(reverse('cityscore:new_metric'))
        elif request.POST.get('enter_val'):
            return HttpResponseRedirect(reverse('cityscore:enter_val'))
        elif request.POST.get('analytics'):
            return HttpResponseRedirect(reverse('cityscore:analytics'))
        elif request.POST.get('delete'):
            city.objects.filter(id={{ metric.id }}).delete()
            return HttpResponseRedirect(reverse('cityscore:today_view'))

# def upload_file(request):
#     if request.method == 'POST':
#         form = UploadFileForm(request.POST, request.FILES)
#         if form.is_valid():
#             instance = Value(file_field=request.FILES['file'])
#             instance
#             return HttpResponseRedirect('/today_view')
#     else:
#         form = UploadFileForm()
#     return render(request, 'upload.html', {'form': form})
    
# def handle_uploaded_file(f):
#     with open('some/file/name.txt', 'wb+') as destination:
#         for chunk in f.chunks():
#             destination.write(chunk)
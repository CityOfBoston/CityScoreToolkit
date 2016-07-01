import numpy as np
import datetime
import simplejson 
import sys
from django.http import HttpResponseRedirect, HttpResponse, Http404, HttpResponseBadRequest
from django.template import loader, Context, Template
from django.shortcuts import render, get_object_or_404, render_to_response, redirect
from .models import Value, Metric, City
from .forms import ValueForm, MetricForm, CityForm
from django.contrib.auth.forms import UserCreationForm
from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django import template

#WELCOME SCREEN (STATIC)
def welcome_city(request):
    return render(request, 'cityscore/welcome_city.html',{})

##SCREEN FOR CREATING AN ACCOUNT
def register(request):
    if request.method == 'POST':
        uf = UserCreationForm(request.POST, prefix='user')
        cf = CityForm(request.POST, prefix='city')
        if uf.is_valid() * cf.is_valid():
            user = uf.save()
            city = cf.save(commit=False)
            city.user = user
            city.save()
            response = HttpResponseRedirect('/login/')
            response.user = user
            return response
        else:
            return render(request, 'cityscore/register.html', {'userform':uf, 'cityform':cf, 'error': " :( "})
    else:
        uf = UserCreationForm(prefix='user')
        cf = CityForm(prefix='city')
    return render(request, 'cityscore/register.html', {'userform':uf, 'cityform':cf})

##SCREEN FOR A CITY TO LOG INTO CITY SCORE        
def login_pls(request):
    template = loader.get_template('cityscore/login_pls.html')
    username = request.POST.get('username')
    password = request.POST.get('password')
    user = authenticate(username=username, password=password)
    if user is not None:
        if user.is_active:
            login(request, user)
            return redirect('today_view')
        else:
            return  render(request, 'cityscore/login_pls.html', {
            'error_message': "disabled_account"
            })
    elif username is None or password is None:
        return render(request, 'cityscore/login_pls.html', {
            })
    else:
        return  render(request, 'cityscore/login_pls.html', {
            'error_message': '',
## something is wrong
            'bad_details': 5
            })

#CENTRAL SCREEN INCLUDING ALL SCORES AND LINKS TO EDIT ANY VALUES OR ANALYTICS TOOLS
#WITHIN THE CITYSCORE FRAMEWORK
@login_required         
def today_view(request):
    if request.user.is_authenticated():
        template = loader.get_template('cityscore/today_view.html')
        this_user = request.user
        this_city = City.objects.get(user = this_user)
        this_name = this_city.cityname.upper()
        c_id = this_city.pk
        c_metrics = Metric.objects.filter(city_id = c_id)
        c_day = this_city.calculate_cityscore_day
        c_week = this_city.calculate_cityscore_week
        c_month = this_city.calculate_cityscore_month
        c_quarter = this_city.calculate_cityscore_quarter
        c_ptile = this_city.calculate_percentile
        context = {
                "city": this_city,
                "name": this_name,
                "day": c_day,
                "week": c_week,
                "month": c_month,
                "quarter":c_quarter,
                "ptile": c_ptile,
                "metrics": c_metrics,
                "today": datetime.date.today(),
                }
        return render(request, 'cityscore/today_view.html', context)
    else:
        HttpResponseRedirect('/login/')

def get_value(request):
    if request.user.is_authenticated():
        this_user=request.user
        this_city = this_user.city
        # if this is a POST request we need to process the form data
        if request.method == 'POST':
            # create a form instance and populate it with data from the request:
            form = ValueForm(request.POST)
            # check whether it's valid:
            if form.is_valid():
                data = form.cleaned_data
                this_metric = data['metric']
                #uncomment the following to debug and delete any extra vals
                # this_metric.value_set.all().delete()
                newVal = Value(
                            metric = data['metric'],
                            city = this_city,
                            entry_date = data['entry_date'],
                            val = data['val']
                                )
                if(this_metric.historic == 1):
                    this_metric.set_historic_target #Refresh the target value as a new value is entered.
                if(this_metric.value_set.filter(entry_date = newVal.entry_date)):
                    m = this_metric.value_set.get(entry_date = newVal.entry_date)
                    m.val = newVal.val
                    m.save()
                else:
                    newVal.save()
                return HttpResponseRedirect('/cityscore/')
            else: 
                return render(request, 'cityscore/get_value.html', {'form': form, 'error': 'error'})
        # if a GET (or any other method) we'll create a blank form
        else:
            form = ValueForm()
        return render(request, 'cityscore/get_value.html', {'form':form})
    else:
        return HttpResponseRedirect('/login/')

def get_metric(request):
    if request.user.is_authenticated():
        this_user=request.user
        this_city = this_user.city
        # if this is a POST request we need to process the form data
        if request.method == 'POST':
            # create a form instance and populate it with data from the request:
            form = MetricForm(request.POST)
            # check whether it's valid:
            if form.is_valid():
                data = form.cleaned_data
                newMetric = Metric(
                                name = data['name'],
                                definition = data['definition'],
                                direction = data['direction'],
                                historic = data['historic'],
                                target = data['target'] if data['target'] else 0,
                                city = this_city
                                )
                newMetric.save()
                return HttpResponseRedirect('/entry/')
            else:
                print >>sys.stderr, form.cleaned_data
                return render(request, 'cityscore/get_metric.html', {'form': form, 'error': 'error'})
        # if a GET (or any other method) we'll create a blank form
        else:
            form = MetricForm(initial = {'target': 1})
        return render(request, 'cityscore/get_metric.html', {'form':form} )
    else:
        return HttpResponseRedirect('/login/')
    
def attn(request):
    if request.user.is_authenticated():
        this_user = request.user
        this_city = City.objects.get(user = this_user)
        this_name = this_city.cityname.upper()
        c_id = this_city.pk
        c_exc = this_city.get_exceeding
        c_follow = this_city.get_follow_up
        context = {
                "city": this_city,
                "name": this_name,
                "exceeding": c_exc,
                "followup": c_follow
                }
        return render(request, 'cityscore/exceeding.html',context)
    else:
        return HttpResponseRedirect('/login/')

def legend(request):
    if request.user.is_authenticated():
        this_user = request.user
        this_city = City.objects.get(user = this_user)
        this_name = this_city.cityname.upper()
        c_id = this_city.pk
        c_exc = this_city.get_exceeding
        c_follow = this_city.get_follow_up
        context = {
                "city": this_city,
                "name": this_name,
                "exceeding": c_exc,
                "followup": c_follow
                }
        return render(request, 'cityscore/legend.html',context)
    else:
        return HttpResponseRedirect('/login/')
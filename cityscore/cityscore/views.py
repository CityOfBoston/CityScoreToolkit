import numpy as np
import datetime
import simplejson 
import json
# import sys
import csv
import base64
from io import TextIOWrapper, StringIO
# import os
from django.http import HttpResponseRedirect, HttpResponse, Http404, HttpResponseBadRequest
from django.template import loader, Context, Template
from django.shortcuts import render, get_object_or_404, render_to_response, redirect
from .models import Value, Metric, City
from .forms import ValueForm, MetricForm, CityForm, DownloadForm, SQLForm, UploadFileForm, UploadMetricForm
from django.contrib.auth.forms import UserCreationForm
from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core import serializers
from django import template
from .settings import DATABASES
import matplotlib
matplotlib.use('Agg')
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.dates import DateFormatter
import urllib
import mpld3
import matplotlib.pyplot as plt
import matplotlib.dates as mdates



#WELCOME SCREEN (STATIC SPLASH PAGE SERVED BY BASIC HTML5/CSS3)
def welcome_city(request):
    return render(request, 'cityscore/welcome_city.html',{})

##SCREEN FOR CREATING AN ACCOUNT
def register(request):
    # if a user is attempting to submit new acct info
    if request.method == 'POST':
        #get the information they have entered about themselves and their city
        uf = UserCreationForm(request.POST, prefix='user')
        cf = CityForm(request.POST, prefix='city')
        #check that the information is valid
        if uf.is_valid() * cf.is_valid():
            #save the new information to the db
            user = uf.save()
            city = cf.save(commit=False)
            city.user = user
            city.save()
            #direct the user to the login page
            response = HttpResponseRedirect('/login/')
            response.user = user
            return response
        else:
            #if they entered invalid credentials, reload the page.
            return render(request, 'cityscore/register.html', {'userform':uf, 'cityform':cf, 'error': " :( "})
    else:
        #if the user is trying to open the page, give them a blank form
        uf = UserCreationForm(prefix='user')
        cf = CityForm(prefix='city')
    #open the page
    return render(request, 'cityscore/register.html', {'userform':uf, 'cityform':cf})


##SCREEN FOR A CITY TO LOG INTO CITY SCORE
def login_pls(request):
    #load the HTML
    template = loader.get_template('cityscore/login_pls.html')
    #get the login information that the user input and ensure it is correct
    username = request.POST.get('username')
    password = request.POST.get('password')
    user = authenticate(username=username, password=password)
    #if the user entered information, process it
    if user is not None:
        #if the user has been using cityscore, go to the infopage
        if user.is_active:
            login(request, user)
            return redirect('legend')
        #if the user has not been around for a while, reload
        else:
            return  render(request, 'cityscore/login_pls.html', {
                           'error_message': "disabled_account"
                           })
#if the user has not entered one of the values, reload
    elif username is None or password is None:
        return render(request, 'cityscore/login_pls.html', {})
                  #otherwise, reload with an error message
    else:
        return render(request, 'cityscore/login_pls.html', {
            'error_message': '',
            ## something is wrong
            'bad_details': 5
        })

##CENTRAL SCREEN INCLUDING ALL SCORES AND LINKS TO EDIT ANY VALUES OR ANALYTICS TOOLS
#WITHIN THE CITYSCORE FRAMEWORK
@login_required
def today_view(request):
    #a user must be logged in to access this
    if request.user.is_authenticated():
        #load the html
        template = loader.get_template('cityscore/today_view.html')
        #get the user on this page and the city they are from
        this_user = request.user
        this_city = City.objects.get(user = this_user)
        #set the name of the city for the title of the page
        this_name = this_city.cityname.upper()
        #extract the city's basic id
        c_id = this_city.pk
        #get all metrics in the city
        c_metrics = Metric.objects.filter(city_id = c_id).order_by('name')
        #calculate cityscore values, percentiles, and last entered date
        c_day = this_city.calculate_cityscore_day
        c_week = this_city.calculate_cityscore_week
        c_month = this_city.calculate_cityscore_month
        c_quarter = this_city.calculate_cityscore_quarter
        c_ptile = this_city.calculate_percentile
        c_led = this_city.last_entered_date
        #instantiate a downloadable button so the user can recoup entered data
        download_form = DownloadForm
        download_val_form = DownloadForm
        #feed this information to the webpage using a dictionary which can be
        #called upon in the html by the name in quotes
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
                "led": c_led,
                "dl_form": download_form,
                "dl_val_form":download_val_form,
                "len": len(c_metrics)
            }
        #open the page with the specification
        return render(request, 'cityscore/today_view.html', context)
    else:
        #if the user hasn't logged in, take them back to the login screen
        HttpResponseRedirect('/login/')

def get_value(request):
    if request.user.is_authenticated():
        this_user=request.user
        this_city = this_user.city
        # if this is a POST request we need to process the form data
        if request.method == 'POST':
            if 'val_submit' in request.POST:
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
                    val_form = ValueForm(request.POST)
                    val_form.fields['metric'].queryset = Metric.objects.filter(city = this_city)
                    upload_form = UploadFileForm()
                    upload_form.fields['metric'].queryset = Metric.objects.filter(city = this_city)
                    return render(request, 'cityscore/get_value.html', {'val_form': val_form, 'upload_form': upload_form, 'error': 'error'})
            else:
                form = UploadFileForm(request.POST, request.FILES)
                if form.is_valid():
                    err = handle_uploaded_file(
                                               this_city,
#                                               TextIOWrapper(
                                                             request.FILES['file']
#                                                             encoding=request.encoding
#                                                             )
                                               )
                    if err is None:
                        return HttpResponseRedirect('/cityscore/')
                    else:
                        val_form = ValueForm()
                        val_form.fields['metric'].queryset = Metric.objects.filter(city = this_city)
                        upload_form = UploadFileForm(request.POST)
                        upload_form.fields['metric'].queryset = Metric.objects.filter(city = this_city)
                        return render(request, 'cityscore/get_value.html', {'val_form': val_form, 'upload_form': upload_form, 'derror': err})
                else:
                    val_form = ValueForm()
                    val_form.fields['metric'].queryset = Metric.objects.filter(city = this_city)
                    upload_form = UploadFileForm(request.POST)
                    upload_form.fields['metric'].queryset = Metric.objects.filter(city = this_city)
                    return render(request, 'cityscore/get_value.html', {'val_form': val_form, 'upload_form': upload_form, 'uerror': 'error'})
        # if a GET (or any other method) we'll create a blank form
        else:
            val_form = ValueForm()
            val_form.fields['metric'].queryset = Metric.objects.filter(city = this_city)
            upload_form = UploadFileForm()
            upload_form.fields['metric'].queryset = Metric.objects.filter(city = this_city)
        return render(request, 'cityscore/get_value.html', {'val_form':val_form, 'upload_form': upload_form})
    else:
        return HttpResponseRedirect('/login/')

## PAGE FOR A USER TO CREATE A NEW METRIC
def get_metric(request):
    if request.user.is_authenticated():
        this_user=request.user
        this_city = this_user.city
        # if this is a POST request we need to process the form data
        if request.method == 'POST':
            if 'upload_submit' in request.POST:
                #if the user uploaded a file rather than manually entered the data
                form = UploadMetricForm(request.POST, request.FILES)
                if form.is_valid():
                    #check for validity and then pass the file
                    err = handle_uploaded_metric_file(this_city, request.FILES['file'])
                    if err is None:
                        #if all is well, go to value entry
                        return HttpResponseRedirect('/entry/')
                    else:
                        #if there was an error, reload the page with a notification
                        mform = MetricForm()
                        uform = UploadMetricForm(request.POST)
                        return render(request, 'cityscore/get_metric_upload.html', {'mform': mform, 'uform': uform, 'error': err})
                else:
                    #if there was an error, reload the page with a notification
                    mform = MetricForm()
                    uform = UploadMetricForm(request.POST)
                    return render(request, 'cityscore/get_metric_upload.html', {'mform': mform, 'uform': uform, 'error': 'error'})
            else:
                # create a form instance and populate it with data from the request:
                form = MetricForm(request.POST)
                # check whether it's valid:
                if form.is_valid():
                    data = form.cleaned_data
                    #add new metric based on entry and save it
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
                    mform = MetricForm(initial = {'target': 1})
                    uform = UploadMetricForm()
                    return render(request, 'cityscore/get_metric_upload.html', {'mform': mform, 'uform': uform, 'error': 'error'})
                    # if a GET (or any other method) we'll create a blank form
        else:
            #open a blank page
            mform = MetricForm(initial = {'target': 1})
            uform = UploadMetricForm()
            return render(request, 'cityscore/get_metric_upload.html', {'mform':mform, 'uform':uform} )
    else:
        return HttpResponseRedirect('/login/')

#EXCEEDING AND FOLLOWUP PAGE
def attn(request):
    if request.user.is_authenticated():
        this_user = request.user
        this_city = City.objects.get(user = this_user)
        this_name = this_city.cityname.upper()
        #call the exceeding and follow-up characteristics of the city object
        #corresponding to the user who is logged in and feed it to the HTML
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

#info page, just screens site for login information.
def legend(request):
    if request.user.is_authenticated():
        this_user = request.user
        this_city = City.objects.get(user = this_user)
        this_name = this_city.cityname.upper()
        c_id = this_city.pk
        context = {
            "city": this_city,
            "name": this_name
        }
        return render(request, 'cityscore/legend.html',context)
    else:
        return HttpResponseRedirect('/login/')

#format a csv file with the cityscore screen
def get_csv_data_cityscore(which_city):
    data = []
    these_metrics = which_city.metric_set.filter(city = which_city.pk)
    for m in these_metrics:
        this_id = str(m.id)
        name = m.name
        definition = m.definition
        d_score = str(m.calculate_score_day)
        w_score = str(m.calculate_score_week)
        m_score = str(m.calculate_score_month)
        q_score = str(m.calculate_score_quarter)
        ptile = str(m.calculate_percentile)
        data.append(', '.join([this_id, name, definition, d_score, w_score, m_score, q_score, ptile]))
    cd = str(which_city.calculate_cityscore_day)
    cw = which_city.calculate_cityscore_week
    cm = which_city.calculate_cityscore_month
    cq = which_city.calculate_cityscore_quarter
    cp = which_city.calculate_percentile
    data.append(', '.join(['','Citywide Data', str(cd), str(cw), str(cm), str(cq), str(cp)]))
    return '\n'.join(data)

#handle a request to download the cityscore screen
def download_cscore_data(request):
    if request.user.is_authenticated():
        this_user=request.user
        this_city = this_user.city
    try:
        metrics = get_csv_data_cityscore(this_city)
        assert metrics
    except AssertionError:
        error = 'Your request has some problems.'
        metrics = error
    
    attachment = 'metrics_data.csv'
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment;filename="{}"'.format(attachment)
    response.write(metrics)
    return response

#create a csv from all the entered values in a city's usage history
def get_csv_data_values(which_city):
    data = []
    these_metrics = which_city.metric_set.filter(city = which_city.pk)
    for m in these_metrics:
        this_id = str(m.id)
        name = m.name
        these_values = m.value_set.filter(metric = m.pk)
        for v in these_values:
            value = v.val
            e_date = v.entry_date
            data.append(', '.join([name, str(value), str(e_date)]))
    return '\n'.join(data)

#handle a request to download a csv of all values
def download_vals_data(request):
    if request.user.is_authenticated():
        this_user=request.user
        this_city = this_user.city
    try:
        value = get_csv_data_values(this_city)
        assert value
    except AssertionError:
        error = 'Your request has some problems.'
        value = error
    
    attachment = 'value_data.csv'
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment;filename="{}"'.format(attachment)
    response.write(value)
    return response

def new_server_connection(request):
    if request.user.is_authenticated():
        this_user = request.user
        this_city = this_user.city
        dbform = SQLForm(initial = {'engine': 'django-pyodbc'})
        context = {'dbform':dbform, 'setting_db': DATABASES}
    return render(request, 'cityscore/upload_server.html',context)

#SYNC DATABASE WITH DATA FROM AN UPLOADED FILE
def handle_uploaded_file(this_city, file):
    #screen for the file type so we call the correct input reader
    if file.content_type == "text/csv" or file.content_type == "application/vnd.ms-excel":
       #the second data type is specific to Microsoft, where it is a saved CSV
        filev = StringIO(file.read().decode())
        reader = csv.reader(filev)
        #extract the data row-by-row. if something is wrong, tell the user where
        #the error occurred.
        for row in reader:
            try: 
                m_set = this_city.metric_set.filter(city = this_city.pk)
                _,created = Value.objects.get_or_create(
                                                        val = float(row[0]),
                                                        entry_date = datetime.datetime.strptime(row[1], "%Y-%m-%d"),
                                                        metric = m_set.filter(name = row[2])[0],
                                                        city = this_city
                                                        )
            except:
                 err = "There was an error processing this at line " + str([row[0], row[1], row[2]])
            else:
                err = None
        return err
    #otherwise, if the file is a JSON...
    elif file.content_type == "text/json":
        #use django's inbuilt data serializer to extract information from the file
        json_file = simplejson.load(file)
        obj_generator = serializers.json.Deserializer(json_file)
        m_set = this_city.metric_set.filter(city = this_city.pk)
        for obj in obj_generator:       
            record = Value(
                        val = obj.val, 
                        entry_date = obj.entry_date, 
                        metric = m_set.filter(name = obj.metric)[0], 
                        city = this_city
                        )
            obj.save()
    else:
        #currently unable to handle non-csv, non-json files.
        return 'That file type is invalid!'

##SCREEN FOR UPLOADING A SERVER
def server(request):
    return render(request, 'cityscore/upload_server.html',{})

#generate a graph of the values for a given metric. metric name is passed as a
#parameter to this function via URL
def analytics_page(request, name = "Library Users"):
    if request.user.is_authenticated():
        this_user=request.user
        this_city = this_user.city
        if request.method == "GET":
            m = name
            m_obj = Metric.objects.filter(name = m)[0]
            score_list = m_obj.get_score_list
            values = m_obj.value_set.all()
            tableau20 = [(31, 119, 180), (174, 199, 232), (255, 127, 14), (255, 187, 120),
                         (44, 160, 44), (152, 223, 138), (214, 39, 40), (255, 152, 150),
                         (148, 103, 189), (197, 176, 213), (140, 86, 75), (196, 156, 148),
                         (227, 119, 194), (247, 182, 210), (127, 127, 127), (199, 199, 199),
                         (188, 189, 34), (219, 219, 141), (23, 190, 207), (158, 218, 229)]
            for i in range(len(tableau20)):
                 r, g, b = tableau20[i]
                 tableau20[i] = (r / 255., g / 255., b / 255.)
            fig=Figure()
            ax=fig.add_subplot(111)
            ax.spines["top"].set_visible(False)
            ax.spines["bottom"].set_visible(False)
            ax.spines["right"].set_visible(False)
            ax.spines["left"].set_visible(False)
            y = [s for s in score_list]
            x = [v.entry_date for v in values]
            ax.plot_date(x, y, '-')
            ax.xaxis.set_major_formatter(DateFormatter('%Y-%m-%d'))
            fig.autofmt_xdate()
            canvas=FigureCanvas(fig)
            response=HttpResponse(content_type='image/png')
            canvas.print_png(response)
            return response

##DUMMY FUNCTION FOR THE ANALYTICS PAGE HTML
def summarise_analysis(request, name = "Library Users"):
    internal = analytics_page(request, name)
    return render(request, 'cityscore/analytics.html', {'name': name, 'graph': internal})


#SYNC DATABASE WITH DATA FROM AN UPLOADED METRIC FILE
def handle_uploaded_metric_file(this_city, file):
    #screen for the file type so we call the correct input reader
    if file.content_type == "text/csv" or file.content_type == "application/vnd.ms-excel":
        #the second data type is specific to Microsoft, where it is a saved CSV
        filev = StringIO(file.read().decode())
        reader = csv.reader(filev)
        #extract the data row-by-row. if something is wrong, tell the user where
        #the error occurred.
        for row in reader:
            try:
                _,created = Metric.objects.get_or_create(
                                                         name = row[0],
                                                         definition = row[1],
                                                         direction = row[2],
                                                         historic = row[3],
                                                         target = row[4],
                                                         trend = row[5],
                                                         city = this_city
                                                         )
            except:
                err = "There was an error processing this at the metric named " + row[0]
            else:
                err = None
        return err
    #otherwise, if the file is a JSON...
    elif file.content_type == "text/json":
        #use django's inbuilt data serializer to extract information from the file
        json_file = simplejson.load(file)
        obj_generator = serializers.json.Deserializer(json_file)
        m_set = this_city.metric_set.filter(city = this_city.pk)
        for obj in obj_generator:
            record = Metric(
                            name = obj.name,
                            definition = obj.definition,
                            direction = obj.direction,
                            historic = obj.historic,
                            target = obj.target,
                            trend = obj.trend,
                            city = this_city
                            )
            obj.save()
    else:
        #currently unable to handle non-csv, non-json files.
        return 'That file type is invalid!'
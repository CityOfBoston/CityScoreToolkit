# -*- coding: utf-8 -*-
from django.db import models
from django.db import connection
from django.forms import ModelForm, Textarea
from django.utils.html import escape
from django.utils.safestring import mark_safe
import django.forms
import sys
import django.core.exceptions
import datetime
import numpy as np
from django.contrib.auth.models import User
import csv
import scipy.stats
import math


#PROXY SECONDARY MODEL FOR THE USER IN CASE THE CITY WANTS TO CREATE CITYWIDE,
#CROSS-METRIC ANALYTICAL TOOLS
class City(models.Model):
    cityname = models.CharField("City or organization name",
                                max_length = 200
                                )
    user = models.OneToOneField(User, on_delete = models.CASCADE, primary_key = True, verbose_name = "user")
   
    @property
    def calculate_cityscore_day(self):
        #get all metrics
        metrics = self.metric_set.filter(city = self.pk)
        score_set = []
        for m in metrics:
            #make sure the metric is not empty
            if m.numVals > 0:
                #if the metric doesn't have a score today and is a trend, we 
                #don't want to include it in cityscore
                if m.trend and m.calculate_score_day == "N/A":
                    pass
                else:
                    #otherwise, add it to our score set
                    score_set.append(m.calculate_score_day)
        #if we have at least 2 scores, we take the mean
        if len(score_set) > 1:
            return math.ceil(np.mean(score_set)*100)/100
        #otherwise, it's just the one score
        elif len(score_set) == 1:
            return math.ceil(score_set[0]*100)/100
        #otherwise, we give the user a reminder.
        else:
            return "Enter Values!"

    @property
    def calculate_cityscore_week(self):
        metrics = self.metric_set.filter(city = self.pk)
        score_set = []
        for m in metrics:
            if m.numVals > 0:
                score_set.append(m.calculate_score_week)
        if len(score_set) > 1:
            #if we have at least 2 values, make sure none of the values are
            #null values, which is a risk for non-daily trends due to the 
            #way the queryset is filtered in django
            for i, x in enumerate(score_set):
                if x is None or math.isnan(x):
                    pass
                score_set[i] = x
            #calculate the mean if needed.
            return math.ceil(np.mean(score_set)*100)/100
        elif len(score_set) == 1:
            return math.ceil(float(score_set[0])*100)/100
        else:
            return "Enter Values!"
    #SAME LOGIC    
    @property
    def calculate_cityscore_month(self):
        metrics = self.metric_set.filter(city = self.pk)
        score_set = []
        for m in metrics:
            if m.numVals > 0:
                score_set.append(m.calculate_score_month)
        if len(score_set) > 1:
            for i, x in enumerate(score_set):
                score_set[i] = x
            return math.ceil(np.mean(score_set)*100)/100
        elif len(score_set) == 1:
            return math.ceil(float(score_set[0])*100)/100
        else:
            return "Enter Values!"
    # SAME LOGIC    
    @property
    def calculate_cityscore_quarter(self):
        metrics = self.metric_set.filter(city = self.pk)
        score_set = []
        for m in metrics:
            if m.numVals > 0:
                score_set.append(m.calculate_score_quarter)
        if len(score_set) > 1:
            for i, x in enumerate(score_set):
                score_set[i] = x
            return math.ceil(np.mean(score_set)*100)/100
        elif len(score_set) == 1:
            return math.ceil(float(score_set[0])*100)/100
        else:
            return "Enter Values!"
        
    @property
    def get_exceeding(self):
        #get all the metrics in this city
        metrics = self.metric_set.filter(city = self.pk)
        score_set = []
        id_set = []
        #extract the scores and ids of the metrics if they aren't null-valued
        #trends.
        for m in metrics:
            if m.trend and m.calculate_score_week == 0:
                pass
            if m.numVals > 0:
                score_set.append(m.calculate_score_week)
                id_set.append(m.id)
        #order the metrics in descending order
        ordered_metrics = [i[1] for i in sorted(enumerate(score_set), key=lambda x:x[1], reverse = True)]
        #figure out how the data was sorted in the first place
        order = [i[0] for i in sorted(enumerate(score_set), key=lambda x:x[1], reverse = True)]
        #add the metrics in the correct order to a set, by id
        ordered_metrics_ids = []
        for n in order:
            ordered_metrics_ids.append(id_set[n])
        #extract the corresponding metric object via id filtering in a query
        exc_set = []
        for x in ordered_metrics_ids:
            exc_set.append(self.metric_set.filter(id = x))
        #get the top 5 if there are at least 5 metrics.
        if len(exc_set) > 5:
            return exc_set[0:4]
        else:
            return exc_set
    
    ## SAME LOGIC AS ABOVE    
    @property
    def get_follow_up(self):
        metrics = self.metric_set.filter(city = self.pk)
        score_set = []
        id_set = []
        for m in metrics:
            if m.trend and m.calculate_score_week == 0:
                continue
            if m.numVals > 0:
                score_set.append(m.calculate_score_week)
                id_set.append(m.id)
        ordered_metrics = [i[1] for i in sorted(enumerate(score_set), key=lambda x:x[1])]
        order = [i[0] for i in sorted(enumerate(score_set), key=lambda x:x[1])]
        ordered_metrics_ids = []
        for n in order:
            ordered_metrics_ids.append(id_set[n])
        follow_up_set = []
        for x in ordered_metrics_ids:
            follow_up_set.append(self.metric_set.filter(id = x))
        if len(follow_up_set) > 5:
            return follow_up_set[0:4]
        else:
            return follow_up_set
   
   ## SAME LOGIC AS THE CITYWIDE SCORES 
    @property
    def calculate_percentile(self):
        metrics = self.metric_set.filter(city = self.pk)
        score_set = []
        for m in metrics:
            if m.numVals > 0:
                score_set.append(m.calculate_percentile)
        if len(score_set) > 1:
            return math.ceil(np.mean(score_set)*100)/100
        elif len(score_set) == 1:
            return math.ceil(score_set[0]*100)/100
        else:
            return "Enter Values!"
    
    @property
    def last_entered_date(self):
        #get all metrics
        metric = self.metric_set.filter(city = self.pk)
        if len(metric) > 0:
            #get most recently added metric
            recent_metric = metric[0]
            #use basic sorting algorithm to find most recently entered date
            for m in metric:
                if m.last_entered_date is not None:
                    if recent_metric.last_entered_date is None or m.last_entered_date > recent_metric.last_entered_date:
                        recent_metric = m
            return recent_metric.last_entered_date
        else:
            return "N/A"

#REPRESENTS ONE PERFORMANCE MANAGEMENT INDICATOR WHICH CAN SUPPORT ANY NUMBER OF 
#MEASUREMENTS. REQUIRES BASIC DEFINITIONS AND IMPORTANTLY, INDICATORS OF HOW TO 
#SET A TARGET VALUE FOR THE PERFORMANCE ANALYSIS TOOL AND WHETHER THE INDICATOR
#IS ONE WHICH SHOULD INCREASE OR DECREASE OVER TIME.
class Metric(models.Model):
    name = models.CharField(
                            "Metric name", 
                            max_length = 200
                            )
    definition = models.CharField(
                                "Definition of metric", 
                                max_length=200
                                )
    direction = models.BooleanField(
                                    "Check this box if an improvement in the metric is indicated by its value going up (e.g., pothole repair on-time %). Leave it unchecked in the opposite case (e.g., ambulance response time).",
                                    default = 1
                                    )
    historic = models.BooleanField(
                                    "Check the box if this metric does not have a target. If checked, please note a minimum of 90 days of data (and ideally 365 days of data) is needed to generate an accurate score. Once there is 90 days of data in the system, the tool will automatically calculate a moving target based on this metric’s historical performance.", 
                                    default = 0
                                    )
    target = models.FloatField(
                                "What is the target value?"
                                )
    city = models.ForeignKey(
        City,
        on_delete = models.PROTECT,
        verbose_name = "city"
    )
    trend = models.BooleanField(
                                "Check this box if this metric may not have a performance value every day (e.g., homicides). If the daily value is zero, no score will be generated for that day.", 
                                default = 0
                                )
    scoreList = []
    #index = models.ForeignKey(
    #       Index
    #       on_delete = models.PROTECT,
    #       verbose_name = "Model Index"
    #)
    #function to extract all of the individual scores value-by-value
    @property 
    def get_score_list(self):
        #set the target value in case it has not already 
        #been set after previous entry
        self.set_historic_target
        v_set = []
        # prints.stderr, self.target
        #add all values to the list from a query set.
        for v in self.value_set.filter(metric_id = self.id):
            v_set.append(v.val)
        scores = []
        #ignore null values from trends, don't allow division by zero, or add 
        #the score.
        for i in v_set:
            if i == 0 and self.trend:
                scores.append(None)
            elif i == 0:
                scores.append(0)
            else:
                if self.direction:
                    scores.append(i/self.target)
                else:
                    scores.append(self.target/i)
        return scores
    
    #figure out the date on which the most recent value was entered.
    @property
    def last_entered_date(self):
        if(self.numVals > 0):
            current = self.value_set.filter(metric = self.id).order_by('-entry_date')[0]
            return current.entry_date
        else:
            "N/A"
    
    #figure out how many values have been entered, used to ensure we arent
    #conducting heavy calculations with too little data.
    @property
    def numVals(self):
        vals = self.value_set.filter(metric_id = self.id)
        return vals.count()
    
    #Calculate the daily score for this metric    
    @property
    def calculate_score_day(self):
        #organize the values by their date of entry, and extract the most recent.
        #organization is critical in case a user is entering bulk data which is
        #disorganized.
        current = self.value_set.filter(metric = self.id).order_by('-entry_date')[0]
        #if the value of the day is null and the metric is a trend, don't give 
        #a 0 score.
        if self.trend and current.val == 0:
            return "N/A"
        else:
            #ensure we have some data, or else we'll get some divisions by 0
            if self.numVals > 0:
                self.set_historic_target
                score = current.val/self.target
                #if the metric moves up, just return the value over its target
                if self.direction == 1:
                    return math.ceil(score*100)/100
                #if the metric goes down, but we only have 1 value, flipping the
                #score may produce confusion
                elif self.numVals < 2:
                    return math.ceil(score*100)/100
                #flip the score for a downward-moving metric as long as it is 
                #not 0, which would create an error.
                else:
                    score = 1/score if score != 0 else 0
                    return math.ceil(score*100)/100
            else:
                #if we don't have the data, we give a 0
                return 0
    
    #extract which dates are within 1 week/7 days of the most recent entry
    @property
    def get_week_set(self):
        if self.numVals > 0:
            #order the data by entry date
            current = self.value_set.filter(metric = self.id).order_by('-entry_date')[0]
            #create a set containing the last 7 days by date
            week = [current.entry_date - datetime.timedelta(days=x) for x in range(7)]
            e_date = []
            #extract the entry dates of each value in this metric
            for v in self.value_set.filter(metric_id = self.id):
                e_date.append(v.entry_date)
            #return only those which are within the past 7 days
            week_set = [e in week for e in e_date]
            return week_set
        else:
            return 0
    
    @property
    def calculate_score_week(self):
        if self.numVals > 0:
            #get the set of value objects which were in the past week.
            self.set_historic_target
            week_set = self.get_week_set
            v_set = []
            #extract from db only values in the last week
            for index, v in enumerate(self.value_set.filter(metric_id = self.id)):
                if week_set[index]:
                    v_set.append(v.val)
            #if we have no values, circumvent errors by returning 0
            if sum(v_set) == 0:
                return 0
            #calculate the weekly score
            score = np.mean(v_set)/self.target
            #adjust for directionality
            if self.direction == 1:
                return math.ceil(score*100)/100
            else:
                if score == 0:
                    return 0
                else: 
                    score = 1/score
                    return math.ceil(score*100)/100
        else:
            return 0
    
    #SEE GET_WEEK_SET
    @property
    def get_month_set(self):
        if self.numVals > 0:
            current = self.value_set.filter(metric = self.id).order_by('-entry_date')[0]
            month = [current.entry_date - datetime.timedelta(days=x) for x in range(30)]
            e_date = []
            for v in self.value_set.filter(metric_id = self.id):
                e_date.append(v.entry_date)
            month_set = [e in month for e in e_date]
            return month_set
        else:
            return 0
    
    #SEE CALCULATE_SCORE_WEEK
    @property
    def calculate_score_month(self):
        if self.numVals > 0:
            self.set_historic_target
            month_set = self.get_month_set
            v_set = []
            for index, v in enumerate(self.value_set.filter(metric_id = self.id)):
                if month_set[index]:
                    v_set.append(v.val)
            if sum(v_set) == 0:
                return 0
            score = np.mean(v_set)/self.target
            if self.direction == 1:
                return math.ceil(score*100)/100
            else:
                if score == 0:
                    return 0
                else: 
                    score = 1/score
                    return math.ceil(score*100)/100
        else:
            return 0
    
    #SEE GET_WEEK_SET    
    @property 
    def get_quarter_set(self):
        if self.numVals > 0:
            current = self.value_set.filter(metric = self.id).order_by('-entry_date')[0]
            quarter = [current.entry_date - datetime.timedelta(days=x) for x in range(90)]
            e_date = []
            for v in self.value_set.filter(metric_id = self.id):
                e_date.append(v.entry_date)
            quarter_set = [e in quarter for e in e_date]
            return quarter_set
        else:
            return 0
   
    #SEE CALCULATE_SCORE_WEEK 
    @property
    def calculate_score_quarter(self):
        if self.numVals > 0:
            self.set_historic_target
            quarter_set = self.get_quarter_set
            v_set = []
            for index, v in enumerate(self.value_set.filter(metric_id = self.id)):
                if quarter_set[index]:
                    v_set.append(v.val)
            if sum(v_set) == 0:
                return 0
            score = np.mean(v_set)/self.target
            if self.direction == 1:
                return math.ceil(score*100)/100
            else:
                if score == 0:
                    return 0
                else: 
                    score = 1/score
                    return math.ceil(score*100)/100
        else:
            return 0
    
    @property
    def calculate_percentile(self):
        if self.numVals > 0:
            self.set_historic_target
            v_set = []
            #extract all the values we have
            for v in self.value_set.filter(metric_id = self.id):
                v_set.append(v.val)
            #variable containing most recent value
            this_val = self.value_set.filter(metric = self.id).order_by('-entry_date')[0]
            #calculate teh score for the current value, ensuring no divison-by-0
            if this_val.val != 0:
                this_score = this_val.val/self.target if self.direction else self.target/this_val.val
            else:
                this_score = this_val.val/self.target if self.direction else None
            scores = []
            #append all the scores to this list, avoiding issues with div. by 0
            for i in v_set:
                if self.direction:
                    scores.append(i/self.target)
                else:
                    if i != 0:
                        scores.append(self.target/i)
                    else:
                        pass
            #if we have no scores at this point, we will return 100th percentile.
            if sum(scores) == 0 or len(scores) == 0:
                ptile = 100
            #calculate the percentile and return it
            else:
                ptile = scipy.stats.percentileofscore(scores,this_score, 'rank')
            return math.ceil(ptile*100)/100 # note this phrase rounds our var
        else:
            return 0
    
    #SEE GET_WEEK_SET
    @property
    def calculate_prev_month_set(self):
        current = self.value_set.filter(metric = self.id).order_by('-entry_date')[0]
        prev_month = [current.entry_date - datetime.timedelta(days=x) for x in range(365, 365 + 90)]
        e_date = []
        for v in self.value_set.filter(metric_id = self.id):
            e_date.append(v.entry_date)
        prev_month_set = [e in prev_month for e in e_date]
        return prev_month_set
            
    @property
    def set_historic_target(self):
        if self.historic == 1:
            #get the list of all values
            vals = self.value_set.filter(metric = self.pk)
            value_list = []
            #if there are more than 365 days of data for a trend
            if self.trend and self.numVals > 365:
                #get this month's data from last year (e.g., July 2015 for July
                #2016)
                prev_month_set = self.calculate_prev_month_set
                v_set = []
                #collect the values from this set
                for index, v in enumerate(self.value_set.filter(metric_id = self.id)):
                    if prev_month_set[index]:
                        v_set.append(v.val)
                #get the mean of these values and set it as the target. 
                self.target = np.mean(v_set)
                return self.save()
            else:
                for v in vals:
                    value_list.append(v.val)
                #otherwise, we deal with the data depending on whether or 
                #not it is historic.
                if self.historic:
                    if self.target == 0:
                    #if there is a target of 0, we have an empty metric
                    #and we simply avoid div-by-0
                        self.target = 1
                        return self.save()
                    if self.numVals > 90 :
                        #if we have enough values, we will use the hist. algorithm
                        avg = np.mean(value_list)
                        std = np.std(value_list)
                        # if the metric goes up, we difference the avg and its std
                        if self.direction == 1:
                            self.target = abs(avg - std)
                            return self.save()
                        #otherwise, we add them.
                        else:
                            self.target = avg + std
                            return self.save()
                    else:
                        pass
                else:
                        pass
                #ensure a check for the target's validity goes through regardless
                #of historicity
                if self.target == 0:
                    self.target = 1
                    return self.save()
    
    @property
    def entered(self):
        #boolean for whether or not there are any values.
        return self.numVals > 0
        
    def __str__(self):
        return self.name
 
#MODEL REPRESENTING A SINGLE ENTRY IN A METRIC TABLE WHICH ESSENTIALLY IS A 
#MEASUREMENT FROM ONE DAY. IMPORTANTLY SEPARATE FROM THE MODEL AS IT MAY FURTHER 
#BE TAILORED TO THE TYPE OF METRIC BY USERS.
class Value(models.Model):
    val = models.FloatField("Value")
    entry_date = models.DateField("Date",
                            default = datetime.date.today
                            )
    metric = models.ForeignKey(
        Metric,
        on_delete = models.PROTECT,
        verbose_name = "Metric"
    )
    city = models.ForeignKey(
        City,
        on_delete = models.PROTECT,
        verbose_name = "city"
        )
    # file_entry - models.FileField()
    @property
    def _get_quarter(self):
        return (self.entry_date.month - 1)//3 + 1
    def __str__(self):
        return str(self.val)
    quarter = property(_get_quarter)
    @property
    def _get_month(self):
        return self.entry_date.month
    month = property(_get_month)
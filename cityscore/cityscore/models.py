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
    cityname = models.CharField("City name",
                                max_length = 200
                                )
    user = models.OneToOneField(User, on_delete = models.CASCADE, primary_key = True, verbose_name = "user")
   
    @property
    def calculate_cityscore_day(self):
        metrics = self.metric_set.filter(city = self.pk)
        score_set = []
        for m in metrics:
            if m.numVals > 1:
                score_set.append(m.calculate_score_day)
        if len(score_set) > 1:
            return math.ceil(np.mean(score_set)*100)/100
        elif len(score_set) == 1:
            return math.ceil(score_set[0]*100)/100
        else:
            return "Enter Values!"

    @property
    def calculate_cityscore_week(self):
        metrics = self.metric_set.filter(city = self.pk)
        score_set = []
        for m in metrics:
            if m.numVals > 1:
                score_set.append(m.calculate_score_week)
        if len(score_set) > 1:
            for i, x in enumerate(score_set):
                score_set[i] = float(x) if '.' in x else int(x)
            return math.ceil(np.mean(score_set)*100)/100
        elif len(score_set) == 1:
            return math.ceil(score_set[0]*100)/100
        else:
            return "Enter Values!"
        
    @property
    def calculate_cityscore_month(self):
        metrics = self.metric_set.filter(city = self.pk)
        score_set = []
        for m in metrics:
            if m.numVals > 1:
                score_set.append(m.calculate_score_month)
        if len(score_set) > 1:
            for i, x in enumerate(score_set):
                score_set[i] = float(x) if '.' in x else int(x)
            return math.ceil(np.mean(score_set)*100)/100
        elif len(score_set) == 1:
            return math.ceil(score_set[0]*100)/100
        else:
            return "Enter Values!"
        
    @property
    def calculate_cityscore_quarter(self):
        metrics = self.metric_set.filter(city = self.pk)
        score_set = []
        for m in metrics:
            if m.numVals > 1:
                score_set.append(m.calculate_score_quarter)
        if len(score_set) > 1:
            for i, x in enumerate(score_set):
                score_set[i] = float(x) if '.' in x else int(x)
            return math.ceil(np.mean(score_set)*100)/100
        elif len(score_set) == 1:
            return math.ceil(score_set[0]*100)/100
        else:
            return "Enter Values!"
        
    @property
    def get_exceeding(self):
        metrics = self.metric_set.filter(city = self.pk)
        score_set = []
        id_set = []
        for m in metrics:
            if m.numVals > 1:
                score_set.append(m.calculate_score_week)
                id_set.append(m.id)
        ordered_metrics = [i[1] for i in sorted(enumerate(score_set), key=lambda x:x[1], reverse = True)]
        order = [i[0] for i in sorted(enumerate(score_set), key=lambda x:x[1], reverse = True)]
        ordered_metrics_ids = []
        for n in order:
            ordered_metrics_ids.append(id_set[n])
        exc_set = []
        for x in ordered_metrics_ids:
            exc_set.append(self.metric_set.filter(id = x))
        if len(exc_set) > 5:
            return exc_set[0:4]
        else:
            return exc_set
        
    @property
    def get_follow_up(self):
        metrics = self.metric_set.filter(city = self.pk)
        score_set = []
        id_set = []
        for m in metrics:
            if m.numVals > 1:
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
    
    @property
    def calculate_percentile(self):
        metrics = self.metric_set.filter(city = self.pk)
        score_set = []
        for m in metrics:
            if m.numVals > 1:
                score_set.append(m.calculate_percentile)
        if len(score_set) > 1:
            return math.ceil(np.mean(score_set)*100)/100
        elif len(score_set) == 1:
            return math.ceil(score_set[0]*100)/100
        else:
            return "Enter Values!"

#REPRESENTS ONE PERFORMANCE MANAGEMENT INDICATOR WHICH CAN SUPPORT ANY NUMBER OF 
#MEASUREMENTS. REQUIRES BASIC DEFINITIONS AND IMPORTANTLY, INDICATORS OF HOW TO 
#SET A TARGET VALUE FOR THE PERFORMANCE ANALYSIS TOOL AND WHETHER THE INDICATOR
#IS ONE WHICH SHOULD INCREASE OR DECREASE OVER TIME.
class Metric(models.Model):
    name = models.CharField("Metric name", 
                            max_length = 200
                            )
    definition = models.CharField("Definition of metric", max_length=200)
    direction = models.BooleanField(
                                    "Check this box if an improvement in the metric is indicated by it going up (e.g., smiles). Leave it unchecked in the opposite case (e.g., frowns).",
                                    default = 1
                                    )
    historic = models.BooleanField(
                                    "Check the box if you lack a target for this metric. If checked, you will not be able to generate scores for this metric without at least a year of data, at which point we will automatically calculate the target.", 
                                    default = 0
                                    )
    target = models.FloatField("What is the target value? (Leave as 1 if the above is checked.)")
    city = models.ForeignKey(
        City,
        on_delete = models.PROTECT,
        verbose_name = "city"
    )
    
    scoreList = []
    
    @property 
    def get_score_list(self):
        v_set = []
        for v in self.value_set.filter(metric_id = self.id):
            v_set.append(v.val)
        scores = []
        for i in v_set:
            if self.direction:
                scores.append(i/self.target)
            else:
                scores.append(self.target/i)
        return scores

    @property
    def numVals(self):
        vals = self.value_set.filter(metric_id = self.id)
        return vals.count()
        
    @property
    def calculate_score_day(self):
        self.set_historic_target
        current = self.value_set.filter(metric = self.id).order_by('-entry_date')[0]
        score = current.val/self.target
        if self.direction == 1:
            return math.ceil(score*100)/100
        elif self.numVals < 2:
            return math.ceil(score*100)/100
        else:
            score = 1/score
            return math.ceil(score*100)/100
    
    @property
    def get_week_set(self):
        current = self.value_set.filter(metric = self.id).order_by('-entry_date')[0]
        week = [current.entry_date - datetime.timedelta(days=x) for x in range(7)]
        e_date = []
        for v in self.value_set.filter(metric_id = self.id):
            e_date.append(v.entry_date)
        week_set = [e in week for e in e_date]
        return week_set
    
    @property
    def calculate_score_week(self):
        self.set_historic_target
        week_set = self.get_week_set
        v_set = []
        for index, v in enumerate(self.value_set.filter(metric_id = self.id)):
            if week_set[index]:
                v_set.append(v.val)
        score = np.mean(v_set)/self.target
        if self.direction == 1:
            return ("%.2f" % score)
        else:
            score = 1/score
            return ("%.2f" % score)
    
    @property
    def get_month_set(self):
        current = self.value_set.filter(metric = self.id).order_by('-entry_date')[0]
        month = [current.entry_date - datetime.timedelta(days=x) for x in range(30)]
        e_date = []
        for v in self.value_set.filter(metric_id = self.id):
            e_date.append(v.entry_date)
        month_set = [e in month for e in e_date]
        return month_set
    
    @property
    def calculate_score_month(self):
        self.set_historic_target
        month_set = self.get_month_set
        v_set = []
        for index, v in enumerate(self.value_set.filter(metric_id = self.id)):
            if month_set[index]:
                v_set.append(v.val)
        score = np.mean(v_set)/self.target
        if self.direction == 1:
            return ("%.2f" % score)
        else:
            score = 1/score
            return ("%.2f" % score)
        
    @property 
    def get_quarter_set(self):
        current = self.value_set.filter(metric = self.id).order_by('-entry_date')[0]
        quarter = [current.entry_date - datetime.timedelta(days=x) for x in range(90)]
        e_date = []
        for v in self.value_set.filter(metric_id = self.id):
            e_date.append(v.entry_date)
        quarter_set = [e in quarter for e in e_date]
        return quarter_set
    
    @property
    def calculate_score_quarter(self):
        self.set_historic_target
        quarter_set = self.get_quarter_set
        v_set = []
        for index, v in enumerate(self.value_set.filter(metric_id = self.id)):
            if quarter_set[index]:
                v_set.append(v.val)
        score = np.mean(v_set)/self.target
        if self.direction == 1:
            return ("%.2f" % score)
        else:
            score = 1/score
            return ("%.2f" % score) 
    
    @property
    def calculate_percentile(self):
        self.set_historic_target
        v_set = []
        for v in self.value_set.filter(metric_id = self.id):
            v_set.append(v.val)
        this_val = self.value_set.filter(metric = self.id).order_by('-entry_date')[0]
        this_score = this_val.val/self.target if self.direction else self.target/this_val.val
        scores = []
        for i in v_set:
            if self.direction:
                scores.append(i/self.target)
            else:
                scores.append(self.target/i)
        ptile = scipy.stats.percentileofscore(scores,this_score, 'rank')
        return math.ceil(ptile*100)/100
        
    @property
    def set_historic_target(self):
        vals = self.value_set.filter(metric = self.pk)
        value_list = []
        for v in vals:
            value_list.append(v.val)
        if self.historic:
            if self.target == 0:
                self.target = 1
            if self.numVals > 90 :
                avg = np.mean(value_list)
                std = np.std(value_list)
                if self.direction == 1:
                    self.target = abs(avg - std)
                else:
                    self.target = avg + std
            else:
                avg = np.mean(value_list)
                std = np.std(value_list)
                if self.direction == 1:
                    self.target = abs(avg - std)
                else:
                    self.target = avg + std
        else:
            pass
    
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
        return self.val
    quarter = property(_get_quarter)
    @property
    def _get_month(self):
        return self.entry_date.month
    month = property(_get_month)

from django.db import models
from django.db import connection
import datetime
import date 
import numpy as np
from django.contrib.auth.models import User
import csv
import scipy.stats.percentileofscore

# from pygments.lexers import get_all_lexers
# from pygments.styles import get_all_styles

# LEXERS = [item for item in get_all_lexers() if item[1]]
# LANGUAGE_CHOICES = sorted([(item[1][0], item[0]) for item in LEXERS])
# STYLE_CHOICES = sorted((item, item) for item in get_all_styles())

# class MetricManager(models.Manager):
#     def meter_count(self,keyword):
#         return filter(name_icontains=keyword).count()

class City(models.Model):
    cityname = models.CharField("City name",
                                max_length = 200
                                )
    input_choices = (
            ("1","Manual"),
            ("2","Server Upload"),
            ("3","SQL Database")
                )
    input_spec = models.CharField(max_length=1, choices=input_choices)
    
    @property
    def calculate_cityscore_day(self):
        metrics = self.metric_set.all()
        score = np.mean(metrics.calculate_score_day)
        return score

    @property
    def calculate_cityscore_week(self):
        metrics = self.metric_set.all()
        score = np.mean(metrics.calculate_score_week)
        return score
        
    @property
    def calculate_cityscore_month(self):
        metrics = self.metric_set.all()
        score = np.mean(metrics.calculate_score_month)
        return score
        
    @property
    def calculate_cityscore_quarter(self):
        metrics = self.metric_set.all()
        score = np.mean(metrics.calculate_score_quarter)
        return score
        
    @property
    def calculate_percentile(self):
        current = self.metric_set.all()
        return np.mean(current.calculate_percentile)
        
class Metric(models.Model):
    name = models.CharField("Metric name", 
                            max_length = 200
                            )
    definition = models.CharField("Definition of metric")
    direction = models.BooleanField("Do you want this value to go up or down?",
                                    default = 1
                                    )
    historic = models.BooleanField("Is the target value based on history, " +
                                    "or is there a manual input?", 
                                    default = 0
                                    )
    target = models.FloatField("What is the target value?")
    city = models.ForeignKey(
        City,
        on_delete = models.PROTECT,
        verbose_name = "The account to which this information belongs"
    )
    
    @property
    def numVals(self):
        vals = self.value_set.all()
        return vals.length
    
    @property
    def calculate_score_day(self):
        current = self.value_set.get(id = 1)
        score = current.val/self.target
        if self.direction == 1:
            return score
        elif self.numVals < 2:
            return score
        else:
            return 1/score    
    
    @property
    def calculate_score_week(self):
        current = self.value_set.get(id = 1)
        week = [current.entry_date - datetime.timedelta(days=x) for x in range(0, 7)]
        query_set = self.value_set.get(all)
        week_set = query_set[query_set.entry_date in week]
        score = np.mean(week_set.val)/self.target
        if self.direction == 1:
            return score
        elif self.numVals < 2:
            return score
        else:
            return 1/score    
    
    @property
    def calculate_score_month(self):
        current = self.value_set.get(id = 1)
        monthly_set = self.value_set.get(month = current.month)
        score = np.mean(monthly_set.val)/self.target
        if self.direction == 1:
            return score
        elif self.numVals < 2:
            return score
        else:
            return 1/score  
        
    @property
    def calculate_score_quarter(self):
        current = self.value_set.get(id = 1)
        quarter_set = self.value_set.get(quarter = current.quarter)
        score = np.mean(quarter_set.val)/self.target
        if self.direction == 1:
            return score
        elif self.numVals < 2:
            return score
        else:
            return 1/score
    
    @property
    def calculate_percentile(self):
        current = self.value_set.get(id = 1)
        others = self.value_set.all()
        return scipy.stats.percentileofscore(others, current, 'mean')
        
    @property
    def set_historic_target(self):
        vals = self.value_set.all()
        if self.numVals > 1 :
            avg = np.mean(vals)
            std = np.std(vals)
        else:
            avg = 1
            std = 0
        return avg - std

class Value(models.Model):
    val = models.FloatField("Input variable value.")
    entry_date = models.DateField("Date when variable value was input.",
                            default = date.today
                            )
    metric = models.ForeignKey(
        Metric,
        on_delete = models.PROTECT,
        verbose_name = "Measured metric corresponding to value"
    )
    # file_entry - models.FileField()
    @property
    def _get_quarter(self):
        return (self.entry_date.month - 1)//3 + 1
    def __str__(self):
        return self.val
    quarter = property(_get_quarter)
    month = property(entry_date.month)
    
# class upload_csv(models.Model):
#     filename = models.CharField(max_length = 200)
#     ext = models.CharField(max_length = 5)
#     upload_date = models.DateField(default = date.today)
#     csv = models.FileField(upload_to = "data/")
#     def __str__(self):
#         return self.filename
#     @property
#     def to_db(self):
#         return csv.reader(self.csv, delimiter=',')
        
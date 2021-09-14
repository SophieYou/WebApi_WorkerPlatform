from django.contrib import admin
from . import models
# Register your models here.

@admin.register(models.UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'user_name', 'user_tel')
    ordering = ['user_id']

@admin.register(models.UserJobtype)
class UserJobytypeAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'jobtype_id')
    ordering = ['user_id']

@admin.register(models.JobtypeDetail)
class JobtypeDetailAdmin(admin.ModelAdmin):
    list_display = ('jobtype_id', 'jobtype_upper', 'jobtype_desc')
    ordering = ['jobtype_upper']

@admin.register(models.RegionInfo)
class RegionInfoAdmin(admin.ModelAdmin):
    list_display = ('region_id', 'region_upper', 'region_desc')
    ordering = ['region_upper']

@admin.register(models.NewsInfo)
class NewsInfoAdmin(admin.ModelAdmin):
    list_display = ('news_id', 'news_title', 'news_overview', 'post_date')
    ordering = ['post_date']

@admin.register(models.TrainingInfo)
class
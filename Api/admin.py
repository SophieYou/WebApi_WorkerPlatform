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
class TrainingInfoAdmin(admin.ModelAdmin):
    list_display = ('training_id', 'training_org', 'region_id', 'updated_on')
    ordering = ['updated_on']

@admin.register(models.SearchInfo)
class SearchInfoAdmin(admin.ModelAdmin):
    list_display = ('search_id', 'contact_person', 'search_status', 'created_on')
    ordering = ['created_on']

@admin.register(models.CompanyInfo)
class CompanyInfoAdmin(admin.ModelAdmin):
    list_display = ('company_id', 'company_name', 'contact_person', 'contact_tel', 'company_status', 'created_on')
    ordering = ['company_id']

@admin.register(models.JobInfo)
class JobInfoAdmin(admin.ModelAdmin):
    list_display = ('job_id', 'company_id', 'jobtype_id', 'region_id', 'job_name', 'job_status')
    ordering = ['job_id']

@admin.register(models.JobApply)
class JobApplyAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'job_id', 'created_on', 'apply_status')
    ordering = ['user_id']

@admin.register(models.JobFavor)
class JobFavorAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'job_id', 'created_on')
    ordering = ['user_id']

@admin.register(models.BenefitList)
class BenefitListAdmin(admin.ModelAdmin):
    list_display = ('benefit_id', 'benefit_desc')
    ordering = ['benefit_id']

@admin.register(models.SalaryList)
class SalaryListAdmin(admin.ModelAdmin):
    list_display = ('salary_id', 'salary_type', 'salary_upper', 'salary_lower')
    ordering = ['salary_type', 'salary_upper']

@admin.register(models.CourseType)
class CourseTypeAdmin(admin.ModelAdmin):
    list_display = ('ctype_id', 'ctype_desc')
    ordering = ['ctype_id']

@admin.register(models.CourseInfo)
class CourseInfoAdmin(admin.ModelAdmin):
    list_display = ('course_id', 'course_title', 'ctype_id', 'course_form','updated_on')
    ordering = ['ctype_id','updated_on']

@admin.register(models.JobVacancyInfo)
class JobVacancyInfoAdmin(admin.ModelAdmin):
    list_display = ('vacancy_id', 'user_id', 'jobtype_id', 'region_id', 'updated_on', 'vacancy_status')
    ordering = ['updated_on']
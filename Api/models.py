from django.contrib.auth.models import User
from django.db import models


# Create your models here.

# worker user profile
class UserProfile(models.Model):
    user_id = models.AutoField(primary_key=True)
    user_auth = models.OneToOneField(User, on_delete=models.CASCADE)
    user_tel = models.CharField(max_length=8)
    user_name = models.CharField(max_length=40, null=True)
    user_year = models.IntegerField(null=True)
    user_sex = models.CharField(max_length=1, null=True)  # F/M
    safecard_date = models.DateField(null=True)
    regcard_date = models.DateField(null=True)
    work_year = models.IntegerField(null=True)
    lan_en = models.IntegerField(null=True)  # 1-5 score
    lan_cantonese = models.IntegerField(null=True)  # 1-5 score
    lan_mandarin = models.IntegerField(null=True)  # 1-5 score
    # user_pwd = models.CharField(max_length=8, null=True)
    created_on = models.DateField(auto_now_add=True)
    updated_on = models.DateField(auto_now=True)

    def __str__(self):
        return str(self.user_id)


# Job type detail
class JobtypeDetail(models.Model):
    jobtype_id = models.AutoField(primary_key=True)
    jobtype_desc = models.CharField(max_length=10)
    jobtype_upper = models.CharField(max_length=10)

    def __str__(self):
        return self.jobtype_desc


# User job type relation
class UserJobtype(models.Model):
    user_id = models.ForeignKey('UserProfile', related_name='jobtype', on_delete=models.CASCADE)
    jobtype_id = models.ForeignKey('JobtypeDetail', related_name='jobtypedesc', on_delete=models.CASCADE)
    updated_on = models.DateField(auto_now=True)

    def __str__(self):
        return str(self.id)


# region info
class RegionInfo(models.Model):
    region_id = models.AutoField(primary_key=True)
    region_desc = models.CharField(max_length=10)
    region_upper = models.CharField(max_length=10)

    def __str__(self):
        return self.region_desc


# news info
class NewsInfo(models.Model):
    news_id = models.AutoField(primary_key=True)
    news_title = models.CharField(max_length=20)
    news_overview = models.CharField(max_length=40)
    news_detail = models.TextField()
    post_date = models.DateField(auto_now=True)
    url_cover = models.ImageField(upload_to='news',null=True)

    def __str__(self):
        return self.news_title


# training info
class TrainingInfo(models.Model):
    training_id = models.AutoField(primary_key=True)
    training_org = models.CharField(max_length=20)
    region_id = models.ForeignKey('RegionInfo', on_delete=models.CASCADE)
    from_date = models.DateField()
    to_date = models.DateField()
    training_tel = models.CharField(max_length=8)
    updated_on = models.DateField(auto_now=True)

    def __str__(self):
        return str(self.training_id)


# search info
class SearchInfo(models.Model):
    search_id = models.AutoField(primary_key=True)
    contact_person = models.CharField(max_length=40)
    contact_tel = models.CharField(max_length=8)
    contact_email = models.CharField(max_length=40, null=True)
    search_text = models.TextField()
    search_status = models.BooleanField(default=False)
    created_on = models.DateField(auto_now_add=True)

    def __str__(self):
        return str(self.search_id)


# company info
class CompanyInfo(models.Model):
    company_id = models.AutoField(primary_key=True)
    user_auth = models.OneToOneField(User, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=40)
    contact_person = models.CharField(max_length=40)
    # company_pwd = models.CharField(max_length=12, null=True)
    contact_tel = models.CharField(max_length=8)
    contact_email = models.CharField(max_length=40)
    company_year = models.IntegerField()
    company_detail = models.TextField()
    company_status = models.BooleanField(default=False)
    company_remarks = models.TextField(null=True)
    url_logo = models.ImageField(upload_to='media/logo',null=True)
    url_cert = models.ImageField(upload_to='media/cert',null=True)
    created_on = models.DateField(auto_now_add=True)
    updated_on = models.DateField(auto_now=True)

    def __str__(self):
        return str(self.company_id)


# job info
class JobInfo(models.Model):
    job_id = models.AutoField(primary_key=True)
    company_id = models.ForeignKey('CompanyInfo', on_delete=models.CASCADE)
    jobtype_id = models.ForeignKey('JobtypeDetail', on_delete=models.CASCADE)
    region_id = models.ForeignKey('RegionInfo', on_delete=models.CASCADE)
    job_name = models.CharField(max_length=40)
    vacancy_num = models.IntegerField(default=1)
    job_duty = models.TextField()
    job_request = models.TextField()
    salary_type = models.CharField(max_length=1, default='M')  # month or day (M/D)
    salary_upper = models.IntegerField()
    salary_lower = models.IntegerField()
    work_date = models.TextField(default='每週一至五，9:00-18:00')
    created_on = models.DateField(auto_now_add=True)
    updated_on = models.DateField(auto_now=True)
    post_date = models.DateField(null=True)
    end_date = models.DateField(null=True)
    job_status = models.CharField(max_length=1, default='0')  # 0： 草稿中；1：刊登中；2：結束
    pre_status = models.CharField(max_length=1, default='0')
    job_benefit = models.TextField(default='無')

    def __str__(self):
        return str(self.job_id)


# job apply
class JobApply(models.Model):
    user_id = models.ForeignKey('UserProfile', related_name='ua_id', on_delete=models.CASCADE)
    job_id = models.ForeignKey('JobInfo', related_name='ja_id', on_delete=models.CASCADE)
    created_on = models.DateField(auto_now_add=True)
    apply_comment = models.TextField(null=True)
    apply_status = models.CharField(max_length=1, default='0')  # 0:未查阅, 1:已保留，2：联系中，3：不合适
    pre_status = models.CharField(max_length=1, default='0')

    def __str__(self):
        return 'user id:' + str(self.user_id) + '; job id:' + str(self.job_id)


# job favorite
class JobFavor(models.Model):
    user_id = models.ForeignKey('UserProfile', related_name='uf_id', on_delete=models.CASCADE)
    job_id = models.ForeignKey('JobInfo', related_name='jf_id', on_delete=models.CASCADE)
    created_on = models.DateField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return 'user id:' + str(self.user_id) + '; job id:' + str(self.job_id)


# benefit list
class BenefitList(models.Model):
    benefit_id = models.AutoField(primary_key=True)
    benefit_desc = models.CharField(max_length=40)

    def __str__(self):
        return str(self.benefit_id)


# salary list
class SalaryList(models.Model):
    salary_id = models.AutoField(primary_key=True)
    salary_type = models.CharField(max_length=1) # M or D
    salary_upper = models.IntegerField()
    salary_lower = models.IntegerField()

    def __str__(self):
        return str(self.salary_id)


# course type
class CourseType(models.Model):
    ctype_id = models.AutoField(primary_key=True)
    ctype_desc = models.CharField(max_length=100)

    def __str__(self):
        return self.ctype_desc


# course info
class CourseInfo(models.Model):
    course_id = models.AutoField(primary_key=True)
    course_title = models.CharField(max_length=40)
    ctype_id = models.ForeignKey('CourseType', on_delete=models.CASCADE)
    course_form = models.BooleanField(default=True) # True: 全日制； False:兼读制
    course_period = models.CharField(max_length=100)
    course_fee = models.IntegerField()
    start_date = models.TextField(default='待定') # if null: 開班日期另作查詢
    course_req = models.TextField(null=True)
    course_detail = models.TextField(null=True)
    course_tel = models.CharField(max_length=8)
    updated_on = models.DateField(auto_now=True)
    course_link = models.TextField(null=True)

    def __str__(self):
        return str(self.course_id)


# job vacancy info
class JobVacancyInfo(models.Model):
    vacancy_id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey('UserProfile', on_delete=models.CASCADE)
    jobtype_id = models.ForeignKey('JobtypeDetail', on_delete=models.CASCADE)
    region_id = models.ForeignKey('RegionInfo', on_delete=models.CASCADE)
    salary_type = models.CharField(max_length=1, default='M')  # month or day (M/D)
    salary_upper = models.IntegerField()
    salary_lower = models.IntegerField()
    start_date = models.DateField()
    created_on = models.DateField(auto_now_add=True)
    updated_on = models.DateField(auto_now=True)
    vacancy_status = models.CharField(max_length=1, default='0') # 0: 匹配中；1：已结束
    match_num = models.IntegerField(default=0)

    def __str__(self):
        return str(self.vacancy_id)
from django.db import models


# Create your models here.

# worker user profile
class UserProfile(models.Model):
    user_id = models.AutoField(primary_key=True)
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
    user_pwd = models.CharField(max_length=8, null=True)
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
    news_detail = models.TextField
    post_date = models.DateField(auto_now=True)
    url_cover = models.TextField

    def __str__(self):
        return self.news_title


# training info
class TrainingInfo(models.Model):
    training_id = models.AutoField(primary_key=True)
    training_org = models.CharField(max_length=20)
    region_id = models.ForeignKey('RegionInfo', related_name='regiondesc', on_delete=models.CASCADE)
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
    search_text = models.TextField
    search_status = models.BooleanField(default=False)
    created_on = models.DateField(auto_now_add=True)

    def __str__(self):
        return str(self.search_id)


# company info
class CompanyInfo(models.Model):
    company_id = models.AutoField(primary_key=True)
    company_name = models.CharField(max_length=40)
    contact_person = models.CharField(max_length=40)
    contact_tel = models.CharField(max_length=8)
    contact_email = models.CharField(max_length=40)
    company_year = models.IntegerField
    company_detail = models.TextField
    company_status = models.BooleanField(default=False)
    company_remarks = models.TextField(null=True)
    url_logo = models.TextField(null=True)
    url_cert = models.TextField
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



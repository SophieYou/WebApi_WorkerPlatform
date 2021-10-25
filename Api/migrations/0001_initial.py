# Generated by Django 3.2.7 on 2021-09-14 07:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CompanyInfo',
            fields=[
                ('company_id', models.AutoField(primary_key=True, serialize=False)),
                ('company_name', models.CharField(max_length=40)),
                ('contact_person', models.CharField(max_length=40)),
                ('contact_tel', models.CharField(max_length=8)),
                ('contact_email', models.CharField(max_length=40)),
                ('company_year', models.IntegerField()),
                ('company_detail', models.TextField()),
                ('company_status', models.BooleanField(default=False)),
                ('company_remarks', models.TextField(null=True)),
                ('url_logo', models.TextField(null=True)),
                ('url_cert', models.TextField()),
                ('created_on', models.DateField(auto_now_add=True)),
                ('updated_on', models.DateField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='JobtypeDetail',
            fields=[
                ('jobtype_id', models.AutoField(primary_key=True, serialize=False)),
                ('jobtype_desc', models.CharField(max_length=10)),
                ('jobtype_upper', models.CharField(max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='NewsInfo',
            fields=[
                ('news_id', models.AutoField(primary_key=True, serialize=False)),
                ('news_title', models.CharField(max_length=20)),
                ('news_overview', models.CharField(max_length=40)),
                ('news_detail', models.TextField()),
                ('post_date', models.DateField(auto_now=True)),
                ('url_cover', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='RegionInfo',
            fields=[
                ('region_id', models.AutoField(primary_key=True, serialize=False)),
                ('region_desc', models.CharField(max_length=10)),
                ('region_upper', models.CharField(max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='SearchInfo',
            fields=[
                ('search_id', models.AutoField(primary_key=True, serialize=False)),
                ('contact_person', models.CharField(max_length=40)),
                ('contact_tel', models.CharField(max_length=8)),
                ('contact_email', models.CharField(max_length=40, null=True)),
                ('search_text', models.TextField()),
                ('search_status', models.BooleanField(default=False)),
                ('created_on', models.DateField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('user_id', models.AutoField(primary_key=True, serialize=False)),
                ('user_tel', models.CharField(max_length=8)),
                ('user_name', models.CharField(max_length=40, null=True)),
                ('user_year', models.IntegerField(null=True)),
                ('user_sex', models.CharField(max_length=1, null=True)),
                ('safecard_date', models.DateField(null=True)),
                ('regcard_date', models.DateField(null=True)),
                ('work_year', models.IntegerField(null=True)),
                ('lan_en', models.IntegerField(null=True)),
                ('lan_cantonese', models.IntegerField(null=True)),
                ('lan_mandarin', models.IntegerField(null=True)),
                ('user_pwd', models.CharField(max_length=8, null=True)),
                ('created_on', models.DateField(auto_now_add=True)),
                ('updated_on', models.DateField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='UserJobtype',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('updated_on', models.DateField(auto_now=True)),
                ('jobtype_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='jobtypedesc', to='Api.jobtypedetail')),
                ('user_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='jobtype', to='Api.userprofile')),
            ],
        ),
        migrations.CreateModel(
            name='TrainingInfo',
            fields=[
                ('training_id', models.AutoField(primary_key=True, serialize=False)),
                ('training_org', models.CharField(max_length=20)),
                ('from_date', models.DateField()),
                ('to_date', models.DateField()),
                ('training_tel', models.CharField(max_length=8)),
                ('updated_on', models.DateField(auto_now=True)),
                ('region_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Api.regioninfo')),
            ],
        ),
        migrations.CreateModel(
            name='JobInfo',
            fields=[
                ('job_id', models.AutoField(primary_key=True, serialize=False)),
                ('job_name', models.CharField(max_length=40)),
                ('vacancy_num', models.IntegerField(default=1)),
                ('job_duty', models.TextField()),
                ('job_request', models.TextField()),
                ('salary_type', models.CharField(default='M', max_length=1)),
                ('salary_upper', models.IntegerField()),
                ('salary_lower', models.IntegerField()),
                ('work_date', models.TextField(default='每週一至五，9:00-18:00')),
                ('created_on', models.DateField(auto_now_add=True)),
                ('updated_on', models.DateField(auto_now=True)),
                ('post_date', models.DateField(null=True)),
                ('end_date', models.DateField(null=True)),
                ('job_status', models.CharField(default='0', max_length=1)),
                ('pre_status', models.CharField(default='0', max_length=1)),
                ('job_benefit', models.TextField(default='無')),
                ('company_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Api.companyinfo')),
                ('jobtype_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Api.jobtypedetail')),
                ('region_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Api.regioninfo')),
            ],
        ),
    ]
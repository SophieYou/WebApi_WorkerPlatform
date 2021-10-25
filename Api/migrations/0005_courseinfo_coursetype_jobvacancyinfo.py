# Generated by Django 3.2.7 on 2021-09-20 09:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Api', '0004_alter_companyinfo_company_pwd'),
    ]

    operations = [
        migrations.CreateModel(
            name='CourseType',
            fields=[
                ('ctype_id', models.AutoField(primary_key=True, serialize=False)),
                ('ctype_desc', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='JobVacancyInfo',
            fields=[
                ('vacancy_id', models.AutoField(primary_key=True, serialize=False)),
                ('salary_type', models.CharField(default='M', max_length=1)),
                ('salary_upper', models.IntegerField()),
                ('salary_lower', models.IntegerField()),
                ('start_date', models.DateField()),
                ('created_on', models.DateField(auto_now_add=True)),
                ('updated_on', models.DateField(auto_now=True)),
                ('vacancy_status', models.CharField(default='0', max_length=1)),
                ('jobtype_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Api.jobtypedetail')),
                ('region_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Api.regioninfo')),
                ('user_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Api.userprofile')),
            ],
        ),
        migrations.CreateModel(
            name='CourseInfo',
            fields=[
                ('course_id', models.AutoField(primary_key=True, serialize=False)),
                ('course_title', models.CharField(max_length=40)),
                ('course_form', models.BooleanField(default=True)),
                ('course_period', models.CharField(max_length=100)),
                ('course_fee', models.IntegerField()),
                ('start_date', models.DateField()),
                ('course_req', models.TextField(null=True)),
                ('course_detail', models.TextField(null=True)),
                ('course_tel', models.CharField(max_length=8)),
                ('updated_on', models.DateField(auto_now=True)),
                ('course_link', models.TextField(null=True)),
                ('cytpe_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Api.coursetype')),
            ],
        ),
    ]

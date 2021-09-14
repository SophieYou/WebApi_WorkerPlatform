# Generated by Django 3.2.7 on 2021-09-08 06:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Api', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='JobtypeDetail',
            fields=[
                ('jobtype_id', models.AutoField(primary_key=True, serialize=False)),
                ('jobtype_desc', models.CharField(max_length=10)),
                ('jobtype_upper', models.CharField(max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='UserJobtype',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('updated_on', models.DateField(auto_now=True)),
                ('jobtype_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Api.jobtypedetail')),
                ('user_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Api.userprofile')),
            ],
        ),
    ]

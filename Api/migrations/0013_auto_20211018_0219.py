# Generated by Django 3.2.7 on 2021-10-18 02:19

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('Api', '0012_companyinfo_user_auth'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='companyinfo',
            name='company_pwd',
        ),
        migrations.AlterField(
            model_name='companyinfo',
            name='user_auth',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='auth.user'),
        ),
    ]

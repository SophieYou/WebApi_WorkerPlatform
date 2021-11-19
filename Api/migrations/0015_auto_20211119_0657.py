# Generated by Django 3.2.7 on 2021-11-19 06:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Api', '0014_alter_newsinfo_url_cover'),
    ]

    operations = [
        migrations.AlterField(
            model_name='companyinfo',
            name='url_cert',
            field=models.ImageField(null=True, upload_to='image/cert'),
        ),
        migrations.AlterField(
            model_name='companyinfo',
            name='url_logo',
            field=models.ImageField(null=True, upload_to='image/logo'),
        ),
        migrations.AlterField(
            model_name='newsinfo',
            name='url_cover',
            field=models.ImageField(null=True, upload_to='image/news'),
        ),
    ]

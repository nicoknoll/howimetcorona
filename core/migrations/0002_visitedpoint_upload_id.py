# Generated by Django 3.0.4 on 2020-03-21 17:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='visitedpoint',
            name='upload_id',
            field=models.CharField(max_length=36, null=True),
        ),
    ]

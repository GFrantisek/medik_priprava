# Generated by Django 4.2.10 on 2024-05-11 13:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('helloapp', '0005_userquestionanswers'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userquestionanswers',
            name='test',
        ),
        migrations.AddField(
            model_name='userquestionanswers',
            name='test_id',
            field=models.IntegerField(default=1),
        ),
    ]

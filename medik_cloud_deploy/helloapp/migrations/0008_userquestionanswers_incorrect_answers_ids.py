# Generated by Django 4.2.10 on 2024-05-11 21:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('helloapp', '0007_alter_userquestionanswers_test_id_testscores'),
    ]

    operations = [
        migrations.AddField(
            model_name='userquestionanswers',
            name='incorrect_answers_ids',
            field=models.JSONField(default=list),
        ),
    ]

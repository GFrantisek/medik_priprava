# Generated by Django 4.1.7 on 2024-04-21 09:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('helloapp', '0002_alter_medapplicant_table'),
    ]

    operations = [
        migrations.AddField(
            model_name='medapplicant',
            name='last_login',
            field=models.DateTimeField(blank=True, null=True, verbose_name='last login'),
        ),
    ]

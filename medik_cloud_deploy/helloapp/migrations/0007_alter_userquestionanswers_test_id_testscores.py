# Generated by Django 4.2.10 on 2024-05-11 18:28

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('helloapp', '0006_remove_userquestionanswers_test_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userquestionanswers',
            name='test_id',
            field=models.UUIDField(default=uuid.uuid4, editable=False),
        ),
        migrations.CreateModel(
            name='TestScores',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('test_id', models.UUIDField(default=uuid.uuid4, editable=False)),
                ('score', models.IntegerField()),
                ('max_score', models.IntegerField()),
                ('test_date', models.DateTimeField(auto_now_add=True)),
                ('duration', models.DurationField(blank=True, null=True)),
                ('user', models.ForeignKey(db_column='user_id', on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'test_scores',
                'indexes': [models.Index(fields=['user_id'], name='idx_test_scores_user_id')],
            },
        ),
    ]

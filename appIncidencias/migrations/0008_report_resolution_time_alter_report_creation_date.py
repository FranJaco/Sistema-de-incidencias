# Generated by Django 4.2.16 on 2024-12-04 15:28

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appIncidencias', '0007_alter_report_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='report',
            name='resolution_time',
            field=models.DurationField(blank=True, help_text='Duración que tomó resolver la incidencia', null=True),
        ),
        migrations.AlterField(
            model_name='report',
            name='creation_date',
            field=models.DateTimeField(default=datetime.datetime.now, editable=False),
        ),
    ]
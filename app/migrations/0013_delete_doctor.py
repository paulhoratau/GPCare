# Generated by Django 5.0.6 on 2024-06-21 10:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0012_rename_clinic_address_doctor_hospital'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Doctor',
        ),
    ]

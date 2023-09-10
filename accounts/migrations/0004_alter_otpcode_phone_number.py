# Generated by Django 4.2.5 on 2023-09-10 11:52

from django.db import migrations
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_alter_customuser_phone_number'),
    ]

    operations = [
        migrations.AlterField(
            model_name='otpcode',
            name='phone_number',
            field=phonenumber_field.modelfields.PhoneNumberField(max_length=128, region='IR', unique=True),
        ),
    ]

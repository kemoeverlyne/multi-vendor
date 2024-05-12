# Generated by Django 5.0.3 on 2024-04-08 09:08

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Vendor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.FileField(blank=True, default='vendor/default.jpg', null=True, upload_to='vendor/')),
                ('name', models.CharField(blank=True, help_text='Vendor name', max_length=100, null=True)),
                ('desctiption', models.TextField(blank=True, null=True)),
                ('mobile', models.CharField(blank=True, help_text='Mobile Number', max_length=100, null=True)),
                ('active', models.BooleanField(default=False)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('slug', models.SlugField(blank=True, max_length=500, null=True, unique=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Vendor',
                'verbose_name_plural': 'Vendors',
                'ordering': ['-date'],
            },
        ),
    ]

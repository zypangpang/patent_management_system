# Generated by Django 2.1.1 on 2018-09-11 07:31

from django.db import migrations, models
import main.models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_auto_20180911_1011'),
    ]

    operations = [
        migrations.CreateModel(
            name='file_test',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('file', models.FileField(upload_to=main.models.pdf_directory_path)),
            ],
        ),
    ]

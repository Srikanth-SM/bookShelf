# Generated by Django 2.1 on 2018-12-24 05:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('library', '0002_auto_20181220_0853'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='bookinstance',
            options={'ordering': ['due_back', 'status']},
        ),
    ]

# Generated by Django 5.0.6 on 2024-08-04 14:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0003_remove_chatsession_context_alter_chatsession_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='chatsession',
            name='context',
            field=models.TextField(blank=True, null=True),
        ),
    ]

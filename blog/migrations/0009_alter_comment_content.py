# Generated by Django 4.2.13 on 2024-07-29 22:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0008_rename_commentpost_comment_alter_comment_options'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='content',
            field=models.TextField(max_length=240),
        ),
    ]

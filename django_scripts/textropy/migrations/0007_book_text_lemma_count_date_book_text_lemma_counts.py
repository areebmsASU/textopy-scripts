# Generated by Django 5.0.2 on 2024-02-09 06:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('textropy', '0006_alter_lemma_text'),
    ]

    operations = [
        migrations.AddField(
            model_name='book',
            name='text_lemma_count_date',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='book',
            name='text_lemma_counts',
            field=models.JSONField(null=True),
        ),
    ]
# Generated by Django 5.0.2 on 2024-02-08 19:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('textropy', '0005_alter_lemma_text_alter_word_text'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lemma',
            name='text',
            field=models.TextField(db_index=True, unique=True),
        ),
    ]

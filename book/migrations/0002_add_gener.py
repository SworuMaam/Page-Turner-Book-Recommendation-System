# 0002_add_genre_field.py

from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('book', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='book',
            name='genre',
            field=models.CharField(max_length=100, default=''),
        ),
    ]

# Generated by Django 3.1 on 2020-08-23 17:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0004_listing_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='listing',
            name='comments',
            field=models.ManyToManyField(blank=True, related_name='comments', to='auctions.Comment'),
        ),
    ]

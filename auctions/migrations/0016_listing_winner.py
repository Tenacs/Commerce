# Generated by Django 4.2.7 on 2024-01-17 22:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("auctions", "0015_remove_user_watchlist_user_watchlist"),
    ]

    operations = [
        migrations.AddField(
            model_name="listing",
            name="winner",
            field=models.CharField(default=None, max_length=50),
        ),
    ]

# Generated manually to align timestamp fields with the model state.

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("people", "0003_campaign_expansion"),
    ]

    operations = [
        migrations.AlterField(
            model_name="person",
            name="created_at",
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name="person",
            name="updated_at",
            field=models.DateTimeField(auto_now=True),
        ),
    ]

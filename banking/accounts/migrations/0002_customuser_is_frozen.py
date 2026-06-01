from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="customuser",
            name="is_frozen",
            field=models.BooleanField(
                default=False,
                db_index=True,
                verbose_name="Frozen",
            ),
        ),
    ]


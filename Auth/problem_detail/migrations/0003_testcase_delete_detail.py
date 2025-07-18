# Generated by Django 4.2.22 on 2025-06-30 11:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("dashboard", "0002_topic_title_alter_userquestionstatus_unique_together"),
        ("problem_detail", "0002_detail_title"),
    ]

    operations = [
        migrations.CreateModel(
            name="TestCase",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("input_file", models.FileField(upload_to="testcases/inputs/")),
                ("output_file", models.FileField(upload_to="testcases/outputs/")),
                ("is_visible", models.BooleanField(default=True)),
                (
                    "question",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="dashboard.question",
                    ),
                ),
            ],
        ),
        migrations.DeleteModel(
            name="Detail",
        ),
    ]

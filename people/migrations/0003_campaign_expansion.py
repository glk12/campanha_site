# Generated manually for campaign expansion.

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models
from django.utils import timezone


def _build_valid_cpf(seed):
    numbers = f"{seed:09d}"[-9:]

    def calculate_digit(base):
        total = sum(int(number) * weight for number, weight in base)
        digit = ((total * 10) % 11) % 10
        return str(digit)

    first_base = zip(numbers, range(10, 1, -1))
    first_digit = calculate_digit(first_base)
    second_base = zip(numbers + first_digit, range(11, 1, -1))
    second_digit = calculate_digit(second_base)
    return numbers + first_digit + second_digit


def populate_existing_people(apps, schema_editor):
    Person = apps.get_model("people", "Person")

    for person in Person.objects.filter(cpf__isnull=True).order_by("pk"):
        person.cpf = _build_valid_cpf(person.pk or 0)
        person.voting_city = ""
        person.electoral_zone = ""
        person.electoral_section = ""
        person.voter_status = "pending"
        person.validation_source = "pending"
        person.data_consent = False
        person.save(
            update_fields=[
                "cpf",
                "voting_city",
                "electoral_zone",
                "electoral_section",
                "voter_status",
                "validation_source",
                "data_consent",
            ]
        )


class Migration(migrations.Migration):

    dependencies = [
        ("people", "0002_userprofile"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="person",
            name="cpf",
            field=models.CharField(blank=True, max_length=11, null=True),
        ),
        migrations.AddField(
            model_name="person",
            name="created_at",
            field=models.DateTimeField(default=timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="person",
            name="created_by",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="created_people",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="person",
            name="data_consent",
            field=models.BooleanField(
                default=False,
                help_text="Confirma que o eleitor autorizou a coleta do CPF e dos dados eleitorais.",
            ),
        ),
        migrations.AddField(
            model_name="person",
            name="electoral_section",
            field=models.CharField(blank=True, max_length=20),
        ),
        migrations.AddField(
            model_name="person",
            name="electoral_zone",
            field=models.CharField(blank=True, max_length=20),
        ),
        migrations.AddField(
            model_name="person",
            name="updated_at",
            field=models.DateTimeField(default=timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="person",
            name="validation_source",
            field=models.CharField(
                choices=[
                    ("pending", "Pendente"),
                    ("simulated", "Simulada"),
                    ("manual", "Manual"),
                ],
                default="pending",
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name="person",
            name="voter_status",
            field=models.CharField(
                choices=[
                    ("pending", "Pendente"),
                    ("apto", "Apto"),
                    ("not_apto", "Nao apto"),
                ],
                default="pending",
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name="person",
            name="voting_city",
            field=models.CharField(blank=True, max_length=150),
        ),
        migrations.CreateModel(
            name="ElectionHistory",
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
                ("election_year", models.PositiveIntegerField()),
                ("municipality", models.CharField(max_length=150)),
                ("electoral_zone", models.CharField(max_length=20)),
                ("electoral_section", models.CharField(max_length=20)),
                ("votes_received", models.PositiveIntegerField()),
                ("notes", models.CharField(blank=True, max_length=255)),
            ],
            options={
                "verbose_name": "Historico eleitoral",
                "verbose_name_plural": "Historicos eleitorais",
                "ordering": [
                    "-election_year",
                    "municipality",
                    "electoral_zone",
                    "electoral_section",
                ],
            },
        ),
        migrations.RunPython(populate_existing_people, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="person",
            name="cpf",
            field=models.CharField(max_length=11, unique=True),
        ),
    ]

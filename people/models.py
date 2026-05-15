from django.contrib.auth.models import User
from django.db import models


class Person(models.Model):
    class VoterStatus(models.TextChoices):
        PENDING = "pending", "Pendente"
        APTO = "apto", "Apto"
        NOT_APTO = "not_apto", "Nao apto"

    class ValidationSource(models.TextChoices):
        PENDING = "pending", "Pendente"
        SIMULATED = "simulated", "Simulada"
        MANUAL = "manual", "Manual"

    full_name = models.CharField(max_length=150)
    cpf = models.CharField(max_length=11, unique=True)
    phone = models.CharField(max_length=20, blank=True)
    local = models.CharField(max_length=150)
    voting_city = models.CharField(max_length=150, blank=True)
    electoral_zone = models.CharField(max_length=20, blank=True)
    electoral_section = models.CharField(max_length=20, blank=True)
    voter_status = models.CharField(
        max_length=20,
        choices=VoterStatus.choices,
        default=VoterStatus.PENDING,
    )
    validation_source = models.CharField(
        max_length=20,
        choices=ValidationSource.choices,
        default=ValidationSource.PENDING,
    )
    data_consent = models.BooleanField(
        default=False,
        help_text="Confirma que o eleitor autorizou a coleta do CPF e dos dados eleitorais.",
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_people",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    parent = models.ForeignKey(
        "self", on_delete=models.SET_NULL, null=True, blank=True, related_name="children"
    )

    def get_hierarchy_ids(self):
        pending_ids = [self.pk]
        visible_ids = set()

        while pending_ids:
            current_id = pending_ids.pop()
            if current_id in visible_ids:
                continue

            visible_ids.add(current_id)
            child_ids = Person.objects.filter(parent_id=current_id).values_list(
                "pk", flat=True
            )
            pending_ids.extend(child_ids)

        return visible_ids

    def __str__(self):
        return self.full_name


class ElectionHistory(models.Model):
    election_year = models.PositiveIntegerField()
    municipality = models.CharField(max_length=150)
    electoral_zone = models.CharField(max_length=20)
    electoral_section = models.CharField(max_length=20)
    votes_received = models.PositiveIntegerField()
    notes = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["-election_year", "municipality", "electoral_zone", "electoral_section"]
        verbose_name = "Historico eleitoral"
        verbose_name_plural = "Historicos eleitorais"

    def __str__(self):
        return (
            f"{self.municipality} - Zona {self.electoral_zone} / "
            f"Secao {self.electoral_section} ({self.election_year})"
        )


class UserProfile(models.Model):
    class AccessLevel(models.TextChoices):
        ADMIN = "admin", "Administrador"
        MANAGER = "manager", "Gerente de equipe"
        AGENT = "agent", "Agente de cadastro"

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    access_level = models.CharField(
        max_length=20,
        choices=AccessLevel.choices,
        default=AccessLevel.AGENT,
    )
    person = models.ForeignKey(
        Person,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="user_profiles",
        help_text="Pessoa vinculada ao usuário quando o acesso depender da hierarquia.",
    )

    def is_admin(self):
        return self.user.is_superuser or self.access_level == self.AccessLevel.ADMIN

    def can_manage_people(self):
        return self.is_admin() or self.access_level == self.AccessLevel.MANAGER

    def can_create_people(self):
        return self.is_admin() or self.access_level in {
            self.AccessLevel.MANAGER,
            self.AccessLevel.AGENT,
        }

    def can_view_reports(self):
        return self.is_admin() or self.access_level == self.AccessLevel.MANAGER

    def get_visible_people_queryset(self):
        if self.is_admin():
            return Person.objects.all()

        if self.access_level == self.AccessLevel.MANAGER and self.person_id:
            visible_ids = self.person.get_hierarchy_ids()
            return Person.objects.filter(pk__in=visible_ids)

        return Person.objects.none()

    def __str__(self):
        return f"{self.user.username} ({self.get_access_level_display()})"

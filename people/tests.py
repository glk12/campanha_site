from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import ElectionHistory, Person, UserProfile


class BasePeopleTestCase(TestCase):
    def setUp(self):
        self.root_manager = Person.objects.create(
            full_name="Gerente Principal",
            cpf="52998224725",
            phone="1111-1111",
            local="Centro",
            voting_city="Recife",
            electoral_zone="101",
            electoral_section="201",
            voter_status=Person.VoterStatus.APTO,
            validation_source=Person.ValidationSource.SIMULATED,
            data_consent=True,
        )
        self.intermediate = Person.objects.create(
            full_name="Articulador de Bairro",
            cpf="11144477735",
            phone="2222-2222",
            local="Zona Norte",
            voting_city="Recife",
            electoral_zone="101",
            electoral_section="202",
            voter_status=Person.VoterStatus.APTO,
            validation_source=Person.ValidationSource.MANUAL,
            data_consent=True,
            parent=self.root_manager,
        )
        self.visible_person = Person.objects.create(
            full_name="Pessoa da Base",
            cpf="12345678909",
            phone="9999-9999",
            local="Zona Norte",
            voting_city="Recife",
            electoral_zone="102",
            electoral_section="301",
            voter_status=Person.VoterStatus.PENDING,
            validation_source=Person.ValidationSource.PENDING,
            data_consent=True,
            parent=self.intermediate,
        )
        self.other_manager = Person.objects.create(
            full_name="Gerente Externo",
            cpf="98765432100",
            phone="3333-3333",
            local="Zona Sul",
            voting_city="Olinda",
            electoral_zone="110",
            electoral_section="401",
            voter_status=Person.VoterStatus.APTO,
            validation_source=Person.ValidationSource.SIMULATED,
            data_consent=True,
        )
        self.other_person = Person.objects.create(
            full_name="Pessoa de Outra Base",
            cpf="71460238001",
            phone="4444-4444",
            local="Zona Sul",
            voting_city="Olinda",
            electoral_zone="111",
            electoral_section="402",
            voter_status=Person.VoterStatus.NOT_APTO,
            validation_source=Person.ValidationSource.MANUAL,
            data_consent=True,
            parent=self.other_manager,
        )
        ElectionHistory.objects.create(
            election_year=2024,
            municipality="Recife",
            electoral_zone="101",
            electoral_section="201",
            votes_received=320,
        )

    def create_user_with_profile(
        self, username, access_level, person=None, is_superuser=False, is_staff=False
    ):
        user = User.objects.create_user(
            username=username,
            password="senha-forte-123",
            is_superuser=is_superuser,
            is_staff=is_staff or is_superuser,
        )
        profile = UserProfile.objects.create(
            user=user,
            access_level=access_level,
            person=person,
        )
        return user, profile


class PersonCrudTests(BasePeopleTestCase):
    def setUp(self):
        super().setUp()
        self.admin_user, _ = self.create_user_with_profile(
            "admin",
            UserProfile.AccessLevel.ADMIN,
            is_staff=True,
        )
        self.client.force_login(self.admin_user)

    def test_list_people(self):
        response = self.client.get(reverse("person_list"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Pessoa da Base")
        self.assertContains(response, "Pessoa de Outra Base")
        self.assertContains(response, "CPF 12345678909")

    def test_create_person_runs_simulated_validation(self):
        payload = {
            "full_name": "Nova Pessoa",
            "cpf": "39053344705",
            "phone": "8888-8888",
            "local": "Zona Oeste",
            "voting_city": "",
            "electoral_zone": "",
            "electoral_section": "",
            "voter_status": Person.VoterStatus.PENDING,
            "data_consent": "on",
            "run_validation": "on",
            "parent": self.root_manager.pk,
        }

        response = self.client.post(reverse("person_create"), payload)

        self.assertEqual(response.status_code, 302)
        person = Person.objects.get(full_name="Nova Pessoa")
        self.assertEqual(person.created_by, self.admin_user)
        self.assertEqual(person.validation_source, Person.ValidationSource.SIMULATED)
        self.assertTrue(person.electoral_zone)
        self.assertTrue(person.electoral_section)

    def test_create_person_requires_consent_for_cpf(self):
        payload = {
            "full_name": "Sem Consentimento",
            "cpf": "39053344705",
            "phone": "8888-8888",
            "local": "Zona Oeste",
            "voter_status": Person.VoterStatus.PENDING,
            "parent": self.root_manager.pk,
        }

        response = self.client.post(reverse("person_create"), payload)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "consentimento")
        self.assertFalse(Person.objects.filter(full_name="Sem Consentimento").exists())

    def test_update_person(self):
        payload = {
            "full_name": "Pessoa Atualizada",
            "cpf": self.visible_person.cpf,
            "phone": "7777-7777",
            "local": "Zona Oeste",
            "voting_city": "Recife",
            "electoral_zone": "115",
            "electoral_section": "333",
            "voter_status": Person.VoterStatus.APTO,
            "data_consent": "on",
            "parent": "",
        }

        response = self.client.post(
            reverse("person_update", args=[self.visible_person.pk]),
            payload,
        )

        self.assertEqual(response.status_code, 302)
        self.visible_person.refresh_from_db()
        self.assertEqual(self.visible_person.full_name, "Pessoa Atualizada")
        self.assertEqual(self.visible_person.local, "Zona Oeste")
        self.assertIsNone(self.visible_person.parent)
        self.assertEqual(self.visible_person.validation_source, Person.ValidationSource.MANUAL)

    def test_delete_person(self):
        response = self.client.post(reverse("person_delete", args=[self.visible_person.pk]))

        self.assertEqual(response.status_code, 302)
        self.assertFalse(Person.objects.filter(pk=self.visible_person.pk).exists())

    def test_person_cannot_be_its_own_parent(self):
        payload = {
            "full_name": self.visible_person.full_name,
            "cpf": self.visible_person.cpf,
            "phone": self.visible_person.phone,
            "local": self.visible_person.local,
            "voting_city": self.visible_person.voting_city,
            "electoral_zone": self.visible_person.electoral_zone,
            "electoral_section": self.visible_person.electoral_section,
            "voter_status": self.visible_person.voter_status,
            "data_consent": "on",
            "parent": self.visible_person.pk,
        }

        response = self.client.post(
            reverse("person_update", args=[self.visible_person.pk]),
            payload,
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("parent", response.context["form"].errors)

    def test_report_page_displays_dashboard_metrics(self):
        response = self.client.get(reverse("person_report"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["summary_total"], 5)
        self.assertEqual(response.context["summary_apto"], 3)
        self.assertEqual(response.context["summary_not_apto"], 1)
        self.assertEqual(response.context["summary_pending"], 1)
        self.assertTrue(response.context["history_cards"])


class AccessControlTests(BasePeopleTestCase):
    def test_manager_sees_only_own_hierarchy(self):
        manager_user, _ = self.create_user_with_profile(
            "gerente",
            UserProfile.AccessLevel.MANAGER,
            person=self.root_manager,
        )
        self.client.force_login(manager_user)

        response = self.client.get(reverse("person_list"))

        self.assertEqual(response.status_code, 200)
        people = list(response.context["people"])
        self.assertEqual(
            {person.pk for person in people},
            {self.root_manager.pk, self.intermediate.pk, self.visible_person.pk},
        )

    def test_manager_does_not_see_other_manager_base(self):
        manager_user, _ = self.create_user_with_profile(
            "gerente",
            UserProfile.AccessLevel.MANAGER,
            person=self.root_manager,
        )
        self.client.force_login(manager_user)

        response = self.client.get(reverse("person_report"))

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Pessoa de Outra Base")
        self.assertEqual(response.context["summary_total"], 3)

    def test_hierarchy_counts_for_top_manager_even_with_intermediate_person(self):
        manager_user, _ = self.create_user_with_profile(
            "gerente",
            UserProfile.AccessLevel.MANAGER,
            person=self.root_manager,
        )
        self.client.force_login(manager_user)

        response = self.client.get(reverse("person_report"))

        self.assertContains(response, "Articulador de Bairro")
        self.assertContains(response, "Pessoa da Base")

    def test_agent_can_create_person(self):
        agent_person = Person.objects.create(
            full_name="Agente Vinculado",
            cpf="15350946056",
            phone="5555-5555",
            local="Centro",
            voting_city="Recife",
            electoral_zone="120",
            electoral_section="250",
            voter_status=Person.VoterStatus.APTO,
            validation_source=Person.ValidationSource.MANUAL,
            data_consent=True,
            parent=self.root_manager,
        )
        agent_user, _ = self.create_user_with_profile(
            "agente",
            UserProfile.AccessLevel.AGENT,
            person=agent_person,
        )
        self.client.force_login(agent_user)

        response = self.client.post(
            reverse("person_create"),
            {
                "full_name": "Novo Apoiador",
                "cpf": "39053344705",
                "phone": "6666-6666",
                "local": "Centro",
                "voting_city": "",
                "electoral_zone": "",
                "electoral_section": "",
                "voter_status": Person.VoterStatus.PENDING,
                "data_consent": "on",
                "run_validation": "on",
                "parent": agent_person.pk,
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(Person.objects.filter(full_name="Novo Apoiador").exists())

    def test_agent_cannot_access_list_or_report(self):
        agent_user, _ = self.create_user_with_profile(
            "agente",
            UserProfile.AccessLevel.AGENT,
        )
        self.client.force_login(agent_user)

        list_response = self.client.get(reverse("person_list"))
        report_response = self.client.get(reverse("person_report"))

        self.assertEqual(list_response.status_code, 403)
        self.assertEqual(report_response.status_code, 403)

    def test_manager_cannot_edit_person_from_another_base(self):
        manager_user, _ = self.create_user_with_profile(
            "gerente",
            UserProfile.AccessLevel.MANAGER,
            person=self.root_manager,
        )
        self.client.force_login(manager_user)

        response = self.client.get(reverse("person_update", args=[self.other_person.pk]))

        self.assertEqual(response.status_code, 404)

    def test_login_is_required(self):
        response = self.client.get(reverse("person_list"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response.url)

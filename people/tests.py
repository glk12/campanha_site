from django.test import TestCase
from django.urls import reverse

from .models import Person


class PersonCrudTests(TestCase):
	def setUp(self):
		self.parent = Person.objects.create(
			full_name="Responsavel", phone="1111-1111", local="Centro"
		)
		self.person = Person.objects.create(
			full_name="Pessoa Teste",
			phone="9999-9999",
			local="Zona Norte",
			parent=self.parent,
		)

	def test_list_people(self):
		response = self.client.get(reverse("person_list"))

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "Pessoa Teste")

	def test_create_person(self):
		payload = {
			"full_name": "Nova Pessoa",
			"phone": "8888-8888",
			"local": "Zona Sul",
			"parent": self.parent.pk,
		}

		response = self.client.post(reverse("person_create"), payload)

		self.assertEqual(response.status_code, 302)
		self.assertTrue(Person.objects.filter(full_name="Nova Pessoa").exists())

	def test_update_person(self):
		payload = {
			"full_name": "Pessoa Atualizada",
			"phone": "7777-7777",
			"local": "Zona Oeste",
			"parent": "",
		}

		response = self.client.post(
			reverse("person_update", args=[self.person.pk]), payload
		)

		self.assertEqual(response.status_code, 302)
		self.person.refresh_from_db()
		self.assertEqual(self.person.full_name, "Pessoa Atualizada")
		self.assertEqual(self.person.local, "Zona Oeste")
		self.assertIsNone(self.person.parent)

	def test_delete_person(self):
		response = self.client.post(reverse("person_delete", args=[self.person.pk]))

		self.assertEqual(response.status_code, 302)
		self.assertFalse(Person.objects.filter(pk=self.person.pk).exists())

	def test_person_cannot_be_its_own_parent(self):
		payload = {
			"full_name": self.person.full_name,
			"phone": self.person.phone,
			"local": self.person.local,
			"parent": self.person.pk,
		}

		response = self.client.post(
			reverse("person_update", args=[self.person.pk]), payload
		)

		self.assertEqual(response.status_code, 200)
		form = response.context["form"]
		self.assertIn("parent", form.errors)

from django import forms
from .models import Person


class PersonForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # On edition, exclude the current instance from parent choices.
        if self.instance and self.instance.pk:
            self.fields["parent"].queryset = Person.objects.exclude(pk=self.instance.pk)

    class Meta:
        model = Person
        fields = ["full_name", "phone", "local", "parent"]

        widgets = {
            "full_name": forms.TextInput(attrs={
                "class": "bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 block w-full p-2.5",
                "placeholder": "Digite o nome completo",
            }),
            "phone": forms.TextInput(attrs={
                "class": "bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 block w-full p-2.5",
                "placeholder": "Digite o telefone",
            }),
            "local": forms.TextInput(attrs={
                "class": "bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 block w-full p-2.5",
                "placeholder": "Digite o local",
            }),
            "parent": forms.Select(attrs={
                "class": "bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 block w-full p-2.5",
            }),
        }

    def clean_parent(self):
        parent = self.cleaned_data.get("parent")

        if self.instance and self.instance.pk and parent and parent.pk == self.instance.pk:
            raise forms.ValidationError("Uma pessoa não pode ser o próprio responsável.")

        return parent

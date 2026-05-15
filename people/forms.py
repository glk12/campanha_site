from django import forms

from .models import Person
from .services import digits_only, is_valid_cpf, simulate_electoral_validation


INPUT_CLASS = (
    "w-full rounded-2xl border border-slate-200 bg-white/80 px-4 py-3 text-sm "
    "text-slate-900 shadow-sm outline-none transition focus:border-emerald-500 "
    "focus:ring-4 focus:ring-emerald-100"
)


class PersonForm(forms.ModelForm):
    run_validation = forms.BooleanField(
        required=False,
        initial=True,
        label="Executar validacao eleitoral simulada ao salvar",
    )

    def __init__(self, *args, **kwargs):
        allowed_parent_queryset = kwargs.pop("allowed_parent_queryset", None)
        super().__init__(*args, **kwargs)

        if allowed_parent_queryset is not None:
            self.fields["parent"].queryset = allowed_parent_queryset.order_by("full_name")

        if self.instance and self.instance.pk:
            self.fields["parent"].queryset = Person.objects.exclude(pk=self.instance.pk)
            if allowed_parent_queryset is not None:
                self.fields["parent"].queryset = allowed_parent_queryset.exclude(
                    pk=self.instance.pk
                ).order_by("full_name")

    class Meta:
        model = Person
        fields = [
            "full_name",
            "cpf",
            "phone",
            "local",
            "voting_city",
            "electoral_zone",
            "electoral_section",
            "voter_status",
            "data_consent",
            "parent",
        ]
        widgets = {
            "full_name": forms.TextInput(
                attrs={"class": INPUT_CLASS, "placeholder": "Nome completo do apoiador"}
            ),
            "cpf": forms.TextInput(
                attrs={"class": INPUT_CLASS, "placeholder": "Somente numeros do CPF"}
            ),
            "phone": forms.TextInput(
                attrs={"class": INPUT_CLASS, "placeholder": "Telefone ou WhatsApp"}
            ),
            "local": forms.TextInput(
                attrs={"class": INPUT_CLASS, "placeholder": "Bairro, comunidade ou local"}
            ),
            "voting_city": forms.TextInput(
                attrs={"class": INPUT_CLASS, "placeholder": "Municipio de votacao"}
            ),
            "electoral_zone": forms.TextInput(
                attrs={"class": INPUT_CLASS, "placeholder": "Zona eleitoral"}
            ),
            "electoral_section": forms.TextInput(
                attrs={"class": INPUT_CLASS, "placeholder": "Secao eleitoral"}
            ),
            "voter_status": forms.Select(attrs={"class": INPUT_CLASS}),
            "parent": forms.Select(attrs={"class": INPUT_CLASS}),
            "data_consent": forms.CheckboxInput(
                attrs={
                    "class": "h-4 w-4 rounded border-slate-300 text-emerald-600 focus:ring-emerald-500"
                }
            ),
        }

    def clean_cpf(self):
        cpf = digits_only(self.cleaned_data.get("cpf"))
        if not is_valid_cpf(cpf):
            raise forms.ValidationError("Informe um CPF valido.")
        return cpf

    def clean_parent(self):
        parent = self.cleaned_data.get("parent")

        if self.instance and self.instance.pk and parent and parent.pk == self.instance.pk:
            raise forms.ValidationError("Uma pessoa nao pode ser o proprio responsavel.")

        return parent

    def clean(self):
        cleaned_data = super().clean()
        cpf = cleaned_data.get("cpf")
        data_consent = cleaned_data.get("data_consent")
        run_validation = cleaned_data.get("run_validation")
        voting_city = cleaned_data.get("voting_city")
        electoral_zone = cleaned_data.get("electoral_zone")
        electoral_section = cleaned_data.get("electoral_section")

        if cpf and not data_consent:
            self.add_error(
                "data_consent",
                "O consentimento e obrigatorio para armazenar CPF e dados eleitorais.",
            )

        if not run_validation and cleaned_data.get("voter_status") != Person.VoterStatus.PENDING:
            if not voting_city:
                self.add_error(
                    "voting_city",
                    "Informe o municipio quando a validacao automatica nao for usada.",
                )
            if not electoral_zone:
                self.add_error(
                    "electoral_zone",
                    "Informe a zona eleitoral quando a validacao automatica nao for usada.",
                )
            if not electoral_section:
                self.add_error(
                    "electoral_section",
                    "Informe a secao eleitoral quando a validacao automatica nao for usada.",
                )

        return cleaned_data

    def save(self, commit=True):
        person = super().save(commit=False)

        if self.cleaned_data.get("run_validation"):
            validation_data = simulate_electoral_validation(
                self.cleaned_data["cpf"],
                self.cleaned_data.get("voting_city") or self.cleaned_data.get("local"),
            )
            person.voter_status = validation_data["voter_status"]
            person.electoral_zone = validation_data["electoral_zone"]
            person.electoral_section = validation_data["electoral_section"]
            person.voting_city = validation_data["voting_city"]
            person.validation_source = validation_data["validation_source"]
        else:
            person.validation_source = Person.ValidationSource.MANUAL

        if commit:
            person.save()
            self.save_m2m()

        return person

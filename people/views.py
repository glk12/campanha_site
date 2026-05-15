import unicodedata
from datetime import timedelta

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Count, Q, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.templatetags.static import static
from django.utils import timezone

from .forms import PersonForm
from .models import ElectionHistory, Person, UserProfile


def normalize_zone(value):
    """Normaliza um numero de zona para casar GeoJSON com Person.

    "007" e "7" passam a ser a mesma chave; vazio vira "".
    """
    text = str(value or "").strip()
    return text.lstrip("0") or ("0" if text else "")


def municipality_slug(name):
    text = unicodedata.normalize("NFKD", str(name or ""))
    text = text.encode("ascii", "ignore").decode("ascii").lower()
    return "".join(char if char.isalnum() else "_" for char in text).strip("_")


def _build_map_points(queryset):
    points = []
    for person in queryset.exclude(latitude__isnull=True).exclude(
        longitude__isnull=True
    ):
        points.append(
            {
                "name": person.full_name,
                "lat": float(person.latitude),
                "lng": float(person.longitude),
                "zone": person.electoral_zone,
                "section": person.electoral_section,
                "status": person.get_voter_status_display(),
            }
        )
    return points


def _zone_intensity_map(zone_cards):
    return {
        normalize_zone(zone["electoral_zone"]): zone["intensity"]
        for zone in zone_cards
        if zone["electoral_zone"]
    }


def get_user_profile(user):
    if not user.is_authenticated:
        return None

    profile = getattr(user, "profile", None)
    if profile:
        return profile

    if user.is_superuser:
        return UserProfile(user=user, access_level=UserProfile.AccessLevel.ADMIN)

    return UserProfile(user=user, access_level=UserProfile.AccessLevel.AGENT)


def get_visible_people_queryset(user):
    profile = get_user_profile(user)
    if not profile:
        return Person.objects.none()

    return profile.get_visible_people_queryset()


def get_allowed_parent_queryset(user):
    profile = get_user_profile(user)
    if not profile:
        return Person.objects.none()

    if profile.is_admin():
        return Person.objects.all()

    if profile.access_level == UserProfile.AccessLevel.MANAGER:
        return profile.get_visible_people_queryset()

    if profile.access_level == UserProfile.AccessLevel.AGENT and profile.person_id:
        return Person.objects.filter(pk__in=profile.person.get_hierarchy_ids())

    return Person.objects.none()


def require_people_management(user):
    profile = get_user_profile(user)
    if not profile or not profile.can_manage_people():
        raise PermissionDenied("Seu perfil nao pode gerenciar esta base.")

    return profile


def require_people_creation(user):
    profile = get_user_profile(user)
    if not profile or not profile.can_create_people():
        raise PermissionDenied("Seu perfil nao pode cadastrar pessoas.")

    return profile


def require_report_access(user):
    profile = get_user_profile(user)
    if not profile or not profile.can_view_reports():
        raise PermissionDenied("Seu perfil nao pode acessar relatorios.")

    return profile


def get_common_context(profile):
    return {
        "profile": profile,
        "can_manage_people": profile.can_manage_people() if profile else False,
        "can_create_people": profile.can_create_people() if profile else False,
        "can_view_reports": profile.can_view_reports() if profile else False,
    }


def apply_people_filters(queryset, request):
    search = request.GET.get("q", "").strip()
    status = request.GET.get("status", "").strip()
    zone = request.GET.get("zona", "").strip()
    responsible_filter = request.GET.get("responsavel", "").strip()

    if search:
        queryset = queryset.filter(
            Q(full_name__icontains=search)
            | Q(cpf__icontains=search)
            | Q(phone__icontains=search)
            | Q(local__icontains=search)
            | Q(voting_city__icontains=search)
        )

    if status:
        queryset = queryset.filter(voter_status=status)

    if zone:
        queryset = queryset.filter(electoral_zone=zone)

    current_filter_label = "Todos"
    if responsible_filter == "none":
        queryset = queryset.filter(parent__isnull=True)
        current_filter_label = "Sem responsavel"
    elif responsible_filter.isdigit():
        selected_responsible = queryset.filter(pk=responsible_filter).first()
        if selected_responsible:
            queryset = queryset.filter(parent=selected_responsible)
            current_filter_label = selected_responsible.full_name

    return queryset, {
        "q": search,
        "status": status,
        "zona": zone,
        "responsavel": responsible_filter,
        "current_filter_label": current_filter_label,
    }


def build_dashboard_context(base_people, filtered_people, profile):
    week_ago = timezone.now() - timedelta(days=7)
    people_with_data = base_people.exclude(
        Q(electoral_zone="") | Q(electoral_section="") | Q(voting_city="")
    )
    zones = list(
        people_with_data.values("electoral_zone")
        .annotate(
            total=Count("id"),
            growth_week=Count("id", filter=Q(created_at__gte=week_ago)),
        )
        .order_by("-total", "electoral_zone")
    )
    sections = list(
        people_with_data.values("electoral_zone", "electoral_section")
        .annotate(total=Count("id"))
        .order_by("-total", "electoral_zone", "electoral_section")[:8]
    )
    cities = list(
        people_with_data.values("voting_city")
        .annotate(total=Count("id"))
        .order_by("-total", "voting_city")[:6]
    )
    histories = list(
        ElectionHistory.objects.values(
            "election_year", "municipality", "electoral_zone", "electoral_section"
        )
        .annotate(votes_received=Sum("votes_received"))
        .order_by("-election_year", "municipality", "electoral_zone", "electoral_section")[:10]
    )

    max_zone_total = max((zone["total"] for zone in zones), default=1)
    max_section_total = max((section["total"] for section in sections), default=1)
    max_city_total = max((city["total"] for city in cities), default=1)
    max_history_votes = max((history["votes_received"] for history in histories), default=1)

    for zone in zones:
        zone["intensity"] = max(20, int((zone["total"] / max_zone_total) * 100))
    for section in sections:
        section["intensity"] = max(20, int((section["total"] / max_section_total) * 100))
    for city in cities:
        city["intensity"] = max(20, int((city["total"] / max_city_total) * 100))
    for history in histories:
        history["intensity"] = max(20, int((history["votes_received"] / max_history_votes) * 100))

    return {
        "summary_total": base_people.count(),
        "summary_filtered_total": filtered_people.count(),
        "summary_apto": base_people.filter(voter_status=Person.VoterStatus.APTO).count(),
        "summary_not_apto": base_people.filter(
            voter_status=Person.VoterStatus.NOT_APTO
        ).count(),
        "summary_pending": base_people.filter(
            voter_status=Person.VoterStatus.PENDING
        ).count(),
        "summary_without_responsible": base_people.filter(parent__isnull=True).count(),
        "summary_growth_week": base_people.filter(created_at__gte=week_ago).count(),
        "summary_with_consent": base_people.filter(data_consent=True).count(),
        "summary_validated": base_people.exclude(
            validation_source=Person.ValidationSource.PENDING
        ).count(),
        "zone_cards": zones,
        "section_cards": sections,
        "city_cards": cities,
        "history_cards": histories,
        "responsible_options": (
            base_people.annotate(total_records=Count("children"))
            .filter(total_records__gt=0)
            .order_by("full_name")
        ),
        "profile": profile,
    }


@login_required
def home_page(request):
    return redirect("index")


@login_required
def index(request):
    profile = get_user_profile(request.user)
    people_scope = get_visible_people_queryset(request.user)
    context = get_common_context(profile)
    context.update(
        {
            "headline_total": people_scope.count() if profile.can_manage_people() else 0,
            "headline_validated": people_scope.exclude(
                validation_source=Person.ValidationSource.PENDING
            ).count()
            if profile.can_manage_people()
            else 0,
            "headline_apto": people_scope.filter(voter_status=Person.VoterStatus.APTO).count()
            if profile.can_manage_people()
            else 0,
            "headline_consent": people_scope.filter(data_consent=True).count()
            if profile.can_manage_people()
            else 0,
        }
    )
    return render(request, "people/index.html", context)


@login_required
def person_list(request):
    profile = require_people_management(request.user)
    base_people = get_visible_people_queryset(request.user).select_related(
        "parent", "created_by"
    )
    people, filter_data = apply_people_filters(base_people, request)
    context = get_common_context(profile)
    context.update(
        {
            "people": people.order_by("full_name"),
            "status_options": Person.VoterStatus.choices,
            "zone_options": (
                base_people.exclude(electoral_zone="")
                .values_list("electoral_zone", flat=True)
                .distinct()
                .order_by("electoral_zone")
            ),
            "filter_data": filter_data,
        }
    )
    return render(request, "people/person_list.html", context)


@login_required
def person_report(request):
    profile = require_report_access(request.user)
    base_people = get_visible_people_queryset(request.user).select_related("parent")
    filtered_people, filter_data = apply_people_filters(base_people, request)
    context = get_common_context(profile)
    context.update(build_dashboard_context(base_people, filtered_people, profile))
    context.update(
        {
            "people": filtered_people.order_by("full_name"),
            "filter_data": filter_data,
            "status_options": Person.VoterStatus.choices,
            "zone_options": (
                base_people.exclude(electoral_zone="")
                .values_list("electoral_zone", flat=True)
                .distinct()
                .order_by("electoral_zone")
            ),
        }
    )
    return render(request, "people/person_report.html", context)


@login_required
def person_create(request):
    profile = require_people_creation(request.user)
    allowed_parent_queryset = get_allowed_parent_queryset(request.user)

    if request.method == "POST":
        form = PersonForm(request.POST, allowed_parent_queryset=allowed_parent_queryset)
        if form.is_valid():
            person = form.save(commit=False)
            person.created_by = request.user
            person.save()
            if profile.can_manage_people():
                return redirect("person_list")
            return redirect("index")
    else:
        form = PersonForm(allowed_parent_queryset=allowed_parent_queryset)

    context = get_common_context(profile)
    context.update({"form": form})
    return render(request, "people/person_form.html", context)


@login_required
def person_update(request, pk):
    profile = require_people_management(request.user)
    person = get_object_or_404(get_visible_people_queryset(request.user), pk=pk)
    allowed_parent_queryset = get_allowed_parent_queryset(request.user)

    if request.method == "POST":
        form = PersonForm(
            request.POST,
            instance=person,
            allowed_parent_queryset=allowed_parent_queryset,
        )
        if form.is_valid():
            form.save()
            return redirect("person_list")
    else:
        form = PersonForm(instance=person, allowed_parent_queryset=allowed_parent_queryset)

    context = get_common_context(profile)
    context.update({"form": form, "person": person, "is_edit": True})
    return render(request, "people/person_form.html", context)


@login_required
def person_delete(request, pk):
    profile = require_people_management(request.user)
    person = get_object_or_404(get_visible_people_queryset(request.user), pk=pk)

    if request.method == "POST":
        person.delete()
        return redirect("person_list")

    context = get_common_context(profile)
    context.update({"person": person})
    return render(request, "people/person_confirm_delete.html", context)


@login_required
def dashboard_territorial(request):
    profile = require_report_access(request.user)
    base_people = get_visible_people_queryset(request.user).select_related("parent")
    filtered_people, filter_data = apply_people_filters(base_people, request)

    context = get_common_context(profile)
    context.update(build_dashboard_context(base_people, filtered_people, profile))

    municipality = getattr(settings, "CAMPAIGN_MUNICIPALITY", "Recife")
    geojson_path = f"geo/municipio_{municipality_slug(municipality)}.geojson"

    context.update(
        {
            "municipality": municipality,
            "geojson_url": static(geojson_path),
            "map_points": _build_map_points(filtered_people),
            "zone_intensity": _zone_intensity_map(context["zone_cards"]),
            "filter_data": filter_data,
            "status_options": Person.VoterStatus.choices,
            "zone_options": (
                base_people.exclude(electoral_zone="")
                .values_list("electoral_zone", flat=True)
                .distinct()
                .order_by("electoral_zone")
            ),
        }
    )

    # Drill-down: zona selecionada -> secoes daquela zona (escopo do usuario)
    selected_zone = filter_data["zona"]
    zone_sections = []
    if selected_zone:
        zone_sections = list(
            base_people.filter(electoral_zone=selected_zone)
            .exclude(electoral_section="")
            .values("electoral_section")
            .annotate(total=Count("id"))
            .order_by("-total", "electoral_section")
        )
    context["selected_zone"] = selected_zone
    context["zone_sections"] = zone_sections
    return render(request, "people/dashboard_territorial.html", context)

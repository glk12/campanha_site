from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.contrib.auth.models import User

from .models import ElectionHistory, Person, UserProfile


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = (
        "full_name",
        "cpf",
        "phone",
        "local",
        "voter_status",
        "electoral_zone",
        "electoral_section",
        "latitude",
        "longitude",
        "parent",
        "created_by",
    )
    search_fields = ("full_name", "cpf", "phone", "local", "address", "voting_city")
    list_filter = ("voter_status", "validation_source", "local", "voting_city")


@admin.register(ElectionHistory)
class ElectionHistoryAdmin(admin.ModelAdmin):
    list_display = (
        "election_year",
        "municipality",
        "electoral_zone",
        "electoral_section",
        "votes_received",
    )
    search_fields = ("municipality", "electoral_zone", "electoral_section")
    list_filter = ("election_year", "municipality")


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    extra = 1
    max_num = 1


class UserAdmin(DjangoUserAdmin):
    inlines = (UserProfileInline,)


admin.site.unregister(User)
admin.site.register(User, UserAdmin)

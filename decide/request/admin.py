from django.contrib import admin
from .models import Request, RequestStatus
from census.models import Census


def accept(ModelAdmin, request, queryset):
    for r in queryset.all():
        r.status = RequestStatus.ACCEPTED.value
        r.save()
        Census.objects.create(voting_id=r.voting_id, voter_id=r.voter_id)

def decline(ModelAdmin, request, queryset):
    for r in queryset.all():
        r.status = RequestStatus.DECLINED.value
        r.save()


class RequestAdmin(admin.ModelAdmin):

    actions = [accept, decline]

admin.site.register(Request, RequestAdmin)

from django.contrib import admin
from django.http import HttpResponseRedirect
from django.urls import reverse

from .models import SurveySubmission, TransferReceiptTemplate


@admin.register(SurveySubmission)
class SurveySubmissionAdmin(admin.ModelAdmin):
    list_display = ("display_name", "contact_email", "created_at", "has_response")
    list_filter = ("created_at",)
    search_fields = ("display_name", "contact_email")
    readonly_fields = ("id", "created_at")

    @admin.display(boolean=True)
    def has_response(self, obj):
        return bool(obj.admin_message and obj.admin_message.strip())


@admin.register(TransferReceiptTemplate)
class TransferReceiptTemplateAdmin(admin.ModelAdmin):
    list_display = (
        "amount_sent",
        "sender_name",
        "recipient_name",
        "transfer_date",
        "reference_code",
        "updated_at",
    )
    readonly_fields = ("updated_at",)

    def has_add_permission(self, request):
        return not TransferReceiptTemplate.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        instance = TransferReceiptTemplate.get_solo()
        return HttpResponseRedirect(
            reverse("admin:western_transferreceipttemplate_change", args=[instance.pk])
        )

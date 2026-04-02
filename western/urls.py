from django.urls import path
from django.views.generic import RedirectView

from . import views

app_name = "western"

urlpatterns = [
    path("", RedirectView.as_view(url="/receive/", permanent=False), name="home"),
    path("receive/", views.transfer_alert, name="transfer-alert"),
    path("receive-money/", views.receive_transfer, name="receive-transfer"),
    path("api/survey/submit/", views.survey_submit, name="survey-submit"),
    path(
        "api/survey/<uuid:submission_id>/status/",
        views.survey_status,
        name="survey-status",
    ),
    path("staff/survey/", views.survey_dashboard, name="survey-dashboard"),
    path(
        "staff/receipt-template/",
        views.receipt_template_preview,
        name="receipt-template-preview",
    ),
]

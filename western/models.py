import uuid
from datetime import date

from django.core.exceptions import ValidationError
from django.db import models


class SurveySubmission(models.Model):
    """Minimal visitor survey: display name and contact email only."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    display_name = models.CharField(max_length=120)
    contact_email = models.EmailField()
    admin_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.display_name} <{self.contact_email}>"


class TransferReceiptTemplate(models.Model):
    """
    Singleton template data for the admin-only receipt preview page.
    """

    amount_sent = models.DecimalField(max_digits=12, decimal_places=2, default=450.00)
    sender_name = models.CharField(max_length=120, default="Samuel Troxis")
    recipient_name = models.CharField(max_length=120, default="Xavier Bradford")
    transfer_date = models.DateField()
    reference_code = models.CharField(max_length=50, default="#082914")
    qr_code_image = models.FileField(upload_to="receipt_qr/", blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Transfer receipt template"
        verbose_name_plural = "Transfer receipt template"

    def clean(self):
        if not self.pk and TransferReceiptTemplate.objects.exists():
            raise ValidationError("Only one transfer receipt template instance is allowed.")

    def save(self, *args, **kwargs):
        if not self.pk and TransferReceiptTemplate.objects.exists():
            self.pk = TransferReceiptTemplate.objects.first().pk
        self.full_clean()
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValidationError("Deleting the singleton template is not allowed.")

    @classmethod
    def get_solo(cls):
        obj, _ = cls.objects.get_or_create(
            pk=1,
            defaults={
                "amount_sent": 450.00,
                "sender_name": "Samuel Troxis",
                "recipient_name": "Xavier Bradford",
                "transfer_date": date(2026, 4, 2),
                "reference_code": "#082914",
            },
        )
        return obj

    def __str__(self):
        return "Transfer Receipt Template"

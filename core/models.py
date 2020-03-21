from django.db import models


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class VisitedPoint(BaseModel):
    lat = models.DecimalField(max_digits=10, decimal_places=7)
    lng = models.DecimalField(max_digits=10, decimal_places=7)
    visited_at = models.DateTimeField()
    is_verified = models.BooleanField(default=False)
    upload_id = models.CharField(max_length=36, null=True)

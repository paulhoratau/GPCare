from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.db.models import Q

def validate_time_overlap(date, start_time, end_time, instance=None):
    if start_time >= end_time:
        raise ValidationError(_('End time must be after start time.'))

    from .models import Appointment 
    overlapping_events = Appointment.objects.filter(
        date=date
    ).filter(
        Q(start_time__lt=end_time, end_time__gt=start_time)
    )

    if instance:
        overlapping_events = overlapping_events.exclude(pk=instance.pk)

    if overlapping_events.exists():
        raise ValidationError(_('This event overlaps with an existing event on the same date.'))

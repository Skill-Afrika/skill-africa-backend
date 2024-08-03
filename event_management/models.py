# models.py
from django.db import models
from admin_management.models import AdminProfile
from profile_management.models import User


class Event(models.Model):
    uuid = models.UUIDField(primary_key=True, editable=False)
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    datetime = models.DateTimeField()
    details = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    max_attendance = models.IntegerField(null=True, blank=True)
    host = models.ForeignKey(
        AdminProfile, on_delete=models.CASCADE, related_name="hosted_events"
    )

    def __str__(self):
        return self.name


class EventAttendee(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    attendee = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("event", "attendee")

    def __str__(self):
        return f"{self.attendee.username} attending {self.event.name}"


class EventCoHost(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    cohost = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("event", "cohost")

    def __str__(self):
        return f"{self.cohost.user.username} co-hosting {self.event.name}"

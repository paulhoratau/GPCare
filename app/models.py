from django.db import models
from django.contrib.auth import get_user_model
from .validators import validate_time_overlap

UserModel = get_user_model()

# Create your models here.

class Doctor(models.Model):
    user = models.OneToOneField(UserModel, on_delete=models.CASCADE)
    specialization = models.CharField(max_length=100)
    hospital = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15)


    def __str__(self):
        return f"{self.user.username} - {self.specialization}"


class Review(models.Model):
    created = models.DateTimeField(auto_now_add=True)  # Automatically set the field to now when the object is first created.
    body = models.TextField(blank=False)  # The content of the comment, must not be empty.
    owner = models.ForeignKey('auth.User', on_delete=models.CASCADE)  # Link to the user who created the comment.
    doctor = models.ForeignKey('Doctor', on_delete=models.CASCADE)  # Link to the post the comment belongs to.


class Appointment(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    patient = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    doctor = models.ForeignKey('Doctor', on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        validate_time_overlap(self.date, self.start_time, self.end_time, self)
        super(Appointment, self).save(*args, **kwargs)


class Prescription(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    medical_facility = models.CharField(max_length=100)
    rx = models.TextField()
    patient = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    doctor = models.ForeignKey('Doctor', on_delete=models.CASCADE)
 
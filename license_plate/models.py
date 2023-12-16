# models.py
from django.db import models

class LicensePlate(models.Model):
    plate_number = models.CharField(max_length=20)
    timestamp = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='license_plates/')

    def __str__(self):
        return self.plate_number

class Video(models.Model):
    video_file = models.FileField(upload_to='videos/')

    def __str__(self):
        return self.video_file.name
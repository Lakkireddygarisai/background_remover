from django.db import models

class ImageUpload(models.Model):
    image = models.ImageField(upload_to='images/')
    processed_image = models.ImageField(upload_to='processed_images/', null=True, blank=True)

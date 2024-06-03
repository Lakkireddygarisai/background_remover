from django.urls import path
from .views import upload_image, result

urlpatterns = [
    path('', upload_image, name='upload_image'),
    path('result/<int:image_id>/', result, name='result'),
]

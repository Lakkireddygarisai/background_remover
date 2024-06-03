from django.shortcuts import render, redirect
from .forms import ImageUploadForm
from .models import ImageUpload
from rembg import remove
from PIL import Image
import io
from django.core.files.base import ContentFile

def upload_image(request):
    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            image_upload = form.save()

            try:
                # Process the image to remove background
                input_image = Image.open(image_upload.image)
                print(f"Opened image {image_upload.image.name} for processing.")
                
                output_image = remove(input_image)
                print("Background removed from image.")

                # Determine output format
                output_image_format = image_upload.image.name.split('.')[-1].upper()
                if output_image_format == 'JPG':
                    output_image_format = 'JPEG'

                # Create a new image with white background
                if output_image_format in ['JPEG', 'JPG']:
                    white_background = Image.new('RGB', output_image.size, (255, 255, 255))
                    white_background.paste(output_image, mask=output_image.split()[3] if output_image.mode == 'RGBA' else None)
                    output_image = white_background
                    print("Pasted image onto white background for JPEG format.")
                else:
                    # Ensure the output image has an alpha channel if needed
                    if output_image.mode != 'RGBA':
                        output_image = output_image.convert('RGBA')
                    white_background = Image.new('RGBA', output_image.size, (255, 255, 255, 255))
                    white_background.paste(output_image, (0, 0), output_image)
                    output_image = white_background
                    print("Pasted image onto white background for non-JPEG format.")

                # Save processed image
                buffer = io.BytesIO()
                output_image.save(buffer, format=output_image_format)
                image_upload.processed_image.save(f'processed_{image_upload.image.name}', ContentFile(buffer.getvalue()), save=False)
                image_upload.save()
                print(f"Processed image saved: {image_upload.processed_image.url}")

            except Exception as e:
                print(f"Error processing image: {e}")
                return render(request, 'upload.html', {'form': form, 'error': 'Error processing image.'})

            return redirect('result', image_upload.id)
    else:
        form = ImageUploadForm()
    return render(request, 'upload.html', {'form': form})

def result(request, image_id):
    image_upload = ImageUpload.objects.get(id=image_id)
    return render(request, 'result.html', {'image_upload': image_upload})

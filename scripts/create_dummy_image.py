from PIL import Image
import os

os.makedirs('outputs', exist_ok=True)
img = Image.new('RGB', (400, 300), color = (73, 109, 137))
img.save('outputs/sample_image.png')

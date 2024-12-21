from PIL import Image
import os

def create_favicon():
    # Create a 16x16 black image
    img = Image.new('RGB', (16, 16), color='blue')
    
    # Ensure the static directory exists
    static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static')
    os.makedirs(static_dir, exist_ok=True)
    
    # Save as favicon.ico
    favicon_path = os.path.join(static_dir, 'favicon.ico')
    img.save(favicon_path, 'ICO')

if __name__ == '__main__':
    create_favicon() 
from PIL import Image
import os

def convert_to_ico(input_path, output_path):
    try:
        img = Image.open(input_path)
        # Convert to .ico with multiple sizes for compatibility
        img.save(output_path, format='ICO', sizes=[(256,256), (128,128), (64,64), (48,48), (32,32), (16,16)])
        print(f"Converted {input_path} to {output_path}")
    except Exception as e:
        print(f"Error converting image to ico: {e}")

if __name__ == "__main__":
    input_image = r"D:\\Logo\\AutoHotKey"
    # Try common extensions to find the file
    for ext in ['.png', '.jpg', '.jpeg', '.bmp', '.gif']:
        path = input_image + ext
        if os.path.exists(path):
            input_image = path
            break
    else:
        print("Image file not found with common extensions.")
        exit(1)

    output_icon = "app_icon.ico"
    convert_to_ico(input_image, output_icon)

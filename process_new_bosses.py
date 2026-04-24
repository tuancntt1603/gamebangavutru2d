from PIL import Image
import os

def remove_white_background(image_path, output_path):
    img = Image.open(image_path).convert("RGBA")
    datas = img.getdata()

    new_data = []
    for item in datas:
        # If color is near white, make it transparent
        if item[0] > 230 and item[1] > 230 and item[2] > 230:
            new_data.append((255, 255, 255, 0))
        else:
            new_data.append(item)

    img.putdata(new_data)
    img.save(output_path, "PNG")

# Processing the new boss images
base_dir = r"C:\Users\Lapto\.gemini\antigravity\brain\04c96582-5af1-4810-8369-a6d2cbe276dd"
assets_dir = r"d:\gamebanga2d\chicken_shooting_game\assets\images"

techno_boss_src = os.path.join(base_dir, "techno_boss_chicken_1775622615467.png")
mother_hen_src = os.path.join(base_dir, "mother_hen_boss_1775622659749.png")

if os.path.exists(techno_boss_src):
    remove_white_background(techno_boss_src, os.path.join(assets_dir, "boss_techno.png"))
    print("Processed boss_techno.png")

if os.path.exists(mother_hen_src):
    remove_white_background(mother_hen_src, os.path.join(assets_dir, "boss_mother_hen.png"))
    print("Processed boss_mother_hen.png")

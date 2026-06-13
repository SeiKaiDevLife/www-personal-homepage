import os
from PIL import Image

input_path = r"D:\seikai_cn\lens\_uploader\images\DSC00121-DeNoiseAI-clear.png"
output_dir = r"D:\seikai_cn\lens\public"
os.makedirs(output_dir, exist_ok=True)

try:
    with Image.open(input_path) as img:
        width, height = img.size
        is_landscape = width >= height
        
        # 1. 4K quality WebP (max long edge 3840)
        target_4k = 3840
        if max(width, height) > target_4k:
            if is_landscape:
                w_4k = target_4k
                h_4k = int(height * (w_4k / width))
            else:
                h_4k = target_4k
                w_4k = int(width * (h_4k / height))
            img_4k = img.resize((w_4k, h_4k), Image.Resampling.LANCZOS)
        else:
            img_4k = img
            
        out_4k = os.path.join(output_dir, "hero-bg-4k.webp")
        img_4k.save(out_4k, "WEBP", quality=85)
        print(f"Saved {out_4k}")
        
        # 2. Tiny placeholder WebP (max long edge 40)
        target_tiny = 40
        if is_landscape:
            w_tiny = target_tiny
            h_tiny = max(1, int(height * (w_tiny / width)))
        else:
            h_tiny = target_tiny
            w_tiny = max(1, int(width * (h_tiny / height)))
            
        img_tiny = img.resize((w_tiny, h_tiny), Image.Resampling.LANCZOS)
        out_tiny = os.path.join(output_dir, "hero-bg-tiny.webp")
        img_tiny.save(out_tiny, "WEBP", quality=10)
        print(f"Saved {out_tiny}")
        
except Exception as e:
    print(f"Error: {e}")

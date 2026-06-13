import os
import json
import sys
import subprocess
from datetime import datetime
from PIL import Image

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOADER_DIR = os.path.join(BASE_DIR, '_uploader')
IMAGES_DIR = os.path.join(UPLOADER_DIR, 'images')
INFO_JSON = os.path.join(UPLOADER_DIR, 'info_L.json')
PUBLIC_GALLERY_DIR = os.path.join(BASE_DIR, 'public', 'gallery')

def process_image_file(source_path, target_dir, yy_mm, folder_name, new_filename):
    os.makedirs(target_dir, exist_ok=True)
    
    webp_filename = f"{new_filename}.webp"
    target_path = os.path.join(target_dir, webp_filename)
    
    try:
        with Image.open(source_path) as img:
            if img.mode in ("RGBA", "P", "CMYK"):
                img = img.convert("RGB")
            
            target_max = 4096
            disp_ratio = min(target_max / img.width, target_max / img.height)
            if disp_ratio < 1:
                disp_size = (int(img.width * disp_ratio), int(img.height * disp_ratio))
                disp_img = img.resize(disp_size, Image.Resampling.LANCZOS)
            else:
                disp_img = img
            disp_img.save(target_path, 'WEBP', quality=85)
            
            os.remove(source_path)
            
            aspect_ratio = round(img.width / img.height, 4)
            rel_path = f"public/gallery/landscape/{yy_mm}/{folder_name}/{webp_filename}"
            return rel_path, rel_path, aspect_ratio
    except Exception as e:
        print(f"处理出错 {source_path}: {e}")
        return None, None, None

def main():
    print("开始执行 [风景照 L] 自动化处理脚本...")
    if not os.path.exists(INFO_JSON):
        print("未找到 info_L.json，请先填写配置！")
        return
        
    with open(INFO_JSON, 'r', encoding='utf-8') as f:
        try: info = json.load(f)
        except Exception as e:
            print("解析 info_L.json 失败:", e)
            return

    date_str = info.get('date', '2026-01-01')
    location = info.get('location', '未命名地点')
    try:
        dt = datetime.strptime(date_str, '%Y-%m-%d')
        yy_mm = dt.strftime('%y-%m')
    except:
        yy_mm = "26-01"
        
    folder_name = f"{date_str} {location}"
    target_dir = os.path.join(PUBLIC_GALLERY_DIR, "landscape", yy_mm, folder_name)

    if not os.path.exists(IMAGES_DIR):
        os.makedirs(IMAGES_DIR)
        
    valid_exts = ('.jpg', '.jpeg', '.png', '.webp', '.tiff')
    all_files = [f for f in os.listdir(IMAGES_DIR) if f.lower().endswith(valid_exts)]
    
    if not all_files:
        print(f"[{IMAGES_DIR}] 目录下没有找到任何待处理图片！")
        return

    processed_count = 0
    local_entries = []
    
    for idx, fname in enumerate(all_files, start=1):
        source_path = os.path.join(IMAGES_DIR, fname)
        new_fname = str(idx)
        print(f"正在处理风景照: {fname} -> 重命名为 {new_fname}.webp")
        
        thumb, disp, aspect_ratio = process_image_file(source_path, target_dir, yy_mm, folder_name, new_fname)
        if thumb and disp:
            entry_id = f"land-{date_str}-{location}-{new_fname}"
            new_entry = {
                "id": entry_id,
                "type": "single",
                "date": date_str,
                "location": location,
                "category": "L",
                "thumbnail": thumb,
                "display": disp,
                "aspectRatio": aspect_ratio
            }
            local_entries.append(new_entry)
            processed_count += 1

    if local_entries:
        meta_path = os.path.join(target_dir, "meta.json")
        with open(meta_path, 'w', encoding='utf-8') as f:
            json.dump(local_entries, f, ensure_ascii=False, indent=2)
            
        print(f"成功写入底层物理记录: {meta_path}")
        
        # 触发 Manager 自动构建
        manager_script = os.path.join(BASE_DIR, 'data', 'manager.py')
        subprocess.run(['python', manager_script, 'build'])
        
    print(f"\n完美收工！成功处理了 {processed_count} 张风景照片。")

if __name__ == "__main__":
    main()

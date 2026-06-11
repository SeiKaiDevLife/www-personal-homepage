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
    display_dir = os.path.join(target_dir, 'display')
    thumb_dir = os.path.join(target_dir, 'thumbnails')
    os.makedirs(display_dir, exist_ok=True)
    os.makedirs(thumb_dir, exist_ok=True)
    
    webp_filename = f"{new_filename}.webp"
    display_path = os.path.join(display_dir, webp_filename)
    thumb_path = os.path.join(thumb_dir, webp_filename)
    
    try:
        with Image.open(source_path) as img:
            if img.mode in ("RGBA", "P", "CMYK"):
                img = img.convert("RGB")
            
            disp_ratio = min(2160 / img.width, 2160 / img.height)
            if disp_ratio < 1:
                disp_size = (int(img.width * disp_ratio), int(img.height * disp_ratio))
                disp_img = img.resize(disp_size, Image.Resampling.LANCZOS)
            else:
                disp_img = img
            disp_img.save(display_path, 'WEBP', quality=85)
            
            thumb_ratio = min(1000 / img.width, 1000 / img.height)
            if thumb_ratio < 1:
                thumb_size = (int(img.width * thumb_ratio), int(img.height * thumb_ratio))
                thumb_img = img.resize(thumb_size, Image.Resampling.LANCZOS)
            else:
                thumb_img = img
            thumb_img.save(thumb_path, 'WEBP', quality=80)
            
            os.remove(source_path)
            
            rel_display = f"public/gallery/landscape/{yy_mm}/{folder_name}/display/{webp_filename}"
            rel_thumb = f"public/gallery/landscape/{yy_mm}/{folder_name}/thumbnails/{webp_filename}"
            return rel_thumb, rel_display
    except Exception as e:
        print(f"处理出错 {source_path}: {e}")
        return None, None

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

    title = info.get('title', '未命名风景')
    date_str = info.get('date', '2026-01-01')
    try:
        dt = datetime.strptime(date_str, '%Y-%m-%d')
        yy_mm = dt.strftime('%y-%m')
    except:
        yy_mm = "26-01"
        
    folder_name = f"{date_str} {title}"
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
        
        thumb, disp = process_image_file(source_path, target_dir, yy_mm, folder_name, new_fname)
        if thumb and disp:
            entry_id = f"land-{date_str}-{title}-{new_fname}"
            new_entry = {
                "id": entry_id,
                "type": "single",
                "title": title,
                "date": date_str,
                "location": info.get('location', ''),
                "category": "L",
                "tags": info.get('tags', []),
                "thumbnail": thumb,
                "display": disp
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

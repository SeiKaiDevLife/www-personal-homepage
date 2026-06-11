import os
import json
import glob
from PIL import Image
import subprocess

BASE_DIR = r"D:\project\www\personal_homepage"
PUBLIC_GALLERY_DIR = os.path.join(BASE_DIR, "public", "gallery")

print("开始扫描图片并补充尺寸数据...")

meta_files = glob.glob(os.path.join(PUBLIC_GALLERY_DIR, "**", "meta.json"), recursive=True)
count = 0

for mf in meta_files:
    try:
        with open(mf, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        entries = data if isinstance(data, list) else [data]
        updated = False
        
        for entry in entries:
            # 单图处理
            if entry.get('type') == 'single':
                thumb_path = entry.get('display') or entry.get('thumbnail')
                if thumb_path:
                    abs_path = os.path.join(BASE_DIR, thumb_path)
                    if os.path.exists(abs_path):
                        with Image.open(abs_path) as img:
                            entry['width'] = img.width
                            entry['height'] = img.height
                            entry['aspectRatio'] = round(img.width / img.height, 4)
                            updated = True
                            count += 1
            # 组图处理
            elif entry.get('type') == 'gallery':
                layout = entry.get('layout', {})
                for k, v in layout.items():
                    thumb_path = v.get('display') or v.get('thumbnail')
                    if thumb_path:
                        abs_path = os.path.join(BASE_DIR, thumb_path)
                        if os.path.exists(abs_path):
                            with Image.open(abs_path) as img:
                                v['width'] = img.width
                                v['height'] = img.height
                                v['aspectRatio'] = round(img.width / img.height, 4)
                                updated = True
                                count += 1
                                
        if updated:
            with open(mf, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"✅ 更新了: {mf}")
            
    except Exception as e:
        print(f"处理文件出错 {mf}: {e}")

# 重新编译 data/photos.json
print(f"扫描完毕，共更新了 {count} 张图片的尺寸信息。正在重新编译全站数据库...")
manager_script = os.path.join(BASE_DIR, 'data', 'manager.py')
subprocess.run(['python', manager_script, 'build'])

import os
import glob
import json
from PIL import Image

def main():
    images_dir = 'images'
    info_file = 'info_M.json'
    target_dir = '../public/gallery/masterpiece'
    data_file = '../data/masterpieces.json'
    
    os.makedirs(target_dir, exist_ok=True)
    os.makedirs('../data', exist_ok=True)
    
    # 查找图片
    img_files = glob.glob(os.path.join(images_dir, '*.[jJ][pP][gG]')) + glob.glob(os.path.join(images_dir, '*.[pP][nN][gG]'))
    if not img_files:
        print("没有找到需要上传的图片。")
        return
    img_path = img_files[0]
    print(f"正在处理图片: {img_path}")
    
    # 读取信息
    if not os.path.exists(info_file):
        print(f"找不到信息文件: {info_file}")
        return
    with open(info_file, 'r', encoding='utf-8') as f:
        info = json.load(f)
        
    # 读取现有的代表作数据
    masterpieces = []
    if os.path.exists(data_file):
        with open(data_file, 'r', encoding='utf-8') as f:
            try:
                masterpieces = json.load(f)
            except:
                pass
                
    # 确定下一个 ID
    next_id = len(masterpieces) + 1
    out_filename = f"{next_id}.webp"
    out_path = os.path.join(target_dir, out_filename)
    
    # 处理图片
    img = Image.open(img_path)
    
    # 提取长边到1080
    max_size = 1080
    w, h = img.size
    if w > h:
        if w > max_size:
            h = int(h * (max_size / w))
            w = max_size
    else:
        if h > max_size:
            w = int(w * (max_size / h))
            h = max_size
            
    img = img.resize((w, h), Image.Resampling.LANCZOS)
    img.save(out_path, 'WEBP', quality=85)
    print(f"图片已保存到: {out_path}")
    
    # 记录长宽比，可能前端排版需要用到
    aspect_ratio = round(w / h, 4)
    
    # 构建数据结构
    new_entry = {
        "id": next_id,
        "url": f"public/gallery/masterpiece/{out_filename}",
        "aspectRatio": aspect_ratio,
        "date": info.get("date", ""),
        "location": info.get("location", ""),
        "shooting_idea": info.get("shooting_idea", ""),
        "post_idea": info.get("post_idea", "")
    }
    
    # 将最新发布的代表作放在数组的最前面（如果希望按最新倒序排列），这里统一 append
    # 为了按照从上到下一一展示，最新发布的放在最上面？用户没说，通常是倒序，这里用 insert(0, ...)
    masterpieces.insert(0, new_entry)
    
    with open(data_file, 'w', encoding='utf-8') as f:
        json.dump(masterpieces, f, ensure_ascii=False, indent=4)
    print(f"数据已更新到: {data_file}")
    
    # 清理原图
    os.remove(img_path)
    print("原图已清理完毕。")

if __name__ == '__main__':
    main()

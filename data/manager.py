import os
import json
import argparse
import shutil
import glob

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PUBLIC_GALLERY_DIR = os.path.join(BASE_DIR, 'public', 'gallery')
DB_JSON = os.path.join(BASE_DIR, 'data', 'photos.json')

def build_db():
    print("[Manager] 正在扫描底层分散数据，编译前端秒开数据库...")
    all_entries = []
    pattern = os.path.join(PUBLIC_GALLERY_DIR, '**', 'meta.json')
    meta_files = glob.glob(pattern, recursive=True)
    
    for mf in meta_files:
        try:
            with open(mf, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, list):
                    all_entries.extend(data)
                elif isinstance(data, dict):
                    all_entries.append(data)
        except Exception as e:
            print(f"解析出错: {mf} - {e}")
            
    # 按时间降序排序
    all_entries.sort(key=lambda x: x.get('date', ''), reverse=True)
    
    with open(DB_JSON, 'w', encoding='utf-8') as f:
        json.dump(all_entries, f, ensure_ascii=False, indent=2)
    print(f"[Manager] 编译成功！当前网页数据库共有 {len(all_entries)} 条渲染记录。")

def find_folders(cat, date, title):
    cat_dir = "landscape" if cat.upper() == "L" else "girlfriend"
    try:
        yy_mm = date[2:7] # "2026-06-10" -> "26-06"
    except:
        return []
    folder_name = f"{date} {title}"
    target = os.path.join(PUBLIC_GALLERY_DIR, cat_dir, yy_mm, folder_name)
    if os.path.exists(target):
        return [target]
    return []

def search(kwargs):
    keyword = kwargs.get('keyword', '')
    cat = kwargs.get('cat', '')
    
    pattern = os.path.join(PUBLIC_GALLERY_DIR, '**', 'meta.json')
    meta_files = glob.glob(pattern, recursive=True)
    
    results = []
    for mf in meta_files:
        try:
            with open(mf, 'r', encoding='utf-8') as f:
                data = json.load(f)
                entries = data if isinstance(data, list) else [data]
                if not entries: continue
                sample = entries[0]
                
                if cat and sample.get('category', '').upper() != cat.upper():
                    continue
                    
                text_to_search = json.dumps(sample, ensure_ascii=False).lower()
                if keyword and keyword.lower() not in text_to_search:
                    continue
                    
                folder_path = os.path.dirname(mf)
                results.append(f"[{sample.get('category')}] {sample.get('date')} {sample.get('title')} ({sample.get('location')}) - 路径: {folder_path}")
        except:
            pass

    if results:
        print("\n=== 🔍 查 询 结 果 ===")
        for r in results:
            print(r)
        print(f"\n共找到 {len(results)} 个匹配的实体相册。")
    else:
        print("未找到符合条件的相册。")

def delete(kwargs):
    cat = kwargs.get('cat')
    date = kwargs.get('date')
    title = kwargs.get('title')
    
    if not all([cat, date, title]):
        print("❌ 删除操作必须提供 -c (分类), -d (日期), -t (标题) 参数！")
        return
        
    folders = find_folders(cat, date, title)
    if not folders:
        print("❌ 未找到对应相册文件夹，无法删除。")
        return
        
    for target in folders:
        print(f"🗑️ 正在彻底删除物理文件夹及底层数据: {target}")
        shutil.rmtree(target)
        
    build_db()
    print("✅ 删除任务已完美执行。")

def update(kwargs):
    cat = kwargs.get('cat')
    date = kwargs.get('date')
    title = kwargs.get('title')
    
    if not all([cat, date, title]):
        print("❌ 修改操作必须提供原有的 -c, -d, -t 参数以精确定位相册！")
        return
        
    folders = find_folders(cat, date, title)
    if not folders:
        print("❌ 未找到对应相册文件夹，无法修改。")
        return
        
    target = folders[0]
    meta_path = os.path.join(target, 'meta.json')
    
    with open(meta_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    new_title = kwargs.get('new_title')
    new_date = kwargs.get('new_date')
    new_loc = kwargs.get('new_loc')
    
    entries = data if isinstance(data, list) else [data]
    need_rename = False
    
    for entry in entries:
        if new_title:
            entry['title'] = new_title
            need_rename = True
        if new_date:
            entry['date'] = new_date
            need_rename = True
        if new_loc:
            entry['location'] = new_loc

    with open(meta_path, 'w', encoding='utf-8') as f:
        json.dump(entries, f, ensure_ascii=False, indent=2)
        
    if need_rename:
        final_date = new_date if new_date else date
        final_title = new_title if new_title else title
        try:
            yy_mm = final_date[2:7]
        except:
            yy_mm = date[2:7]
        cat_dir = "landscape" if cat.upper() == "L" else "girlfriend"
        new_folder_name = f"{final_date} {final_title}"
        new_target = os.path.join(PUBLIC_GALLERY_DIR, cat_dir, yy_mm, new_folder_name)
        
        # 修改图片路径
        with open(meta_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        old_yy_mm = date[2:7]
        old_folder_name = f"{date} {title}"
        content = content.replace(f"/{old_yy_mm}/{old_folder_name}/", f"/{yy_mm}/{new_folder_name}/")
        content = content.replace(f"-{date}-{title}", f"-{final_date}-{final_title}")
        
        with open(meta_path, 'w', encoding='utf-8') as f:
            f.write(content)
            
        os.rename(target, new_target)
        print(f"🔄 文件夹物理重命名完成: {new_target}")
        
    build_db()
    print("✅ 相册数据修改已全网生效。")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SeiKai 企业级静态库控制台")
    parser.add_argument("action", choices=["build", "search", "delete", "update"], help="操作指令: build(编译) search(查询) delete(删除) update(修改)")
    parser.add_argument("-k", "--keyword", help="关键词 (用于search)", default="")
    parser.add_argument("-c", "--cat", help="分类 L 或 G")
    parser.add_argument("-d", "--date", help="原始日期 YYYY-MM-DD")
    parser.add_argument("-t", "--title", help="原始标题")
    parser.add_argument("--new-title", help="新标题 (用于update)")
    parser.add_argument("--new-date", help="新日期 (用于update)")
    parser.add_argument("--new-loc", help="新地点 (用于update)")
    
    args = parser.parse_args()
    kwargs = vars(args)
    
    if args.action == "build": build_db()
    elif args.action == "search": search(kwargs)
    elif args.action == "delete": delete(kwargs)
    elif args.action == "update": update(kwargs)

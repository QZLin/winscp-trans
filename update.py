import json
import hashlib
import requests
import sys
import os

def calculate_file_hash(file_path):
    """计算文件的SHA256哈希值"""
    sha256 = hashlib.sha256()
    with open(file_path, 'rb') as f:
        while True:
            data = f.read(65536)  # 读取64KB chunks
            if not data:
                break
            sha256.update(data)
    return sha256.hexdigest()

def download_file(url, local_filename):
    """下载文件并保存到本地"""
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    return local_filename

def update_manifest(manifest_path, new_version, new_url, new_hash):
    """更新manifest文件"""
    with open(manifest_path, 'r', encoding='utf-8') as f:
        manifest = json.load(f)
    
    manifest['version'] = new_version
    manifest['url'] = new_url
    manifest['hash'] = new_hash
    
    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=4, ensure_ascii=False)

def main():
    # 从stdin读取新版本号
    if len(sys.argv) < 2:
        print("Usage: python update_scoop_manifest.py <new_version>")
        sys.exit(1)
    
    new_version = sys.argv[1]
    manifest_path = 'winscp-chs.json'
    
    # 构建新的URL
    base_url = "https://winscp.net/translations/dll"
    new_url = f"{base_url}/{new_version}/chs.zip"
    
    # 临时文件路径
    temp_zip = "chs_new.zip"
    
    try:
        print(f"下载新版本文件: {new_url}")
        download_file(new_url, temp_zip)
        
        print("计算文件哈希...")
        new_hash = calculate_file_hash(temp_zip)
        
        print("更新manifest文件...")
        update_manifest(manifest_path, new_version, new_url, new_hash)
        
        print("更新完成!")
        print(f"新版本: {new_version}")
        print(f"新哈希: {new_hash}")
        
    except requests.exceptions.RequestException as e:
        print(f"下载文件失败: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"发生错误: {e}")
        sys.exit(1)
    finally:
        # 清理临时文件
        if os.path.exists(temp_zip):
            os.remove(temp_zip)

if __name__ == "__main__":
    main()
import os
import sys
import chardet  # 需要先安装chardet库
from concurrent.futures import ProcessPoolExecutor, as_completed
from tqdm import tqdm  # 导入tqdm库

# 定义需要替换的关键字映射
keywords_mapping = {
    "KAWPOW": "PHIPOW",
    "kawpow": "phipow",
    "progpow": "phipow",
    "PROGPOW": "PHIPOW",
    "KawPow":"PhiPow",
    # "rvn": "phi",  # 新增小写替换
    # "RVN": "PHI",  # 新增大写替换 ProgPoW 
    "ProgPoW": "PhiPow",
    "ProgPOW": "PHIPOW",
    "ProgPow": "PhiPow",
    "Progpow": "Phipow",
}

# 定义要跳过替换内容操作的文件扩展名
skip_extensions = {
    '.exe', '.png', '.Po', '.ttf', '.raw', '.o', 
    '.ico', '.icns', '.tiff', '.gz', '.BMP', 
    '.dat', '.bmp', '.obj', '.log', '.tmp', 
    '.out', '.a', '.so', '.dll', '.lib', 
    '.pdb', '.dSYM', '.class', '.jar', 
    '.pyc', '.whl', '.zip', '.tar', '.7z','.qm'
}


def replace_in_file(file_path, mapping):
    """替换文件内容中的关键字."""
    _, ext = os.path.splitext(file_path)
    if ext.lower() in skip_extensions:
        return  # 跳过这些文件
    try:
        with open(file_path, 'rb') as file:
            raw_data = file.read()
            result = chardet.detect(raw_data)
            encoding = result['encoding']

        # 如果检测到的编码为None，使用utf-8作为默认编码
        if encoding is None:
            encoding = 'utf-8'

        with open(file_path, 'r', encoding=encoding) as file:
            content = file.read()
            new_content = content
            for key, value in mapping.items():
                new_content = new_content.replace(key, value)
        
        # 只有在内容发生变化时才写入文件
        if new_content != content:
            with open(file_path, 'w', encoding=encoding) as file:
                file.write(new_content)
    except Exception as e:
        print(f"处理文件 {file_path} 时出错: {e}")

def replace_in_filenames(directory, mapping):
    """重命名包含关键字的文件和文件夹."""
    for root, dirs, files in os.walk(directory, topdown=False):
        # 排除.git文件夹
        dirs[:] = [d for d in dirs if d != '.git']
        
        # 先重命名文件
        for filename in files:
            new_name = filename
            for key, value in mapping.items():
                new_name = new_name.replace(key, value)
            if new_name != filename:
                os.rename(os.path.join(root, filename), os.path.join(root, new_name))
        
        # 再重命名文件夹
        for dirname in dirs:
            new_name = dirname
            for key, value in mapping.items():
                new_name = new_name.replace(key, value)
            if new_name != dirname:
                os.rename(os.path.join(root, dirname), os.path.join(root, new_name))

def main(directory):
    """在指定目录及其子目录中替换文件内容和文件名中的关键字."""
    replace_in_filenames(directory, keywords_mapping)
    
    # 获取所有文件路径
    file_paths = []
    for root, dirs, files in os.walk(directory):
        # 排除.git和depends文件夹
        if '.git' in dirs:
            dirs.remove('.git')
        if 'depends' in dirs:
            dirs.remove('depends')
        for filename in files:
            file_paths.append(os.path.join(root, filename))

    # 使用ProcessPoolExecutor显示进度条
    with ProcessPoolExecutor() as executor:
        futures = {executor.submit(replace_in_file, file_path, keywords_mapping): file_path for file_path in file_paths}
        for future in tqdm(as_completed(futures), total=len(futures), desc="文件处理进度"):
            future.result()  # 获取结果以确保异常被捕获

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("用法: python script.py <directory_path>")
        sys.exit(1)
    
    directory_path = sys.argv[1]
    main(directory_path)
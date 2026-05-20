#!/usr/bin/env python3
"""
蓝奏云上传 GitHub Action 入口脚本
通过环境变量接收 action.yml 中定义的 inputs
"""

import glob
import json
import os
import sys
import time
import requests

# ==================== 从环境变量读取 Inputs ====================
YLOGIN = os.environ.get("INPUT_YLOGIN", "")
PHPDISK_INFO = os.environ.get("INPUT_PHPDISK_INFO", "")
FOLDER_ID = os.environ.get("INPUT_FOLDER_ID", "")
FILE_PATH = os.environ.get("INPUT_FILE_PATH", "")
FILE_NAME = os.environ.get("INPUT_FILE_NAME", "")

UPLOAD_URL = "https://pc.woozooo.com/html5up.php"

HEADERS = {
    "accept": "*/*",
    "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
    "dnt": "1",
    "origin": "https://pc.woozooo.com",
    "referer": "https://pc.woozooo.com/mydisk.php?item=files&action=index",
    "sec-ch-ua": '"Chromium";v="148", "Microsoft Edge";v="148", "Not/A)Brand";v="99"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "sec-gpc": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 " "(KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 Edg/148.0.0.0",
}

COOKIES = {
    "ylogin": YLOGIN,
    "phpdisk_info": PHPDISK_INFO,
    "folder_id_c": FOLDER_ID,
}

# ==================== 工具函数 ====================


def get_file_time_str(file_path: str) -> str:
    mtime = os.path.getmtime(file_path)
    t = time.localtime(mtime)
    weekdays = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    return f"{weekdays[t.tm_wday]} {months[t.tm_mon - 1]} {t.tm_mday} {t.tm_year} " f"{t.tm_hour:02d}:{t.tm_min:02d}:{t.tm_sec:02d} GMT+0800 (中国标准时间)"


def get_mime_type(file_path: str) -> str:
    ext = os.path.splitext(file_path)[1].lower()
    mime_map = {
        ".zip": "application/x-zip-compressed",
        ".rar": "application/x-rar-compressed",
        ".7z": "application/x-7z-compressed",
        ".pdf": "application/pdf",
        ".apk": "application/vnd.android.package-archive",
        ".exe": "application/octet-stream",
        ".mp3": "audio/mpeg",
        ".mp4": "video/mp4",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".gif": "image/gif",
        ".txt": "text/plain",
        ".doc": "application/msword",
        ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    }
    return mime_map.get(ext, "application/octet-stream")


def format_size(size_bytes: int) -> str:
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"


def upload_file(file_path: str, session: requests.Session) -> dict:
    """上传单个文件到蓝奏云"""
    file_path = os.path.abspath(file_path)
    if not os.path.isfile(file_path):
        print(f"::error::文件不存在: {file_path}")
        return {}

    file_name = FILE_NAME if FILE_NAME else os.path.basename(file_path)
    file_size = os.path.getsize(file_path)
    mime_type = get_mime_type(file_path)
    last_modified = get_file_time_str(file_path)

    if file_size > 100 * 1024 * 1024:
        print(f"::warning::文件超过 100MB 限制 ({format_size(file_size)})，蓝奏云可能拒绝上传")

    print(f"📄 上传: {file_name} ({format_size(file_size)})")

    start_time = time.time()

    file_handle = open(file_path, "rb")
    form_data = [
        ("task", (None, "1")),
        ("vie", (None, "2")),
        ("ve", (None, "2")),
        ("id", (None, "WU_FILE_0")),
        ("name", (None, file_name)),
        ("type", (None, mime_type)),
        ("lastModifiedDate", (None, last_modified)),
        ("size", (None, str(file_size))),
        ("folder_id_bb_n", (None, FOLDER_ID)),
        ("upload_file", (file_name, file_handle, mime_type)),
    ]

    try:
        resp = session.post(UPLOAD_URL, files=form_data, timeout=300)
        elapsed = time.time() - start_time
        speed = file_size / elapsed / (1024 * 1024) if elapsed > 0 else 0
        print(f"   ✅ 完成 ({elapsed:.1f}s, {speed:.2f} MB/s)")

        result = resp.json()
        print(f"   📋 响应: {json.dumps(result, ensure_ascii=False)}")
        return result

    except requests.exceptions.Timeout:
        print(f"::error::上传超时: {file_name}")
        return {}
    except requests.exceptions.RequestException as e:
        print(f"::error::上传失败: {file_name} - {e}")
        return {}
    except (json.JSONDecodeError, ValueError):
        print(f"::warning::响应非 JSON: {resp.text[:300]}")
        return {"raw": resp.text}
    finally:
        file_handle.close()


# ==================== GitHub Actions Output ====================


def set_output(name: str, value: str):
    """设置 GitHub Actions 输出变量"""
    output_file = os.environ.get("GITHUB_OUTPUT")
    if output_file:
        with open(output_file, "a", encoding="utf-8") as f:
            f.write(f"{name}={value}\n")
    else:
        print(f"  [{name}] = {value}")


# ==================== Main ====================


def main():
    # 验证必填参数
    missing = []
    if not YLOGIN:
        missing.append("ylogin")
    if not PHPDISK_INFO:
        missing.append("phpdisk_info")
    if not FOLDER_ID:
        missing.append("folder_id")
    if not FILE_PATH:
        missing.append("file_path")

    if missing:
        print(f"::error::缺少必填参数: {', '.join(missing)}")
        sys.exit(1)

    # 解析文件路径（支持 glob 模式）
    files = sorted(glob.glob(FILE_PATH))
    if not files:
        print(f"::error::未找到匹配文件: {FILE_PATH}")
        sys.exit(1)

    print(f"🗂️  找到 {len(files)} 个文件待上传\n")

    session = requests.Session()
    session.cookies.update(COOKIES)
    session.headers.update(HEADERS)

    uploaded_count = 0
    first_download_url = ""
    first_file_id = ""

    for f in files:
        if not os.path.isfile(f):
            continue

        result = upload_file(f, session)
        if result and result.get("zt") == 1:
            uploaded_count += 1
            if not first_download_url:
                text_list = result.get("text", [])
                if text_list and isinstance(text_list, list) and len(text_list) > 0:
                    first_item = text_list[0]
                    first_file_id = str(first_item.get("f_id", ""))
                    # 尝试构造下载URL
                    is_newd = first_item.get("is_newd", "")
                    if is_newd and first_file_id:
                        first_download_url = f"{is_newd}/{first_file_id}"
                    else:
                        first_download_url = ""
                else:
                    first_file_id = str(result.get("f_id", "") or result.get("id", ""))

    session.close()

    # 设置输出
    set_output("download_url", first_download_url)
    set_output("file_id", first_file_id)
    set_output("uploaded_count", str(uploaded_count))

    print(f"\n🎉 上传完成: {uploaded_count}/{len(files)} 个文件成功")

    if uploaded_count == 0:
        print("::error::没有文件上传成功")
        sys.exit(1)


if __name__ == "__main__":
    main()

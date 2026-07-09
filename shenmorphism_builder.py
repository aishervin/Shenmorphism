#!/usr/bin/env python3
"""
SHΞN™ Morphism - UI Galaxy Builder v2
با نام‌گذاری اعداد، رفع محدودیت ۱۰۰۰ فایل، و برندسازی کامل
"""

import os
import json
import shutil
import subprocess
import sys
import re
from pathlib import Path
from datetime import datetime
import requests
from bs4 import BeautifulSoup

# ============================================================
# Configuration
# ============================================================
REPO_URL = "https://github.com/uiverse-io/galaxy.git"
REPO_DIR = Path("./galaxy_source")
OUTPUT_DIR = Path("./shenmorphism_ui_kit")
INDEX_FILE = Path("./index.json")
BRAND_NAME = "SHΞN™ Morphism"
BRAND_SLUG = "shenmorphism"
COMMIT_TITLE = "💾 SHΞN™"

CATEGORIES = [
    "Buttons",
    "Cards",
    "Checkboxes",
    "Forms",
    "Inputs",
    "Loaders",
    "Patterns",
    "RadioButtons",
    "Switches",
    "Tooltips"
]

REPLACEMENT_PATTERNS = [
    (r'Uiverse\.io', BRAND_NAME),
    (r'Uiverse', BRAND_NAME),
    (r'uiverse\.io', BRAND_SLUG),
    (r'uiverse', BRAND_SLUG),
    (r'galaxy', f'{BRAND_SLUG}-kit'),
    (r'Galaxy', f'{BRAND_SLUG}-kit'),
    (r'uiverse-io', BRAND_SLUG),
]

# ============================================================
# Functions
# ============================================================

def run_command(cmd, cwd=None):
    try:
        subprocess.run(cmd, cwd=cwd, check=True, capture_output=True, text=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Command failed: {' '.join(cmd)}")
        print(f"   Error: {e.stderr}")
        return False

def clone_repo():
    """Clone galaxy repo با depth=1 برای سرعت بیشتر"""
    if REPO_DIR.exists():
        print("🧹 Removing old galaxy_source...")
        shutil.rmtree(REPO_DIR)
    print("📥 Cloning galaxy repository (shallow clone)...")
    return run_command(["git", "clone", "--depth", "1", REPO_URL, str(REPO_DIR)])

def get_all_html_files():
    """جستجوی همه فایل‌های HTML در کل ریپو (بدون محدودیت)"""
    html_files = []
    for root, dirs, files in os.walk(REPO_DIR):
        for file in files:
            if file.endswith((".html", ".htm")):
                full_path = Path(root) / file
                # تشخیص category از مسیر
                category = "Other"
                for cat in CATEGORIES:
                    if cat in str(full_path):
                        category = cat
                        break
                html_files.append((full_path, category))
    return html_files

def rebrand_content(content):
    for pattern, replacement in REPLACEMENT_PATTERNS:
        content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)
    return content

def extract_metadata(file_path, category, index):
    content = file_path.read_text(encoding='utf-8', errors='ignore')
    name = file_path.stem.replace('-', ' ').title()
    title_match = re.search(r'<title>(.*?)</title>', content, re.IGNORECASE)
    if title_match:
        name = title_match.group(1).strip()
    author = "Community"
    author_match = re.search(r'<!--\s*Author:\s*(.*?)\s*-->', content, re.IGNORECASE)
    if author_match:
        author = author_match.group(1).strip()
    return {
        "index": index,
        "id": file_path.stem,
        "name": name,
        "category": category,
        "author": author,
        "brand": BRAND_NAME,
        "license": "MIT"
    }

def build_ui_kit():
    print("\n" + "="*60)
    print(f"🚀 {BRAND_NAME} - UI Galaxy Builder v2")
    print("="*60 + "\n")

    # Clone repository
    if not clone_repo():
        print("❌ Failed to clone galaxy repo.")
        return False

    # Clear output
    if OUTPUT_DIR.exists():
        shutil.rmtree(OUTPUT_DIR)
    OUTPUT_DIR.mkdir(parents=True)

    # Get all HTML files
    print("🔍 Scanning for HTML files...")
    html_files = get_all_html_files()
    print(f"✅ Found {len(html_files)} HTML files.")

    # Process files with numbering
    all_components = []
    category_counts = {cat: 0 for cat in CATEGORIES}

    for file_path, category in html_files:
        # افزایش شمارنده برای هر دسته
        category_counts[category] = category_counts.get(category, 0) + 1
        count = category_counts[category]

        # ساخت نام جدید: Category-Number.html
        new_name = f"{category}-{count}.html"
        output_category_dir = OUTPUT_DIR / category
        output_category_dir.mkdir(parents=True, exist_ok=True)
        output_file = output_category_dir / new_name

        # Rebrand و ذخیره
        content = file_path.read_text(encoding='utf-8', errors='ignore')
        rebranded = rebrand_content(content)
        output_file.write_text(rebranded, encoding='utf-8')

        # متادیتا
        meta = extract_metadata(file_path, category, count)
        all_components.append(meta)

    # اضافه کردن دسته‌های خالی (اگر هیچ فایلی نداشته باشن)
    for cat in CATEGORIES:
        if cat not in category_counts:
            category_counts[cat] = 0

    total = len(all_components)

    # Save index
    index_data = {
        "brand": BRAND_NAME,
        "version": "2.0.0",
        "generated": datetime.now().isoformat(),
        "total_components": total,
        "categories": category_counts,
        "components": all_components
    }
    INDEX_FILE.write_text(json.dumps(index_data, indent=2, ensure_ascii=False), encoding='utf-8')

    # README (بدون ذکر نام اصلی)
    readme = f"""# {BRAND_NAME} UI Kit

> **{total}** آماده‌ی استفاده، با مجوز MIT.

## 📁 دسته‌بندی
{chr(10).join([f"- **{cat}**: {count} قطعه" for cat, count in category_counts.items() if count > 0])}

## 🚀 استفاده
فایل‌های HTML را مستقیماً در پروژه‌های خود استفاده کنید.

## 📄 لایسنس
MIT License
"""
    (OUTPUT_DIR / "README.md").write_text(readme, encoding='utf-8')

    print("\n" + "="*60)
    print("✅ BUILD COMPLETE!")
    print(f"📊 Total components: {total}")
    for cat, count in category_counts.items():
        if count > 0:
            print(f"   📂 {cat}: {count} files")
    print(f"📁 Output: {OUTPUT_DIR.absolute()}")
    print("="*60)
    return True

if __name__ == "__main__":
    sys.exit(0 if build_ui_kit() else 1)

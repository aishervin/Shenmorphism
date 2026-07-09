#!/usr/bin/env python3
"""
SHΞN™ Morphism - UI Galaxy Builder
Automated build script for GitHub Actions
"""

import os
import json
import shutil
import subprocess
import sys
from pathlib import Path
from datetime import datetime
import re

# ============================================================
# Configuration
# ============================================================
REPO_URL = "https://github.com/uiverse-io/galaxy.git"
REPO_DIR = Path("./galaxy_source")
OUTPUT_DIR = Path("./shenmorphism_ui_kit")
INDEX_FILE = Path("./index.json")  # index رو بذار توی ریشه
BRAND_NAME = "SHΞN™ Morphism"
BRAND_SLUG = "shenmorphism"

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
]

# ============================================================
# Core Functions
# ============================================================

def run_command(cmd, cwd=None):
    try:
        subprocess.run(cmd, cwd=cwd, check=True, capture_output=True, text=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Command failed: {' '.join(cmd)}")
        print(f"   Error: {e.stderr}")
        return False

def clone_or_update_repo():
    if not REPO_DIR.exists():
        print("📥 Cloning galaxy repository...")
        return run_command(["git", "clone", "--depth", "1", REPO_URL, str(REPO_DIR)])
    else:
        print("🔄 Updating galaxy repository...")
        return run_command(["git", "pull"], cwd=REPO_DIR)

def rebrand_content(content):
    for pattern, replacement in REPLACEMENT_PATTERNS:
        content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)
    return content

def extract_metadata(file_path, category):
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
        "id": file_path.stem,
        "name": name,
        "category": category,
        "author": author,
        "source_file": str(file_path.relative_to(REPO_DIR)),
        "brand": BRAND_NAME,
        "license": "MIT"
    }

def process_component(file_path, category, output_category_dir):
    try:
        content = file_path.read_text(encoding='utf-8', errors='ignore')
        rebranded = rebrand_content(content)
        output_category_dir.mkdir(parents=True, exist_ok=True)
        output_file = output_category_dir / file_path.name
        output_file.write_text(rebranded, encoding='utf-8')
        return extract_metadata(file_path, category)
    except Exception as e:
        print(f"⚠️  Error processing {file_path.name}: {e}")
        return None

def build_ui_kit():
    print("\n" + "="*60)
    print("🚀 SHΞN™ Morphism - UI Galaxy Builder (GitHub Action)")
    print("="*60 + "\n")

    if not clone_or_update_repo():
        print("❌ Failed to clone/update galaxy repo.")
        return False

    if OUTPUT_DIR.exists():
        shutil.rmtree(OUTPUT_DIR)
    OUTPUT_DIR.mkdir(parents=True)

    all_components = []
    total = 0

    for category in CATEGORIES:
        category_path = REPO_DIR / category
        if not category_path.exists():
            print(f"⚠️  Category '{category}' not found, skipping.")
            continue

        output_category_dir = OUTPUT_DIR / category
        html_files = list(category_path.glob("*.html")) + list(category_path.glob("*.htm"))

        for html_file in html_files:
            meta = process_component(html_file, category, output_category_dir)
            if meta:
                all_components.append(meta)
                total += 1

        print(f"   ✅ {category}: {len(html_files)} components")

    # Save index
    index_data = {
        "brand": BRAND_NAME,
        "version": "1.0.0",
        "generated": datetime.now().isoformat(),
        "total_components": total,
        "categories": CATEGORIES,
        "components": all_components
    }
    INDEX_FILE.write_text(json.dumps(index_data, indent=2, ensure_ascii=False), encoding='utf-8')

    # README
    readme = f"""# {BRAND_NAME} UI Kit

> The largest Open-Source UI Library! Community-made and free to use.

**{total}** UI components, sourced from Galaxy and rebranded under **{BRAND_NAME}**.

## 📁 Categories
- Buttons · Cards · Checkboxes · Forms · Inputs
- Loaders · Patterns · RadioButtons · Switches · Tooltips

## 📄 License
MIT License

## 🙏 Attribution
Originally from [Uiverse.io](https://uiverse.io/). Curated by **{BRAND_NAME}**.
"""
    (OUTPUT_DIR / "README.md").write_text(readme, encoding='utf-8')

    print("\n" + "="*60)
    print("✅ BUILD COMPLETE!")
    print(f"📊 Total components: {total}")
    print(f"📁 Output: {OUTPUT_DIR.absolute()}")
    print("="*60)
    return True

if __name__ == "__main__":
    sys.exit(0 if build_ui_kit() else 1)

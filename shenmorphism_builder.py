#!/usr/bin/env python3
"""
SHΞN™ Morphism - UI Galaxy Builder
This script clones/updates the uiverse-io/galaxy repository, processes all UI components,
and reorganizes them under the SHΞN™ Morphism brand.
"""

import os
import json
import shutil
import subprocess
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import re

# ============================================================
# Configuration
# ============================================================
REPO_URL = "https://github.com/uiverse-io/galaxy.git"
REPO_DIR = Path("./galaxy_source")
OUTPUT_DIR = Path("./shenmorphism_ui_kit")
INDEX_FILE = OUTPUT_DIR / "index.json"
BRAND_NAME = "SHΞN™ Morphism"
BRAND_SLUG = "shenmorphism"
ORIGINAL_BRAND = "Uiverse.io"
ORIGINAL_BRAND_SHORT = "Uiverse"

# Categories based on actual galaxy repo structure
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

# Patterns to replace for rebranding
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

def run_command(cmd: List[str], cwd: Optional[Path] = None) -> bool:
    """Run a shell command and return success status."""
    try:
        subprocess.run(cmd, cwd=cwd, check=True, capture_output=True, text=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Command failed: {' '.join(cmd)}")
        print(f"   Error: {e.stderr}")
        return False

def clone_or_update_repo():
    """Clone the galaxy repo if it doesn't exist, otherwise pull updates."""
    if not REPO_DIR.exists():
        print(f"📥 Cloning repository from {REPO_URL}...")
        if run_command(["git", "clone", REPO_URL, str(REPO_DIR)]):
            print("✅ Repository cloned successfully.")
            return True
        return False
    else:
        print(f"🔄 Updating existing repository...")
        if run_command(["git", "pull"], cwd=REPO_DIR):
            print("✅ Repository updated successfully.")
            return True
        return False

def rebrand_content(content: str) -> str:
    """Replace all brand-related strings with SHΞN™ Morphism."""
    for pattern, replacement in REPLACEMENT_PATTERNS:
        content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)
    return content

def extract_component_metadata(file_path: Path, category: str) -> Dict:
    """Extract metadata from a component HTML file."""
    content = file_path.read_text(encoding='utf-8', errors='ignore')
    
    # Try to extract title/name from the file
    name = file_path.stem.replace('-', ' ').title()
    
    # Try to find a title tag or h1/h2
    title_match = re.search(r'<title>(.*?)</title>', content, re.IGNORECASE)
    if title_match:
        name = title_match.group(1).strip()
    
    # Try to find author from comment or meta
    author = "Community"
    author_match = re.search(r'<!--\s*Author:\s*(.*?)\s*-->', content, re.IGNORECASE)
    if author_match:
        author = author_match.group(1).strip()
    
    # Detect if it uses Tailwind
    uses_tailwind = 'tailwind' in content.lower() or 'tw-' in content.lower()
    
    # Count lines of code
    lines = content.count('\n') + 1
    
    return {
        "id": file_path.stem,
        "name": name,
        "category": category,
        "author": author,
        "uses_tailwind": uses_tailwind,
        "lines_of_code": lines,
        "source_file": str(file_path.relative_to(REPO_DIR)),
        "brand": BRAND_NAME,
        "license": "MIT",
        "tags": []
    }

def process_component(file_path: Path, category: str, output_category_dir: Path):
    """Process a single component: rebrand and copy to output."""
    try:
        content = file_path.read_text(encoding='utf-8', errors='ignore')
        
        # Rebrand the content
        rebranded_content = rebrand_content(content)
        
        # Create output directory
        output_category_dir.mkdir(parents=True, exist_ok=True)
        
        # Write rebranded file
        output_file = output_category_dir / file_path.name
        output_file.write_text(rebranded_content, encoding='utf-8')
        
        # Extract and return metadata
        metadata = extract_component_metadata(file_path, category)
        return metadata
        
    except Exception as e:
        print(f"⚠️  Error processing {file_path.name}: {e}")
        return None

def build_ui_kit():
    """Main function to build the SHΞN™ Morphism UI Kit."""
    print("\n" + "="*60)
    print(f"🚀 SHΞN™ Morphism - UI Galaxy Builder")
    print("="*60 + "\n")
    
    # Step 1: Clone/Update repository
    if not clone_or_update_repo():
        print("❌ Failed to clone/update repository. Exiting.")
        return False
    
    # Step 2: Prepare output directory
    if OUTPUT_DIR.exists():
        print(f"🧹 Cleaning existing output directory...")
        shutil.rmtree(OUTPUT_DIR)
    OUTPUT_DIR.mkdir(parents=True)
    
    # Step 3: Process each category
    print("\n📦 Processing components...")
    all_components = []
    total_processed = 0
    
    for category in CATEGORIES:
        category_path = REPO_DIR / category
        if not category_path.exists() or not category_path.is_dir():
            print(f"⚠️  Category '{category}' not found, skipping.")
            continue
        
        output_category_dir = OUTPUT_DIR / category
        print(f"   📂 Processing {category}...")
        
        # Find all HTML files in the category
        html_files = list(category_path.glob("*.html")) + list(category_path.glob("*.htm"))
        
        for html_file in html_files:
            metadata = process_component(html_file, category, output_category_dir)
            if metadata:
                all_components.append(metadata)
                total_processed += 1
        
        print(f"      ✅ Processed {len(html_files)} components in {category}")
    
    # Step 4: Generate index file
    print(f"\n📝 Generating index file...")
    index_data = {
        "brand": BRAND_NAME,
        "version": "1.0.0",
        "generated": datetime.now().isoformat(),
        "source_repo": REPO_URL,
        "total_components": total_processed,
        "categories": CATEGORIES,
        "components": all_components
    }
    
    INDEX_FILE.write_text(json.dumps(index_data, indent=2, ensure_ascii=False), encoding='utf-8')
    
    # Step 5: Create a README file
    readme_content = f"""# {BRAND_NAME} UI Kit

> The largest Open-Source UI Library! Community-made and free to use.

This is a curated collection of over **{total_processed}** UI elements, sourced from the original Galaxy repository and rebranded under **{BRAND_NAME}**.

## 📁 Structure

- **Buttons** - Various button styles and interactions
- **Cards** - Card layouts and containers
- **Checkboxes** - Custom checkbox designs
- **Forms** - Form elements and layouts
- **Inputs** - Input field variations
- **Loaders** - Loading animations and spinners
- **Patterns** - Background patterns and textures
- **RadioButtons** - Radio button designs
- **Switches** - Toggle switches
- **Tooltips** - Tooltip components

## 📄 License

All components are available under the **MIT License**.

## 🙏 Attribution

Originally sourced from [Uiverse.io](https://uiverse.io/). Rebranded and curated by **{BRAND_NAME}**.
"""
    
    (OUTPUT_DIR / "README.md").write_text(readme_content, encoding='utf-8')
    
    # Step 6: Summary
    print("\n" + "="*60)
    print("✅ BUILD COMPLETE!")
    print("="*60)
    print(f"📁 Output directory: {OUTPUT_DIR.absolute()}")
    print(f"📄 Index file: {INDEX_FILE.absolute()}")
    print(f"📊 Total components processed: {total_processed}")
    print(f"📂 Categories: {len([c for c in CATEGORIES if (REPO_DIR / c).exists()])}")
    print("\n🔍 Next steps:")
    print("   1. Browse the output directory to see your curated UI kit")
    print("   2. Check index.json for a complete catalog of all components")
    print("   3. Use the components directly in your projects!")
    print("\n✨ SHΞN™ Morphism - Your UI Galaxy is ready!")
    
    return True

# ============================================================
# Entry Point
# ============================================================

if __name__ == "__main__":
    try:
        success = build_ui_kit()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⏹️  Build cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        sys.exit(1)

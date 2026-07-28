#!/usr/bin/env python3
"""
Generate a comprehensive JSON catalog of all UI components in Shenmorphism UI Kit.
This script scans all component directories and extracts raw GitHub links with code content.
Components are labeled with SHΞN™ branding while preserving original content.
"""

import os
import json
import re
from pathlib import Path
from typing import Dict, List, Any

# Configuration
REPO_PATH = "shenmorphism_ui_kit"
CATEGORIES = ["Buttons", "Cards", "Inputs", "Forms", "Checkboxes", "Patterns", "Tooltips", "Other"]
GITHUB_RAW_URL_BASE = "https://raw.githubusercontent.com/aishervin/Shenmorphism/main"
OUTPUT_FILE = "index.json"

# SHΞN™ Branding mapping for display names
BRAND_PREFIX = "SHΞN™"

def get_shen_display_name(filename: str, category: str, index: int) -> str:
    """Generate a SHΞN™ branded display name based on category and index."""
    # Map categories to SHΞN™ style names
    category_map = {
        "Buttons": "Button",
        "Cards": "Card", 
        "Inputs": "Input",
        "Forms": "Form",
        "Checkboxes": "Checkbox",
        "Patterns": "Pattern",
        "Tooltips": "Tooltip",
        "Other": "Component"
    }
    
    base_name = category_map.get(category, "Component")
    
    # Extract number from filename if exists (e.g., Buttons-1 -> 1)
    num_match = re.search(r'-(\d+)\.html$', filename)
    if num_match:
        num = num_match.group(1)
        return f"{BRAND_PREFIX} {base_name} #{num}"
    else:
        return f"{BRAND_PREFIX} {base_name} #{index + 1}"

def get_file_path(category: str, filename: str) -> str:
    """Get the relative path for a component file."""
    return os.path.join(REPO_PATH, category, filename)

def get_raw_github_url(category: str, filename: str) -> str:
    """Get the raw GitHub URL for a component file."""
    file_path = get_file_path(category, filename)
    return f"{GITHUB_RAW_URL_BASE}/{file_path}"

def extract_component_info(filename: str, content: str, category: str, index: int) -> Dict[str, Any]:
    """Extract relevant information from HTML component file with SHΞN™ branding."""
    # Remove excessive whitespace
    cleaned_content = content.strip()
    
    # Generate SHΞN™ branded display name
    display_name = get_shen_display_name(filename, category, index)
    
    # Try to extract tags/description from comments for metadata
    tags_match = re.search(r'Tags:\s*(.+?)(?:\s*-|\s*/|\s*\*/)', content)
    tags = tags_match.group(1).strip() if tags_match else ""
    
    return {
        "id": f"{category}-{index + 1}",
        "name": display_name,  # SHΞN™ branded display name
        "original_filename": filename,  # Keep original filename for reference
        "category": category,
        "tags": tags,
        "status": "ready",
        "raw_url": get_raw_github_url(category, filename),
        "code": cleaned_content,  # Original content preserved
        "size_bytes": len(content)
    }

def scan_directory(category: str) -> List[Dict[str, Any]]:
    """Scan a category directory for component files."""
    components = []
    category_path = os.path.join(REPO_PATH, category)
    
    if not os.path.exists(category_path):
        print(f"⚠️  Directory not found: {category_path}")
        return components
    
    # Get all HTML files in the category
    html_files = sorted([f for f in os.listdir(category_path) if f.endswith('.html')])
    
    for index, filename in enumerate(html_files):
        file_path = os.path.join(category_path, filename)
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            component_info = extract_component_info(filename, content, category, index)
            components.append(component_info)
            print(f"✓ Processed {category}/{filename} → {component_info['name']}")
        
        except Exception as e:
            print(f"✗ Error reading {file_path}: {e}")
    
    return components

def generate_catalog() -> Dict[str, Any]:
    """Generate the complete UI Kit catalog."""
    catalog = {
        "metadata": {
            "project": "Shenmorphism UI Kit",
            "description": "Comprehensive catalog of all UI components with raw GitHub links and code content",
            "version": "1.0",
            "last_updated": None,
            "total_components": 0,
            "categories": []
        },
        "components": []
    }
    
    total_components = 0
    
    # Scan each category
    for category in CATEGORIES:
        print(f"\n📁 Scanning category: {category}")
        components = scan_directory(category)
        
        if components:
            catalog["components"].extend(components)
            total_components += len(components)
            catalog["metadata"]["categories"].append({
                "name": category,
                "count": len(components)
            })
            print(f"   Found {len(components)} components")
    
    # Update metadata
    catalog["metadata"]["total_components"] = total_components
    from datetime import datetime
    catalog["metadata"]["last_updated"] = datetime.now().isoformat()
    
    return catalog

def save_catalog(catalog: Dict[str, Any], output_path: str = OUTPUT_FILE) -> None:
    """Save the catalog to a JSON file."""
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(catalog, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Catalog saved to: {output_path}")
    
    # Print summary
    print(f"\n📊 Summary:")
    print(f"   Total Components: {catalog['metadata']['total_components']}")
    print(f"   Categories: {len(catalog['metadata']['categories'])}")
    print(f"   File Size: {os.path.getsize(output_path) / 1024:.2f} KB")

def main():
    """Main entry point."""
    print("🚀 Starting UI Kit Catalog Generation\n")
    
    # Check if we're in the right directory
    if not os.path.exists(REPO_PATH):
        print(f"❌ Error: {REPO_PATH} directory not found!")
        print("   Please run this script from the repository root.")
        return
    
    # Generate catalog
    catalog = generate_catalog()
    
    # Save to JSON
    save_catalog(catalog)
    
    print("\n✨ Catalog generation complete!")

if __name__ == "__main__":
    main()

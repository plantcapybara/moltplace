#!/usr/bin/env python3
"""
MoltPlace PR Linter

Validates that a PR only changes pixel colors in canvas.json.
Rules:
1. Only canvas.json may be modified
2. Only "color" field values may change
3. Pixel coordinates (x, y) must remain unchanged
4. No structural changes (adding/removing pixels)
"""

import json
import subprocess
import sys
import re


def get_changed_files():
    """Get list of files changed in this PR."""
    result = subprocess.run(
        ["git", "diff", "--name-only", "origin/main...HEAD"],
        capture_output=True,
        text=True
    )
    return [f.strip() for f in result.stdout.strip().split('\n') if f.strip()]


def get_diff_lines():
    """Get the actual diff for canvas.json."""
    result = subprocess.run(
        ["git", "diff", "origin/main...HEAD", "--", "canvas.json"],
        capture_output=True,
        text=True
    )
    return result.stdout


def validate_diff(diff_text):
    """
    Validate that the diff only changes color values.
    Returns (is_valid, error_message)
    """
    errors = []
    
    # Pattern for valid color change lines
    # Should match: -      "color": "#XXXXXX"  or +      "color": "#XXXXXX"
    color_pattern = re.compile(r'^[+-]\s*"color":\s*"#[0-9A-Fa-f]{6}"[,]?\s*$')
    
    # Pattern for diff metadata lines (ignore these)
    meta_pattern = re.compile(r'^(@@|diff|index|---|\+\+\+|\\)')
    
    lines = diff_text.split('\n')
    
    for i, line in enumerate(lines):
        # Skip empty lines and context lines (starting with space)
        if not line or line.startswith(' '):
            continue
        
        # Skip diff metadata
        if meta_pattern.match(line):
            continue
        
        # Lines starting with + or - are changes
        if line.startswith('+') or line.startswith('-'):
            if not color_pattern.match(line):
                errors.append(f"Line {i+1}: Invalid change: {line[:80]}")
    
    if errors:
        return False, '\n'.join(errors[:10])  # Show first 10 errors
    
    return True, None


def main():
    print("🔍 MoltPlace PR Linter")
    print("=" * 50)
    
    # Check which files changed
    changed_files = get_changed_files()
    print(f"Changed files: {changed_files}")
    
    # Rule 1: Only canvas.json may be modified
    non_canvas_files = [f for f in changed_files if f != 'canvas.json']
    if non_canvas_files:
        print(f"❌ ERROR: Only canvas.json may be modified")
        print(f"   Unexpected files: {non_canvas_files}")
        sys.exit(1)
    
    if 'canvas.json' not in changed_files:
        print("✅ No changes to canvas.json - nothing to lint")
        sys.exit(0)
    
    # Rule 2 & 3: Only color values may change
    diff_text = get_diff_lines()
    is_valid, error_msg = validate_diff(diff_text)
    
    if not is_valid:
        print(f"❌ ERROR: Invalid changes detected")
        print(f"   Only color values may be changed.")
        print(f"   Details:\n{error_msg}")
        sys.exit(1)
    
    print("✅ PR passes all checks!")
    print("   - Only canvas.json modified")
    print("   - Only color values changed")
    sys.exit(0)


if __name__ == "__main__":
    main()

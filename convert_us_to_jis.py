#!/usr/bin/env python3
"""
Convert US keyboard layout keymap to JIS keyboard layout

Usage:
    python convert_us_to_jis.py input.keymap
    
This will:
    - Backup original file to input.keymap_original
    - Convert and save to input.keymap
"""

import re
import sys
import shutil
from pathlib import Path
from typing import Dict, List, Tuple

# Conversion table: (JP_define_name, [US_key_names], define_value, symbol_comment)
# Multiple US key name variations are supported in the list
CONVERSION_TABLE: List[Tuple[str, List[str], str, str]] = [
    ("JP_DQUOTE", ["DOUBLE_QUOTES", "DOUBLE_QUOTE", "DQT"], "AT", '"'),
    ("JP_AMPERSAND", ["AMPERSAND", "AMPS", "AMP"], "CARET", "&"),
    ("JP_QUOTE", ["SINGLE_QUOTE", "SQT", "APOS"], "AMPERSAND", "'"),
    ("JP_EQUAL", ["EQUAL", "EQL"], "UNDERSCORE", "="),
    ("JP_CARET", ["CARET"], "EQUAL", "^"),
    ("JP_YEN", ["YEN"], "0x89", "¥"),
    ("JP_PLUS", ["PLUS"], "COLON", "+"),
    ("JP_TILDE", ["TILDE"], "PLUS", "~"),
    ("JP_PIPE", ["PIPE"], "LS(0x89)", "|"),
    ("JP_AT", ["AT"], "LEFT_BRACKET", "@"),
    ("JP_COLON", ["COLON"], "SINGLE_QUOTE", ":"),
    ("JP_ASTERISK", ["ASTERISK", "ASTRK", "STAR"], "DOUBLE_QUOTES", "*"),
    ("JP_BACKQUOTE", ["BACKQUOTE", "GRAVE"], "LEFT_BRACE", "`"),
    ("JP_UNDERSCORE", ["UNDERSCORE", "UNDER"], "LS(0x87)", "_"),
    ("JP_LBRACKET", ["LEFT_BRACKET", "LBKT", "LBRC"], "RIGHT_BRACKET", "["),
    ("JP_RBRACKET", ["RIGHT_BRACKET", "RBKT", "RBRC"], "BACKSLASH", "]"),
    ("JP_LPAREN", ["LEFT_PARENTHESIS", "LPAR"], "ASTERISK", "("),
    ("JP_RPAREN", ["RIGHT_PARENTHESIS", "RPAR"], "LEFT_PARENTHESIS", ")"),
    ("JP_LBRACE", ["LEFT_BRACE", "LBRC"], "RIGHT_BRACE", "{"),
    ("JP_RBRACE", ["RIGHT_BRACE", "RBRC"], "PIPE", "}"),
    ("JP_KANA", ["KANA"], "LANGUAGE_1", "kana"),
    ("JP_EISU", ["EISU"], "LANGUAGE_2", "eisu"),
    ("JP_HANZEN", ["HANZEN", "HANKAKU_ZENKAKU"], "GRAVE", "hankaku/zenkaku"),
]


def generate_define_header() -> str:
    """Generate #define header for JIS layout"""
    lines = [
        "// ========================================",
        "// JIS Keyboard Layout Definitions",
        "// ========================================",
    ]
    
    for jp_name, _, us_value, comment in CONVERSION_TABLE:
        # Align define names with padding
        padding = " " * (20 - len(jp_name))
        lines.append(f"#define {jp_name}{padding}{us_value:<20}// {comment}")
    
    lines.append("")  # Add blank line
    return "\n".join(lines)


def create_conversion_map() -> Dict[str, str]:
    """Create US -> JP conversion map"""
    conversion_map = {}
    
    for jp_name, us_names, _, _ in CONVERSION_TABLE:
        for us_name in us_names:
            conversion_map[us_name] = jp_name
    
    return conversion_map


def convert_keymap_line(line: str, conversion_map: Dict[str, str]) -> str:
    """Convert a single line of keymap"""
    # Match pattern: &kp KEYNAME
    pattern = r'&kp\s+([A-Z_0-9]+)'
    
    def replace_key(match):
        key_name = match.group(1)
        if key_name in conversion_map:
            return f"&kp {conversion_map[key_name]}"
        return match.group(0)  # Keep original if not in conversion map
    
    return re.sub(pattern, replace_key, line)


def convert_file(input_path: str) -> None:
    """Convert keymap file from US to JIS layout"""
    input_file = Path(input_path)
    
    # Check if input file exists
    if not input_file.exists():
        print(f"Error: File '{input_path}' not found", file=sys.stderr)
        sys.exit(1)
    
    # Create backup file path
    backup_file = Path(f"{input_path}_original")
    
    # Backup original file
    try:
        shutil.copy2(input_file, backup_file)
        print(f"Backup created: {backup_file}")
    except Exception as e:
        print(f"Error creating backup: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Read original file
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except Exception as e:
        print(f"Error reading file: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Convert lines
    conversion_map = create_conversion_map()
    converted_lines = []
    conversion_count = 0
    
    for line in lines:
        original_line = line
        converted_line = convert_keymap_line(line, conversion_map)
        converted_lines.append(converted_line)
        
        # Count conversions
        if original_line != converted_line:
            conversion_count += 1
    
    # Generate output with header
    header = generate_define_header()
    output_content = header + "\n" + "".join(converted_lines)
    
    # Write converted file
    try:
        with open(input_file, 'w', encoding='utf-8') as f:
            f.write(output_content)
        print(f"Conversion completed: {input_file}")
        print(f"Lines converted: {conversion_count}")
        print(f"Total key definitions: {len(conversion_map)}")
    except Exception as e:
        print(f"Error writing file: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    if len(sys.argv) != 2:
        print("Usage: python convert_us_to_jis.py <input_keymap_file>")
        print("\nExample:")
        print("  python convert_us_to_jis.py input.keymap")
        print("\nThis will:")
        print("  - Backup: input.keymap -> input.keymap_original")
        print("  - Convert: input.keymap (overwritten with JIS layout)")
        sys.exit(1)
    
    input_file = sys.argv[1]
    convert_file(input_file)


if __name__ == "__main__":
    main()
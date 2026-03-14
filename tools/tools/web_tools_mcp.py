#!/usr/bin/env python3
"""
Web Tools MCP Server
Provides tools to interact with web-based applications without login requirements
"""

import json
import base64
from typing import Any, Dict, List
from urllib.parse import quote


def text_to_base64(text: str) -> str:
    """Encode text to Base64 format"""
    try:
        encoded = base64.b64encode(text.encode('utf-8')).decode('utf-8')
        return json.dumps({
            "success": True,
            "original": text,
            "encoded": encoded,
            "length": len(encoded)
        }, indent=2)
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)}, indent=2)


def base64_to_text(encoded: str) -> str:
    """Decode Base64 to text"""
    try:
        decoded = base64.b64decode(encoded).decode('utf-8')
        return json.dumps({
            "success": True,
            "encoded": encoded,
            "decoded": decoded,
            "length": len(decoded)
        }, indent=2)
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)}, indent=2)


def reverse_text(text: str) -> str:
    """Reverse the given text"""
    try:
        reversed_text = text[::-1]
        return json.dumps({
            "success": True,
            "original": text,
            "reversed": reversed_text
        }, indent=2)
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)}, indent=2)


def count_text_stats(text: str) -> str:
    """Count various statistics about the text"""
    try:
        lines = text.split('\n')
        words = text.split()
        chars = len(text)
        chars_no_spaces = len(text.replace(' ', '').replace('\n', '').replace('\t', ''))
        
        return json.dumps({
            "success": True,
            "characters": chars,
            "characters_no_spaces": chars_no_spaces,
            "words": len(words),
            "lines": len(lines),
            "sentences": text.count('.') + text.count('!') + text.count('?'),
            "paragraphs": len([p for p in text.split('\n\n') if p.strip()])
        }, indent=2)
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)}, indent=2)


def sort_lines(text: str, ascending: bool = True) -> str:
    """Sort lines in text alphabetically"""
    try:
        lines = text.split('\n')
        sorted_lines = sorted(lines, reverse=not ascending)
        sorted_text = '\n'.join(sorted_lines)
        
        return json.dumps({
            "success": True,
            "original": text,
            "sorted": sorted_text,
            "order": "ascending" if ascending else "descending"
        }, indent=2)
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)}, indent=2)


def find_and_replace(text: str, find: str, replace: str, case_sensitive: bool = True) -> str:
    """Find and replace text patterns"""
    try:
        if not case_sensitive:
            import re
            pattern = re.compile(re.escape(find), re.IGNORECASE)
            result = pattern.sub(replace, text)
            count = len(pattern.findall(text))
        else:
            count = text.count(find)
            result = text.replace(find, replace)
        
        return json.dumps({
            "success": True,
            "original": text,
            "result": result,
            "replacements_made": count
        }, indent=2)
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)}, indent=2)


def generate_random_password(length: int = 16, include_symbols: bool = True) -> str:
    """Generate a random secure password"""
    try:
        import random
        import string
        
        chars = string.ascii_letters + string.digits
        if include_symbols:
            chars += string.punctuation
        
        password = ''.join(random.choice(chars) for _ in range(length))
        
        return json.dumps({
            "success": True,
            "password": password,
            "length": len(password),
            "includes_symbols": include_symbols
        }, indent=2)
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)}, indent=2)


def shuffle_text(text: str, mode: str = "words") -> str:
    """Shuffle text by words, lines, or characters"""
    try:
        import random
        
        if mode == "words":
            items = text.split()
            random.shuffle(items)
            result = ' '.join(items)
        elif mode == "lines":
            items = text.split('\n')
            random.shuffle(items)
            result = '\n'.join(items)
        elif mode == "characters":
            items = list(text)
            random.shuffle(items)
            result = ''.join(items)
        else:
            return json.dumps({"success": False, "error": f"Invalid mode: {mode}"}, indent=2)
        
        return json.dumps({
            "success": True,
            "original": text,
            "shuffled": result,
            "mode": mode
        }, indent=2)
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)}, indent=2)


def convert_case(text: str, case_type: str) -> str:
    """Convert text case"""
    try:
        if case_type == "upper":
            result = text.upper()
        elif case_type == "lower":
            result = text.lower()
        elif case_type == "title":
            result = text.title()
        elif case_type == "sentence":
            sentences = text.split('. ')
            result = '. '.join(s.capitalize() for s in sentences)
        else:
            return json.dumps({"success": False, "error": f"Invalid case type: {case_type}"}, indent=2)
        
        return json.dumps({
            "success": True,
            "original": text,
            "converted": result,
            "case_type": case_type
        }, indent=2)
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)}, indent=2)


def remove_duplicates(text: str, mode: str = "lines") -> str:
    """Remove duplicate lines or words from text"""
    try:
        if mode == "lines":
            items = text.split('\n')
        elif mode == "words":
            items = text.split()
        else:
            return json.dumps({"success": False, "error": f"Invalid mode: {mode}"}, indent=2)
        
        seen = set()
        unique = []
        for item in items:
            if item not in seen:
                seen.add(item)
                unique.append(item)
        
        result = ('\n' if mode == "lines" else ' ').join(unique)
        duplicates_removed = len(items) - len(unique)
        
        return json.dumps({
            "success": True,
            "original": text,
            "result": result,
            "duplicates_removed": duplicates_removed,
            "mode": mode
        }, indent=2)
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)}, indent=2)


def url_encode(text: str) -> str:
    """URL encode text"""
    try:
        encoded = quote(text)
        return json.dumps({
            "success": True,
            "original": text,
            "encoded": encoded
        }, indent=2)
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)}, indent=2)


def json_beautify(json_text: str) -> str:
    """Beautify (pretty print) JSON"""
    try:
        parsed = json.loads(json_text)
        beautified = json.dumps(parsed, indent=2, sort_keys=False)
        
        return json.dumps({
            "success": True,
            "original": json_text,
            "beautified": beautified
        }, indent=2)
    except json.JSONDecodeError as e:
        return json.dumps({"success": False, "error": f"Invalid JSON: {str(e)}"}, indent=2)
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)}, indent=2)


def json_minify(json_text: str) -> str:
    """Minify JSON (remove whitespace)"""
    try:
        parsed = json.loads(json_text)
        minified = json.dumps(parsed, separators=(',', ':'))
        
        original_size = len(json_text)
        minified_size = len(minified)
        saved = original_size - minified_size
        
        return json.dumps({
            "success": True,
            "original": json_text,
            "minified": minified,
            "original_size": original_size,
            "minified_size": minified_size,
            "bytes_saved": saved,
            "reduction_percent": round((saved / original_size) * 100, 2) if original_size > 0 else 0
        }, indent=2)
    except json.JSONDecodeError as e:
        return json.dumps({"success": False, "error": f"Invalid JSON: {str(e)}"}, indent=2)
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)}, indent=2)


def get_available_tools(input_data: str = "") -> str:
    """Get list of available web tools"""
    tools = [
        {"name": "Text to Base64", "function": "webtools_base64_encode", "description": "Encode text to Base64 format"},
        {"name": "Base64 to Text", "function": "webtools_base64_decode", "description": "Decode Base64 back to text"},
        {"name": "Reverse Text", "function": "webtools_reverse", "description": "Reverse the order of characters"},
        {"name": "Count Stats", "function": "webtools_stats", "description": "Get text statistics"},
        {"name": "Sort Lines", "function": "webtools_sort", "description": "Sort lines alphabetically"},
        {"name": "Find & Replace", "function": "webtools_find_replace", "description": "Find and replace patterns"},
        {"name": "Generate Password", "function": "webtools_password", "description": "Generate secure passwords"},
        {"name": "Shuffle Text", "function": "webtools_shuffle", "description": "Shuffle words/lines/characters"},
        {"name": "Convert Case", "function": "webtools_case", "description": "Convert text case"},
        {"name": "Remove Duplicates", "function": "webtools_dedup", "description": "Remove duplicate lines/words"},
        {"name": "URL Encode", "function": "webtools_url_encode", "description": "Encode text for URLs"},
        {"name": "JSON Beautify", "function": "webtools_json_beautify", "description": "Format JSON with indentation"},
        {"name": "JSON Minify", "function": "webtools_json_minify", "description": "Remove whitespace from JSON"}
    ]
    
    result = "Available Web Tools (No Login Required):\n\n"
    for i, tool in enumerate(tools, 1):
        result += f"{i}. {tool['name']} ({tool['function']})\n"
        result += f"   - {tool['description']}\n\n"
    
    return result

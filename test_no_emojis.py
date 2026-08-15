import os
import sys

def contains_emoji(text):
    for char in text:
        cp = ord(char)
        if (0x1F600 <= cp <= 0x1F64F or
            0x1F300 <= cp <= 0x1F5FF or
            0x1F680 <= cp <= 0x1F6FF or
            0x1F1E0 <= cp <= 0x1F1FF or
            0x2600  <= cp <= 0x26FF  or
            0x2700  <= cp <= 0x27BF  or
            0x1F900 <= cp <= 0x1F9FF or
            0x1FA70 <= cp <= 0x1FAFF or
            0x2300  <= cp <= 0x23FF  or
            0x2B00  <= cp <= 0x2BFF):
            return True, char
    return False, None

SCAN_PATHS = ["frontend", "backend", "docs", "README.md", "app.py", "tests"]
EXCLUDE_DIRS = {"node_modules", ".git", "dist", "build", "__pycache__", ".venv"}

def scan_file(filepath):
    violations = []
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            for line_num, line in enumerate(f, 1):
                has_emoji, char = contains_emoji(line)
                if has_emoji:
                    violations.append((filepath, line_num, char))
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
    return violations

def main():
    root_dir = os.path.dirname(os.path.abspath(__file__))
    all_violations = []

    for path in SCAN_PATHS:
        full_path = os.path.join(root_dir, path)
        if os.path.isfile(full_path):
            all_violations.extend(scan_file(full_path))
        elif os.path.isdir(full_path):
            for current_root, dirs, files in os.walk(full_path):
                dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
                for file in files:
                    if file.endswith((".py", ".jsx", ".js", ".tsx", ".ts", ".html", ".css", ".md", ".json")):
                        filepath = os.path.join(current_root, file)
                        all_violations.extend(scan_file(filepath))

    print("==========================================")
    print("EMOJI RECURSIVE SCANNER REPORT")
    print("==========================================")
    if all_violations:
        print(f"FAILED: Found {len(all_violations)} emoji violations:\n")
        for v_file, v_line, v_char in all_violations:
            rel = os.path.relpath(v_file, root_dir)
            hex_val = hex(ord(v_char))
            print(f"  {rel}:{v_line} -> Offending character: {hex_val}")
        sys.exit(1)
    else:
        print("Emoji scan: PASS")
        sys.exit(0)

if __name__ == "__main__":
    main()

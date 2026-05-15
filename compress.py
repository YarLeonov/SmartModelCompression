#!/usr/bin/env python3
import argparse
import json
import re
import zlib
import tarfile
import os
from pathlib import Path
from typing import Set

class DeckParser:
    def __init__(self, root_dir: Path):
        self.root_dir = root_dir.resolve()
        self.included_files: Set[Path] = set()

    def parse(self, file_path: Path):
        file_path = file_path.resolve()
        if not file_path.exists(): return
        rel_path = file_path.relative_to(self.root_dir)
        if rel_path in self.included_files: return
        self.included_files.add(rel_path)
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            matches = re.finditer(r'INCLUDE\s+[\'"]?([^\'"]+)[\'"]?', content, re.IGNORECASE)
            for match in matches:
                inc_path = (file_path.parent / match.group(1).strip().replace('\\', '/')).resolve()
                if str(inc_path).startswith(str(self.root_dir)):
                    self.parse(inc_path)
        except: pass

def quantize_floats(text: str) -> str:
    def q(match):
        try: return f"{float(match.group(0)):.6g}"
        except: return match.group(0)
    return re.sub(r'-?\d+\.\d+(?:e[+-]?\d+)?', q, text)

def compress_file(file_path: Path, root_dir: Path, archive: tarfile.TarFile):
    rel_path = file_path.relative_to(root_dir)
    ext = file_path.suffix.lower()
    content = file_path.read_bytes()
    
    if ext in ['.inc', '.data']:
        try:
            text = content.decode('utf-8', errors='ignore')
            processed_text = quantize_floats(text)
            compressed = zlib.compress(processed_text.encode('utf-8'))
            temp_file = Path(f"{rel_path}.z")
            temp_file.parent.mkdir(parents=True, exist_ok=True)
            temp_file.write_bytes(compressed)
            archive.add(temp_file, arcname=str(rel_path) + ".z")
            temp_file.unlink()
            return "compressed_numeric"
        except: pass

    # Fallback for binary or non-numeric
    archive.add(file_path, arcname=str(rel_path))
    return "raw"

def run_compression(input_path: str, output_path: str, progress_callback=None):
    input_dir = Path(input_path).resolve()
    output_archive = Path(output_path).resolve()
    output_archive.parent.mkdir(parents=True, exist_ok=True)
    
    # 1. Map hierarchy
    dp = DeckParser(input_dir)
    data_files = list(input_dir.glob("*.DATA"))
    for df in data_files: dp.parse(df)
    
    # 2. Archive everything
    file_map = {}
    
    # Count total files for progress
    all_files = list(input_dir.rglob("*"))
    total_files = len([f for f in all_files if f.is_file()])
    processed_count = 0

    with tarfile.open(output_archive, "w:gz") as archive:
        # Hierarchy files (smart compression)
        for rel_path in dp.included_files:
            abs_path = input_dir / rel_path
            if abs_path.is_file():
                file_map[str(rel_path)] = compress_file(abs_path, input_dir, archive)
                processed_count += 1
                if progress_callback: progress_callback(processed_count, total_files, f"Compressing {rel_path}")
        
        # Other files (RESULTS, USER, etc.) - simple tar
        for path in all_files:
            if path.is_file():
                rel_path = path.relative_to(input_dir)
                if str(rel_path) not in file_map:
                    archive.add(path, arcname=str(rel_path))
                    file_map[str(rel_path)] = "raw"
                    processed_count += 1
                    if progress_callback: progress_callback(processed_count, total_files, f"Archiving {rel_path}")

    meta = {"files": file_map, "generator": "Antigravity Team"}
    output_archive.with_suffix(output_archive.suffix + ".metadata.json").write_text(json.dumps(meta, indent=2))
    return True

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    
    run_compression(args.input, args.output, lambda c, t, m: print(f"[{c}/{t}] {m}"))

if __name__ == "__main__": main()

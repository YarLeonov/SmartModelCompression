#!/usr/bin/env python3
import argparse
import json
import zlib
import tarfile
from pathlib import Path

def run_decompression(input_path: str, output_path: str, progress_callback=None):
    archive_path = Path(input_path).resolve()
    output_dir = Path(output_path).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    
    if progress_callback: progress_callback(0, 100, "Opening archive...")
    with tarfile.open(archive_path, "r:gz") as archive:
        members = archive.getmembers()
        total_members = len(members)
        # Extract all first
        for i, member in enumerate(members):
            archive.extract(member, output_dir)
            if progress_callback: progress_callback(i + 1, total_members * 2, f"Extracting {member.name}")
        
    # Process .z files
    z_files = list(output_dir.rglob("*.z"))
    total_z = len(z_files)
    for i, path in enumerate(z_files):
        original_rel_path = path.name[:-2]
        original_path = path.parent / original_rel_path
        
        content = path.read_bytes()
        try:
            decompressed = zlib.decompress(content)
            original_path.write_bytes(decompressed)
            path.unlink()
        except: pass
        if progress_callback: progress_callback(total_members + i + 1, total_members + total_z, f"Decompressing {path.name}")
    
    if progress_callback: progress_callback(100, 100, "Done")
    return True

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    
    run_decompression(args.input, args.output, lambda c, t, m: print(f"[{c}/{t}] {m}"))

if __name__ == "__main__": main()

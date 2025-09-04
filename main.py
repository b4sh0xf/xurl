#!/usr/bin/env python3
import argparse
import os
import re
import subprocess
import sys

def decompile_apk(apk_path, output_dir):
    try:
        print(f"[*] decompiling {apk_path} ...")
        subprocess.run(
            ["apktool", "d", "-f", "-o", output_dir, apk_path],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        print(f"[+] apk source code are in: {output_dir}")
    except subprocess.CalledProcessError:
        print("[!] error in decompilation")
        sys.exit(1)

def extract_urls_from_dir(target_dir):
    url_regex = re.compile(
        r"(https?://[^\s'\"<>]+)",
        re.IGNORECASE
    )
    urls = set()

    for root, _, files in os.walk(target_dir):
        for f in files:
            try:
                with open(os.path.join(root, f), "r", errors="ignore") as file:
                    data = file.read()
                    found = url_regex.findall(data)
                    urls.update(found)
            except Exception:
                pass
    return urls

def apply_filters(urls, filters):
    if not filters:
        return urls
    filtered = {u for u in urls if any(f.lower() in u.lower() for f in filters)}
    return filtered

def save_urls(urls, output_file):
    output_file = os.path.expanduser(output_file)
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, "w") as f:
        for u in sorted(urls):
            f.write(u + "\n")
    print(f"[-] urls saved on: {output_file}")

def main():
    parser = argparse.ArgumentParser(description="[+] xurl: extract urls from an apk")
    parser.add_argument("-a", "--apk", required=True, help="apk")
    parser.add_argument("-d", "--decompile", action="store_true", help="decompile apk")
    parser.add_argument("-u", "--urls", action="store_true", help="extract urls")
    parser.add_argument("-f", "--filter", nargs="+", help="Filtros de URL (ex: github, firebase, gitlab, gitea, amazonaws)")
    args = parser.parse_args()

    apk_name = os.path.splitext(os.path.basename(args.apk))[0]

    # base fixa em ~/xurl
    base_dir = os.path.expanduser("~/xurl")
    os.makedirs(base_dir, exist_ok=True)

    # onde salvar decompilação e urls
    decompiled_dir = os.path.join(base_dir, f"{apk_name}_src")
    output_file = os.path.join(base_dir, "apk_urls.txt")

    if args.decompile:
        decompile_apk(args.apk, decompiled_dir)

    if args.urls:
        target_dir = decompiled_dir if os.path.isdir(decompiled_dir) else args.apk
        urls = extract_urls_from_dir(target_dir)

        urls = apply_filters(urls, args.filter)

        if urls:
            save_urls(urls, output_file)
        else:
            print("[!] no urls found")

if __name__ == "__main__":
    main()

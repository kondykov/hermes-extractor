def generate_diff(old_spec, new_spec, output_dir):
    out_path = os.path.join(output_dir, "API_VERSIONS_DIFF.md")

    old_urls = set(old_spec.keys())
    new_urls = set(new_spec.keys())

    added = new_urls - old_urls
    removed = old_urls - new_urls

    with open(out_path, "w", encoding="utf-8") as out:
        out.write("## DIFF API (hbctool)\n\n")
        out.write("### Добавлены:\n")
        for u in sorted(added):
            out.write(f"- {u}\n")

        out.write("\n### Удалены:\n")
        for u in sorted(removed):
            out.write(f"- {u}\n")

    print(f"[+] DIFF готов: {out_path}")

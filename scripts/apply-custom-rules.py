#!/usr/bin/env python3
"""Apply fork-local routing additions to generated routing profiles."""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CUSTOM_DIR = ROOT / "custom"


def read_items(path: Path) -> list[str]:
    items: list[str] = []
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.split("#", 1)[0].strip()
        if line and line not in items:
            items.append(line)
    return items


def update_happ_profiles(
    direct_domains: list[str], proxy_domains: list[str]
) -> None:
    direct_entries = [f"domain:{domain}" for domain in direct_domains]
    proxy_entries = [f"domain:{domain}" for domain in proxy_domains]

    for relative_path in ("HAPP/DEFAULT.JSON", "INCY/DEFAULT.JSON"):
        path = ROOT / relative_path
        data = json.loads(path.read_text(encoding="utf-8"))
        direct_sites = data.setdefault("DirectSites", [])
        changed = False

        for entry in direct_entries:
            if entry not in direct_sites:
                direct_sites.append(entry)
                changed = True

        proxy_sites = data.setdefault("ProxySites", [])
        for entry in proxy_entries:
            if entry not in proxy_sites:
                proxy_sites.append(entry)
                changed = True

        if changed:
            path.write_text(
                json.dumps(data, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )


def managed_block(
    lines: list[str],
    begin_marker: str,
    end_marker: str,
) -> str:
    return "\n".join([begin_marker, *lines, end_marker]) + "\n"


def replace_or_insert_block(
    text: str,
    begin_marker: str,
    end_marker: str,
    block: str,
    anchor: str,
) -> str:
    pattern = re.compile(
        re.escape(begin_marker) + r".*?" + re.escape(end_marker) + r"\r?\n?",
        re.DOTALL,
    )
    # Remove an older managed block first so that changing the source list
    # also moves the block back to its intended precedence position.
    text = pattern.sub("", text, count=1)

    anchor_index = text.find(anchor)
    if anchor_index < 0:
        raise RuntimeError(f"Could not find YAML anchor: {anchor}")

    return text[:anchor_index] + block + text[anchor_index:]


def update_mihomo_profiles(
    direct_domains: list[str], proxy_domains: list[str], processes: list[str]
) -> None:
    direct_domain_lines = [
        f"  - DOMAIN-SUFFIX,{domain},DIRECT" for domain in direct_domains
    ]
    proxy_domain_lines = [
        f"  - DOMAIN-SUFFIX,{domain},PROXY" for domain in proxy_domains
    ]
    process_lines = [f"  - PROCESS-NAME,{process},DIRECT" for process in processes]

    direct_domain_begin = "  # BEGIN CUSTOM DIRECT DOMAINS"
    direct_domain_end = "  # END CUSTOM DIRECT DOMAINS"
    proxy_domain_begin = "  # BEGIN CUSTOM PROXY DOMAINS"
    proxy_domain_end = "  # END CUSTOM PROXY DOMAINS"
    process_begin = "  # BEGIN CUSTOM DIRECT PROCESSES"
    process_end = "  # END CUSTOM DIRECT PROCESSES"

    for relative_path in ("MIHOMO/default.yaml", "MIHOMO/template_remnawave.yaml"):
        path = ROOT / relative_path
        text = path.read_text(encoding="utf-8")

        text = replace_or_insert_block(
            text,
            proxy_domain_begin,
            proxy_domain_end,
            managed_block(
                proxy_domain_lines, proxy_domain_begin, proxy_domain_end
            ),
            "  - RULE-SET,google-play,PROXY",
        )
        text = replace_or_insert_block(
            text,
            direct_domain_begin,
            direct_domain_end,
            managed_block(
                direct_domain_lines, direct_domain_begin, direct_domain_end
            ),
            "  - RULE-SET,google-play,PROXY",
        )
        text = replace_or_insert_block(
            text,
            process_begin,
            process_end,
            managed_block(process_lines, process_begin, process_end),
            "  - RULE-SET,games,🎮 Игры",
        )

        path.write_text(text, encoding="utf-8")


def main() -> None:
    direct_domains = read_items(CUSTOM_DIR / "direct-domains.txt")
    proxy_domains = read_items(CUSTOM_DIR / "proxy-domains.txt")
    processes = read_items(CUSTOM_DIR / "direct-processes.txt")

    if not direct_domains:
        raise SystemExit("custom/direct-domains.txt is empty")
    if not proxy_domains:
        raise SystemExit("custom/proxy-domains.txt is empty")
    if not processes:
        raise SystemExit("custom/direct-processes.txt is empty")

    update_happ_profiles(direct_domains, proxy_domains)
    update_mihomo_profiles(direct_domains, proxy_domains, processes)


if __name__ == "__main__":
    main()

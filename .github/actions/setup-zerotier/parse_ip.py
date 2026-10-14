"""Extract this node's ZeroTier IPv4 address from `zerotier-cli listnetworks` output.

Reads the CLI's raw stdout on stdin and prints a single routable IPv4 address
to stdout. Exits 0 with no output when the network has no address yet (the
caller polls, or reports an authorization problem).

Usage:  zerotier-cli -j listnetworks | python3 parse_ip.py <network-id>

Kept as a standalone file rather than an inline `python3 -c` string so the YAML
block scalar is never terminated by unindented lines.
"""

import json
import re
import sys

# 999.x.x.x is ZeroTier's non-routable placeholder and must never be returned.
PLACEHOLDER_PREFIX = "999."
IPV4 = re.compile(r"\d+\.\d+\.\d+\.\d+")


def iter_addresses(node):
    """Yield candidate addresses from a network entry, tolerating field-name drift."""
    addrs = node.get("addresses") or node.get("address") or []
    if isinstance(addrs, str):
        addrs = [addrs]
    for entry in addrs:
        if isinstance(entry, dict):
            entry = entry.get("ip") or entry.get("address") or ""
        yield str(entry).split("/")[0].strip()


def pick_address(node):
    for ip in iter_addresses(node):
        if IPV4.fullmatch(ip) and not ip.startswith(PLACEHOLDER_PREFIX):
            return ip
    return None


def from_json(raw, target):
    try:
        networks = json.loads(raw)
    except Exception:
        return None
    if not isinstance(networks, list):
        return None
    for node in networks:
        if not isinstance(node, dict):
            continue
        nid = str(node.get("id") or node.get("nwid") or node.get("networkId") or "").lower()
        if nid != target:
            continue
        ip = pick_address(node)
        if ip:
            return ip
    return None


def from_text(raw, target):
    """Fallback: scrape the tab-formatted human-readable listnetworks output."""
    match = re.search(re.escape(target) + r"(.{0,4000})", raw, re.S | re.I)
    if not match:
        return None
    for line in match.group(1).splitlines():
        found = re.search(r"\b(\d+\.\d+\.\d+\.\d+)/", line)
        if found and not found.group(1).startswith(PLACEHOLDER_PREFIX):
            return found.group(1)
    return None


def main():
    if len(sys.argv) < 2:
        print("usage: parse_ip.py <network-id>", file=sys.stderr)
        return 2

    target = sys.argv[1].strip().lower()
    raw = sys.stdin.read()

    address = from_json(raw, target)
    if address is None:
        address = from_text(raw, target)

    if address:
        print(address)
    return 0


if __name__ == "__main__":
    sys.exit(main())
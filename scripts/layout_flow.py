#!/usr/bin/env python3
"""
Layout horizontal em colunas para fluxos Leona via MCP.

- Coluna (X) = profundidade forward (back-edges ignorados).
- Y = empilhamento por altura do bloco (nº de ações).
- Ramos paralelos empilhados na mesma coluna.

Uso:
  python layout_flow.py <flow_id> [--col-w 330] [--gap 70] [--dry-run]

Credenciais: .cursor/mcp.json ou LEONA_MCP_URL + LEONA_MCP_TOKEN.
"""
import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from collections import defaultdict, deque
from pathlib import Path


def find_mcp_config():
    for base in [Path.cwd(), *Path.cwd().parents]:
        cfg = base / ".cursor" / "mcp.json"
        if cfg.exists():
            return cfg
    home = Path.home() / ".cursor" / "mcp.json"
    return home if home.exists() else None


def pick_leona_server(servers):
    if not servers:
        return None
    if "leona" in servers:
        return servers["leona"]
    for k, v in servers.items():
        if "leona" in k.lower():
            return v
    for v in servers.values():
        if "leonasolutions" in (v.get("url") or "").lower():
            return v
    return None


def load_credentials():
    url = os.environ.get("LEONA_MCP_URL")
    token = os.environ.get("LEONA_MCP_TOKEN")
    if url and token:
        return url, token
    cfg = find_mcp_config()
    if not cfg:
        sys.exit("Nao encontrei .cursor/mcp.json nem LEONA_MCP_URL/LEONA_MCP_TOKEN.")
    data = json.loads(cfg.read_text(encoding="utf-8"))
    leona = pick_leona_server(data.get("mcpServers", {}))
    if not leona:
        sys.exit("Nenhum server Leona em mcp.json.")
    url = url or leona["url"]
    if not token:
        auth = (leona.get("headers") or {}).get("Authorization", "")
        token = auth.replace("Bearer ", "").strip()
    if not token:
        sys.exit("Token Leona ausente.")
    return url, token


def mcp_call(url, token, tool, args):
    payload = json.dumps(
        {"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": tool, "arguments": args}}
    ).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=payload,
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        sys.exit(f"HTTP error em {tool}: {e.code} {e.reason}")
    except urllib.error.URLError as e:
        sys.exit(f"URL error em {tool}: {e.reason}")
    if "error" in data:
        sys.exit(f"MCP error em {tool}: {data['error']}")
    return json.loads(data["result"]["content"][0]["text"])


def is_timeout(conn):
    cfg = conn.get("condition_config") or {}
    return conn.get("condition_type") == "timeout_or_unknown" or cfg.get("source_handle") in ("timeout", "b")


def node_height(node, out_count):
    t = node["node_type"]
    a = len(node.get("actions") or [])
    if t == "start":
        return 70
    if t == "tags":
        return 90
    if t == "distributor":
        return 90 + 26 * max(1, out_count)
    if t == "wait_response":
        return 240
    if t == "interactive_menu":
        return 200
    if t == "ai":
        return 120
    return 70 + 40 * max(1, a)


def compute_layout(flow, col_w=330, gap=70, x0=80, y0=80):
    nodes = {n["id"]: n for n in flow["nodes"]}
    conns = flow["connections"]
    outg, inc = defaultdict(list), defaultdict(list)
    for c in conns:
        outg[c["from_node_id"]].append(c)
        inc[c["to_node_id"]].append(c)
    start = next(n["id"] for n in flow["nodes"] if n["node_type"] == "start")

    color = {n: 0 for n in nodes}
    back = set()

    def dfs(u):
        color[u] = 1
        for c in outg[u]:
            v = c["to_node_id"]
            if color[v] == 1:
                back.add((u, v))
            elif color[v] == 0:
                dfs(v)
        color[u] = 2

    sys.setrecursionlimit(10000)
    dfs(start)

    fwd = [c for c in conns if (c["from_node_id"], c["to_node_id"]) not in back]
    o2, i2 = defaultdict(list), defaultdict(list)
    for c in fwd:
        o2[c["from_node_id"]].append(c)
        i2[c["to_node_id"]].append(c)

    layer = {start: 0}
    indeg = {n: len(i2[n]) for n in nodes}
    q = deque([n for n in nodes if indeg[n] == 0])
    topo = []
    while q:
        u = q.popleft()
        topo.append(u)
        for c in o2[u]:
            v = c["to_node_id"]
            indeg[v] -= 1
            if indeg[v] == 0:
                q.append(v)
    for u in topo:
        for c in o2[u]:
            v = c["to_node_id"]
            layer[v] = max(layer.get(v, 0), layer.get(u, 0) + 1)

    by_layer = defaultdict(list)
    for n in nodes:
        by_layer[layer.get(n, 0)].append(n)

    pos = {}
    for L in sorted(by_layer):
        def sortkey(n):
            parents = i2[n]
            py = min([pos[p["from_node_id"]]["y"] for p in parents if p["from_node_id"] in pos], default=0)
            bi = 0
            for p in parents:
                cfg = p.get("condition_config") or {}
                h = cfg.get("output_id") or cfg.get("source_handle") or ""
                if h.startswith("a") and h[1:].isdigit():
                    bi = int(h[1:])
                if is_timeout(p):
                    bi += 100
            return (py, bi, n)

        x = x0 + L * col_w
        y = y0
        for n in sorted(by_layer[L], key=sortkey):
            pos[n] = {"x": x, "y": int(y)}
            y += node_height(nodes[n], len(outg[n])) + gap

    return pos, max(by_layer) + 1 if by_layer else 0


def main():
    ap = argparse.ArgumentParser(description="Layout em colunas para fluxo Leona")
    ap.add_argument("flow_id")
    ap.add_argument("--col-w", type=int, default=330)
    ap.add_argument("--gap", type=int, default=70)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    url, token = load_credentials()
    flow = mcp_call(url, token, "get_flow", {"flow_id": args.flow_id})
    pos, ncols = compute_layout(flow, col_w=args.col_w, gap=args.gap)
    positions = [{"node_id": nid, **p} for nid, p in pos.items()]

    print(f"Fluxo {args.flow_id}: {len(positions)} nos em {ncols} colunas (col_w={args.col_w}px, gap={args.gap}px)")
    if args.dry_run:
        for nid, p in sorted(pos.items(), key=lambda kv: (kv[1]["x"], kv[1]["y"])):
            print(f"  ({p['x']:5},{p['y']:5}) {nid}")
        return
    mcp_call(url, token, "reposition_flow_nodes", {"flow_id": args.flow_id, "positions": positions})
    print("Reposicionado. De refresh / fit view no Leona.")


if __name__ == "__main__":
    main()

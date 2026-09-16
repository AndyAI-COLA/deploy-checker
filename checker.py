# -*- coding: utf-8 -*-
import os
import sys
import json
import time
import socket
import platform
import subprocess
import argparse
from datetime import datetime


class Color:
    """ANSI color codes for terminal output."""
    RESET   = "\033[0m"
    BOLD    = "\033[1m"
    RED     = "\033[91m"
    GREEN   = "\033[92m"
    YELLOW  = "\033[93m"
    BLUE    = "\033[94m"
    CYAN    = "\033[96m"
    DIM     = "\033[2m"


def c(text, color):
    """Wrap text with color and reset."""
    return color + text + Color.RESET


def icon(ok):
    """Return colored [PASS] or [FAIL] icon."""
    if ok:
        return c("[PASS]", Color.GREEN)
    return c("[FAIL]", Color.RED)


def bar(pct):
    """Return a progress bar string."""
    filled = int(pct / 5)
    empty = 20 - filled
    return c("[", Color.DIM) + c("#" * filled, Color.GREEN) + c("." * empty, Color.DIM) + c("]", Color.DIM)


# ── Check functions ─────────────────────────────────────────────────────────

def check_python():
    """Check Python version (>= 3.8)."""
    v = sys.version_info
    vs = f"{v.major}.{v.minor}.{v.micro}"
    ok = v.major >= 3 and v.minor >= 8
    m = f"Version {vs}, OK" if ok else f"Version {vs}, TOO OLD"
    return dict(name="Python", key="python", passed=ok,
                detail=f"Python {vs}", expected=">= 3.8", message=m)


def check_cmd(cmd, name):
    """Check if a command is available and return its version."""
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        ver = r.stdout.strip()
        ok = bool(ver)
        k = name.lower().replace(".", "_")
        if ok:
            detail = ver
            message = ver
        else:
            detail = "Not installed"
            message = f"{name} not found"
        return dict(name=name, key=k, passed=ok, detail=detail,
                    expected="Installed", message=message)
    except FileNotFoundError:
        k = name.lower().replace(".", "_")
        return dict(name=name, key=k, passed=False, detail="Not installed",
                    expected="Installed", message=f"{name} not found")
    except subprocess.TimeoutExpired:
        k = name.lower().replace(".", "_")
        return dict(name=name, key=k, passed=False, detail="Timeout",
                    expected="Installed", message="Timeout")


def check_network():
    """Check network connectivity by pinging 8.8.8.8."""
    try:
        p = "-n" if platform.system().lower() == "windows" else "-c"
        r = subprocess.run(["ping", p, "2", "8.8.8.8"],
                           capture_output=True, text=True, timeout=15)
        ok = r.returncode == 0
        return dict(name="Network", key="network", passed=ok,
                    detail="Reachable" if ok else "Unreachable",
                    expected="Reachable (8.8.8.8)",
                    message="Ping 8.8.8.8 OK" if ok else "Ping FAILED")
    except Exception:
        return dict(name="Network", key="network", passed=False,
                    detail="Error", expected="Reachable (8.8.8.8)",
                    message="Error")


def check_port(port):
    """Check if a specific port on 127.0.0.1 is occupied."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2)
        result = s.connect_ex(("127.0.0.1", port))
        s.close()
        occupied = result == 0
        name = f"Port {port}"
        if occupied:
            return dict(name=name, key="ports", passed=False,
                        detail="Occupied", expected="Available",
                        message=f"{name} is occupied")
        return dict(name=name, key="ports", passed=True,
                    detail="Available", expected="Available",
                    message=f"{name} is available")
    except Exception as e:
        name = f"Port {port}"
        return dict(name=name, key="ports", passed=True,
                    detail="Error", expected="Available", message=str(e))


def check_disk():
    """Check disk free space on the current drive (must be > 5 GB)."""
    try:
        drive = os.path.splitdrive(os.path.abspath("."))[0]
        if platform.system().lower() == "windows":
            import ctypes
            free_bytes = ctypes.c_ulonglong(0)
            total_bytes = ctypes.c_ulonglong(0)
            ctypes.windll.kernel32.GetDiskFreeSpaceExW(
                ctypes.c_wchar_p(drive), None,
                ctypes.pointer(total_bytes), ctypes.pointer(free_bytes))
            free = free_bytes.value / (1024 ** 3)
            total = total_bytes.value / (1024 ** 3)
        else:
            st = os.statvfs(".")
            total = (st.f_blocks * st.f_frsize) / (1024 ** 3)
            free = (st.f_bavail * st.f_frsize) / (1024 ** 3)
        pct = ((total - free) / total * 100) if total > 0 else 0
        ok = free > 5
        name = f"Disk ({drive})"
        if ok:
            msg = f"Usage {round(pct,1)}%, Free {round(free,1)}GB OK"
        else:
            msg = f"Usage {round(pct,1)}%, Free {round(free,1)}GB LOW"
        return dict(name=name, key="disk", passed=ok,
                    detail=f"Free {round(free,1)}GB / Total {round(total,1)}GB",
                    expected="Free > 5 GB", message=msg)
    except Exception as e:
        return dict(name="Disk", key="disk", passed=False,
                    detail="Error", expected="Free > 5 GB", message=str(e))


# ── Run checks ──────────────────────────────────────────────────────────────

def run(only=None):
    """
    Run all checks (or only the ones whose key is in `only`).
    Returns a list of result dicts, each including a duration_ms field.
    """
    res = []
    print()
    print(c("=" * 60, Color.CYAN))
    print(c("  SYSTEM ENVIRONMENT CHECK", Color.BOLD))
    print(c(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", Color.CYAN))
    print(c("=" * 60, Color.CYAN))
    print()

    steps = [
        ("python",  "[1/6] Python version ...",        lambda: check_python()),
        ("node",    "[2/6] Node.js ............",       lambda: check_cmd(["node", "--version"], "Node.js")),
        ("git",     "[3/6] Git .................",      lambda: check_cmd(["git", "--version"], "Git")),
        ("network", "[4/6] Network ............",       lambda: check_network()),
        ("ports",   "[5/6] Ports ..............",       None),
        ("disk",    "[6/6] Disk space .........",      lambda: check_disk()),
    ]

    for key, lbl, fn in steps:
        if only and key not in only:
            continue

        # Ports step: check multiple ports in a loop
        if key == "ports":
            print(c(lbl, Color.BLUE))
            for port in [8080, 3000, 5000]:
                t0 = time.time()
                r = check_port(port)
                r["duration_ms"] = round((time.time() - t0) * 1000)
                res.append(r)
                ms = c(f"({r.get('duration_ms', 0)}ms)", Color.DIM)
                print(f"  {icon(r['passed'])} {r['detail'].ljust(12)} {r['message'].ljust(30)} {ms}")
            print()
            continue

        # Other steps
        print(c(lbl, Color.BLUE))
        t0 = time.time()
        r = fn()
        r["duration_ms"] = round((time.time() - t0) * 1000)
        res.append(r)
        ms = c(f"({r.get('duration_ms', 0)}ms)", Color.DIM)
        print(f"  {icon(r['passed'])} {r['detail'].ljust(20)} {r['message'].ljust(30)} {ms}")
        print()

    return res


# ── Summary ─────────────────────────────────────────────────────────────────

def summary(res):
    """Print a summary of check results to the terminal."""
    total = len(res)
    passed = sum(1 for r in res if r["passed"])
    failed = total - passed
    pct = (passed / total * 100) if total > 0 else 0

    print(c("=" * 60, Color.CYAN))
    print(c("  SUMMARY", Color.BOLD))
    print(c("=" * 60, Color.CYAN))
    print()
    print(f"  Total checks: {total}")
    print(f"  Passed: {c(str(passed), Color.GREEN)}")
    if failed > 0:
        print(f"  Failed: {c(str(failed), Color.RED)}")
    else:
        print(f"  Failed: {failed}")
    print(f"  Score: {bar(pct)} {round(pct)}%")
    print()
    if failed == 0:
        print(c("  >> ALL CHECKS PASSED - System is ready for deployment!", Color.GREEN))
    else:
        print(c(f"  >> {failed} check(s) failed:", Color.YELLOW))
        print()
        for r in res:
            if not r["passed"]:
                print(f"     {c('FAIL', Color.RED)} {r['name']}: {r['message']}")
    print()
    print(c("=" * 60, Color.CYAN))


# ── Save outputs ────────────────────────────────────────────────────────────

def save_log(res, fn):
    """Save a plain-text report to a .log file."""
    lines = [
        "System Check Report",
        f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "=" * 50,
        "",
    ]
    for r in res:
        tag = "PASS" if r["passed"] else "FAIL"
        dur = r.get("duration_ms", 0)
        lines.append(f"[{tag}] {r['name']}: {r['message']} ({dur}ms)")
    lines.append("")
    lines.append("-" * 50)
    total = len(res)
    passed = sum(1 for r in res if r["passed"])
    lines.append(f"Total: {total}, Passed: {passed}, Failed: {total - passed}")
    with open(fn, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def save_json(res, fn):
    """Save a structured report to a .json file."""
    report = dict(
        title="System Check Report",
        time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        system=dict(
            os=platform.system(),
            ver=platform.version(),
            arch=platform.machine(),
            python=platform.python_version(),
        ),
        summary=dict(
            total=len(res),
            passed=sum(1 for r in res if r["passed"]),
            failed=sum(1 for r in res if not r["passed"]),
        ),
        results=res,
    )
    with open(fn, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)


# ── CLI entry point ─────────────────────────────────────────────────────────

def main():
    p = argparse.ArgumentParser(description="System Check Tool")
    p.add_argument("-o", "--output", default="deploy_check_report",
                   help="Output prefix (default: deploy_check_report)")
    p.add_argument("-c", "--check-only", nargs="+",
                   choices=["python", "node", "git", "network", "ports", "disk"],
                   metavar="CHECK",
                   help="Only run specified checks")
    args = p.parse_args()

    res = run(only=args.check_only)
    if not res:
        print(c("  No checks to run.", Color.YELLOW))
        return

    summary(res)

    log_path = args.output + ".log"
    json_path = args.output + ".json"
    save_log(res, log_path)
    save_json(res, json_path)
    print(f"  Log  : {log_path}")
    print(f"  JSON : {json_path}")
    print()


if __name__ == "__main__":
    main()

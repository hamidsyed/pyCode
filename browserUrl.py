import time
import win32gui
import win32process
import psutil
import uiautomation as auto
import re
from urllib.parse import urlparse

SUPPORTED_BROWSERS = {
    "chrome.exe": "chrome",
    "msedge.exe": "edge",
    "firefox.exe": "firefox",
}

def get_foreground_process():
    hwnd = win32gui.GetForegroundWindow()
    if not hwnd:
        return None, None

    _, pid = win32process.GetWindowThreadProcessId(hwnd)
    try:
        proc = psutil.Process(pid)
    except psutil.NoSuchProcess:
        return None, None

    return hwnd, proc


YOUTUBE_SHORTS_REGEX = re.compile(
    r"^https?://(www\.)?youtube\.com/shorts/[A-Za-z0-9_-]{3,}$",
    re.IGNORECASE,
)

def is_youtube_shorts_url(url: str) -> bool:
    if not url:
        return False

    parsed = urlparse(url)
    host = (parsed.netloc or "").lower()
    path = (parsed.path or "").lower()

    if "youtube.com" not in host:
        return False

    # Native shorts path, e.g. /shorts/0dPkkQeRwTI
    if path.startswith("/shorts/") and YOUTUBE_SHORTS_REGEX.match(url):
        return True

    # Fallback: some experimental formats; keep strict to avoid FPs
    return False

def get_browser_url(hwnd, proc_name: str) -> str | None:
    """
    Try to get the URL from the active tab of Chrome/Edge/Firefox using UI Automation.
    """
    # Attach to root AutomationElement of window
    element = auto.ControlFromHandle(hwnd)
    if not element:
        return None

    # Patterns for address bar search differ slightly by browser;
    # we try a few generic heuristics that work on recent versions. [web:18][web:19][web:22][web:25]
    candidates = []

    if proc_name == "chrome.exe" or proc_name == "msedge.exe":
        # In recent builds, the address bar is usually an Edit control with
        # name/value pattern; fallback to searching descendants with "Address and search bar".
        candidates = element.GetChildren()

    elif proc_name == "firefox.exe":
        # In Firefox, the URL bar is an Edit control with certain names; scanning descendants is needed. [web:19][web:26]
        candidates = element.GetChildren()

    # Depth‑limited search for an Edit‑like control that exposes a URL‑looking Value
    url = None

    def dfs(control, depth=0, max_depth=5):
        nonlocal url
        if url is not None or depth > max_depth:
            return

        try:
            # Many browsers expose the URL bar as an 'Edit' control type
            if control.ControlTypeName == "Edit":
                val = control.CurrentValue()
                if val and val.startswith("http"):
                    url_candidate = val.strip()
                    # Minimal sanity check to avoid unrelated edits
                    if " " not in url_candidate and "." in url_candidate:
                        url = url_candidate
                        return
        except Exception:
            pass

        try:
            for child in control.GetChildren():
                dfs(child, depth + 1, max_depth)
                if url is not None:
                    return
        except Exception:
            return

    dfs(element)
    return url

def is_focused_browser_playing_youtube_shorts() -> tuple[bool, str | None]:
    hwnd, proc = get_foreground_process()
    if not hwnd or not proc:
        return False, None

    proc_name = proc.name().lower()
    if proc_name not in SUPPORTED_BROWSERS:
        return False, None

    url = get_browser_url(hwnd, proc_name)
    if not url:
        return False, None

    return is_youtube_shorts_url(url), url

if __name__ == "__main__":
    # Simple poller demo; Ctrl+C to stop.
    while True:
        is_shorts, url = is_focused_browser_playing_youtube_shorts()
        if is_shorts:
            print(f"[+] Focused browser is on YouTube Shorts: {url}")
        else:
            if url:
                print(f"[-] Focused browser URL: {url}")
            else:
                print("[-] No URL detected for focused window.")
        time.sleep(2)

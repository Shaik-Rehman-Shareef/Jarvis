#!/usr/bin/env python3
"""
JARVIS Startup Diagnostic & Auto-Fix Script (Windows)
Runs a full add/remove cycle, verifies both Startup folder shortcut and HKCU Run key.
Usage:
  python startup_diagnostic.py
"""
import os, sys, time, traceback
import winreg

RESULT = {}

def safe(fn, key):
    try:
        return fn()
    except Exception as e:
        RESULT[key] = f"ERROR: {e}"
        return None

def get_run_key_value(name):
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_READ) as k:
            try:
                v, t = winreg.QueryValueEx(k, name)
                return v
            except FileNotFoundError:
                return None
    except Exception:
        return None

def list_startup_shortcut(path):
    if not path or not os.path.exists(path):
        return None
    # Light inspection only (no COM deep read): record size & mtime
    st = os.stat(path)
    return {"exists": True, "size": st.st_size, "modified": time.ctime(st.st_mtime)}

def main():
    print("=== JARVIS STARTUP DIAGNOSTIC ===")
    print(f"Python executable: {sys.executable}")
    print(f"Working directory: {os.getcwd()}")

    # Confirm main.py presence
    base_dir = os.path.dirname(os.path.abspath(__file__))
    main_py = os.path.join(base_dir, 'main.py')
    print(f"main.py found: {os.path.exists(main_py)} -> {main_py}")

    # Import manager
    from startup_manager import startup_manager

    print("\nCurrent status BEFORE:")
    in_startup = startup_manager.is_in_startup()
    print(f"  is_in_startup(): {in_startup}")

    shortcut_info = list_startup_shortcut(getattr(startup_manager, 'shortcut_path', None))
    print(f"  Shortcut path: {getattr(startup_manager, 'shortcut_path', None)}")
    print(f"  Shortcut info: {shortcut_info}")

    run_val = get_run_key_value(startup_manager.app_name)
    print(f"  Registry Run value: {run_val}")

    print("\nAttempting removal (cleanup)...")
    removed = startup_manager.remove_from_startup()
    print(f"  remove_from_startup(): {removed}")
    print(f"  After removal is_in_startup(): {startup_manager.is_in_startup()}")
    print(f"  Run key now: {get_run_key_value(startup_manager.app_name)}")
    print(f"  Shortcut exists now: {os.path.exists(getattr(startup_manager, 'shortcut_path', '') or '')}")

    print("\nAttempting ADD...")
    added = startup_manager.add_to_startup()
    print(f"  add_to_startup(): {added}")

    print("\nStatus AFTER ADD:")
    print(f"  is_in_startup(): {startup_manager.is_in_startup()}")
    shortcut_info2 = list_startup_shortcut(getattr(startup_manager, 'shortcut_path', None))
    print(f"  Shortcut info: {shortcut_info2}")
    run_val2 = get_run_key_value(startup_manager.app_name)
    print(f"  Registry Run value: {run_val2}")

    # Summary logic
    method = None
    if shortcut_info2 and shortcut_info2.get('exists'):
        method = 'Startup Shortcut'
    elif run_val2:
        method = 'Registry Run Key'
    else:
        method = 'NONE (FAIL)'

    print("\nDETECTION SUMMARY:")
    print(f"  Persistence method: {method}")

    if method == 'NONE (FAIL)':
        print("\nNEXT STEPS:")
        print("  1. Ensure you have write permission to Startup folder.")
        print("  2. Try running: python -m pip install winshell")
        print("  3. Verify no security software blocked shortcut creation.")
        print("  4. Manual fallback: Create shortcut in %APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\Startup")
        print(f"     Target: \"{sys.executable}\" \"{main_py}\"")

    print("\nDone.")

if __name__ == '__main__':
    try:
        main()
    except Exception:
        traceback.print_exc()
        print("Fatal diagnostic error.")

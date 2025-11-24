import socket
import re
import subprocess
import sys

# نام دامنه‌ای که مشکل دارد
domain = "soft98.ir"

print(f"--- START DEBUGGING FOR: {domain} ---")

# 1. تست اتصال مستقیم سوکت
print("\n[1] Testing Direct Socket (whois.nic.ir:43)...")
try:
    with socket.create_connection(("whois.nic.ir", 43), timeout=10) as s:
        s.send(f"{domain}\r\n".encode())
        response = b""
        while True:
            data = s.recv(4096)
            if not data: break
            response += data
        text = response.decode(errors='ignore')
        print(f">>> SOCKET STATUS: Connected")
        print(">>> RAW OUTPUT (First 300 chars):")
        print(text[:300] + "...\n")
        
        match = re.search(r'expire-date:\s*(\d{4}-\d{2}-\d{2})', text, re.IGNORECASE)
        if match:
            print(f">>> RESULT: FOUND DATE ✅ ({match.group(1)})")
        else:
            print(">>> RESULT: DATE NOT FOUND ❌ (Regex mismatch)")
except Exception as e:
    print(f">>> SOCKET ERROR: {e}")

# 2. تست دستور سیستم عامل
print("\n[2] Testing System Command (whois)...")
try:
    result = subprocess.run(['whois', domain], capture_output=True, text=True, timeout=10)
    print(f">>> COMMAND EXIT CODE: {result.returncode}")
    
    if result.stdout:
        print(">>> STDOUT (First 300 chars):")
        print(result.stdout[:300] + "...\n")
        
        match = re.search(r'expire-date:\s*(\d{4}-\d{2}-\d{2})', result.stdout, re.IGNORECASE)
        if match:
            print(f">>> RESULT: FOUND DATE ✅ ({match.group(1)})")
        else:
            print(">>> RESULT: DATE NOT FOUND ❌ (Regex mismatch)")
    else:
        print(">>> STDOUT IS EMPTY")
        
    if result.stderr:
        print(f">>> STDERR: {result.stderr}")

except Exception as e:
    print(f">>> COMMAND ERROR: {e}")

print("\n--- END DEBUGGING ---")
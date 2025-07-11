# login_save_cookies.py
from playwright.sync_api import sync_playwright
import os

STATE_PATH = "app/state.json"

def main():
   with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        
        # Buat context TANPA storage_state dulu
        context = browser.new_context()  # ← ini diperbaiki

        page = context.new_page()
        print("Silakan login ke X.com secara manual...")
        page.goto("https://x.com/login")

        input("✅ Tekan ENTER setelah selesai login...")

        # Setelah login, baru simpan ke state.json
        context.storage_state(path=STATE_PATH)
        print(f"✅ Session login berhasil disimpan ke: {STATE_PATH}")

        browser.close()

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
簡單的 Hello World 腳本
用於驗證 GitHub Actions workflow 能夠執行存放在 repository 中的 Python 腳本
"""

def main():
    print("=" * 50)
    print("🎉 Hello World from GitHub Actions! 🎉")
    print("=" * 50)
    print("\n此腳本成功執行，證明 workflow 可以運行 repository 中的 Python 腳本。")
    print("\n✅ Python 腳本執行測試成功！")
    print("=" * 50)

if __name__ == "__main__":
    main()

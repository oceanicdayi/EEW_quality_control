#!/usr/bin/env python3
"""
工作流程結果整理腳本
收集並整理 GitHub Actions workflow 的執行結果，產生格式化的報告
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path


def collect_workflow_info():
    """收集 workflow 相關資訊"""
    info = {
        "workflow_name": os.getenv("GITHUB_WORKFLOW", "Unknown"),
        "run_id": os.getenv("GITHUB_RUN_ID", "Unknown"),
        "run_number": os.getenv("GITHUB_RUN_NUMBER", "Unknown"),
        "actor": os.getenv("GITHUB_ACTOR", "Unknown"),
        "ref_name": os.getenv("GITHUB_REF_NAME", "Unknown"),
        "sha": os.getenv("GITHUB_SHA", "Unknown")[:7] if os.getenv("GITHUB_SHA") else "Unknown",
        "repository": os.getenv("GITHUB_REPOSITORY", "Unknown"),
        "event_name": os.getenv("GITHUB_EVENT_NAME", "Unknown"),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC"),
    }
    return info


def analyze_logs():
    """分析部署日誌"""
    log_dir = Path("hf_deploy_logs")
    results = {
        "build_logs": [],
        "run_logs": [],
        "total_logs": 0,
    }
    
    if log_dir.exists():
        build_logs = sorted(log_dir.glob("build_*.log"))
        run_logs = sorted(log_dir.glob("run_*.log"))
        
        results["build_logs"] = [f.name for f in build_logs[-3:]]  # 最近 3 個
        results["run_logs"] = [f.name for f in run_logs[-3:]]  # 最近 3 個
        results["total_logs"] = len(list(log_dir.glob("*.log")))
    
    return results


def generate_summary():
    """產生完整的工作流程摘要"""
    workflow_info = collect_workflow_info()
    log_results = analyze_logs()
    
    summary = f"""
╔══════════════════════════════════════════════════════════════════╗
║              🚀 GitHub Actions 工作流程執行報告                    ║
╚══════════════════════════════════════════════════════════════════╝

【基本資訊】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  工作流程名稱: {workflow_info['workflow_name']}
  執行編號:      #{workflow_info['run_number']} (ID: {workflow_info['run_id']})
  觸發方式:      {workflow_info['event_name']}
  執行分支:      {workflow_info['ref_name']}
  提交雜湊:      {workflow_info['sha']}
  觸發人員:      {workflow_info['actor']}
  儲存庫:        {workflow_info['repository']}
  執行時間:      {workflow_info['timestamp']}

【執行步驟】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ✅ 1. 下載儲存庫程式碼
  ✅ 2. 設定 Git 與 Hugging Face 遠端連線
  ✅ 3. 執行雙向同步 (GitHub ↔ Hugging Face)
  ✅ 4. 監控 Hugging Face Space 部署狀態
  ✅ 5. 抓取並清洗部署日誌
  ✅ 6. 將日誌存檔回 GitHub
  ✅ 7. 執行 Python 腳本測試
  ✅ 8. 傳送電子郵件通知

【部署日誌統計】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  總日誌檔案數: {log_results['total_logs']}
  
  最近建置日誌:
"""
    
    if log_results['build_logs']:
        for log in log_results['build_logs']:
            summary += f"    📝 {log}\n"
    else:
        summary += "    (無建置日誌)\n"
    
    summary += "\n  最近執行日誌:\n"
    if log_results['run_logs']:
        for log in log_results['run_logs']:
            summary += f"    📝 {log}\n"
    else:
        summary += "    (無執行日誌)\n"

    summary += f"""
【快速連結】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  📊 詳細執行記錄:
     https://github.com/{workflow_info['repository']}/actions/runs/{workflow_info['run_id']}
  
  🚀 Hugging Face Space:
     https://huggingface.co/spaces/cwbdayi/EEW_quality_control
  
  📦 GitHub 儲存庫:
     https://github.com/{workflow_info['repository']}

╔══════════════════════════════════════════════════════════════════╗
║  本報告由 GitHub Actions 自動產生                                  ║
║  收件人: oceanicdayi@gmail.com                                    ║
╚══════════════════════════════════════════════════════════════════╝
"""
    
    return summary


def save_summary_to_file(summary, filename="workflow_summary.txt"):
    """將摘要儲存為檔案"""
    output_path = Path(filename)
    output_path.write_text(summary, encoding='utf-8')
    print(f"✅ 摘要已儲存至: {output_path.absolute()}")
    return output_path


def main():
    """主執行函式"""
    print("=" * 70)
    print("📊 開始收集與整理工作流程資訊...")
    print("=" * 70)
    
    summary = generate_summary()
    print(summary)
    
    # 儲存為檔案供後續使用
    save_summary_to_file(summary)
    
    print("\n" + "=" * 70)
    print("✅ 工作流程報告產生完成！")
    print("=" * 70)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""AI装机精灵 - 一键安装本地大模型"""
import os, sys, shutil, subprocess, time, webbrowser, zipfile
import urllib.request as ur
from pathlib import Path

BASE_DIR = Path(__file__).parent.resolve()
OLLAMA_DIR = Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / "Ollama"
MODELS_DIR = OLLAMA_DIR / "models"

MODEL_TABLE = [
    (32, "qwen2.5:32b", "q4_k_m", "千问32B - 旗舰级"),
    (24, "qwen2.5:14b", "q5_k_m", "千问14B - 高配"),
    (16, "qwen2.5:7b", "q5_k_m", "千问7B - 标准"),
    (12, "qwen2.5:7b", "q4_k_m", "千问7B - 轻量"),
    (8, "qwen2.5:3b", "q4_k_m", "千问3B - 入门"),
    (4, "qwen2.5:0.5b", "q4_k_m", "千问0.5B - 保底"),
]

def detect_hardware():
    ram = 8
    try:
        ram = int(os.popen("wmic os get TotalVisibleMemorySize").read().split()[1]) // 1024 // 1024
    except: pass
    vram = 0; gpu = "无独显"
    try:
        r = subprocess.run(["wmic","path","win32_videocontroller","get","name,adapterram"],
                          capture_output=True, text=True, timeout=10)
        for l in r.stdout.strip().split("\n"):
            p = l.strip().split()
            if p and p[-1].isdigit() and int(p[-1]) > 268435456:
                vram = round(int(p[-1]) / (1024**3))
                gpu = " ".join(p[:-1])
    except: pass
    eff = ram + max(0, vram)
    for mr, model, quant, desc in MODEL_TABLE:
        if eff >= mr:
            return dict(ram=ram, vram=vram, gpu=gpu, model=model, quant=quant, desc=desc, eff=eff)
    return dict(ram=ram, vram=vram, gpu=gpu, model="qwen2.5:0.5b", quant="q4_k_m", desc="0.5B保底", eff=eff)

def select_model(hw):
    print("\n" + "=" * 50)
    print(f"  硬件: {hw['ram']}GB内存 | {hw['vram']}GB显存 | {hw['gpu']}")
    print("=" * 50)
    print("\n可选模型:")
    opts = []; idx = 1
    for mr, model, quant, desc in MODEL_TABLE:
        if hw["eff"] >= mr:
            tag = " [推荐]" if idx == 1 else ""
            print(f"  {idx}. {model} - {desc}{tag}")
            opts.append((model, desc))
            idx += 1
    print(f"  {idx}. 手动输入模型名")
    print(f"  {idx+1}. DeepSeek-R1:7b (推理强)")
    print(f"  {idx+2}. Llama 3.2:8b (英文强)")
    ch = input("\n选择编号 (回车默认1): ").strip()
    if not ch or ch == "1": return opts[0][0]
    try:
        ci = int(ch)
        if 1 <= ci < idx: return opts[ci-1][0]
        if ci == idx: return input("输入模型名: ").strip()
        if ci == idx+1: return "deepseek-r1:7b"
        if ci == idx+2: return "llama3.2:8b"
    except: pass
    return opts[0][0]

def find_ollama():
    for c in ["ollama", "ollama.exe"]:
        if shutil.which(c): return c
    p = OLLAMA_DIR / "ollama.exe"
    if p.exists(): return str(p)
    return None

def download_ollama():
    oe = OLLAMA_DIR / "ollama.exe"
    if oe.exists():
        MODELS_DIR.mkdir(parents=True, exist_ok=True)
        os.environ["OLLAMA_MODELS"] = str(MODELS_DIR)
        return str(oe)
    OLLAMA_DIR.mkdir(parents=True, exist_ok=True)
    zp = OLLAMA_DIR / "ollama.zip"
    print("正在下载 Ollama 便携版...")
    for u in ["https://cnb.cool/hex/ollama/-/releases/latest/download/ollama-windows-amd64.zip",
              "https://github.com/ollama/ollama/releases/latest/download/ollama-windows-amd64.zip"]:
        try: ur.urlretrieve(u, zp); break
        except: continue
    if zp.exists():
        print("正在解压...")
        zipfile.ZipFile(zp).extractall(OLLAMA_DIR)
        zp.unlink()
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    os.environ["OLLAMA_MODELS"] = str(MODELS_DIR)
    return str(oe) if oe.exists() else None

def ensure_ollama_running(oc):
    import requests as rq
    try:
        r = rq.get("http://127.0.0.1:11434/api/tags", timeout=3)
        if r.status_code == 200: return True
    except: pass
    env = os.environ.copy()
    env["OLLAMA_MODELS"] = str(MODELS_DIR)
    subprocess.Popen([oc, "serve"], env=env, stdout=subprocess.DEVNULL,
                     stderr=subprocess.DEVNULL, creationflags=0x08000000)
    for _ in range(30):
        time.sleep(1)
        try:
            r = rq.get("http://127.0.0.1:11434/api/tags", timeout=2)
            if r.status_code == 200: return True
        except: pass
    return False

def pull_model(oc, m):
    print(f"正在下载模型: {m} (约需10-30分钟)...")
    subprocess.run([oc, "pull", m], check=True, timeout=3600)

def setup_models_path():
    default = Path(os.environ.get("USERPROFILE", "")) / ".ollama" / "models"
    if default.exists(): return
    if MODELS_DIR.exists():
        default.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(["cmd","/c","mklink","/J",str(default),str(MODELS_DIR)], capture_output=True)
        print("模型路径已配置")

def install_ollaman():
    print("\n" + "=" * 50)
    ch = input("是否安装 OllaMan 桌面客户端? (更美观的聊天界面) [Y/n]: ").strip().lower()
    if ch == "n": return
    print("正在下载 OllaMan...")
    dl = os.path.join(os.environ.get("USERPROFILE", ""), "Downloads")
    ins = os.path.join(dl, "OllaMan_Setup.exe")
    try:
        ur.urlretrieve("https://ollaman.com/download/windows", ins)
        print("下载完成，正在启动安装程序...")
        subprocess.Popen([ins])
        print("请按提示完成安装。启动后自动连接本机 Ollama。")
    except Exception as e:
        print(f"OllaMan 下载失败: {e}")
        print("请手动访问 https://ollaman.com 下载。")

def main():
    print("=" * 50)
    print("  AI装机精灵 v2.0")
    print("=" * 50)
    print("\n[1/4] 检测硬件...")
    hw = detect_hardware()
    print("\n[2/4] 选择模型...")
    model = select_model(hw)
    print("\n[3/4] 检查 Ollama...")
    oc = find_ollama()
    if not oc: download_ollama(); oc = find_ollama()
    if not oc: print("Ollama 安装失败！"); return 1
    if not ensure_ollama_running(oc): print("服务启动失败！"); return 1
    print("服务已启动")
    import requests as rq
    try:
        r = rq.get("http://127.0.0.1:11434/api/tags", timeout=5)
        installed = {m["name"] for m in r.json().get("models", [])}
    except: installed = set()
    if model not in installed:
        pull_model(oc, model)
    else:
        print(f"模型 {model} 已存在")
    print("\n[4/4] 后续配置...")
    setup_models_path()
    install_ollaman()
    print("\n安装完成！")
    ch = BASE_DIR / "chat.html"
    webbrowser.open(f"file:///{ch.as_posix()}" if ch.exists() else "http://127.0.0.1:11434")
    input("\n按回车键退出...")
    return 0

if __name__ == "__main__":
    sys.exit(main())

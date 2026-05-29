#!/usr/bin/env python3
"""AI装机精灵 - 一键安装本地大模型"""

import os,sys,json,shutil,subprocess,time,webbrowser
from pathlib import Path

BASE_DIR=Path(__file__).parent.resolve()
OLLAMA_DIR=BASE_DIR/"ollama"
MODELS_DIR=OLLAMA_DIR/"models"

MODEL_TABLE=[
 (32,"qwen2.5:32b","q4_k_m","千问32B - 旗舰级"),
 (24,"qwen2.5:14b","q5_k_m","千问14B - 高配"),
 (16,"qwen2.5:7b","q5_k_m","千问7B - 标准"),
 (12,"qwen2.5:7b","q4_k_m","千问7B - 轻量"),
 (8,"qwen2.5:3b","q4_k_m","千问3B - 入门"),
 (4,"qwen2.5:0.5b","q4_k_m","千问0.5B - 保底"),
]

def detect_hardware():
    ram=8
    try:
        ram=int(os.popen("wmic os get TotalVisibleMemorySize").read().split()[1])//1024//1024
    except:pass
    vram=0;gpu="无独显"
    try:
        r=subprocess.run(["wmic","path","win32_videocontroller","get","name,adapterram"],capture_output=True,text=True,timeout=10)
        for l in r.stdout.strip().split(chr(10)):
            p=l.strip().split()
            if p and p[-1].isdigit() and int(p[-1])>268435456:
                vram=round(int(p[-1])/(1024**3));gpu=" ".join(p[:-1])
    except:pass
    eff=ram+max(0,vram)
    for mr,model,quant,desc in MODEL_TABLE:
        if eff>=mr:return dict(ram=ram,vram=vram,gpu=gpu,model=model,quant=quant,desc=desc,eff=eff)
    return dict(ram=ram,vram=vram,gpu=gpu,model="qwen2.5:0.5b",quant="q4_k_m",desc="0.5B保底",eff=eff)

def find_ollama():
    for c in["ollama","ollama.exe"]:
        if shutil.which(c):return c
    p=OLLAMA_DIR/"ollama.exe"
    if p.exists():return str(p)
    return None

def download_ollama():
    import zipfile
    oe=OLLAMA_DIR/"ollama.exe"
    if oe.exists():MODELS_DIR.mkdir(parents=True,exist_ok=True);os.environ["OLLAMA_MODELS"]=str(MODELS_DIR);return str(oe)
    OLLAMA_DIR.mkdir(parents=True,exist_ok=True);zp=OLLAMA_DIR/"ollama.zip"
    for u in["https://cnb.cool/hex/ollama/-/releases/latest/download/ollama-windows-amd64.zip","https://github.com/ollama/ollama/releases/latest/download/ollama-windows-amd64.zip"]:
        try:ur.urlretrieve(u,zp);break
        except:continue
    if zp.exists():zipfile.ZipFile(zp).extractall(OLLAMA_DIR);zp.unlink()
    MODELS_DIR.mkdir(parents=True,exist_ok=True);os.environ["OLLAMA_MODELS"]=str(MODELS_DIR)
    return str(oe) if oe.exists() else None
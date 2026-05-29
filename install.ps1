Write-Host "AI装机精灵 - 一键安装" -ForegroundColor Cyan
$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
  Write-Host "请先安装 Python 3.10+" -ForegroundColor Red
  Write-Host "https://www.python.org/downloads/"
  pause
  exit 1
}
Write-Host "安装依赖..." -ForegroundColor Yellow
python -m pip install requests -q
Write-Host "启动安装..." -ForegroundColor Yellow
python ai_installer.py
Write-Host "完成！" -ForegroundColor Green
pause
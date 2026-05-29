import subprocess,sys,os
subprocess.check_call([sys.executable,"-m","pip","install","requests","-q"])
subprocess.run([sys.executable,os.path.join(os.path.dirname(__file__),"ai_installer.py")])
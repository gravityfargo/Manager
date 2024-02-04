import os
import sys
import venv
import subprocess

def create_virtual_environment(directory_path, venvpath):
    reqspath = f"{directory_path}requirements.txt"
    pip_executable = os.path.join(venvpath, 'bin', 'pip') if sys.platform != 'win32' else os.path.join(venvpath, 'Scripts', 'pip.exe')
    
    if not os.path.exists(venvpath):
        os.makedirs(venvpath)
        venv.create(venvpath, with_pip=True)
        subprocess.check_call([pip_executable, 'install', '-r', reqspath], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
def run_py_file_in_venv(venvpath, script_path):
    python_executable = os.path.join(venvpath, 'bin', 'python') if sys.platform != 'win32' else os.path.join(venvpath, 'Scripts', 'python.exe')
    subprocess.run([python_executable, script_path])

if __name__ == '__main__':
    path = os.path.realpath(__file__)
    directory_path = path.replace(path.split("/")[-1], '')
    venvpath = f"{directory_path}venv"
    script_path = f"{directory_path}Manager.py"
    create_virtual_environment(directory_path, venvpath)
    run_py_file_in_venv(venvpath, script_path)
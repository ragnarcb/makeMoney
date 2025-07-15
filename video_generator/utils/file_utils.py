import shutil
import os

def cleanup_temp_dirs(*dirs):
    for d in dirs:
        if os.path.exists(d):
            shutil.rmtree(d) 
import os
from datetime import datetime

def get_last_update_date():
    input_dir = 'input'  # your data directory
    files = [os.path.join(input_dir, f) for f in os.listdir(input_dir)]
    if files:
        latest_file = max(files, key=os.path.getmtime)
        mod_time = os.path.getmtime(latest_file)
        return datetime.fromtimestamp(mod_time).strftime('%B %d, %Y')
    
    
    return 'Unknown'
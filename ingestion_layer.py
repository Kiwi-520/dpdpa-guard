from datetime import datetime
import os
def file_upload(file_name):
    input_data = {}
    try:
        time_slot = datetime.now()
        with open(file_name, 'r') as f:
            text = f.read()
            timing = time_slot.strftime("%Y-%m-%d %H:%M:%S")
            input_data['data'] = text
            input_data['time'] = timing
            input_data['source_tag'] = os.path.abspath(file_name)
            input_data['source_type'] = 'file'
        return input_data
    except FileNotFoundError as e:
        return e

from datetime import datetime

def file_upload(file_name):
    input_data = {}
    try:
        time_slot = datetime.now()
        with open(file_name, 'r') as f:
            text = f.read()
            timing = time_slot.strftime("%Y-%m-%d %H:%M:%S")
            input_data['data'] = text
            input_data['time'] = timing
        return input_data
    except FileNotFoundError as e:
        return e

ans = file_upload('text2.txt')
print(ans)


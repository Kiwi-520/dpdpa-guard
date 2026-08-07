from datetime import datetime

input_data = {}

def file_upload(file_name):
    with open(file_name, 'r') as f:
        text = f.read()
        start_time = datetime.today()
        timing = start_time.strftime("%Y-%m-%d %H:%M:%S")
        input_data['data'] = text
        input_data['time'] = timing
    return input_data

ans = file_upload('text.txt')
print(ans)


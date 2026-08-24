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

# Output
# {
# 'data':
#         'Dr. John Smith is a Professor at ABC Technologies. His Aadhaar number is 2345-6789-1234 and his PAN card number is ABCDE1234F. His passport number is A1234567 and voter ID is ABC1234567. His driving license number is MH-12-20210012345. The bank IFSC code is SBIN0001234. You can send money to his UPI ID john.smith@oksbi. His registered vehicle number is MH 12 AB 1234. Contact him at john.smith@gmail.com or call him at +91 9876543210. His office IP address is 192.168.1.100.\n',
# 'time': '2026-08-16 20:34:50',
# 'source_tag': 'C:\\Users\\disha\\Disha\\OpenSourceContribution\\dpdpa-guard\\dpdpa-guard\\text.txt',
# 'source_type': 'file'
# }

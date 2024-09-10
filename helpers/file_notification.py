from config import test_balance_txt_name
from datetime import datetime
import json as json


# Writes the current balance at the end of the configured text_file
def write_balance(balance):
    write_time = str(datetime.now())
    try:
        balance_str = json.dumps(balance, indent=2)
        file_path = test_balance_txt_name
        with open(file_path, 'a') as file:
            file.writelines([f"\n{write_time}\n", balance_str, "\n\n---------------------------------------"])
        print(f"Balance written to: {file_path}")
    except Exception as e:
        print(f"From binance_notification: {e}")

import re
import schedule
import subprocess
from datetime import datetime
from database import db, ScheduledMessage, Settings, IncomingMessage, CustomerInfo
from message_processor import analyze_message

def send_message(phone_number, message_text):
    command = f'osascript send_message.applescript "{phone_number}" "{message_text}"'
    try:
        subprocess.run(command, shell=True, check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Failed to send message to {phone_number}: {e}")
        return False

def schedule_messages():
    schedule.clear('message')
    messages = ScheduledMessage.query.all()
    for msg in messages:
        schedule.every().day.at(msg.send_time).do(send_message, msg.phone_number, msg.message).tag('message')

def read_incoming_messages(file_path='~/Documents/incoming_messages.txt'):
    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()
        with open(file_path, 'w') as file:
            file.write('')
        return lines
    except FileNotFoundError:
        return []

def check_incoming_messages():
    messages = read_incoming_messages()
    for message in messages:
        analysis_result = analyze_message(message.strip())
        print(f"Received message: {message.strip()}")
        print(f"Analysis result: {analysis_result}")

        # 통관고유부호(P로 시작하는 문자열) 감지
        match = re.search(r'\bP\w+', message)
        if match:
            clearance_code = match.group(0)
            # 기존 고객 정보 업데이트 또는 새로 추가
            customer_info = CustomerInfo.query.filter_by(phone_number=message.phone_number).first()
            if customer_info:
                customer_info.clearance_code = clearance_code
            else:
                customer_info = CustomerInfo(phone_number=message.phone_number, name=message.sender, clearance_code=clearance_code)
                db.session.add(customer_info)
            db.session.commit()

        new_incoming_message = IncomingMessage(message=message.strip(), analysis_result=str(analysis_result))
        db.session.add(new_incoming_message)
        db.session.commit()

def schedule_incoming_message_checks():
    schedule.clear('incoming_check')
    setting = Settings.query.first()
    if setting:
        interval = setting.check_interval
        schedule.every(interval).minutes.do(check_incoming_messages).tag('incoming_check')

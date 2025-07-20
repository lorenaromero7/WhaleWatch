import requests
import time
import datetime
import smtplib
from email.message import EmailMessage

API_URL = "https://api.whale-alert.io/v1/transactions"
API_KEY = "your_whale_alert_api_key_here"

MIN_VALUE_USD = 5000000  # минимальная сумма транзакции в долларах для "кита"

EMAIL_TO_NOTIFY = "your_email@example.com"
EMAIL_FROM = "alert_sender@example.com"
EMAIL_PASSWORD = "your_email_password"

def send_email(subject, body):
    msg = EmailMessage()
    msg.set_content(body)
    msg["Subject"] = subject
    msg["From"] = EMAIL_FROM
    msg["To"] = EMAIL_TO_NOTIFY

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(EMAIL_FROM, EMAIL_PASSWORD)
        smtp.send_message(msg)

def fetch_whale_transactions():
    params = {
        "api_key": API_KEY,
        "min_value": MIN_VALUE_USD,
        "start": int(time.time()) - 60,
        "limit": 10
    }
    response = requests.get(API_URL, params=params)
    return response.json()

def analyze_intent(transaction):
    if transaction["to"]["owner_type"] == "exchange":
        return "🔥 ВОЗМОЖЕН СЛИВ (отправка на биржу)"
    elif transaction["from"]["owner_type"] == "exchange":
        return "🧊 ХОЛД или выход в холодный кошелёк"
    return "🤔 Неопределённое намерение"

def main():
    print(f"[{datetime.datetime.now()}] Запуск WhaleWatch...")

    data = fetch_whale_transactions()
    txs = data.get("transactions", [])

    if not txs:
        print("Нет китовых транзакций в последнее время.")
        return

    for tx in txs:
        intent = analyze_intent(tx)
        message = (
            f"🚨 Обнаружена крупная транзакция!\n"
            f"- Токен: {tx['symbol']}\n"
            f"- Сумма: {tx['amount']} {tx['symbol']} (~${tx['amount_usd']:,.2f})\n"
            f"- От: {tx['from']['owner'] or 'аноним'} ({tx['from']['owner_type']})\n"
            f"- Кому: {tx['to']['owner'] or 'аноним'} ({tx['to']['owner_type']})\n"
            f"- Намерение: {intent}\n"
            f"- Время: {datetime.datetime.fromtimestamp(tx['timestamp'])}\n"
        )
        print(message)
        send_email("WhaleWatch Alert 🚨", message)

if __name__ == "__main__":
    main()

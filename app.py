import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
import schedule
import time
from dotenv import load_dotenv
import requests

# Load environment variables
load_dotenv()

EMAIL_ADDRESS = os.getenv('EMAIL_ADDRESS')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')  # SendGrid API Key
RECIPIENT_EMAILS = os.getenv('RECIPIENT_EMAILS').split(',')  # Multiple recipients separated by commas
NEWS_API_KEY = os.getenv('NEWS_API_KEY')

def get_top_headlines():
    url = f"https://newsapi.org/v2/top-headlines?country=us&apiKey={NEWS_API_KEY}"
    response = requests.get(url)

    print(f"Status Code: {response.status_code}")
    print(f"Response Content: {response.text}")

    if response.status_code == 200:
        data = response.json()
        print(f"JSON Response: {data}")

        headlines = [article['title'] for article in data.get('articles', [])]
        return headlines
    else:
        return []

def send_email(headlines):
    if not headlines:
        print("No headlines to send.")
        return

    for recipient in RECIPIENT_EMAILS:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = recipient
        msg['Subject'] = 'Top 20 Headlines'

        body = "\n".join(headlines)
        msg.attach(MIMEText(body, 'plain'))

        try:
            with smtplib.SMTP('smtp.sendgrid.net', 587) as server:
                server.starttls()  # Upgrade to a secure connection
                server.login('apikey', EMAIL_PASSWORD)
                server.send_message(msg)
            print(f"Email sent successfully to {recipient}.")
        except smtplib.SMTPAuthenticationError as e:
            print(f"SMTP Authentication Error: {e.smtp_code} - {e.smtp_error}")
        except smtplib.SMTPConnectError as e:
            print(f"SMTP Connect Error: {e.smtp_code} - {e.smtp_error}")
        except smtplib.SMTPException as e:
            print(f"SMTP Error: {e}")
        except Exception as e:
            print(f"Unexpected Error: {e}")

def job():
    headlines = get_top_headlines()
    send_email(headlines)

# Schedule the job to run at 8:00 AM every day
schedule.every().day.at("08:00").do(job)

print("Scheduler started. Waiting for the scheduled time...")

while True:
    schedule.run_pending()
    time.sleep(60)  # Wait a minute before checking again

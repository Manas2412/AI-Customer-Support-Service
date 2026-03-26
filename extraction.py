import os
import imaplib
import email
import asyncio
import concurrent.futures
from email.utils import parseaddr
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import yaml
from dotenv import load_dotenv

load_dotenv()
    
class EmailFetcher:
    def __init__(self):
        self.user = os.getenv("EMAIL_USER")
        self.password = os.getenv("EMAIL_PASSWORD")
        self.host = os.getenv("IMAP_HOST")
        self.smtp_server = os.getenv("SMTP_SERVER")

        with open("whitelist.yaml", "r") as file:
            data = yaml.safe_load(file)
            self.whitelist = set(data.get("whitelist", []))

    def login(self):
        print(f"Logging in to {self.host} with {self.user}...")
        mail = imaplib.IMAP4_SSL(self.host)
        mail.login(self.user, self.password)
        print("Login successful.")
        mail.select("inbox")
        return mail

    async def fetch_new_emails(self):
        loop = asyncio.get_event_loop()
        with concurrent.futures.ThreadPoolExecutor() as pool:
            new_emails = await loop.run_in_executor(pool, self._fetch_new_emails)
        return new_emails

    def _fetch_new_emails(self):
        try:
            mail = self.login()
            print("Searching for UNSEEN emails...")
            response, email_ids_bytes = mail.uid("search", None, "UNSEEN")
            if response != "OK":
                print(f"Failed to search emails (response: {response}).")
                return []

            email_ids = email_ids_bytes[0].decode("utf-8").split()
            print(f"Found {len(email_ids)} total unread emails. Processing the 10 most recent...")

            if len(email_ids) == 0:
                print("No new unseen emails found.")
                return []

            # Reverse to get newest first and limit to 10
            recent_email_ids = email_ids[-10:]
            recent_email_ids.reverse()

            new_emails = []
            for email_id in recent_email_ids:
                # 1. Fetch only headers first to check the sender (saves bandwidth/time)
                res, header_data = mail.uid("fetch", email_id, "(BODY.PEEK[HEADER.FIELDS (FROM)])")
                if res != "OK":
                    continue

                header_content = header_data[0][1].decode("utf-8")
                email_header = email.message_from_string(header_content)
                sender_name, sender_addr = parseaddr(email_header["From"])

                if sender_addr not in self.whitelist:
                    print(f"Skipping {sender_addr} (Not in whitelist)")
                    # Mark as seen so we don't check it again next time
                    mail.uid("store", email_id, "+FLAGS", "(\\Seen)")
                    continue

                # 2. Whitelisted! Now download the full body
                print(f"Whitelisted sender found! Fetching full content from {sender_addr}...")
                response, email_data = mail.uid("fetch", email_id, "(BODY[])")
                if response != "OK":
                    print(f"Failed to fetch full email with ID {email_id}")
                    continue

                raw_email = email_data[0][1]
                email_message = email.message_from_bytes(raw_email)

                new_emails.append((email_message, sender_name, sender_addr))
                mail.uid("store", email_id, "+FLAGS", "(\\Seen)")

            mail.logout()
            return new_emails
        except Exception as e:
            print(f"Error in _fetch_new_emails: {e}")
            return []

    def send_email(self, recipient, subject, body):
        msg = MIMEMultipart()
        msg["From"] = self.user
        msg["To"] = recipient
        msg["Subject"] = subject

        msg.attach(MIMEText(body, "plain"))

        server = smtplib.SMTP(self.smtp_server, 587)
        server.starttls()
        server.login(self.user, self.password)
        text = msg.as_string()
        server.sendmail(self.user, recipient, text)
        server.quit()
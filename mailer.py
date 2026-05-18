import csv
import os
import smtplib
import time
from datetime import date
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from email.utils import formataddr

from dotenv import load_dotenv

load_dotenv()

GMAIL_USER = os.environ["GMAIL_USER"]
GMAIL_APP_PASSWORD = os.environ["GMAIL_APP_PASSWORD"]
SENDER_NAME = os.environ["SENDER_NAME"]
SENDER_PHONE = os.environ["SENDER_PHONE"]

CONTACTS_FILE = "contacts.csv"
TEMPLATE_FILE = "template.txt"
LOG_FILE = "log.csv"
DELAY_SECONDS = 5


def load_template():
    with open(TEMPLATE_FILE, encoding="utf-8") as f:
        lines = f.read().splitlines()
    subject_line = lines[0]
    if subject_line.startswith("Ämne: "):
        subject = subject_line[len("Ämne: "):]
    else:
        subject = subject_line
    body = "\n".join(lines[2:])  # skip subject line and blank separator
    return subject, body


def personalize(text, namn, ort, telefon):
    return (
        text
        .replace("{namn}", namn)
        .replace("{ort}", ort)
        .replace("{telefon}", telefon)
    )


def send_email(to_email, subject, body):
    msg = MIMEMultipart("alternative")
    msg["Subject"] = str(Header(subject, "utf-8"))
    msg["From"] = formataddr((SENDER_NAME, GMAIL_USER))
    msg["To"] = to_email
    msg.attach(MIMEText(body, "plain", "utf-8"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
        server.sendmail(GMAIL_USER, to_email, msg.as_bytes())


def append_log(datum, namn, email, status):
    write_header = not os.path.exists(LOG_FILE)
    with open(LOG_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if write_header:
            writer.writerow(["datum", "namn", "email", "status"])
        writer.writerow([datum, namn, email, status])


def update_sent_date(rows, index, today):
    rows[index]["skickat_datum"] = today
    with open(CONTACTS_FILE, "w", newline="", encoding="utf-8") as f:
        fieldnames = ["namn", "email", "telefon", "ort", "skickat_datum", "notering"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main():
    subject_template, body_template = load_template()

    with open(CONTACTS_FILE, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    pending = [(i, row) for i, row in enumerate(rows) if not row["skickat_datum"].strip()]

    if not pending:
        print("Inga väntande kontakter – alla har redan fått mail.")
        return

    print(f"{len(pending)} mail att skicka.\n")
    today = date.today().isoformat()

    for i, (row_index, row) in enumerate(pending):
        namn = row["namn"].strip()
        email = row["email"].strip()
        ort = row["ort"].strip()
        telefon = row["telefon"].strip() or SENDER_PHONE

        subject = personalize(subject_template, namn, ort, telefon)
        body = personalize(body_template, namn, ort, telefon)

        try:
            send_email(email, subject, body)
            update_sent_date(rows, row_index, today)
            append_log(today, namn, email, "OK")
            print(f"[OK]  {namn} <{email}>")
        except Exception as exc:
            append_log(today, namn, email, f"FEL: {exc}")
            print(f"[FEL] {namn} <{email}> – {exc}")

        if i < len(pending) - 1:
            time.sleep(DELAY_SECONDS)

    print("\nKlart.")


if __name__ == "__main__":
    main()

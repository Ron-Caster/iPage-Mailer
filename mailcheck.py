import imaplib
import email
from email.header import decode_header
import csv

def read_credentials(file_path):
    with open(file_path, mode='r') as file:
        reader = csv.reader(file)
        next(reader)  # Skip header row
        return next(reader)

def connect_to_mail_server(username, password, imap_server="imap.ipage.com"):
    mail = imaplib.IMAP4_SSL(imap_server)
    mail.login(username, password)
    mail.select("inbox")
    return mail

def list_emails(mail, start=0, count=4):
    # Search for all emails in the inbox
    status, messages = mail.search(None, "ALL")

    # Convert messages to a list of email IDs
    email_ids = messages[0].split()
    email_ids.reverse()  # Reverse to have the latest email first

    # Fetch the specified range of emails
    selected_email_ids = email_ids[start:start + count]

    emails = []
    # Iterate through the selected emails
    for i, email_id in enumerate(selected_email_ids, start + 1):
        # Fetch the email by ID
        status, msg_data = mail.fetch(email_id, "(RFC822)")

        # Parse the email content
        for response_part in msg_data:
            if isinstance(response_part, tuple):
                msg = email.message_from_bytes(response_part[1])
                subject, encoding = decode_header(msg["Subject"])[0]
                if isinstance(subject, bytes):
                    subject = subject.decode(encoding if encoding else "utf-8")
                date = msg.get("Date")
                emails.append((email_id, subject, date))
                print(f"{i}. Subject: {subject}")
                print(f"   Date: {date}")
                print("-" * 40)
    return emails

def show_email_content(mail, email_id):
    # Fetch the email by ID
    status, msg_data = mail.fetch(email_id, "(RFC822)")

    # Parse the email content
    for response_part in msg_data:
        if isinstance(response_part, tuple):
            msg = email.message_from_bytes(response_part[1])
            subject, encoding = decode_header(msg["Subject"])[0]
            if isinstance(subject, bytes):
                subject = subject.decode(encoding if encoding else "utf-8")
            date = msg.get("Date")
            print(f"Subject: {subject}")
            print(f"Date: {date}")
            print("-" * 40)

            # If the email message is multipart
            if msg.is_multipart():
                for part in msg.walk():
                    content_type = part.get_content_type()
                    content_disposition = str(part.get("Content-Disposition"))

                    try:
                        body = part.get_payload(decode=True).decode()
                    except:
                        pass

                    if content_type == "text/plain" and "attachment" not in content_disposition:
                        print("Body:", body)
            else:
                content_type = msg.get_content_type()
                body = msg.get_payload(decode=True).decode()
                if content_type == "text/plain":
                    print("Body:", body)

def main():
    username, password = read_credentials('credentials.csv')
    mail = connect_to_mail_server(username, password)

    start_index = 0
    all_emails = list_emails(mail, start_index)

    while True:
        command = input("For help type 'help': ").strip().lower()
        if command == "help":
            print("Available commands:")
            print("  back   - List the emails again")
            print("  more   - Show more emails")
            print("  logout - Exit the program")
        elif command == "logout":
            break
        elif command == "back":
            start_index = 0
            all_emails = list_emails(mail, start_index)
        elif command == "more":
            start_index += 4
            all_emails.extend(list_emails(mail, start_index))
        elif command.isdigit() and 1 <= int(command) <= len(all_emails):
            email_id = all_emails[int(command) - 1][0]
            show_email_content(mail, email_id)
        else:
            print("Invalid command. Please try again.")

    mail.close()
    mail.logout()

if __name__ == "__main__":
    main()
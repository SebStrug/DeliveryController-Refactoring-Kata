import smtplib
from email.mime.text import MIMEText


class DummyGateway:
    def __init__(self):
        self.sent = 0

    def send(self, address, subject, message):
        self.sent += 1


class EmailGateway:
    def __init__(self):
        self.sent = 0

    def send(self, address, subject, message):
        msg = MIMEText(message)

        # me == the sender's email address
        # you == the recipient's email address
        msg["Subject"] = subject
        from_address = "noreply@example.com"
        msg["From"] = from_address
        msg["To"] = address

        # Send the message via our own SMTP server, but don't include the
        # envelope header.
        s = smtplib.SMTP("localhost")
        s.sendmail(from_address, [address], msg.as_string())
        s.quit()

        self.sent += 1

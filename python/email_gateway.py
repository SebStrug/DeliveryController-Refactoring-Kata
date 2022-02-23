import smtplib
from email.mime.text import MIMEText


class Gateway:
    def __init__(self) -> None:
        self.sent = 0

    def send(self, address: str, subject: str, message: str) -> None:
        raise NotImplementedError


class EmailGateway:
    def __init__(self) -> None:
        self.sent = 0

    def send(self, address: str, subject: str, message: str) -> None:
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

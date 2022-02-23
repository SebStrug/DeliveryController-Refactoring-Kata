import smtplib
from email.mime.text import MIMEText


class Gateway:
    def __init__(self) -> None:
        self.sent: list = []

    def send(self, address: str, subject: str, message: str) -> None:
        raise NotImplementedError


class EmailGateway:
    def __init__(self) -> None:
        self.sent: list[MIMEText] = []
        self.from_address = "noreply@example.com"

    def compose_message(self, address: str, subject: str, message: str) -> MIMEText:
        msg = MIMEText(message)
        # me == the sender's email address
        # you == the recipient's email address
        msg["Subject"] = subject
        msg["From"] = self.from_address
        msg["To"] = address
        return msg

    def send(self, address: str, subject: str, message: str) -> None:
        msg = self.compose_message(address, subject, message)
        # Send the message via our own SMTP server, but don't include the
        # envelope header.
        s = smtplib.SMTP("localhost")
        s.sendmail(self.from_address, [address], msg.as_string())
        s.quit()

        self.sent += [msg]

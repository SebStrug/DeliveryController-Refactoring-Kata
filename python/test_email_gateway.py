from email_gateway import EmailGateway


def test_compose_message():
    res = EmailGateway().compose_message("seb@gmail.com", "kata", "hello world")
    res_items = res.items()
    assert res.get_payload() == "hello world"
    assert ("To", "seb@gmail.com") in res_items
    assert ("Subject", "kata") in res_items
    assert ("From", "noreply@example.com") in res_items


def test_send(mocker):
    m_client = mocker.patch("email_gateway.smtplib.SMTP")
    client = EmailGateway()
    client.send("seb@gmail.com", "kata", "hello world")
    assert client.sent == 1
    m_client.return_value.sendmail.assert_called_once()

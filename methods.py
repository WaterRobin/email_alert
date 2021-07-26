import smtplib
import re


def password_checker(password):
    if len(password) >= 10 and re.search("[A-Z]", password) and \
            re.search("[0-9]", password) and re.search('[a-z]', password):
        return True
    return False


def send_email(auth_inf, db_object):
    s = smtplib.SMTP('smtp.gmail.com', 587, timeout=3)
    s.ehlo()
    s.starttls()
    s.ehlo()
    s.login('tstmiigaik@gmail.com', 'testpassword_01')
    to_email = db_object['Почта']
    msg = f"""
    Письмо от {auth_inf['author']}
    Тема: {auth_inf['title']}.

    {auth_inf['description']}

    Спасибо за внимание.
    """.encode('utf-8')
    s.sendmail("tstmiigaik@gmail.com", to_email, msg)
    s.quit()


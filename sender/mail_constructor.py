from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage


def construct_mail(subject, _from, to, chosen_template, chosen_image):
    msg_root = MIMEMultipart('related')
    msg_root['Subject'] = subject
    msg_root['From'] = _from
    msg_root['To'] = to

    msg_alternative = MIMEMultipart('alternative')
    html_body = MIMEText(chosen_template, 'html')
    msg_alternative.attach(html_body)
    msg_root.attach(msg_alternative)

    mime_image = MIMEImage(chosen_image)
    mime_image.add_header('Content-ID', '<image1>')
    msg_root.attach(mime_image)

    return msg_root.as_string()

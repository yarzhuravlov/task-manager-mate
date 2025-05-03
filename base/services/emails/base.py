from base.utils.mail import send_email


class BaseEmailService:
    subject = ""
    template_name_html: str = None

    def __init__(self, context: dict, to_email: str | list[str]):
        self.context = context
        self.to_email = to_email

    def send(self):
        send_email(
            self.get_subject(),
            self.get_template_name_html(),
            self.context,
            self.to_email,
        )

    def get_subject(self):
        return self.subject

    def get_template_name_html(self):
        return self.template_name_html

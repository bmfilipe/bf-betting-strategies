import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

class EmailService:
    """Service to handle async/sync SMTP email transmission with attachments."""

    @staticmethod
    def send_report_email(
        sender_email: str,
        sender_password: str,
        recipient_email: str,
        subject: str,
        body_text: str,
        pdf_bytes: bytes = None,
        txt_content: str = None
    ) -> tuple[bool, str]:
        """
        Send email with optional PDF/TXT attachments.
        Returns (success: bool, message: str).
        """
        if not sender_email or not sender_password:
            return False, "Credenciais SMTP não configuradas pelo Administrador."

        if not recipient_email or "@" not in recipient_email:
            return False, "Endereço de e-mail do destinatário inválido."

        try:
            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = recipient_email
            msg['Subject'] = subject

            # Body
            msg.attach(MIMEText(body_text, 'plain', 'utf-8'))

            # Attach PDF if present
            if pdf_bytes:
                pdf_attachment = MIMEApplication(pdf_bytes, _subtype="pdf")
                pdf_attachment.add_header('Content-Disposition', 'attachment', filename="boletins_futebol_ev.pdf")
                msg.attach(pdf_attachment)

            # Attach TXT if present
            if txt_content:
                txt_attachment = MIMEText(txt_content, 'plain', 'utf-8')
                txt_attachment.add_header('Content-Disposition', 'attachment', filename="boletins_futebol_ev.txt")
                msg.attach(txt_attachment)

            # Connect to SMTP Server (Gmail / standard TLS on port 587)
            server = smtplib.SMTP('smtp.gmail.com', 587, timeout=10)
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
            server.quit()

            return True, f"E-mail enviado com sucesso para {recipient_email}!"

        except Exception as e:
            return False, f"Falha no envio de e-mail via SMTP: {str(e)}"

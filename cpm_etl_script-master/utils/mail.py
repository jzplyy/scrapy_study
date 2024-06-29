import os.path
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import traceback
import smtplib

from . import BASE_DIR

EMAIL_HOST = 'outlook.wuxibiologics.com'
EMAIL_PORT = 25
FROM_EMAIL = 'DL.SBD@wuxibiologics.com'


def send_email(to_email, quotation_code_list, email_type):
    server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
    try:
        msg = MIMEMultipart('mixed')
        msg['From'] = FROM_EMAIL
        msg['To'] = to_email
        if email_type == 'new':
            msg['Subject'] = 'CPM 新增订单（系统邮件请勿回复）'
        elif email_type == 'update':
            msg['Subject'] = 'CPM 订单确认（系统邮件请勿回复）'
        else:
            msg['Subject'] = 'CPM 订单发布（系统邮件请勿回复）'
        # 邮件正文
        if email_type == 'new':
            text_info = '附件为CPM中新增的订单信息(仅作参考，用户可能会修改)'
        elif email_type == 'update':
            text_info = '附件为CPM中新确认的订单信息'
        else:
            text_info = '附件为CPM中状态更新为“已发布”的订单信息'
        text_info += '\n\n对此邮件有任何疑问请联系： lu_jingzheng@wuxibiologics.com'
        text_sub = MIMEText(text_info, 'plain', 'utf-8')
        msg.attach(text_sub)
        # 邮件附件
        for quotation_code in quotation_code_list:
            file_path = os.path.join(BASE_DIR, f'_temp/{quotation_code}.xlsx')
            with open(file_path, 'rb') as f:
                attach_file = f.read()
            txt = MIMEText(attach_file, 'base64', 'utf-8')
            txt["Content-Type"] = 'application/octet-stream'
            txt.add_header('Content-Disposition', 'attachment', filename=f'{quotation_code}.xlsx')
            msg.attach(txt)
        server.sendmail(FROM_EMAIL, to_email, msg.as_string())
        print(f'EMAIL SEND:{to_email} ,TYPE:{email_type}')
    except Exception as e:
        traceback.print_exc()
        raise e
    finally:
        server.quit()

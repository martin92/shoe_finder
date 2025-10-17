from secret import MAIL_SENDER, MAIL_PASS, MAIL_RECIPIENT, SIZE
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from bs4 import BeautifulSoup
import pandas as pd
import requests
import smtplib
import json


def check_page():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
    }

    url = "https://www.columbia.com/p/mens-benson-shoe-2077141.html?color=278"

    page = requests.get(url, headers=headers)
    soup_page = BeautifulSoup(page.content, 'html.parser')
    json_data = soup_page.find('script', {'type': 'application/ld+json'})
    loaded_json = json.loads(json_data.text)['hasVariant']
    items = []

    for productos in loaded_json:
        if productos['color'] in ('278', '007'):
            items.append(
                [
                    productos['sku'],
                    productos['mpn'],
                    productos['name'],
                    productos['color'],
                    productos['offers']['price'],
                    productos['size'],
                    productos['image'],
                    productos['offers']['url']
                ]
            )

    df = pd.DataFrame(items)
    df.columns = ['sku', 'modelo', 'descripcion', 'color', 'precio', 'talla', 'image', 'url']
    df['color'] = df['color'].replace('278', 'Beige')
    df['color'] = df['color'].replace('007', 'Cafe')
    df_final = df[df['talla'] == SIZE]
    return df_final


def send_mail(result):

    sender = MAIL_SENDER
    passw = MAIL_PASS
    recipient = MAIL_RECIPIENT

    # Create message container - the correct MIME type is multipart/alternative.
    msg = MIMEMultipart('alternative')
    msg['Subject'] = "Producto encontrado!"
    msg['From'] = sender
    msg['To'] = recipient
    html_body = ""

    for index, row in result.iterrows():
        html_body += f"""
        <br>
            <br><b>Sku</b>: {row['sku']}
            <br><b>Modelo</b>: {row['modelo']}
            <br><b>Color</b>: {row['color']}
            <br><b>Talla</b>: {row['talla']}
            <br><b>Link</b>: <a href='{row['url']}'>Store</a>
            <br><a href={row['url']}><img src='{row['image']}'/></a>
        <br>
        """

    # Create the body of the message (a plain-text and an HTML version).
    #text = "Hi!\nHow are you?\nHere is the link you wanted:\nhttp://www.python.org"
    html = """\
    <html>
      <head></head>
      <body>
        <p>Se encontro el producto!
           """+html_body+"""
        </p>
      </body>
    </html>
    """


    # Record the MIME types of both parts - text/plain and text/html.
    part = MIMEText(html, 'html')

    # Attach parts into message container.
    # According to RFC 2046, the last part of a multipart message, in this case
    # the HTML message, is best and preferred.
    msg.attach(part)

    # Send the message via local SMTP server.
    s = smtplib.SMTP('smtp.grupotersa.com.mx: 1025')

    # Login para poder enviar mail
    s.login(sender, passw)

    # sendmail function takes 3 arguments: sender's address, recipient's address
    # and message to send - here it is sent as one string.
    s.sendmail(sender, recipient, msg.as_string())
    s.quit()

def main():
    result = check_page()

    if len(result) > 0:
        send_mail(result)
    else:
        print("No se encontraron productos :(")

if __name__ == '__main__':
    main()

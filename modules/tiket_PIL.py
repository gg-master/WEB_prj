import io
import os
from PIL import Image, ImageFont, ImageDraw
import qrcode

path_for_system_img = 'static/img/'


class Ticket:
    """Класс билета"""

    def __init__(self, film_title, cinema_hall_id,
                 place_row, place_col, time_s, time_to, phone, code):
        if os.getcwd().endswith('modules'):
            os.chdir('..')
        # Загрузка данных билета
        self.film_title = film_title
        self.cinema_hall_id = cinema_hall_id
        self.place_row = place_row
        self.place_col = place_col
        self.time_s = time_s
        self.time_to = time_to
        self.phone = phone
        self.code = code
        # Загрузка шаблона билета
        self.im = Image.open(path_for_system_img + 'ticket_new.jpg')
        # Отрисовка всех данных на билете
        self.draw_text()
        self.im.paste(self.make_qrcode().resize((150, 150), Image.ANTIALIAS),
                      (360 - 5, 175 - 18))
        # self.im.show()
        # Преобразование картинка в строку байтов
        self.bytes_str = self.save_tct()

    def draw_text(self):
        font17 = ImageFont.truetype('.fonts/arial.ttf', size=17)
        font15 = ImageFont.truetype('.fonts/arial.ttf', size=15)
        font13 = ImageFont.truetype('.fonts/arial.ttf', size=13)
        draw_text = ImageDraw.Draw(self.im)
        draw_text.text(
            (123, 112 - 16), self.film_title, font=font17, fill='#000000')
        draw_text.text(
            (123, 148 - 18), str(self.cinema_hall_id), font=font17,
            fill='#000000')
        draw_text.text(
            (123, 176 - 16), str(self.place_col), font=font17, fill='#000000')
        draw_text.text(
            (256, 176 - 16), str(self.place_row), font=font17, fill='#000000')
        draw_text.text(
            (57, 232 - 16), f'{self.time_s}', font=font15, fill='#000000')
        draw_text.text(
            (57, 249 - 16), f'{self.time_to}', font=font15, fill='#000000')
        draw_text.text(
            (102, 284 - 12), f'{self.phone}', font=font13, fill='#000000')

    def make_qrcode(self):
        # Создание Qr кода
        text = f'Билет на фильм {self.film_title} ' \
            f'подтвержден. Ждем Вас на сеансе в {self.time_s}.\n' \
            f'Ваш код подтверждения - {self.code}'
        return qrcode.make(text)

    def save_tct(self):
        # Преобразование картинки в строку байтов
        img_bytes = io.BytesIO()
        self.im.save(img_bytes, format='PNG')
        return img_bytes.getvalue()

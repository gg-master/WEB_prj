import io
import os
from PIL import Image, ImageFont, ImageDraw
import qrcode

path_for_system_img = 'static/img/'


class Ticket:
    """Класс билета. Показывает билет, кнопку для
    выбора пути сохранения и созраняет билет по выбранному пути"""

    def __init__(self, film_title, cinema_hall_id,
                 place_row, place_col, time_s, time_to, phone, code):
        if os.getcwd().endswith('modules'):
            os.chdir('..')
        self.title = film_title
        self.hall_id = cinema_hall_id
        self.place_row = place_row
        self.place_col = place_col
        self.time_start = time_s
        self.time_end = time_to
        self.phone = phone
        self.code = code
        font17 = ImageFont.truetype('arial.ttf', size=17)
        font15 = ImageFont.truetype('arial.ttf', size=15)
        font13 = ImageFont.truetype('arial.ttf', size=13)
        self.im = Image.open(path_for_system_img + 'ticket_new.jpg')
        draw_text = ImageDraw.Draw(self.im)
        draw_text.text(
            (123, 112 - 16), film_title, font=font17, fill='#000000')
        draw_text.text(
            (123, 148 - 18), str(cinema_hall_id), font=font17, fill='#000000')
        draw_text.text(
            (123, 176 - 16), str(place_col), font=font17, fill='#000000')
        draw_text.text(
            (256, 176 - 16), str(place_row), font=font17, fill='#000000')
        draw_text.text(
            (57, 232 - 16), f'{time_s}', font=font15, fill='#000000')
        draw_text.text(
            (57, 249 - 16), f'{time_to}', font=font15, fill='#000000')
        draw_text.text(
            (102, 284 - 12), f'{phone}', font=font13, fill='#000000')
        self.im.paste(self.make_qrcode().resize((150, 150), Image.ANTIALIAS),
                      (360 - 5, 175 - 18))
        # self.im.show()
        self.bytes_str = self.save_tct()

    def make_qrcode(self):
        text = f'Билет на фильм {self.title} ' \
            f'подтвержден. Ждем Вас на сеансе в {self.time_start}.\n' \
            f'Ваш код подтверждения - {self.code}'
        return qrcode.make(text)

    def save_tct(self):
        img_bytes = io.BytesIO()
        self.im.save(img_bytes, format='PNG')
        return img_bytes.getvalue()

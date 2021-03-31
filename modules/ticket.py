import sys

from PyQt5.Qt import *
from PyQt5 import QtGui, QtCore
import qrcode
import os

# print(os.getcwd())
path_for_system_img = 'static/img/'

# print(path_for_system_img)


def my_exception_hook(exctype, value, traceback):
    # Print the error and traceback
    print(exctype, value, traceback)
    # Call the normal Exception hook after
    sys._excepthook(exctype, value, traceback)
    sys.exit(1)


# Set the exception hook to our wrapping function
sys.excepthook = my_exception_hook


class Image(qrcode.image.base.BaseImage):
    def __init__(self, border, width, box_size):
        self.border = border
        self.width = width
        self.box_size = box_size
        size = (width + border * 2) * box_size
        self._image = QtGui.QImage(
            size, size, QtGui.QImage.Format_RGB16)
        self._image.fill(QtCore.Qt.white)

    def pixmap(self):
        return QtGui.QPixmap.fromImage(self._image)

    def drawrect(self, row, col):
        painter = QtGui.QPainter(self._image)
        painter.fillRect(
            (col + self.border) * self.box_size,
            (row + self.border) * self.box_size,
            self.box_size, self.box_size,
            QtCore.Qt.black)

    def save(self, stream, kind=None):
        pass


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
        # Разметка
        app = QApplication(sys.argv)
        self.pixmap = QPixmap(path_for_system_img + 'ticket_new.jpg')
        qp = QPainter()
        qp.begin(self.pixmap)
        qp.setFont(QFont('Peignot', 17))
        qp.drawText(QPoint(123, 112), film_title)
        qp.drawText(QPoint(123, 148), str(cinema_hall_id))
        qp.drawText(QPoint(123, 176), str(place_col))
        qp.drawText(QPoint(256, 176), str(place_row))

        qp.setFont(QFont('Peignot', 15))
        qp.drawText(QPoint(57, 232), f'{time_s}')
        qp.drawText(QPoint(57, 249), f'{time_to}')

        qp.setFont(QFont('Peignot', 13))
        qp.drawText(QPoint(102, 284), f'{phone}')

        qrcode = self.make_qrcode()
        qrcode = qrcode.scaled(179, 125, Qt.KeepAspectRatio)
        qp.drawPixmap(QPoint(360, 175), qrcode)
        qp.end()
        self.bytes_str = self.save_tct()

    def make_qrcode(self):
        """Возврадащет сгенеррированный Qrcode как объект Qpixmap"""
        import qrcode
        text = f'Билет на фильм {self.title} ' \
            f'подтвержден. Ждем Вас на сеансе в {self.time_start}.\n' \
            f'Ваш код подтверждения - {self.code}'
        return qrcode.make(text, image_factory=Image).pixmap()

    def save_tct(self):
        # self.pixmap.save(f'ticket333.jpg')
        ba = QtCore.QByteArray()
        buff = QtCore.QBuffer(ba)
        buff.open(QtCore.QIODevice.WriteOnly)
        self.pixmap.save(buff, "PNG")
        pixmap_bytes = ba.data()
        # print(type(pixmap_bytes))
        return pixmap_bytes

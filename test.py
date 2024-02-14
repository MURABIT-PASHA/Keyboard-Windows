import json
import os
import sys
import socket
import threading
import time
import traceback
from pathlib import Path

import keyboard
import pyperclip
import qrcode
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QApplication
from win10toast import ToastNotifier

import resources

QR_IMAGE_NAME = "qrcode.png"
APP_DATA_LOCAL = os.getenv('LOCALAPPDATA')
FOLDER_NAME = "keyboard"

IMAGE_PATH = Path(APP_DATA_LOCAL) / FOLDER_NAME

PORT = 7800
connected_devices = set()


def get_local_ip():
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
    except Exception as e:
        ip = "Error: " + str(e)
    return ip


def create_qr_code():
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(get_local_ip())
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    IMAGE_PATH.mkdir(parents=True, exist_ok=True)
    img.save(f"{Path(APP_DATA_LOCAL)}/{FOLDER_NAME}/{QR_IMAGE_NAME}")


class QRCodeDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("QR Kodu")
        self.setWindowIcon(QtGui.QIcon(":icon_png"))
        self.setGeometry(100, 100, 200, 200)
        layout = QVBoxLayout()

        self.qr_label = QLabel(self)
        pixmap = QPixmap(f"{Path(APP_DATA_LOCAL)}/{FOLDER_NAME}/{QR_IMAGE_NAME}")
        self.qr_label.setPixmap(pixmap)

        layout.addWidget(self.qr_label)
        self.setLayout(layout)
        screen_geometry = QApplication.desktop().screenGeometry()
        self.move(screen_geometry.width() - 350,
                  screen_geometry.height() - 350)


class SystemTrayIcon(QtWidgets.QSystemTrayIcon):
    def __init__(self, icon, parent=None):
        QtWidgets.QSystemTrayIcon.__init__(self, icon, parent)
        self.dialog = None
        self.setToolTip(f'Uygulama Arka Planda Çalışıyor')
        menu = QtWidgets.QMenu(parent)
        create_qr_action = menu.addAction('Bağla')
        create_qr_action.triggered.connect(self.show_qr)
        exit_action = menu.addAction('Çıkış')
        exit_action.triggered.connect(self.exit)
        self.setContextMenu(menu)

    def show_qr(self):
        self.dialog = QRCodeDialog()
        self.dialog.show()

    def exit(self):
        QtWidgets.qApp.quit()


def background_process():
    thread = threading.Thread(target=listen_for_connections)
    thread.daemon = True
    thread.start()
    create_qr_code()


def foreground_process():
    app = QtWidgets.QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    w = QtWidgets.QWidget()
    tray_icon = SystemTrayIcon(QtGui.QIcon(":icon_png"), w)
    tray_icon.show()
    sys.exit(app.exec_())


def main():
    background_process()
    foreground_process()


def listen_for_connections():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((get_local_ip(), PORT))
        s.listen()

        while True:
            conn, addr = s.accept()
            connected_devices.add(conn)
            handle_connection(conn)


def handle_connection(conn):
    with conn:
        while True:
            data = conn.recv(1024)
            if not data:
                break
            else:
                process_message(data.decode())

    connected_devices.remove(conn)


def process_message(msg):
    try:
        message = json.loads(msg)
        order_type = message["orderType"]

        if order_type == "connect":
            try:
                toaster = ToastNotifier()
                toaster.show_toast("Cihaz Bağlandı",
                                   "Android cihazınız başarıyla bağlandı",
                                   icon_path="icon.ico",
                                   duration=10)
            except Exception:
                with open("log.txt", "a") as log_file:
                    log_file.write(traceback.format_exc())
        elif order_type == "type" and message["message"] is not None:
            try:
                keyboard.press_and_release(message["message"])
            except ValueError:
                pyperclip.copy(message["message"])
                time.sleep(0.1)
                keyboard.press_and_release('ctrl+v')
                time.sleep(0.1)
        else:
            toaster = ToastNotifier()
            toaster.show_toast("Hata",
                               "Tanımlanamayan mesaj türü",
                               icon_path="icon.ico",
                               duration=5)
    except json.JSONDecodeError:

        toaster = ToastNotifier()
        toaster.show_toast("Hata",
                           "Gelen mesaj Json formatında değil.\nFarklı bir kaynak bağlanmaya çalışıyor olabilir",
                           icon_path="icon.ico",
                           duration=5)


if __name__ == '__main__':
    main()

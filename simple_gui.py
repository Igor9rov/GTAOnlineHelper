# https://thispointer.com/python-check-if-a-process-is-running-by-name-and-find-its-process-id-pid/
import time
import psutil

from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QPushButton, QApplication, QMessageBox, QStyle

NOT_CORRECT_PID = -1
SECONDS_TO_SLEEP = 8


class ButtonForPausingGTA(QPushButton):
    """Основное окно приложения. из одной кнопки, больше и не нужно"""
    def __init__(self, parent=None):
        QPushButton.__init__(self, parent)
        self.setText("Выкинуть всех из текущей сессии GTA Online")
        self.setWindowTitle("GTA Online Helper")
        self.setWindowIcon(QIcon("icon.png"))
        self.setFixedSize(400, 100)

        # Отдельный поток на приостановку и запуск процесса с gta 5
        self.working_thread = WorkingThread()

        # Связь сигналов и слотов
        self.clicked.connect(self.on_clicked)
        self.working_thread.error_signal.connect(self.on_error)
        self.working_thread.finished.connect(self.on_finished)

    def on_clicked(self):
        """Выполняется при клике на кнопку

        :return: None
        """
        self.working_thread.start()
        self.setEnabled(False)
        self.setText("Процесс приостановлен")

    def on_error(self):
        """Показываем окно пользователю при ошибке, возвращаем кнопку в первоначальное положение

        :return: None
        """
        ErrorMessageBox().exec()
        self.setEnabled(True)
        self.setText("Выкинуть всех из текущей сессии GTA Online")

    def on_finished(self):
        """Выполняется при прекращении работы потоком

        :return: None
        """
        self.setEnabled(True)
        self.setText("Выкинуть всех из текущей сессии GTA Online")


class WorkingThread(QThread):
    error_signal = pyqtSignal()
    """Поток для остановки и запуска процесса с GTA 5"""
    def __init__(self, parent=None):
        QThread.__init__(self, parent)

    def run(self):
        """Ставит и прододжает процесс с GTA 5, если он запущен, если же нет, то отправляет сигнал на кнопку

        :return: None
        """
        pid = get_pid_with_name("gta5")
        if pid == NOT_CORRECT_PID:
            self.error_signal.emit()
        else:
            # Ссылка на процесс с GTA 5
            gta_process = psutil.Process(pid)
            gta_process.suspend()
            # 8 секунд необходимо "висеть", чтобы всех выкинуло из сессии
            time.sleep(SECONDS_TO_SLEEP)
            gta_process.resume()
            

def get_pid_with_name(process_name: str) -> int:
    """Возвращает PID по процессу с указанным именем, если указанный процесс не найден, то возвращает -1

    :param process_name: Имя процесса
    :return: PID по процессу с указанным именем
    :rtype: int
    """
    # Цикл по всем процессам
    for process in psutil.process_iter():
        try:
            process_info = process.as_dict(attrs=["pid", "name"])
            # Проверка на имя процесса
            if process_name.lower() in process_info["name"].lower():
                return process_info["pid"]
        # Ожидаем следующее
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return NOT_CORRECT_PID


class ErrorMessageBox(QMessageBox):
    """Сообщение о ошибке"""
    def __init__(self, parent=None):
        QMessageBox.__init__(self, parent)
        self.setIcon(QMessageBox.Critical)
        self.setWindowTitle("Ошибка")
        self.setWindowIcon(self.style().standardIcon(QStyle.SP_MessageBoxCritical))
        self.setText("Процесс GTA5.exe не найден!")


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    application = ButtonForPausingGTA()
    application.show()
    sys.exit(app.exec())

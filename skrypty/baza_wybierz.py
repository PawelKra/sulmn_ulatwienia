import os
from qgis.core import Qgis, QgsSettings
from PyQt5.QtWidgets import QFileDialog, QDialog, QMessageBox
from PyQt5 import uic

Ui_Dialog, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), '..', 'ui', 'ui_baza.ui'))


class Wskaz:
    def __init__(self, iface):
        self.iface = iface

    def pobierz(self):
        w = PobierzDane()
        w.exec_()

        if not w.porzucone:
            self.iface.messageBar().pushMessage(
                'OK',
                'Wybrana została baza: ' + w.ui.lineEdit.text(),
                Qgis.Success,
                10
            )
            return True
        else:
            return

        # TODO: dodaj sprawdzenie poprawności połączenia sie z baza
        self.iface.messageBar().pushMessage(
            'BŁĄD',
            'Nie udało się połączyć ze wskazaną bazą',
            Qgis.Critical,
            10
        )
        return False


class PobierzDane(QDialog):
    def __init__(self):
        super(PobierzDane, self).__init__()

        self.sett = QgsSettings()
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.kat = ''
        if os.path.exists(self.sett.value('sulmn_uproszcz', '')):
            self.ui.lineEdit.setText(self.sett.value('sulmn_uproszcz'))

        # wartosc True jezeli uzytkownik zrezygnowal z przetwarzania
        self.porzucone = True

        self.ui.pushButton_ok.clicked.connect(self.sprawdz_ok)
        self.ui.pushButton_porzuc.clicked.connect(self.porzuc)
        self.ui.pushButton_wybierz.clicked.connect(self.kat_baza)

    def porzuc(self):
        self.porzucone = True
        self.hide()

    def kat_baza(self):
        sc = QFileDialog().getOpenFileName(
            self,
            'Wskaż baze Taksatora',
            self.kat,
            "Access MDB (*.mdb);;SQLite (*.sqlite)")[0]
        if sc != '':
            self.kat = os.path.dirname(sc)
            self.ui.lineEdit.setText(sc)

    def sprawdz_ok(self):
        if os.path.isfile(self.ui.lineEdit.text()):
            self.porzucone = False
            self.hide()
            self.sett.setValue('sulmn_uproszcz', self.ui.lineEdit.text())
        else:
            msbx = QMessageBox.information(
                self, 'BŁĄD', 'Nie udało się odnaleźć bazy taksatora!'
            )
            return False

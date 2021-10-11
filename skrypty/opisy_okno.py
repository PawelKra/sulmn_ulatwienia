import os
from PyQt5.QtWidgets import QDialog, QTableWidgetItem
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from .baza import Baza
from .opisy_odczyt import OpisyObs
from PyQt5 import uic

Ui_Dialog, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), '..', 'ui', 'ui_taks.ui'))


class OpisyUI(QDialog, OpisyObs):
    def __init__(self):
        super(OpisyUI, self).__init__()

        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.baza = False

        # sygnały
        self.ui.comboBox_obr.currentIndexChanged.connect(
            self.zmiana_obrebu)
        self.ui.tableWidget_lwydz.itemSelectionChanged.connect(
            self.wczytaj_wydzielenie)
        self.ui.lineEdit_filtr.textChanged.connect(self.filtrowanie)
        self.ui.pushButton_czysc.clicked.connect(self.czysc_filtr)

        # połączenie przewijania poszczególnych tabel
        self.ui.tableWidget_gatunki.verticalScrollBar().valueChanged.connect(
            self.ui.tableWidget_warstwy.verticalScrollBar().setValue)
        self.ui.tableWidget_warstwy.verticalScrollBar().valueChanged.connect(
            self.ui.tableWidget_gatunki.verticalScrollBar().setValue)
        self.ui.tableWidget_pnsw.verticalScrollBar().valueChanged.connect(
            self.ui.tableWidget_pnsw_gat.verticalScrollBar().setValue)
        self.ui.tableWidget_pnsw_gat.verticalScrollBar().valueChanged.connect(
            self.ui.tableWidget_pnsw.verticalScrollBar().setValue)

    def dodaj_baze(self, b):
        ''' dodawana baza powinna być sprawdzona pod kątem poprawnosci
        '''
        self.czysc(True)
        self.baza = Baza(b)
        self.baza.polacz()
        self.przygotuj_strukture()  # opisy_odczyt
        self.przygotuj_obreby()  # opisy_odczyt
        # wczytaj obreby comboxa
        for it in sorted([x[3] for x in self.sl_obr.values()]):
            self.ui.comboBox_obr.addItem(it)

    def czysc_filtr(self):
        self.ui.lineEdit_filtr.setText('')
        self.wczytaj_wydzielenia()

    def czysc(self, obr=False):
        if obr:
            self.ui.comboBox_obr.blockSignals(True)
            self.ui.comboBox_obr.clear()
            self.ui.comboBox_obr.blockSignals(False)

        self.ui.label_gmi.setText('<<nazwa_gminy>>')
        self.ui.label_obr.setText('<<nazwa_obrębu>>')
        self.ui.label_woj.setText('<<nazwa_województwa>>')
        self.ui.label_pow.setText('<<nazwa_powiatu>>')
        self.ui.label_ewid_staty.setText('')
        self.ui.lineEdit_adrles.setText('')
        self.ui.lineEdit_powwydz.setText('')
        self.ui.textEdit_opis.setText('')
        self.ui.lineEdit_filtr.setText('')

        sl = {
            self.ui.tableWidget_lwydz: [1, ['Wydzielenia', ], 260],
            self.ui.tableWidget_ewid: [
                6,
                ['Nr. dz.', 'AU', 'SQ', 'Pow. uż.', 'Pow. w wydz.', 'Pow. dz.',
                 ],
                90,
            ],
            self.ui.tableWidget_owydz: [
                9,
                ['Rodz. pow.', 'Cecha d-stanu', 'Bud. pion.', 'TSL', 'TD',
                 'Typ pokrywy', 'Drewno martwe', 'Gł. przycz. zagr.',
                 'Stopień uszk.', ],
                90
                ],
            self.ui.tableWidget_warstwy: [
                7,
                ['Kod', 'Zmiesz.', 'Zwarcie', 'Zd.', 'Zagęsz.', 'Jak.hod.',
                 'Lokal.'],
                39,
            ],
            self.ui.tableWidget_gatunki: [
                11,
                ['Kod', 'Udział', 'Wiek', 'D13', 'Wys.', 'Bonit.', 'Zasob.',
                 'Zasob.obl', 'Jak.tech.', 'Przyrost', 'Przyr./p.(10l)'],
                50,
            ],
            self.ui.tableWidget_wskgosp: [
                6,
                ['Gr. czyn.', 'Pilność', '%pow. wydz.', 'Pow.', '% grub.',
                 'm3 grub'],
                80,
            ],
            self.ui.tableWidget_pnsw: [
                5,
                ['Nr', 'Kod', 'Lok.', 'Pow.', 'Liczba'],
                100,
            ],
            self.ui.tableWidget_pnsw_gat: [2, ['Gat.', 'Wiek'], 104],
            self.ui.tableWidget_osobl: [
                7,
                ['Nr', 'Rodz. ob.', 'Nazwa', 'Pom. prz.', 'Lokaliz.', 'Pow.',
                 'Liczba'],
                100
            ],
            self.ui.tableWidget_fochr: [1, ['Forma Ochrony'], 500],
            self.ui.tableWidget_wlasciciele: [
                6,
                ['Nr. dz.', 'Nr. wł.', 'Nazwisko/Nazwa wł.', 'Nr. małż.',
                 'Nazwisko małżonka', 'Udział'],
                110
            ],
        }

        self.ui.tableWidget_warstwy.setVerticalScrollBarPolicy(
            Qt.ScrollBarAlwaysOff)
        self.ui.tableWidget_pnsw.setVerticalScrollBarPolicy(
            Qt.ScrollBarAlwaysOff)

        for k, v in sl.items():
            k.blockSignals(True)
            k.clear()
            k.setColumnCount(len(v[1]))
            k.setHorizontalHeaderLabels(v[1])
            k.setAlternatingRowColors(True)
            k.setSortingEnabled(False)
            # k.resizeColumnsToContents()
            k.horizontalHeader().setDefaultSectionSize(v[2])
            if v[1][0] in ['Kod', 'Gr. czyn.', 'Nr. dz.', 'Nr', 'Gat.']:
                k.verticalHeader().setDefaultSectionSize(14)
            if v[1][0] == 'Rodz. pow.':
                k.verticalHeader().setDefaultSectionSize(44)
            k.blockSignals(False)

    def zmiana_obrebu(self):
        obr = self.ui.comboBox_obr.currentText()
        self.ui.lineEdit_filtr.setText('')
        if obr[0] == '(':
            self.pobierz_l_wydz(obr[1:8])
        self.wczytaj_wydzielenia()

    def wczytaj_wydzielenia(self):
        self.ui.tableWidget_lwydz.blockSignals(True)
        self.ui.tableWidget_lwydz.setRowCount(len(self.l_wydz_w))
        font = QFont()
        font.setPointSize(12)
        for i, val in enumerate(self.l_wydz_w):
            it = QTableWidgetItem(val)
            it.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
            it.setFont(font)
            self.ui.tableWidget_lwydz.setItem(i, 0, it)
        self.ui.tableWidget_lwydz.blockSignals(False)

    def filtrowanie(self):
        filtr = str(self.ui.lineEdit_filtr.text())
        filtr = filtr.replace(' ', '').replace('-', '')
        # jeżeli filtr wprowadzony przez użytkownika jest krótszy od 2 znaków,
        # pomijamy filtrowanie i zwracamy wszystkie wydzielenia
        if len(filtr) < 2:
            if len(self.l_wydz_w) != list(self.sl_wydz_f.keys()):
                self.l_wydz_w = [x for x in sorted(
                    list(self.sl_wydz.keys()),
                    key=lambda y: self.sl_wydz_sort[y])]
            return

        self.l_wydz_w = sorted(
            [v for k, v in self.sl_wydz_f.items() if filtr in k],
            key=lambda y: self.sl_wydz_sort[y]
        )

        self.wczytaj_wydzielenia()

    def wczytaj_wydzielenie(self):
        n = self.ui.tableWidget_lwydz.currentItem()
        if str(n.text()) not in self.sl_wydz:
            return

        n = self.ui.tableWidget_lwydz.currentItem()
        self.przetworz_wydzielenie(self.sl_wydz[str(n.text())])
        # slownik dopasowujacy maciez do odpowiedniego widgetu
        sl = {
            self.ui.tableWidget_ewid: self.w_ewid,
            self.ui.tableWidget_owydz: self.w_opog,
            self.ui.tableWidget_warstwy: self.w_opwa,
            self.ui.tableWidget_gatunki: self.w_opgt,
            self.ui.tableWidget_wskgosp: self.w_wsgs,
            self.ui.tableWidget_pnsw: self.w_pnsw,
            self.ui.tableWidget_pnsw_gat: self.w_pngt,
            self.ui.tableWidget_osobl: self.w_phen,
            self.ui.tableWidget_fochr: self.w_foch,
            self.ui.tableWidget_wlasciciele: self.w_wlas,
        }

        for k, v in sl.items():
            self.zaladuj_tab(k, v)

        self.ui.label_woj.setText(self.w_adr[0])
        self.ui.label_pow.setText(self.w_adr[1])
        self.ui.label_gmi.setText(self.w_adr[2])
        self.ui.label_obr.setText(self.w_adr[3])

        self.ui.lineEdit_adrles.setText(
            str(n.text()))

        self.ui.lineEdit_powwydz.setText(self.w_pow)
        self.ui.textEdit_opis.setText(self.w_opis)

    def pokaz_wydzielenie(self, adr):
        ''' Metoda pokazuje okno opisu wydzielenia z konkretnym adresem podanym
        przez użytkownika, adr musi być poprawny i znajdować sie w bazie.
        metoda powinna zostać uruchomiona po zainicjowaniu obrebow
        '''
        ind = [i for i in range(self.ui.comboBox_obr.count())
               if adr[3:10] in self.ui.comboBox_obr.itemText(i)][0]
        self.ui.comboBox_obr.setCurrentIndex(ind)
        # self.wczytaj_wydzielenia()
        rcount = self.ui.tableWidget_lwydz.rowCount()
        ind = [i for i in range(rcount)
               if adr == self.ui.tableWidget_lwydz.item(i, 0).text()][0]
        self.ui.tableWidget_lwydz.setCurrentCell(ind, 0)

    def zaladuj_tab(self, tabwidget, lista):
        '''Metoda ładuje podaną macież do odpowiedniego widgetu, macież musi
        miec takie rozmiary jak zadeklarowane w inicie'''

        tabwidget.blockSignals(True)
        tabwidget.setRowCount(len(lista))
        for i, val in enumerate(lista):
            for j, v in enumerate(val):
                it = QTableWidgetItem(str(v))
                it.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                tabwidget.setItem(i, j, it)
        tabwidget.blockSignals(False)

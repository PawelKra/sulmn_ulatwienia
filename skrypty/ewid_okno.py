import os
from PyQt5.QtWidgets import QDialog, QTableWidgetItem, QTableWidget
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from .baza import Baza

from .ewid_opisy import EwidObs

from PyQt5 import uic
Ui_Dialog, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), '..', 'ui', 'ui_ewid.ui'))


class EwidUI(QDialog, EwidObs):
    def __init__(self):
        super(EwidUI, self).__init__()

        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.baza = False

        self.ui.tableWidget_spis.setSelectionBehavior(QTableWidget.SelectRows)

        # sygnały
        self.ui.lineEdit_filtr.textChanged.connect(self.filtrowanie)
        self.ui.pushButton_czysc.clicked.connect(self.czysc_filtr)
        self.ui.comboBox_woj.currentIndexChanged.connect(self.ustaw_pow)
        self.ui.comboBox_pow.currentIndexChanged.connect(self.ustaw_gm)
        self.ui.comboBox_gmi.currentIndexChanged.connect(self.ustaw_obr)
        self.ui.comboBox_obr.currentIndexChanged.connect(
            self.przeladuj_obreb)
        self.ui.tableWidget_spis.currentCellChanged.connect(
            self.wczytaj_dzewid)

        # połączenie przewijania poszczególnych tabel
        self.ui.tableWidget_uzytki.verticalScrollBar().valueChanged.connect(
            self.ui.tableWidget_wydz.verticalScrollBar().setValue)
        self.ui.tableWidget_wydz.verticalScrollBar().valueChanged.connect(
            self.ui.tableWidget_uzytki.verticalScrollBar().setValue)

    def dodaj_baze(self, b):
        ''' dodawana baza powinna być sprawdzona pod kątem poprawnosci
        '''
        self.czysc(True)
        self.baza = Baza(b)
        self.baza.polacz()
        self.przygotuj_strukture()  # ewid_odczyt
        self.przygotuj_adresy()  # ewid_odczyt

        # wczytaj woj comboxa
        wkody = sorted([w['ops'] for w in self.sl_adr.values()])
        self.ui.comboBox_woj.blockSignals(True)
        for it in wkody:
            self.ui.comboBox_woj.addItem(it)
        self.ui.comboBox_woj.blockSignals(False)
        self.ustaw_pow()

    def ustaw_pow(self):
        kod_woj = self.ui.comboBox_woj.currentText()[1:3]
        pkody = sorted([self.sl_adr[kod_woj][p]['ops']
                        for p in self.sl_adr[kod_woj].keys()
                        if p != 'ops'])

        self.ui.comboBox_pow.blockSignals(True)
        for it in pkody:
            self.ui.comboBox_pow.addItem(it)
        self.ui.comboBox_pow.blockSignals(False)
        self.ui.comboBox_pow.setCurrentIndex(0)
        self.ustaw_gm()

    def ustaw_gm(self):
        kod_woj = self.ui.comboBox_woj.currentText()[1:3]
        kod_pow = self.ui.comboBox_pow.currentText()[1:3]

        gkody = sorted([self.sl_adr[kod_woj][kod_pow][g]['ops']
                        for g in self.sl_adr[kod_woj][kod_pow].keys()
                       if g != 'ops'])

        self.ui.comboBox_gmi.blockSignals(True)
        for it in gkody:
            self.ui.comboBox_gmi.addItem(it)
        self.ui.comboBox_gmi.blockSignals(False)
        self.ui.comboBox_gmi.setCurrentIndex(0)
        self.ustaw_obr()

    def ustaw_obr(self):
        kod_woj = self.ui.comboBox_woj.currentText()[1:3]
        kod_pow = self.ui.comboBox_pow.currentText()[1:3]
        kod_gmi = self.ui.comboBox_gmi.currentText()[1:4]
        okody = sorted([
            self.sl_adr[kod_woj][kod_pow][kod_gmi][o]
            for o in self.sl_adr[kod_woj][kod_pow][kod_gmi].keys()
            if o != 'ops'])

        self.ui.comboBox_obr.blockSignals(True)
        self.ui.comboBox_obr.clear()
        for it in okody:
            self.ui.comboBox_obr.addItem(it)
        self.ui.lineEdit_filtr.setText('')
        self.czysc()
        self.ui.comboBox_obr.blockSignals(False)
        self.ui.comboBox_obr.setCurrentIndex(0)
        self.wczytaj_spis_dzewid()

    def czysc_filtr(self):
        self.ui.lineEdit_filtr.setText('')
        self.filtrowanie()

    def filtrowanie(self):
        filtr = str(self.ui.lineEdit_filtr.text())
        if len(filtr) < 2:
            if len(self.l_dz) != len(self.l_dz_w):
                self.l_dz_w = self.l_dz
            self.wczytaj_spis_dzewid()
            return

        self.l_dz_w = [x for x in self.l_dz if
                       filtr in x.split('-')[4]]
        self.wczytaj_spis_dzewid()

    def czysc(self, adr=False):
        if adr:
            comb = [self.ui.comboBox_woj,
                    self.ui.comboBox_pow,
                    self.ui.comboBox_gmi,
                    self.ui.comboBox_obr,
                    ]
            for c in comb:
                c.blockSignals(True)
                c.clear()
                c.blockSignals(False)

            self.ui.tableWidget_spis.blockSignals(True)
            self.ui.tableWidget_spis.clear()
            lab = ['Woj.', 'Pow.', 'Gm.', 'Obr.', 'Nr dz.', 'Pow.']
            self.ui.tableWidget_spis.setColumnCount(len(lab))
            self.ui.tableWidget_spis.setHorizontalHeaderLabels(lab)
            self.ui.tableWidget_spis.horizontalHeader().setDefaultSectionSize(
                                                                         34)
            self.ui.tableWidget_spis.blockSignals(False)

        sl = {
            self.ui.tableWidget_wlasc: [
                ['Nr wł.', 'Nazwa/Nazwisko', 'Nr małżonka',
                 'Nazwisko małżonka', 'Udział'], 60],
            self.ui.tableWidget_uzytki: [
                ['Uż.', 'Kl.', 'Pow. uż.', 'Do zal.'], 61],
            self.ui.tableWidget_wydz: [
                ['Adr. leś.', 'Pow. wydz.', 'Pow. w wydz.', 'Rodz. pow.'],
                85]
        }

        self.ui.lineEdit_nrdz.setText('')
        self.ui.lineEdit_ark.setText('')
        self.ui.lineEdit_pow.setText('0.0000')

        sl_czysc = {
            self.ui.tableWidget_adres: 4,
            self.ui.tableWidget_wlasn: 7,
        }
        for k, v in sl_czysc.items():
            for i in range(0, v):
                it = QTableWidgetItem('')
                k.setItem(0, i, it)

        for k, v in sl.items():
            k.clear()
            k.setAlternatingRowColors(True)
            k.setColumnCount(len(v[0]))
            k.setHorizontalHeaderLabels(v[0])
            k.horizontalHeader().setDefaultSectionSize(v[1])
            k.setSortingEnabled(False)

        self.ui.tableWidget_uzytki.setVerticalScrollBarPolicy(
            Qt.ScrollBarAlwaysOff)
        self.ui.tableWidget_uzytki.setHorizontalScrollBarPolicy(
            Qt.ScrollBarAlwaysOff)
        self.ui.tableWidget_wydz.setHorizontalScrollBarPolicy(
            Qt.ScrollBarAlwaysOff)

        self.ui.tableWidget_wydz.setColumnWidth(0, 200)
        self.ui.tableWidget_spis.setColumnWidth(4, 80)
        self.ui.tableWidget_spis.setColumnWidth(5, 80)
        self.ui.tableWidget_wlasc.setColumnWidth(1, 260)
        self.ui.tableWidget_wlasc.setColumnWidth(3, 260)

    def przeladuj_obreb(self):
        self.ui.lineEdit_filtr.blockSignals(True)
        self.ui.lineEdit_filtr.setText('')
        self.ui.lineEdit_filtr.blockSignals(False)
        self.wczytaj_spis_dzewid()

    def wczytaj_spis_dzewid(self):
        kod_woj = self.ui.comboBox_woj.currentText()[1:3]
        kod_pow = self.ui.comboBox_pow.currentText()[1:3]
        kod_gmi = self.ui.comboBox_gmi.currentText()[1:4]
        kod_obr = self.ui.comboBox_obr.currentText()[1:5]

        if self.ui.lineEdit_filtr.text() == '':
            self.przygotuj_dzewid(kod_woj, kod_pow, kod_gmi, kod_obr)

        self.ui.tableWidget_spis.blockSignals(True)
        self.ui.tableWidget_spis.setRowCount(len(self.l_dz_w))

        for i, it in enumerate(self.l_dz_w):
            its = it.split('-')
            for j, kom in enumerate(its):
                cell = QTableWidgetItem(str(kom))
                cell.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                self.ui.tableWidget_spis.setItem(i, j, cell)
        self.ui.tableWidget_spis.blockSignals(False)

    def wczytaj_dzewid(self):
        # jako kod trakotwany jest zbitek kolumn dla wiersza z tableWidget_spis

        self.czysc()
        row = self.ui.tableWidget_spis.currentRow()
        if row < 0:
            self.czysc()

        kodt = []
        for col in range(0, 6):
            cell = self.ui.tableWidget_spis.item(row, col)
            kodt.append(cell.text())

        kod = '-'.join(kodt)

        self.przetworz_dzewid(kod)

        self.ui.lineEdit_nrdz.setText(kodt[4])
        self.ui.lineEdit_pow.setText(kodt[5])
        self.ui.lineEdit_ark.setText(self.ark)

        self.zaladuj_tab(self.ui.tableWidget_adres,
                         [[self.ui.comboBox_woj.currentText(),
                           self.ui.comboBox_pow.currentText(),
                           self.ui.comboBox_gmi.currentText(),
                           self.ui.comboBox_obr.currentText()]])

        self.zaladuj_tab(self.ui.tableWidget_wlasc, self.e_wlasc)
        self.zaladuj_tab(self.ui.tableWidget_wlasn, self.e_wlasn)
        self.zaladuj_tab(self.ui.tableWidget_uzytki, self.e_uzyt)
        self.zaladuj_tab(self.ui.tableWidget_wydz, self.e_wydz)

    def zaladuj_tab(self, tabwidget, lista):
        '''Metoda ładuje podaną macież do odpowiedniego widgetu, macież musi
        miec takie rozmiary jak zadeklarowane w inicie'''

        tabwidget.blockSignals(True)
        tabwidget.setRowCount(len(lista))
        poprzedni = ''
        for i, val in enumerate(lista):
            for j, v in enumerate(val):
                it = QTableWidgetItem(str(v))
                it.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                tabwidget.setItem(i, j, it)
                if tabwidget == self.ui.tableWidget_uzytki or \
                        tabwidget == self.ui.tableWidget_wydz:
                    if self.e_uzyt[i][0] == 'Ls' or \
                            (poprzedni == 'Ls' and self.e_uzyt[i][0] == ''):
                        tabwidget.item(i, j).setBackground(
                            QColor(161, 199, 170))
                        if self.e_uzyt[i][0] != '':
                            poprzedni = self.e_uzyt[i][0]
        tabwidget.blockSignals(False)

    def pokaz_dz_wybrana(self, w, p, g, o, pid):
        iw = [i for i in range(self.ui.comboBox_woj.count())
              if self.ui.comboBox_woj.itemText(i)[1:3] == w][0]
        self.ui.comboBox_woj.setCurrentIndex(iw)

        ip = [i for i in range(self.ui.comboBox_pow.count())
              if self.ui.comboBox_pow.itemText(i)[1:3] == p][0]
        self.ui.comboBox_pow.setCurrentIndex(ip)

        ig = [i for i in range(self.ui.comboBox_gmi.count())
              if self.ui.comboBox_gmi.itemText(i)[1:4] == g][0]
        self.ui.comboBox_gmi.setCurrentIndex(ig)

        io = [i for i in range(self.ui.comboBox_obr.count())
              if self.ui.comboBox_obr.itemText(i)[1:5] == o][0]
        self.ui.comboBox_obr.setCurrentIndex(io)

        nr = ''
        powdz = '0.0000'
        for key, val in self.sl_dzi.items():
            if val == pid:
                nr = key.split('-')[4]
                powdz = key.split('-')[5]

        if nr == '' or powdz == '0.0000':
            return

        for row in range(self.ui.tableWidget_spis.rowCount()):
            it = self.ui.tableWidget_spis.item(row, 4)
            if it.text() == nr:
                itp = self.ui.tableWidget_spis.item(row, 5)
                if itp.text() == powdz:
                    self.ui.tableWidget_spis.setCurrentCell(row, 0)

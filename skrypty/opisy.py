import os
import re
from qgis.core import Qgis, QgsSettings
from .baza_wybierz import Wskaz
from .baza import Baza
from .opisy_okno import OpisyUI


class Opisy:
    def __init__(self, iface):
        self.iface = iface
        self.baza = False

    def pokaz_okno(self):
        """Metoda wyświetla okno opisowe, dodaje wsyzstkie nagłowki i kasuje
        całą zawartość tabel, podczytuje liste wydzieleń z bazy oraz obręby
        """
        self.okno = OpisyUI()
        self.okno.dodaj_baze(self.baza)
        self.okno.exec_()

    def podczytaj_baze(self):
        braw = QgsSettings().value('sulmn_uproszcz', '')
        b = os.path.normpath(os.sep.join(re.split(r'\\|/', braw)))
        if not os.path.exists(b):
            pd = Wskaz(self.iface)
            if not pd.pobierz():
                return False

        if os.path.isfile(b):
            self.baza = Baza(b)
            if self.baza.polacz():
                self.baza.zamknij()
                self.baza = b
                return True

        self.iface.messageBar().pushMessage(
            'BAZA', 'Nie udało się połączyć z bazą danych.',
            Qgis.Critical,
            20
        )
        return False

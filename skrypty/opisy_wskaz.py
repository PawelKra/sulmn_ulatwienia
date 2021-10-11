import os
from qgis.core import Qgis, QgsFeatureRequest, QgsRectangle, QgsProject

from .opisy import Opisy
from .baza import Baza
from .opisy_okno import OpisyUI


class OpisWskazany(Opisy):
    def __init__(self, iface):
        self.iface = iface
        self.padr = ''  # nazwa kolumny z adresem lesnym

    def sprawdz_podstawe(self):
        '''Metoda sprawdza czy w warstwie zaznaczonej w TOC znajduje się
        odpowiednia kolumna ADR_LES lub ADR_BDL, a następnie czy polaczenie
        z baza jest poprawne
        '''
        try:
            lyrs = [x for x in QgsProject.instance().mapLayers().values()
                    if x.name() in ['POW', 'WYDZ', 'WYDZ_POL']]
            if len(lyrs) == 0:
                lyr = self.iface.activeLayer()
                if lyr.wkbType() in [3, 6]:
                    if len([x.name() for x in
                            lyr.dataProvider().fields().toList()
                            if x.name() in ['ADR_LES', 'ADR_BDL']]) > 0:
                        lyrs.append(lyr)

            if len(lyrs) == 0:
                self.iface.messageBar().pushCritical(
                    'BŁĄD',
                    'Brak odpowiednich warstw w Polu pracy!'
                )
                return False

            self.wydz = lyrs[0]
            pola = [x.name() for x in
                    self.wydz.dataProvider().fields().toList()
                    if x.name() in ['ADR_LES', 'ADR_BDL']]
        except Exception:
            self.iface.messageBar().pushCritical(
                'BŁĄD', 'Brak odpowiednich warstw w Polu pracy!'
            )
            return False

        if len(pola) == 2:
            self.padr = 'ADR_LES'
        elif len(pola) == 1:
            self.padr = pola[0]
        else:
            self.iface.messageBar().pushMessage(
                'BŁĄD',
                'Brak odpowiedniego pola w zaznaczonej warstwie \'ADR_LES\'',
                Qgis.Critical,
                20
            )
            return False

        if not self.podczytaj_baze():
            return False

        return True

    def sprawdz_reszte(self, k):
        koord = list(k)
        rec = QgsRectangle(koord[0]-0.1, koord[1]-0.1,
                           koord[0]+0.1, koord[1]+0.1)
        req = QgsFeatureRequest().setFilterRect(rec)
        f = False
        for fw in self.wydz.getFeatures(req):
            f = fw[self.padr]

        if f is False:
            self.iface.messageBar().pushMessage(
                'BŁĄD',
                'Proszę wskazać poligon wydzielenia',
                Qgis.Warning,
                5
            )
            return False

        if len(f) < 11:
            self.iface.messageBar().pushMessage(
                'BŁĄD',
                'Proszę sprawdzić czy adres leśny w warstwie jest poprawny'
                ', proszę sprawdzić kolumnę: '+self.padr,
                Qgis.Critical, 10)
            return False

        self.baza_l = Baza(self.baza)
        self.baza_l.polacz()
        obr = [x[0]+x[1] for x in self.baza_l.pobierz_obr()]
        if f[3:10] not in obr:
            self.iface.messageBar().pushMessage(
                'BŁĄD',
                'We wskazanej bazie nie występuje taki obręb, sprawdź czy '
                'czy wskazałeś poprawną bazę',
                Qgis.Critical, 10)
            self.baza_l.zamknij()
            return False

        if f not in [x[1] for x in self.baza_l.pobierz_lwydz(f[3:10])]:
            self.iface.messageBar().pushMessage(
                'BŁĄD',
                'We wskazanej bazie nie występuje takie wydzielenie, '
                'sprawdź czy czy wskazałeś poprawną bazę',
                Qgis.Critical, 10)
            self.baza_l.zamknij()
            return False

        self.baza_l.zamknij()
        self.adr = f
        self.pokaz_okno_wybrane()

    def pokaz_okno_wybrane(self):
        self.okno = OpisyUI()
        self.okno.dodaj_baze(self.baza)
        self.okno.pokaz_wydzielenie(self.adr)
        self.okno.exec_()

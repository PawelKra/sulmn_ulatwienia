import os
from qgis.core import Qgis, QgsFeatureRequest, QgsRectangle, QgsProject, \
    QgsFeature
from .ewid import Ewidencja
from .baza import Baza
from .ewid_okno import EwidUI



class EwidWskazana(Ewidencja):
    def __init__(self, iface):
        self.iface = iface
        self.tryb = ''  # 'pryw'-'DZKAT'; 'sulmn'-'DZ_EWID'

    def sprawdz_podstawe(self):
        """Metoda sprawdza czy w warstwie zaznaczonej w TOC znajduje się
        odpowiednia kolumna PARCELID, a następnie czy polaczenie
        z baza jest poprawne

        PARCELID w postaci:
        '24050220012.142/7' lub '240502_20012.142/7' albo
        '24050220012.AR_1.142/7'
        """

        # czy jest poprawna baza?
        if not self.podczytaj_baze():
            return False

        try:
            # tryb warstwy prywatnej
            lyrp = [x for x in QgsProject.instance().mapLayers().values()
                    if x.name() == 'DZKAT']
            if len(lyrp) == 1:
                self.dz = lyrp[0]
                pola = [x.name() for x in
                        self.dz.dataProvider().fields().toList()
                        if x.name() == 'PARCELID']
                if len(pola) == 1:
                    self.tryb = 'pryw'
                    self.padr = 'PARCELID'
                else:
                    self.iface.messageBar().pushMessage(
                        'BŁĄD',
                        'Brak odpowiedniego pola w zaznaczonej '
                        'warstwie \'PARCELID\' (24050220012.142/7)',
                        Qgis.Critical,
                        20
                    )
                    return False
            elif len(lyrp) > 1:
                self.iface.messageBar().pushMessage(
                    'BŁĄD',
                    'W projekcie powinna znajdować się tylko 1 warstwa DZKAT!',
                    Qgis.Critical,
                    20
                )
                return False
        except Exception:
            self.iface.messageBar().pushMessage(
                'BŁĄD',
                'Coś poszło nie tak w podczytywaniu warstwy DZKAT',
                Qgis.Critical,
                20
            )
            return False

        # tryb warstwy sulmn  (DZ_EWID)
        try:
            lyrs = [x for x in QgsProject.instance().mapLayers().values()
                    if x.name() == 'DZ_EWID']
            if len(lyrs) == 1:
                self.dz = lyrs[0]
                pola = [x.name() for x in
                        self.dz.dataProvider().fields().toList()
                        if x.name() in ['ADR_ADM', 'NR_EW']]
                if len(pola) == 2:
                    self.tryb = 'sulmn'
                else:
                    self.iface.messageBar().pushMessage(
                        'BŁĄD',
                        'Brak odpowiednich pól w zaznaczonej '
                        'warstwie (ADR_ADM, NR_EW)',
                        Qgis.Critical,
                        20
                    )
                    return False
            else:
                self.iface.messageBar().pushMessage(
                    'BŁĄD',
                    'W projekcie powinna znajdować się tylko '
                    '1 warstwa DZ_EWID!',
                    Qgis.Critical,
                    20
                )
                return False
        except Exception:
            self.iface.messageBar().pushMessage(
                'BŁĄD',
                'Coś poszło nie tak w podczytywaniu warstwy DZ_EWID',
                Qgis.Critical,
                20
            )
            return False

        if len(lyrs) + len(lyrp) == 0:
            self.iface.messageBar().pushMessage(
                'BŁĄD',
                'Brak warstw z działkami [DZKAT, DZ_EWID]',
                Qgis.Critical,
                20
            )
            return False

        return True

    def sprawdz_reszte(self, k):
        koord = list(k)
        rec = QgsRectangle(koord[0]-0.1, koord[1]-0.1,
                           koord[0]+0.1, koord[1]+0.1)
        req = QgsFeatureRequest().setFilterRect(rec)

        fd = False
        try:
            fd = next(self.dz.getFeatures(req))
        except StopIteration:
            pass

        if not isinstance(fd, QgsFeature):
            self.iface.messageBar().pushWarning(
                'BŁĄD', 'Proszę wskazać poligon działki'
            )
            return False

        fadr = False
        if self.tryb == 'pryw':
            ftemp = str(fd[self.padr])  # str bo inaczej moze byc QVariant
            if len(ftemp) == 0:
                self.iface.messageBar().pushWarning(
                    'BŁĄD', 'Kolumna PARCELID musi być wypełniona!'
                )
                return False

            if '_' in ftemp:
                ftemp = ftemp.replace('_', '')
            fadr = ftemp

        if self.tryb == 'sulmn':
            adr = str(fd['ADR_ADM']).replace('-', '')
            dz = str(fd['NR_EW'])

            if len(adr) == 0 and len(dz) == 0:
                self.iface.messageBar().pushWarning(
                    'BŁĄD', 'Kolumny ADR_ADM i NR_EW muszą być wypełnione!'
                )
                return False

            fadr = f'{adr}.{dz}'
        self.sprawdz(fadr)

    def sprawdz(self, f):
        self.fwoj = ''
        self.fpow = ''
        self.fgmi = ''
        self.fobr = ''
        self.fark = ''
        self.fnr = ''
        self.fpid = ''
        if len(f) < 11:
            self.iface.messageBar().pushMessage(
                'BŁĄD',
                'Proszę sprawdzić czy adres działki w warstwie jest poprawny'
                ', proszę sprawdzić kolumnę: '+self.padr,
                Qgis.Critical, 10)
            return False

        self.baza_l = Baza(self.baza)
        self.baza_l.polacz()
        self.okno = EwidUI()
        self.okno.dodaj_baze(self.baza)
        self.okno.przygotuj_strukture()
        self.okno.przygotuj_adresy()

        if f[:2] not in self.okno.sl_adr:
            self.iface.messageBar().pushMessage(
                'BŁĄD',
                'We wskazanej bazie nie występuje takie województwo, '
                'sprawdź czy czy wskazałeś poprawną bazę', Qgis.Critical, 10)
            self.baza_l.zamknij()
            return False
        self.fwoj = f[:2]

        if f[2:4] not in self.okno.sl_adr[f[:2]]:
            self.iface.messageBar().pushMessage(
                'BŁĄD',
                'We wskazanej bazie nie występuje taki powiat, '
                'sprawdź czy czy wskazałeś poprawną bazę', Qgis.Critical, 10)
            self.baza_l.zamknij()
            return False
        self.fpow = f[2:4]

        if f[4:7] not in self.okno.sl_adr[f[:2]][f[2:4]]:
            self.iface.messageBar().pushMessage(
                'BŁĄD',
                'We wskazanej bazie nie występuje taka gmina,  '
                'sprawdź czy czy wskazałeś poprawną bazę', Qgis.Critical, 10)
            self.baza_l.zamknij()
            return False
        self.fgmi = f[4:7]

        if f[7:11] not in self.okno.sl_adr[f[:2]][f[2:4]][f[4:7]]:
            self.iface.messageBar().pushMessage(
                'BŁĄD',
                'We wskazanej bazie nie występuje taki obręb ewid.,  '
                'sprawdź czy czy wskazałeś poprawną bazę', Qgis.Critical, 10)
            self.baza_l.zamknij()
            return False
        self.fobr = f[7:11]

        # przypadek gdy w obrebach nie ma arkuszy
        if len(f.split('.')) == 2:
            self.fnr = f.split('.')[1]
        elif len(f.split('.')) == 3:
            self.fnr = f.split('.')[2]
            self.fark = f.split('.')[1]

        self.fpid = self.baza_l.pobierz_pid(self.fwoj,
                                            self.fpow,
                                            self.fgmi,
                                            self.fobr,
                                            self.fnr,
                                            self.fark
                                            )[0][0]

        if self.fpid is False:
            return False

        self.baza_l.zamknij()
        self.pokaz_okno_wybrane()

    def pokaz_okno_wybrane(self):
        self.okno.pokaz_dz_wybrana(self.fwoj,
                                   self.fpow,
                                   self.fgmi,
                                   self.fobr,
                                   self.fpid,
                                   )
        self.okno.exec_()

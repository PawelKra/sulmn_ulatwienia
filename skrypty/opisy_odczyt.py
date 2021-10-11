class OpisyObs:
    # klasa do bsługi danych z bazy, przygotwuje dane do prezentacji
    # użtykownikowi
    def przygotuj_strukture(self):
        # slownik w postaci adr_les: int_num
        self.sl_wydz = {}
        # lista wydzielen w odpowiedniej kolejności do wyświetlenia uż.
        self.l_wydz_w = []
        # sl wydz z ograniczona liczba spacji do 1, do latwego filrowania
        self.sl_wydz_f = {}

        # tablice z danymi opisowymi wydzielenia
        self.w_ewid = []
        self.w_wlas = []
        self.w_adr = ['--', '--', '--', '--']
        self.w_opog = []  # opis ogolny
        self.w_opwa = []  # opis warstw d-stanu
        self.w_opgt = []  # opis gatunkow dstanu dla warstw
        self.w_wsgs = []  # wskazania gosp
        self.w_phen = []  # roslinki i inne
        self.w_pnsw = []  # pnsw
        self.w_pngt = []  # gatunki w pnsw
        self.w_foch = []  # formy ochrony dla danego wydz
        self.w_opis = ''  # opis tekstowy z subarea
        self.w_pow = ''  # pow wydzieleia z bazy

        # slownik obrebow 0320001: [032, 0001, Nazwa, '(0320001) Nazwa']
        self.sl_obr = {}

    def przygotuj_obreby(self):
        o = self.baza.pobierz_obr()
        self.sl_obr['-------'] = ['---', '----', '', '-------']
        if o is False:
            return

        for oi in o:
            self.sl_obr[oi[0]+oi[1]] = [
                oi[0], oi[1], oi[2], '('+oi[0]+oi[1]+') '+oi[2]
            ]

    def pobierz_l_wydz(self, obr):
        # metoda uruchamiana tylko po zmianie aktywnego obrebu!
        lwydz = self.baza.pobierz_lwydz(obr)
        if lwydz is False:
            return

        self.sl_wydz_sort = {x[1]: x[2] for x in lwydz}
        self.sl_wydz = {x[1]: x[0] for x in lwydz}
        self.l_wydz_w = [x[1] for x in sorted(lwydz, key=lambda y: y[2])]
        self.sl_wydz_f = {x[1].replace(' ', '').replace('-', ''): x[1]
                          for x in lwydz}

    def przetworz_wydzielenie(self, int_num):
        # zbiorcza dla pobrania wszystkich danych dla wydzielenia
        it = self.baza.pobierz_ewid(int_num)
        if it is not False:
            self.w_ewid = [list(map(self.baza.isNone, x)) for x in it]

        it = self.baza.pobierz_wlasc(int_num)
        if it is not False:
            self.w_wlas = [list(map(self.baza.isNone, x)) for x in it]

        it = self.baza.pobierz_ciecia(int_num)
        if it is not False:
            self.w_wsgs = [list(map(self.baza.isNone, x[:6])) for x in it]

        it = self.baza.pobierz_phenom(int_num)
        if it is not False:
            self.w_phen = [list(map(self.baza.isNone, x)) for x in it]

        it = self.baza.pobierz_odstanu(int_num)
        if it is not False:
            self.w_opog = [[x for x in it][:-2]]
            self.w_opis = it[-2]
            p = it[-1].split('.')
            self.w_pow = '.'.join([p[0], p[1]+(4-len(p[1]))*'0'])

        it = self.baza.pobierz_fochr(int_num)
        if it is not False:
            self.w_foch = [x for x in it]

        it = self.baza.pobierz_adr_adm(int_num)
        if it is not False:
            self.w_adr = it

        # przygotuj tabelki dla pnsw
        self._w_przyg_pnsw(int_num)

        # przygotuj tabelki dla opisu warstw i dstanu w wydzieleniu
        self._w_przyg_ops(int_num)

    def _w_przyg_ops(self, int_num):  # noqa
        itw = self.baza.pobierz_owarstwy(int_num)
        itg = self.baza.pobierz_ogatunki(int_num)

        if itw is False or itg is False:
            return

        # tabela trzymająca kolejnosc warstw
        # ['DRZEW', 'PODR', 'PODSZ', ...]
        warstwy = []
        # slownik z opisem warstw oraz gatunkow w odpowieniej kolejnosci
        # {'DRZEW': {
        #      'ops': ['DRZEW', 'GRP', ...],
        #      'gat': [[opis1], [opis2], ...],
        #  }}
        sl = {}

        for it in itw:
            warstwy.append(it[1])
            zd = self.baza.isNone(it[3])
            if isinstance(it[3], float):
                zd = round(it[3], 2)

            sl[it[1]] = {'ops': [self.baza.isNone(it[1]),
                                 self.baza.isNone(it[4]),
                                 self.baza.isNone(it[5]),
                                 zd,
                                 self.baza.isNone(it[6]),
                                 self.baza.isNone(it[7]),
                                 self.baza.isNone(it[8]),
                                 ],
                         'gat': [],
                         }

        for it in itg:
            # jezeli w f_arod_storey nie ma takiejWarstwy dodaj pusty rekord
            if it[2] not in sl:
                sl[it[2]] = {'ops': ['', '', '', '', '', '', ''], 'gat': []}

            tab = list(it[4:9])+[it[10], it[13], it[9], it[11]]

            if isinstance(it[12], float):
                tab.append(round(it[12], 2))
            if isinstance(it[14], float):
                tab.append(round(it[14], 2))

            tab = list(map(self.baza.isNone, tab))
            sl[it[2]]['gat'].append(tab)

        # sprawdz czy we wszystkich warstwach sa gatunki, jezeli nie, dodaj
        # pusta warstwe do uzupelnienia widgetu
        for v in sl.values():
            if len(v['gat']) == 0:
                v['gat'].append(['', '', '', '', '', '', '', '', '', '', ''])

        self.w_opwa = []
        self.w_opgt = []
        for val in warstwy:
            v = sl[val]
            self.w_opwa.append(v['ops'])
            for i, g in enumerate(v['gat']):
                if i > 0:
                    self.w_opwa.append(['', '', '', '', '', '', ''])
                self.w_opgt.append(g)

    def _w_przyg_pnsw(self, int_num):
        # metoda dla przygowowania obu tabel pnsw do pokazania uz.
        it = self.baza.pobierz_pnsw(int_num)
        itg = self.baza.pobierz_pnsw_gat(int_num)
        # przygotuj slownik gat na pnsw, arod_sparea_order:[[gat, wiek],...]
        # kolejnosc zachowana z bazy
        slg = {}
        if itg is not False:
            for ig in itg:
                if ig[0] not in slg:
                    slg[ig[0]] = []
                slg[ig[0]].append([ig[1], ig[2]])

        # listy dla obu tablic pnsw
        self.w_pnsw = []
        self.w_pngt = []

        if it is False:
            return

        for ip in it:
            self.w_pnsw.append(list(ip))
            if ip[0] in slg:
                for i, tab in enumerate(slg[ip[0]]):
                    if i > 0:
                        self.w_pnsw.append(['', '', '', '', '', ''])
                    self.w_pngt.append([self.baza.isNone(tab[0]),
                                        self.baza.isNone(tab[1])])
            else:
                self.w_pngt.append(['', ''])

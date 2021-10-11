class EwidObs:
    # klasa do bsługi danych z bazy, przygotwuje dane do prezentacji
    # użtykownikowi
    def przygotuj_strukture(self):
        # slownik w postaci :
        # 'kod_woj' : {'ops': '(12) Małopolskie'
        #              'kod_pow': {'ops': '(12) Krakowski',
        #                          'kod_gm': {'ops: '(022) Skała',
        #                                     'kod_obr': '(0002) Maszyce'}}}

        self.sl_adr = {}

        # sl w-p-g-o-parcel_nr-pow: parcel_int_num (ograniczony do obrebu)
        self.sl_dzi = {}
        # posortowana lista działek dla obrebu
        self.l_dz = []
        # wyfiltrowana posortowana lista dzialek dla obrebu
        self.l_dz_w = []

        # tablice z opisami
        self.e_uzyt = []  # uzytki na dzialce
        self.e_wydz = []  # wydz na uzytku
        self.e_wlasn = []  # opis wlasnosci dzialki
        self.e_wlasc = []  # lista wlascicieli z wspolmalzonkami i udzialem
        self.ark = ''  # arkusz o ile wystepuje

    def przygotuj_adresy(self):
        adr = self.baza.pobierz_adr_adm_all()

        s = self.sl_adr
        for a in adr:
            # woj
            if a[0] not in s:
                s[a[0]] = {'ops': '('+a[0]+') '+a[1]}
            # pow
            if a[2] not in s[a[0]]:
                s[a[0]][a[2]] = {'ops': '('+a[2]+') '+a[3]}
            # gmi
            if a[4] not in s[a[0]][a[2]]:
                s[a[0]][a[2]][a[4]] = {'ops': '('+a[4]+') '+a[5]}

            # obr
            s[a[0]][a[2]][a[4]][a[6]] = '(' + a[6] + ') ' + a[7]

    def przygotuj_dzewid(self, w, p, g, o):
        # litery obrazują kody poszczególnych jenostek
        ldz = self.baza.pobierz_l_dzewid(w, p, g, o)

        self.sl_dzi = {'-'.join([w, p, g, o, l[1], self.zaok(str(l[2]))]): l[0]
                       for l in ldz}
        try:
            self.l_dz = sorted([x for x in self.sl_dzi.keys()],
                            key=lambda y: float(
                                '.'.join(y.split('-')[4].split('/')))
                            # key=lambda y: self.__sortowanie(y.split('-')[4])
                            )
        except Exception:
            self.l_dz = sorted([x for x in self.sl_dzi.keys()])

        self.l_dz_w = self.l_dz

    def przetworz_dzewid(self, key):
        # jako key podac klucz ze sl sl_dzi
        if key not in self.sl_dzi:
            return False

        pid = self.sl_dzi[key]
        it = self.baza.pobierz_dzewid(pid)
        if it is not False:
            it = list(map(self.baza.isNone, it[0]))
            self.ark = it[1]
            self.e_wlasn = [list(map(self.baza.isNone, it[2:]))]

        it = self.baza.pobierz_wlasc_dzewid(pid)
        if it is not False:
            self.e_wlasc = [list(map(self.baza.isNone, x)) for x in it]

        it = self.baza.pobierz_wydz_uz(pid)
        au = ''
        sq = ''
        lua = 0
        self.e_uzyt = []
        self.e_wydz = []
        if it is not False:
            for t in it:
                tok = list(map(self.baza.isNone, t))
                for j in [2, 5, 6]:
                    tok[j] = self.zaok(tok[j])
                if au == tok[0] and sq == tok[1] and lua == tok[2]:
                    self.e_uzyt.append(['', '', '', ''])
                else:
                    atemp = 'N' if tok[3] in ['0', '', False] else 'T'
                    self.e_uzyt.append(tok[:3]+[atemp])
                    au = tok[0]
                    sq = tok[1]
                    lua = tok[2]
                self.e_wydz.append(tok[4:])

    def zaok(self, it):
        if it == '':
            return it

        it = str(round(float(it), 4))
        a = it.split('.')
        if len(a) > 1:
            wyn = a[0] + '.' + a[1] + (4-len(a[1]))*'0'
            return wyn
        return a[0] + '.0000'

    def __sortowanie(self, nr):
        n = nr.split('/')
        if len(n) == 1:
            return nr
        return float(n[0] + '.' + ((10-len(n[1]))*'0') + n[1])


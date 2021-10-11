import os
import platform
import pyodbc
import sqlite3
from datetime import datetime
from shutil import copyfile
from PyQt5.QtCore import QVariant


class Baza:
    def __init__(self, b):
        # otworz podana baze danych
        self.con = False
        self.cur = False
        self.ok = False
        self.baza = b
        self.os = 'w'  # w-windows, l-linux

    def polacz(self):
        '''Metoda sprawdzajaca i laczaca sie z bazą'''

        # jezeli juz jestesmy polaczeni, nic ni rob
        if self.con and self.cur:
            return True

        if self.baza[-3:].upper() == 'MDB':
            MDB = self.baza
            DRV = '{Microsoft Access Driver (*.mdb, *.accdb)}'
            PWD = 'pw'
            # polacz
            self.con = pyodbc.connect('DRIVER={};DBQ={};PWD={}'.format(DRV,
                                                                       MDB,
                                                                       PWD))
            self.cur = self.con.cursor()
            self.ok = True
            self.os = 'w'
            return True

        elif self.baza[-6:] == 'sqlite':
            self.con = sqlite3.connect(self.baza)
            self.cur = self.con.cursor()
            self.ok = True
            self.os = 'l'
            return True

        return False

    def zamknij(self):
        try:
            self.cur.close()
            self.con.close()
            self.con = False
            self.cur = False
        except Exception:
            pass

    def wpisz(self, sql, debug=False):
        """Metoda dopisuje do bazy podanego sql"""
        if debug:
            self.cur.execute(sql)
            self.con.commit()
            return True
        else:
            try:
                self.cur.execute(sql)
                self.con.commit()
            except Exception:
                return False
            return True

    def wpisz_tab(self, tab):
        """Metoda dopisuje do bazy podaną tabele, uprzednio ja rozpakowujac"""
        try:
            self.cur.execute(*tab)
            self.con.commit()
        except Exception:
            return False
        return True

    def pobierz(self, sql, debug=False):
        """Metoda pobiera z bazy podanego sql"""
        if debug:
            return self.cur.execute(sql).fetchall()
            try:
                return self.cur.execute(sql).fetchall()
            except Exception:
                pass
        try:
            return self.cur.execute(sql).fetchall()
        except Exception:
            return False

    def utworz_kopie(self, wpis=''):
        """Metoda tworzy w katalogu z podana baza kopie bezpieczenstwa ze
        znacznikiem czasu oraz ew podanym wpisem"""
        katalog, plik = os.path.split(self.baza)
        self.czas = \
            datetime.now().isoformat().replace(':', '')[:-7]
        plikn = '.'.join(plik.split('.')[:-1]) + \
            '_' + wpis + '_' + self.czas

        if platform.system()[:3] == 'Win':
            plikn += '.mdb'
        else:
            plikn += '.sqlite'

        self.zamknij()
        copyfile(self.baza, os.path.join(katalog, plikn))
        self.polacz()

    def isNone(self, a):
        if a in [None, 'NULL', '', ]:
            return ''
        elif isinstance(a, QVariant):
            if a.isNull():
                return ''
            else:
                return str(a)
        else:
            return str(a)

    def pobierz_obr(self):
        sql = 'select MUNICIPALITY_CD, COMMUNITY_CD, COMMUNITY_NAME ' + \
            'from f_community;'
        return self.pobierz(sql)

    def pobierz_lwydz(self, a):
        """ Pobiera wydzielenia z adresu administracyjnego podanego w formie
        kodu gminy i obrebu: 0320001
        """
        adr = str(a)
        if len(adr) != 7 or not adr.isdigit():
            return False

        sql = 'select arodes_int_num, adress_forest, order_key ' +\
            'from f_arodes where arodes_typ_cd = \'WYDZIEL\' and '
        substr = 'mid' if self.os == 'w' else 'substr'
        sql += substr + '(adress_forest, 4, 7) = \''+adr+'\';'

        return self.pobierz(sql)

    def pobierz_arod_adress(self, adr):
        sql = 'select adress_forest from f_arodes where arodes_int_num =' +\
            str(adr) + ';'
        return self.pobierz(sql)

    def pobierz_liste_wydzielen(self):
        """Pobiera liste wszystkich wydzielen (WYDZ)"""
        sql = 'select adress_forest, arodes_int_num ' +\
            'from f_arodes where arodes_typ_cd=\'' +\
            'WYDZIEL\' order by order_key asc;'
        return self.pobierz(sql)

    def pobierz_arod_int_num(self, adr):
        sql = 'select arodes_int_num from f_arodes where adress_forest=\'' +\
            adr + '\';'
        return self.pobierz(sql)

    def pobierz_ciecia(self, int_num):
        if not isinstance(int_num, int) and int_num < 0:
            return False

        sql = 'select measure_cd, urgency, proc_area, cutting_area, ' + \
            'large_timber_perc, large_timber_value, ' +\
            'cue_rank_order ' + \
            'from f_arod_cue ' +\
            f'where arodes_int_num = {int_num}' + \
            ' order by cue_rank_order asc;'
        return self.pobierz(sql)

    def pobierz_phenom(self, int_num):
        if not isinstance(int_num, int) or int_num < 0:
            return False

        sql = 'select phen_rank_order, phenomena_cd, plant_cd, ' +\
            'nature_mon_fl, location_cd, phen_area, phen_num from ' +\
            'f_arod_phenomena where arodes_int_num = '+str(int_num) +\
            ' order by phen_rank_order asc;'
        return self.pobierz(sql)

    def pobierz_pnsw(self, int_num):
        if not isinstance(int_num, int) and int_num < 0:
            return False
        sql = 'select arod_sparea_order, special_area_cd, location_cd, ' +\
            'special_area, special_area_num from f_arod_spec_area where ' +\
            'arodes_int_num = '+str(int_num)+' order by arod_sparea_order asc;'
        return self.pobierz(sql)

    def pobierz_pnsw_gat(self, int_num):
        if not isinstance(int_num, int) and int_num < 0:
            return False

        sql = 'select arod_sparea_order, species_cd, sp_age ' + \
            'from f_species_sparea where ' +\
            'arodes_int_num = '+str(int_num)+' order by sp_rank_order asc;'
        return self.pobierz(sql)

    def pobierz_ewid(self, int_num):
        if not isinstance(int_num, int) and int_num < 0:
            return False

        sql = '''SELECT F_PARCEL.PARCEL_NR,
        F_PARCEL_LAND_USE.AREA_USE_CD,
        F_PARCEL_LAND_USE.SOIL_QUALITY_CD,
        F_PARCEL_LAND_USE.LAND_USE_AREA,
        F_AROD_LAND_USE.AROD_LAND_USE_AREA,
        F_PARCEL.PARCEL_AREA
        FROM
        (F_ARODES INNER JOIN F_SUBAREA ON
        F_ARODES.ARODES_INT_NUM = F_SUBAREA.ARODES_INT_NUM)
        INNER JOIN (F_PARCEL_LAND_USE INNER JOIN
        (F_PARCEL INNER JOIN F_AROD_LAND_USE ON
        F_PARCEL.PARCEL_INT_NUM = F_AROD_LAND_USE.PARCEL_INT_NUM)
        ON (F_PARCEL.PARCEL_INT_NUM = F_PARCEL_LAND_USE.PARCEL_INT_NUM)
        AND (F_PARCEL_LAND_USE.SHAPE_NR = F_AROD_LAND_USE.SHAPE_NR)
        AND (F_PARCEL_LAND_USE.PARCEL_INT_NUM =
             F_AROD_LAND_USE.PARCEL_INT_NUM))
        ON F_ARODES.ARODES_INT_NUM = F_AROD_LAND_USE.ARODES_INT_NUM
        where
        F_ARODES.ARODES_INT_NUM = '''
        sql += str(int_num) + ' order by f_parcel.parcel_nr asc;'

        return self.pobierz(sql)

    def pobierz_wlasc(self, int_num):
        if not isinstance(int_num, int) or int_num < 0:
            return False

        if self.os == 'l':
            sql = '''
        SELECT distinct
        t.pnr, t.wnr, t.nazwa,
        coalesce(t.wnr2 , ''),
        trim(coalesce(v_address.name_1, '') || ' '
        || coalesce(v_address.name_2, '')) AS wspml, t.udz

        FROM ((
        SELECT
        F_PARCEL.PARCEL_NR as pnr,
        F_PARCEL.PARCEL_INT_NUM AS pid,
        V_ADDRESS.ADDR_NR as wnr,
        coalesce(trim([NAME_1]), '') || ' ' || coalesce([NAME_2], '') AS nazwa,
        V_PARCEL_PARTICIPATION.second_addr_nr as wnr2,
        cast([part_numerator] as int) || '/' ||
        cast([part_denominator] as int) AS udz
        FROM
        ((F_PARCEL INNER JOIN V_PARCEL_PARTICIPATION ON
        F_PARCEL.PARCEL_INT_NUM = V_PARCEL_PARTICIPATION.parcel_int_num)
        INNER JOIN V_ADDRESS ON
        V_PARCEL_PARTICIPATION.addr_nr = V_ADDRESS.ADDR_NR)
        ) AS t LEFT JOIN V_ADDRESS ON t.wnr2 = V_ADDRESS.ADDR_NR )
        LEFT JOIN F_AROD_LAND_USE ON t.pid = f_arod_land_use.PARCEL_INT_NUM
        WHERE f_arod_land_use.ARODES_INT_NUM =
        '''
        else:
            sql = '''SELECT distinct
        t.pnr, t.wnr, t.nazwa,
        t.wnr2,
        trim(v_address.name_1 & ' ' & v_address.name_2) AS wspml, t.udz
        FROM
        ((SELECT
        F_PARCEL.PARCEL_NR as pnr,
        F_PARCEL.PARCEL_INT_NUM AS pid,
        V_ADDRESS.ADDR_NR as wnr,
        trim([NAME_1]) & ' ' & trim([NAME_2]) AS nazwa,
        V_PARCEL_PARTICIPATION.second_addr_nr as wnr2,
        [part_numerator] & '/' & [part_denominator] AS udz
        FROM
        ((F_PARCEL INNER JOIN V_PARCEL_PARTICIPATION ON
        F_PARCEL.PARCEL_INT_NUM = V_PARCEL_PARTICIPATION.parcel_int_num)
        INNER JOIN V_ADDRESS ON
        V_PARCEL_PARTICIPATION.addr_nr = V_ADDRESS.ADDR_NR)
        )  AS t LEFT JOIN V_ADDRESS ON t.wnr2 = V_ADDRESS.ADDR_NR)
        LEFT JOIN F_AROD_LAND_USE ON t.pid = f_arod_land_use.PARCEL_INT_NUM
        WHERE f_arod_land_use.ARODES_INT_NUM = '''

        sql += str(int_num) + ' order by t.pnr asc;'
        return self.pobierz(sql)

    def pobierz_wlasc_dzewid(self, pid):
        if not isinstance(pid, int) or pid < 0:
            return False

        if self.os == 'l':
            sql = '''
        SELECT distinct
        t.wnr, t.nazwa,
        coalesce(t.wnr2 , ''),
        coalesce(v_address.name_1, '') || ' '
        || coalesce(v_address.name_2, '') AS wspml, t.udz

        FROM (
        SELECT
        F_PARCEL.PARCEL_NR as pnr,
        F_PARCEL.PARCEL_INT_NUM AS pid,
        V_ADDRESS.ADDR_NR as wnr,
        coalesce(trim([NAME_1]), '') || ' ' || coalesce([NAME_2], '') AS nazwa,
        V_PARCEL_PARTICIPATION.second_addr_nr as wnr2,
        cast([part_numerator] as int) || '/' ||
        cast([part_denominator] as int) AS udz
        FROM
        ((F_PARCEL INNER JOIN V_PARCEL_PARTICIPATION ON
        F_PARCEL.PARCEL_INT_NUM = V_PARCEL_PARTICIPATION.parcel_int_num)
        INNER JOIN V_ADDRESS ON
        V_PARCEL_PARTICIPATION.addr_nr = V_ADDRESS.ADDR_NR)
        ) AS t LEFT JOIN V_ADDRESS ON t.wnr2 = V_ADDRESS.ADDR_NR
        WHERE t.pid = '''
        else:
            sql = '''SELECT distinct
        t.wnr, t.nazwa,
        t.wnr2, trim(v_address.name_1) & ' ' & trim(v_address.name_2) AS wspml,
        t.udz
        FROM
        ((SELECT
        F_PARCEL.PARCEL_NR as pnr,
        F_PARCEL.PARCEL_INT_NUM AS pid,
        V_ADDRESS.ADDR_NR as wnr,
        trim([NAME_1]) & ' ' & [NAME_2] AS nazwa,
        V_PARCEL_PARTICIPATION.second_addr_nr as wnr2,
        [part_numerator] & '/' & [part_denominator] AS udz
        FROM
        ((F_PARCEL INNER JOIN V_PARCEL_PARTICIPATION ON
        F_PARCEL.PARCEL_INT_NUM = V_PARCEL_PARTICIPATION.parcel_int_num)
        INNER JOIN V_ADDRESS ON
        V_PARCEL_PARTICIPATION.addr_nr = V_ADDRESS.ADDR_NR)
        )  AS t LEFT JOIN V_ADDRESS ON t.wnr2 = V_ADDRESS.ADDR_NR)
        WHERE t.pid = '''

        sql += str(pid) + ' order by t.nazwa asc;'
        return self.pobierz(sql)

    def pobierz_owarstwy(self, int_num):
        if not isinstance(int_num, int) and int_num < 0:
            return False

        sql = 'select * from f_arod_storey where arodes_int_num = '
        sql += str(int_num) + ' order by storey_rank_order asc;'
        return self.pobierz(sql)

    def pobierz_ogatunki(self, int_num):
        if not isinstance(int_num, int) and int_num < 0:
            return False

        sql = 'select * from f_storey_species where arodes_int_num = '
        sql += str(int_num) + ';'
        return self.pobierz(sql)

    def pobierz_odstanu(self, int_num):
        if not isinstance(int_num, int) and int_num < 0:
            return False

        tab = []
        # f_subarea
        sql = 'select area_type_cd, stand_struct_cd, site_type_cd, ' +\
            'veg_cover_cd, dead_wood, subarea_info, cause_cd, ' +\
            'damage_degree_cd, sub_area ' +\
            'from f_subarea where arodes_int_num = '
        sql += str(int_num) + ';'
        subar = self.pobierz(sql)

        # f_arod_stand_pec
        sql = 'select forest_pec_cd from f_arod_stand_pec where ' +\
            'arodes_int_num = '+str(int_num)+' order by pec_rank_order asc;'
        pec = self.pobierz(sql)

        pect = ''
        if len(pec) > 0:
            pect = ', '.join([str(x[0]) for x in pec])

        # f_arod_stand_pec
        sql = 'select species_cd from f_arod_goal where ' +\
            'arodes_int_num = '+str(int_num)+' order by goal_rank_order asc;'
        goal = self.pobierz(sql)

        goalt = ''
        if len(goal) > 0:
            goalt = ' '.join([str(x[0]) for x in goal])

        tab = [subar[0][0], pect, ] + list(subar[0][1:3]) + [goalt]
        # dead wood
        itt = subar[0][4] if isinstance(subar[0][4], float) else 0

        tab += [subar[0][3], int(itt)] + \
            list(map(self.isNone, subar[0][6:8])) + \
            [subar[0][5],  # opis
             round(subar[0][8], 4)  # powierzchnia
             ]
        tab = list(map(self.isNone, tab))
        # kolejnosc w tablicy:
        # 0 area_type
        # 1 cecha d-stanu
        # 2 bud pion
        # 3 tsl
        # 4 td
        # 5 typ pokrywy
        # 6 drewno martwe
        # 7 uszkodzenia
        # 8 stopien uszk
        # 9 opis tekstowy
        # 10 pow wydz

        return tab

    def pobierz_lic(self):
        """Pobiera dano o bazie do zalogowania w systemie"""
        sql = '''
            SELECT
                taxation_year,
                dbvalidityyearfrom,
                dbvalidityyearto
            from
                f_parameter
            ;
            '''
        return self.pobierz(sql)

    def pobierz_fochr(self, int_num):
        if not isinstance(int_num, int) and int_num < 0:
            return False

        sql = '''
            SELECT
            f_land_protect.LAND_PROTECT_NAME
            FROM
            F_set LEFT JOIN F_LAND_PROTECT ON
            f_set.MY_INT_NUM = f_land_protect.INT_NUM
            WHERE arodes_int_num =
            '''
        sql += str(int_num) + ';'
        return self.pobierz(sql)

    def pobierz_adr_adm_all(self):
        sql = '''
        SELECT
        F_COMMUNITY.COUNTY_CD,
        F_COUNTY.COUNTY_NAME,
        F_COMMUNITY.DISTRICT_CD,
        F_DISTRICT.DISTRICT_NAME,
        F_COMMUNITY.MUNICIPALITY_CD,
        F_MUNICIPALITY.MUNICIPALITY_NAME,
        F_COMMUNITY.COMMUNITY_CD,
        F_COMMUNITY.COMMUNITY_NAME
        FROM
        (F_COUNTY INNER JOIN
        (F_DISTRICT INNER JOIN F_MUNICIPALITY ON
        (F_DISTRICT.COUNTY_CD=F_MUNICIPALITY.COUNTY_CD)
        AND
        (F_DISTRICT.DISTRICT_CD=F_MUNICIPALITY.DISTRICT_CD)
        )
        ON F_COUNTY.COUNTY_CD=F_DISTRICT.COUNTY_CD)

        INNER JOIN F_COMMUNITY ON
         (F_MUNICIPALITY.COUNTY_CD=F_COMMUNITY.COUNTY_CD)
         AND
         (F_MUNICIPALITY.DISTRICT_CD=F_COMMUNITY.DISTRICT_CD)
         AND
         (F_MUNICIPALITY.MUNICIPALITY_CD=F_COMMUNITY.MUNICIPALITY_CD)
        GROUP BY
            F_COMMUNITY.COUNTY_CD,
            F_COUNTY.COUNTY_NAME,
            F_COMMUNITY.DISTRICT_CD,
            F_DISTRICT.DISTRICT_NAME,
            F_COMMUNITY.MUNICIPALITY_CD,
            F_MUNICIPALITY.MUNICIPALITY_NAME,
            F_COMMUNITY.COMMUNITY_CD,
            F_COMMUNITY.COMMUNITY_NAME
        ORDER BY F_COMMUNITY.COMMUNITY_CD;
        '''

        return self.pobierz(sql)

    def pobierz_adr_adm(self, int_num):
        if not isinstance(int_num, int) and int_num < 0:
            return False

        t_adr = self.pobierz_adr_adm_all()
        sql = 'select adress_forest from f_arodes ' +\
            'where arodes_int_num = ' + str(int_num) + ';'
        adr = self.pobierz(sql)

        if adr is False or t_adr is False:
            return False

        adr = adr[0][0]
        tab = [['('+x[0]+') '+x[1],
                '('+x[2]+') '+x[3],
                '('+x[4]+') '+x[5],
                '('+x[6]+') '+x[7]]
               for x in t_adr
               if x[4] == adr[3:6] and x[6] == adr[6:10]]

        if len(tab[0]) != 4:
            tab = [['', '', '', '']]

        return tab[0]

    def pobierz_l_dzewid(self, w, p, g, o):
        sql = '''select parcel_int_num, parcel_nr, parcel_area from f_parcel
         where '''
        sql += ' COUNTY_CD = \'' + w
        sql += '\' and DISTRICT_CD = \'' + p
        sql += '\' and MUNICIPALITY_CD = \'' + g
        sql += '\' and COMMUNITY_CD = \'' + o
        sql += '\';'
        return self.pobierz(sql)

    def pobierz_pid(self, w, p, g, o, nr, a=''):
        """
        kolejnosc: woj, powiat, gmina, obr, nrdz, arkusz
        """
        sql = 'select parcel_int_num from f_parcel where ' +\
            'county_cd = \'' + w +\
            '\' and district_cd = \'' + p +\
            '\' and municipality_cd = \'' + g +\
            '\' and community_cd = \'' + o + '\''

        if a != '':
            sql += ' and reg_sheet_nr2 = \'' + a + '\''

        sql += ' and parcel_nr = \'' + nr + '\';'

        return self.pobierz(sql)

    def pobierz_dzewid(self, pid):
        sql = '''select
            parcel_area,
            reg_sheet_nr2,
            dist_court_reg_nr,
            dist_court_reg_dat,
            land_register_nr,
            ownership_cd,
            parcel_add_info,
            register_mon_nr,
            parcel_nr
        from f_parcel
        where '''
        sql += ' PARCEL_INT_NUM = ' + str(pid)
        sql += ';'
        return self.pobierz(sql)

    def pobierz_wydz_uz(self, pid):
        if self.os == 'l':
            sql = '''
        SELECT F_PARCEL_LAND_USE.AREA_USE_CD,
           F_PARCEL_LAND_USE.SOIL_QUALITY_CD,
           F_PARCEL_LAND_USE.LAND_USE_AREA,
           F_PARCEL_LAND_USE.AFFORESTATION,
           F_ARODES.ADRESS_FOREST,
           F_SUBAREA.SUB_AREA,
           F_AROD_LAND_USE.AROD_LAND_USE_AREA,
           F_SUBAREA.AREA_TYPE_CD
        FROM (F_PARCEL_LAND_USE
          left JOIN ((F_ARODES
                INNER JOIN F_AROD_LAND_USE ON
                F_ARODES.ARODES_INT_NUM = F_AROD_LAND_USE.ARODES_INT_NUM)
                INNER JOIN F_PARCEL ON
                F_AROD_LAND_USE.PARCEL_INT_NUM = F_PARCEL.PARCEL_INT_NUM)
                ON
                (F_PARCEL.PARCEL_INT_NUM = F_PARCEL_LAND_USE.PARCEL_INT_NUM)
          AND (F_PARCEL_LAND_USE.SHAPE_NR = F_AROD_LAND_USE.SHAPE_NR)
          AND (
          F_PARCEL_LAND_USE.PARCEL_INT_NUM = F_AROD_LAND_USE.PARCEL_INT_NUM))
        left JOIN
        F_SUBAREA ON F_ARODES.ARODES_INT_NUM = F_SUBAREA.ARODES_INT_NUM
        WHERE F_PARCEL_LAND_USE.PARCEL_INT_NUM =
            '''
            sql += str(pid) + ' order by f_parcel_land_use.shape_nr asc;'
            return self.pobierz(sql)
        else:
            sql = '''
            SELECT
                F_PARCEL_LAND_USE.AREA_USE_CD as au,
                F_PARCEL_LAND_USE.SOIL_QUALITY_CD as sq,
                F_PARCEL_LAND_USE.LAND_USE_AREA as area,
                F_PARCEL_LAND_USE.AFFORESTATION as aff,
                F_PARCEL_LAND_USE.SHAPE_NR as snr
                FROM F_PARCEL_LAND_USE
            WHERE f_parcel_land_use.parcel_int_num = '''
            sql += str(pid) + ' order by F_PARCEL_LAND_USE.SHAPE_NR asc;'
            uz = self.pobierz(sql)

            sql = '''
            SELECT
                F_ARODES.ADRESS_FOREST as adr,
                F_SUBAREA.SUB_AREA as wpow,
                F_AROD_LAND_USE.AROD_LAND_USE_AREA as apow,
                F_SUBAREA.AREA_TYPE_CD as atyp,
                F_AROD_LAND_USE.SHAPE_NR as snr
            FROM (
            F_ARODES INNER JOIN F_AROD_LAND_USE ON
            F_ARODES.ARODES_INT_NUM = F_AROD_LAND_USE.ARODES_INT_NUM)
            INNER JOIN F_SUBAREA ON
            F_ARODES.ARODES_INT_NUM = F_SUBAREA.ARODES_INT_NUM
            where f_arod_land_use.parcel_int_num = '''
            sql += str(pid) + ' order by F_ARODES.ADRESS_FOREST asc;'
            wy = self.pobierz(sql)
            swy = {}
            if wy is not False:
                if len(wy) > 0:
                    for w in wy:
                        if w[4] not in swy:
                            swy[w[4]] = []
                        swy[w[4]].append(w[:4])

            tab = []
            aff = ''
            for u in uz:
                wiersz = list(u[:3])
                aff = 'N' if u[3] in ['0', '', False] else 'T'
                wiersz.append(aff)
                if u[4] in swy:
                    for w in swy[u[4]]:
                        wiersz += list(w[:4])
                        tab.append(wiersz)
                        if len(swy[u[4]]) > 1:
                            wiersz = tab[-1][:4]
                else:
                    wiersz += ['', '', '', '']
                    tab.append(wiersz)
            return tab

    def pobierz_dzew_dla_aint(self, aint):
        """Pobierz nazwy dzialek dla wybranego arodes_int_num"""
        sql = 'select f_parcel.parcel_nr, ' +\
            ' f_arod_land_use.arod_land_use_area,' + \
            ' f_parcel.parcel_int_num ' +\
            'from f_parcel inner join f_arod_land_use ' +\
            'on f_parcel.parcel_int_num=f_arod_land_use.parcel_int_num ' +\
            ' where f_arod_land_use.arodes_int_num=' + str(aint) + \
            ' order by f_parcel.parcel_nr asc;'
        return self.pobierz(sql)

    def rozkoduj_adr_pid_do_rejestr(self, val):
        '''Rozkodywywuje adres adm i leśny na podstawie podanego klucza w
        postaci indeksów parcel_int_num, i arodes_int_num : aid|pid
        '''
        try:
            aint, pid = val.split('|')
            if not pid.isdigit() or not aint.isdigit():
                return False
        except Exception:
            return False

        sql = '''
        SELECT distinct
            F_PARCEL.MUNICIPALITY_CD,
            F_MUNICIPALITY.MUNICIPALITY_NAME,
            F_COMMUNITY.COMMUNITY_CD,
            F_COMMUNITY.COMMUNITY_NAME,
            F_ARODES.ADRESS_FOREST,
            F_PARCEL.PARCEL_NR
        FROM
            F_MUNICIPALITY INNER JOIN (F_COMMUNITY INNER JOIN
            ((F_ARODES INNER JOIN F_AROD_LAND_USE ON
            F_ARODES.ARODES_INT_NUM = F_AROD_LAND_USE.ARODES_INT_NUM)
            INNER JOIN F_PARCEL ON
            F_AROD_LAND_USE.PARCEL_INT_NUM = F_PARCEL.PARCEL_INT_NUM) ON
            (F_COMMUNITY.COMMUNITY_CD = F_PARCEL.COMMUNITY_CD) AND
            (F_COMMUNITY.MUNICIPALITY_CD = F_PARCEL.MUNICIPALITY_CD) AND
            (F_COMMUNITY.DISTRICT_CD = F_PARCEL.DISTRICT_CD) AND
            (F_COMMUNITY.COUNTY_CD = F_PARCEL.COUNTY_CD)) ON
            (F_MUNICIPALITY.MUNICIPALITY_CD = F_COMMUNITY.MUNICIPALITY_CD)
            AND (F_MUNICIPALITY.DISTRICT_CD = F_COMMUNITY.DISTRICT_CD) AND
            (F_MUNICIPALITY.COUNTY_CD = F_COMMUNITY.COUNTY_CD) where
        '''
        sql += ' f_parcel.parcel_int_num=' + str(pid) + \
            ' and f_arod_land_use.arodes_int_num=' + str(aint) + ';'
        return self.pobierz(sql)

    def pobierz_adr_lic(self):
        """Pobiera kod adresu do zalogowania w licencji"""
        sql = '''
            SELECT distinct
                F_COUNTY.COUNTY_CD,
                F_COMMUNITY.DISTRICT_CD
            FROM
                F_COUNTY INNER JOIN
                ((F_DISTRICT INNER JOIN F_MUNICIPALITY
                ON (F_DISTRICT.DISTRICT_CD = F_MUNICIPALITY.DISTRICT_CD)
                AND (F_DISTRICT.COUNTY_CD = F_MUNICIPALITY.COUNTY_CD))
                INNER JOIN F_COMMUNITY ON
                (F_MUNICIPALITY.MUNICIPALITY_CD = F_COMMUNITY.MUNICIPALITY_CD)
                AND (F_MUNICIPALITY.DISTRICT_CD = F_COMMUNITY.DISTRICT_CD)
                AND
                (F_MUNICIPALITY.COUNTY_CD = F_COMMUNITY.COUNTY_CD))
                ON F_COUNTY.COUNTY_CD = F_DISTRICT.COUNTY_CD
                ;
        '''
        return self.pobierz(sql)

    def pobierz_naglowek(self):
        """Metoda pobiera dane naglowkowe, nazwy i kody administracyjne, dla
        wpisanych obrebow w bazie"""

        sql = """
            SELECT
                F_COUNTY.COUNTY_NAME,
                F_DISTRICT.DISTRICT_NAME,
                F_MUNICIPALITY.MUNICIPALITY_NAME,
                F_COMMUNITY.COMMUNITY_NAME,
                F_COMMUNITY.MUNICIPALITY_CD,
                F_COMMUNITY.COMMUNITY_CD
            FROM
                F_COUNTY INNER JOIN
                ((F_DISTRICT INNER JOIN F_MUNICIPALITY
                ON (F_DISTRICT.DISTRICT_CD = F_MUNICIPALITY.DISTRICT_CD)
                AND (F_DISTRICT.COUNTY_CD = F_MUNICIPALITY.COUNTY_CD))
                INNER JOIN F_COMMUNITY ON
                (F_MUNICIPALITY.MUNICIPALITY_CD = F_COMMUNITY.MUNICIPALITY_CD)
                AND (F_MUNICIPALITY.DISTRICT_CD = F_COMMUNITY.DISTRICT_CD)
                AND
                (F_MUNICIPALITY.COUNTY_CD = F_COMMUNITY.COUNTY_CD))
                ON F_COUNTY.COUNTY_CD = F_DISTRICT.COUNTY_CD
                ;
            """
        return self.cur.execute(sql).fetchall()

    def pobierz_pozyskanie(self, pid, aint):  # noqa
        '''Zwraca slownik dla podanego parcel_int_numi arodes_int_num w postaci
        sl = {
        'pow_wydz': powierzchnia_wydzielenia,
        'pow_wydz_dz': pow_wydz_na_dzew,
        'pozysk_wydz': 222,  # sumaryczne pozyskanie w wydzieleniu
        'pozysk_dz': 10,  # sumaryczne pozyskanie na dz (np: PRZES + IIB)
        'zab': [['IIB', 23], ['PRZES', 10], ]  przeliczone dla dzialki,
        'zab_id': {'IIB': 1, 'PRZES': 2, ...}
        }
        '''
        sl = {
            'aint': aint,
            'pid': pid,
            'pow_wydz': 0.00,
            'pow_wydz_dz': 0.00,
            'pozysk_wydz': 0,
            'pozysk_dz': 0,
            'zab': [],
            'zab_id': {},
            'gat': [],
            'gat_gl': ''
        }

        def pobierz(sql):
            wyn = self.pobierz(sql)
            try:
                if not wyn[0][0] is None:
                    return wyn[0][0]
                else:
                    return 0.0
            except Exception:
                return 0.0

        if not str(aint).isdigit() or not str(pid).isdigit():
            return

        def sortuj(val):
            v = self.isNone(val)
            if v == '':
                return 20
            elif v.isdigit():
                return 10 - int(v)
            elif v == 'MJS':
                return 11
            elif v == 'PJD':
                return 12

        sql = 'select sub_area, area_type_cd from f_subarea where ' +\
            'arodes_int_num='+str(aint)+';'
        sl['pow_wydz'] = self.pobierz(sql)[0][0]
        sl['typ_pow'] = self.isNone(self.pobierz(sql)[0][1])

        sql = 'select sum(arod_land_use_area) from f_arod_land_use where ' +\
            'parcel_int_num='+str(pid)+' and arodes_int_num='+str(aint)+';'
        sl['pow_wydz_dz'] = pobierz(sql)

        sql = 'select sum(large_timber_value) from f_arod_cue where ' +\
            'arodes_int_num='+str(aint)+';'
        sl['pozysk_wydz'] = pobierz(sql)

        try:
            sl['pozysk_wydz_dz'] = round(
                sl['pozysk_wydz']*sl['pow_wydz_dz']/sl['pow_wydz'], 2
            )
        except Exception:
            sl['pozysk_wydz_dz'] = '<<brak danych>>'

        # pobierz zabiegi i pozyskanie
        sql = 'select measure_cd, large_timber_value, cue_rank_order ' + \
            'from f_arod_cue where arodes_int_num='+str(aint) + \
            ' order by cue_rank_order asc;'
        val = self.pobierz(sql)
        try:
            zab = [[x[0], x[1] if x[1] not in [None, ''] else 0] for x in val]
            zab_id = {x[2]: x[0] for x in val}
        except Exception:
            zab = []
            zab_id = {}
        sl['zab'] = zab
        sl['zab_id'] = zab_id

        sql = 'select storey_cd, part_cd, species_cd, species_age, volume ' +\
            'from f_storey_species where arodes_int_num = '+str(aint) +\
            ' order by volume desc, species_age desc;'
        val = self.pobierz(sql)
        try:
            val.sort(key=lambda x: sortuj(x[1]))
            gat = [
                ''.join([
                    x[0],
                    ' - ',
                    x[1],
                    x[2][0]+x[2][1:].lower(),
                    x[3],
                    '   '+x[4]+'m3' if x[4] != '' else '',
                ])
                for x in [list(map(self.isNone, y)) for y in val[:5]]]
            if len(val) > 0:
                if len(val[0]) > 1:
                    sl['gat_gl'] = self.isNone(val[0][2])
        except Exception:
            gat = []
        sl['gat'] = gat

        return sl

    def pobierz_do_rejestru_zab(self, aintnums):
        if self.os == 'w':
            sql = '''SELECT
                F_ARODES.ARODES_INT_NUM,
                first(F_ARODES.ADRESS_FOREST),
                first(F_SUBAREA.SUB_AREA),
                first(F_SUBAREA.AREA_TYPE_CD),
                sum(F_AROD_CUE.LARGE_TIMBER_VALUE)
                '''
        else:
            sql = '''SELECT
                F_ARODES.ARODES_INT_NUM,
                F_ARODES.ADRESS_FOREST,
                F_SUBAREA.SUB_AREA,
                F_SUBAREA.AREA_TYPE_CD,
                sum(F_AROD_CUE.LARGE_TIMBER_VALUE)
                '''

        sql += '''
        FROM
            (F_ARODES INNER JOIN F_SUBAREA ON
            F_ARODES.ARODES_INT_NUM = F_SUBAREA.ARODES_INT_NUM)
            left JOIN F_AROD_CUE ON
            F_SUBAREA.ARODES_INT_NUM = F_AROD_CUE.ARODES_INT_NUM
            where F_ARODES.ARODES_INT_NUM in
            ''' + \
            ' (' + ','.join(aintnums) +\
            ') group by F_ARODES.ARODES_INT_NUM;'
        return self.pobierz(sql)
        self.e_wczytaj_pozyskanie()

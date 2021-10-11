import os
from qgis.core import QgsVectorLayer, QgsProject, Qgis, QgsField, \
    QgsLayerTreeGroup, QgsLayerTreeLayer
from PyQt5.QtCore import QVariant


def oblicz_pow_graf(iface):
    """ Funkcja sprawdza czy w aktywnej warstwie jest pole POW_GRAF
    jeżeli tak oblicza w nim pow graf. [ha]
    Jeżeli nie ma, dodaje nowe POW_GRAF i w nim oblicza pow.
    Powierzchnia obliczana jest na podstawie układu wspł z ramki.

    W przypadku stwierdzenia nipoprawnych poligonów dodawana jest tymczasowa
    warstwa z błędnymi poligonami do sprawdzenia
    """

    try:
        if not iface.activeLayer().isValid():
            iface.messageBar().pushMessage(
                'BŁĄD',
                'Warstwa niepoprawna!',
                Qgis.Critical
            )
            return False

    except Exception:
        iface.messageBar().pushMessage(
            'BŁĄD',
            'Warstwa niepoprawna!',
            Qgis.Critical
        )
        return False

    if iface.activeLayer().wkbType() not in [3, 6]:
        iface.messageBar().pushMessage(
            'BŁĄD',
            'Warstwa musi mieć geometrię powierzchniową!',
            Qgis.Critical
        )
        return False

    # ustal pole w którym będziemy oblczać pow graf
    fnm = iface.activeLayer().dataProvider().fieldNameMap()
    ind = -1
    nazwa_pola = 'POW_GRAF'
    if 'POW_GRAF' in [k.upper() for k in fnm.keys()]:
        ind = [v for k, v in fnm.items() if k.upper() == 'POW_GRAF'][0]
    else:
        pole = QgsField("POW_GRAF", QVariant.Double, "double", 10, 4)

        iface.activeLayer().startEditing()
        iface.activeLayer().dataProvider().addAttributes([pole])
        iface.activeLayer().updateFields()
        iface.activeLayer().commitChanges()

        fnm = iface.activeLayer().dataProvider().fieldNameMap()
        ind = fnm['POW_GRAF']

    bledy = 0
    tabb = []   # tab z featurami z bledna geometria

    for feat in iface.activeLayer().getFeatures():
        iface.activeLayer().dataProvider().changeAttributeValues({
            feat.id(): {ind: feat.geometry().area()/10000}
        })
        if not feat.geometry().isGeosValid():
            tabb.append(feat)
            bledy += 1

    if bledy == 0:
        wyps_gl = 'OK'
        wyps = \
            'Powierzchnia graficzna obliczona i zapisana w polu [' + \
            nazwa_pola + ']'
        typ = Qgis.Success
    else:
        wyps_gl = 'BŁĘDY'
        wyps = \
            'Powierzchnia graficzna obliczona i zapisana w polu [' + \
            nazwa_pola + \
            '] -->  Znaleziono poligony z błędną geometrią (GEOS): ' + \
            str(bledy)
        typ = Qgis.Warning

    if len(tabb) > 0:
        bledy = QgsVectorLayer("MultiPolygon?crs=epsg:2180&index=yes",
                               "Poligony_z_bledna_geom",
                               "memory"
                               )

        bledy.startEditing()
        bledy.dataProvider().addAttributes(
            iface.activeLayer().dataProvider().fields().toList())
        bledy.updateFields()
        bledy.addFeatures(tabb)
        bledy.commitChanges()
        QgsProject.instance().addMapLayer(bledy)

    iface.messageBar().pushMessage(wyps_gl, wyps, typ)


def przelacz_wezly(iface):
    plug = os.path.dirname(__file__)
    root = QgsProject.instance().layerTreeRoot()

    # sprawdź czy juz nie ma węzełków, jeżeli są usuń
    for ro in root.children():
        if isinstance(ro, QgsLayerTreeGroup):
            if ro.name() == 'Węzełki':
                root.removeChildNode(ro)
                return

    # jeżeli nie ma, wyszukaj wszystkie warstwy, dla których obsługujemy węzły
    # dodaj symbolizację i dodaj do grupy
    war = []
    for lyr in iface.mapCanvas().layers():
        # obsługa wyjątku dla wszystkich wartw, które nie są wektorami
        try:
            if lyr.wkbType() in [2, 3, 5, 6]:
                pass
        except Exception:
            continue

        if lyr.wkbType() in [2, 3, 5, 6] and \
                '_węzełki' not in lyr.name():
            lyrw = QgsVectorLayer(
                lyr.source(),
                lyr.name() + '_węzełki',
                lyr.providerType()
            )
            war.append(lyrw)

    if len(war) > 0:
        gr = root.insertGroup(0, 'Węzełki')
        for w in war:
            lyrw = QgsProject.instance().addMapLayer(w, False)
            if lyrw.wkbType() in [2, 5]:
                lyrw.loadNamedStyle(os.path.join(
                    plug, '..', 'qml', 'vertices_lft.qml'))
            else:
                lyrw.loadNamedStyle(os.path.join(
                    plug, '..', 'qml', 'vertices_aft.qml'))

            gr.insertChildNode(0, QgsLayerTreeLayer(lyrw))

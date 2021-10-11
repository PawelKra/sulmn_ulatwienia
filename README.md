# SULMN Ułatwienia

Plugin do QGISa ułatwiający pracę ze standardem SULMN. Umożliwia łatyw podgląd opisów wydzieleń i działek ewidencyjnych bezpośrednio w programie, umożliwia łatwe liczenie powierzchni poligonów, sprawdzanie poprawności geometrycznej oraz wyświetlanie węzełków geometrii.


## Instalacja

Umieść ten katalog w miejscu gdzie w twoim systemie operacyjnym znajdują się pluginy QGISa
Np:
* /home/user/.local/share/QGIS/QGIS3/profiles/default/python/plugins/  (Linux)
* C:\Users\user\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins  (Windows)


## Funkcjonalność

![Alt text](/toolbar.png?raw_true)

Ikonki od lewej na toolbarze SULMN_ulatwienia:
* **Wskaż baze**  - wskaż bazę taksatora PU, obsługiwane formaty ( MDB, sqlite)
* **Pokaż Opisy TPU** - pokaż opisy (zwykłe przeglądanie opisów taksacyjnych)
* **Pokaż opis wskazanego wydzielenia** - Przy założeniu że w TOC znajduje się warstwa POW lub WYDZ_POL z odpowiednią strukturą, program odczyta adres leśny ze wskazanego poligonu i wyświetli okno opisu taksacyjnego z wybranym wydzieleniem
* **Pokaż opisy działek ewidencyjnych** - pokaż dane działek ewidencyjnych
* **Pokaż opis wskazanej dz ewid** - Przy założeniu że w TOC znajduje się warstwa DZ_EWID lub DZKAT z adekwatną strukturą, zostaną wyśtwietlone dane wskazanej działki.
* **Pokaż węzełki geometrii dla wszystkich warstw** - ułatwia identyfikację wezełków w geometrii
* **Oblicz pow graf dla poligonów we wskazanej warstwie** - do warstwy dodawana jest kolumn POW_GRAF a następnie obliczna jest pow graficzna w ha. Przy okazji program sprawdza wszystkie poligony czy są poprawne (GEOS) jeżeli nie dodaje nową warstwę tymczasową w której wskazuje które poligony wymagają uwagi użytkownika


## Przykładowe okna opisów

![Alt text](/opisy_TPU.png?raw_true)

![Alt text](/opisy_ewid.png?raw_true)

## Obsługiwane formaty bazy taksatora:
* MDB
* sqlite

# BitBroker – Indítási és használati útmutató

Interaktív gazdasági és kapacitásmenedzsment-szimuláció: 2D grafikus játékfejlesztés Pygame könyvtárral (Eszterházy Károly Katolikus Egyetem, Gazdaságinformatikus BSc szakdolgozati projekt).

---

## 1. Gyors indítás (Windows)

1. **Kicsomagolás:** Csomagolja ki a ZIP-állományt egy normál mappába (*Jobb klikk -> Összes kibontása*).
   > **Fontos:** Ne közvetlenül a tömörített ZIP-fájlból indítsa a programot, mert a virtuális környezet létrehozásához és a mentéshez írási jogosultság szükséges!
2. **Indítás:** Kattintson duplán a **`run.bat`** fájlra.
   * Ha a Windows SmartScreen (*„A Windows megvédte a számítógépét”*) ablak jelenik meg, válassza a **További információ** -> **Futtatás mindenképpen** lehetőséget.
   * **Első indításkor** a parancsfájl létrehoz egy helyi virtuális környezetet (`.venv`), és telepíti a `pygame-ce 2.5.8` csomagot. Ehhez internetkapcsolat szükséges.
   * Ha a gépen nincs telepítve Python 3.10 vagy újabb verzió, a script automatikusan letölti és telepíti a **Python 3.14.5** verziót az aktuális felhasználónak (rendszergazdai jogosultság nem szükséges).
   * **A további indítások** már internetkapcsolat nélkül is lefutnak.

### Kézi indítás (alternatív mód)
Ha a `run.bat` valamiért nem futtatható, a program parancssorból (a projekt gyökérkönyvtárában állva, telepített Python 3.10+ esetén) az alábbi parancsokkal indítható:

py -3 -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe src\main.py

* **Fejlesztői környezet:** Python 3.14.5, pygame-ce 2.5.8 (SDL 2.32.10), 1920x1080 felbontás.
* A forráskód elérhető a ```` linken is.

## 2. Irányítás és mentés

A játék minden funkciója vezérelhető **egérrel (bal klikk)**, a navigációt pedig gyorsbillentyűk segítik:

| Billentyű / Művelet | Funkció |
| :--- | :--- |
| **F1** | **Dashboard** (Fő műszerfal: árfolyamok, szerverpark, saját készlet) |
| **F2** | **Marketplace** (Piactér: adatcsomagok és szerverek vásárlása) |
| **F3** | **Financial** (Pénzügyek: KPI-mutatók, egyenlegdiagram, eredmény- és cash-flow kimutatás) |
| **ESC** | Szünet menü (*Pause*) megnyitása / bezárása, vagy mentés és visszalépés a főmenübe |
| **R** | Gyors újraindítás csőd (*Game Over*) képernyőn |

* **Mentés és kilépés:** A játékállapot a szünet menü (`ESC`) **SAVE & QUIT TO MENU** gombjával, vagy az ablak bezárásakor automatikusan elmentődik a projekt mappájában lévő `savegame.json` fájlba. A mentett játék a főmenü **CONTINUE** gombjával folytatható. Csőd esetén a mentési fájl automatikusan törlődik.

## 3. Játékmenet és használati útmutató (Hogyan játsszon?)

A játékban egy adatkereskedelmi vállalkozást irányít **$5,000 induló tőkével**, hitelfelvételi lehetőség nélkül. A cél a szerverkapacitás kiépítése, a titkosított adatcsomagok (*Jobs*) megvásárlása, dekriptálása és nyereséges értékesítése a likviditási csőd elkerülése mellett.

### Kezdő lépések
1. **Szerver vásárlása:** Indítás után lépjen a **Marketplace (`F2`)** fülre! A *Server Shop* táblázatban kattintson a **Basic Rack** ($1,500) sorára egy szerver megvásárlásához. *(Szerver nélkül nem tud munkát feldolgozni.)*
2. **Adatcsomag (Job) vásárlása:** Ugyanitt, a felső *Job Market* táblázatban látja a folyamatosan frissülő, lejárati idővel (*EXPIRES*) rendelkező ajánlatokat. Kezdésként vásároljon meg egy **Personal** vagy egy olcsóbb **Small Business** csomagot rákattintva a sorára!
   * A **COST** a csomag vételára, a **PROFIT** pedig a jelenlegi árfolyamon számított várható bruttó árrés.
3. **Munka hozzárendelése a szerverhez:** Lépjen vissza a **Dashboard (`F1`)** fülre!
   * A jobb oldali **OWNED JOBS** panelen kattintson a megvásárolt munkára (zöld keretet kap).
   * Ezután kattintson a középső **SERVERPARK** panelen a szabad (`IDLE`) szerverre. A szerver `WORKING` állapotba vált, és elkezdi a csomag dekriptálását (*PROG* sáv).
4. **Értékesítés:** Amikor a feldolgozás eléri a 100%-ot, a szerver felszabadul (`IDLE`), a munka pedig a jobb oldali listában **SELL $...** felirattal jelenik meg. Kattintson rá az eladáshoz! A csomagot mindig az adott kategória **aktuális piaci árán** értékesíti.

### Fontos mechanikák és tippek
* **Hőmérséklet és túlmelegedés (`OVERHEATED`):** Munkavégzés közben a szerverek melegszenek (*TEMP* sáv). Ha egy szerver eléri a maximális hőfokát, `OVERHEATED` állapotba kerül: a munkavégzés teljesen leáll, amíg vissza nem hűl 30 °C-ra, de **ezalatt is a teljes, magas működési költséget (OPEX) vonja le**!
* **Megszakítás (`UNLOAD` gomb):** Ha látja, hogy egy nagy munka alatt a szerver mindjárt túlmelegszik, a szerverkártyán lévő **UNLOAD** gombbal leveheti róla a feladatot. A munka eddigi előrehaladása megmarad, a szerver pedig `IDLE` állapotban **töredéknyi költség mellett** hűl vissza, vagy a munkát átrakhatja egy másik, hideg szerverre.
* **Árfolyam-időzítés:** A **Dashboard (`F1`)** bal oldalán lévő **BLACKMARKET** grafikonokon a szaggatott vonal jelöli a kategória egyensúlyi alapárát. A már dekriptált munkák nem járnak le: ha van elég tartaléka, érdemes megvárni az eladással, amíg az árfolyam az alapár fölé emelkedik.
* **Pénzügyek és Csőd (`Game Over`):** A szerverek másodpercenkénti üzemeltetési költséget (**OPEX**) vonnak le (üresjáratban csökkentett, munka és túlmelegedés alatt teljes rátával). A **Financial (`F3`)** fülön a **RUNWAY** mutató jelzi, hány másodpercig elegendő a pénze a jelenlegi költségszint mellett. Ha az egyenlege **0 dollár alá** csökken, a cég azonnal csődbe megy!

## 4. Automatizált tesztek futtatása

A szakdolgozat 4. fejezetében dokumentált egységtesztek és szimulációs mérések grafikus ablak nélkül (*headless* módban) közvetlenül futtathatók a projekt gyökérkönyvtárából:

.venv\Scripts\python.exe src\test_unit.py
.venv\Scripts\python.exe src\test_simulation.py
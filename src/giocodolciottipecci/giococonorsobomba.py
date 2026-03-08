import pygame          # libreria per creare videogiochi (grafica, suoni, input)
import random           # per generare numeri casuali (posizioni nemici, tempi di sparo, ecc.)
import sys              # per uscire dal programma con sys.exit()
import os               # per controllare se un file esiste sul disco
import json             # per leggere/scrivere la classifica in formato JSON
from pathlib import Path  # per costruire percorsi di file in modo compatibile con tutti i sistemi operativi

pygame.init()  # inizializza tutti i moduli di pygame (deve essere chiamato prima di tutto)

# ── Dimensioni della finestra di gioco ──
LARGHEZZA = 1500
ALTEZZA = 900
FPS = 60  # fotogrammi al secondo: quante volte al secondo si aggiorna lo schermo

# ── Colori definiti come tuple RGB (rosso, verde, blu) da 0 a 255 ──
BIANCO = (255, 255, 255)
NERO = (0, 0, 0)
ROSSO = (255, 0, 0)
VERDE = (0, 255, 0)
GRIGIO = (150, 150, 150)
GIALLO = (255, 255, 0)
ARANCIONE = (255, 165, 0)
BLU_SCURO = (10, 10, 40)
BLU_CHIARO = (80, 140, 255)
ORO = (255, 215, 0)

# ── Parametri di gioco (valori facilmente modificabili per bilanciamento) ──
VITA_FOCA = 400          # punti vita del giocatore
VITA_ORSO = 20           # punti vita di ogni orso (nemico normale)
VITA_ORCA = 100          # punti vita dell'orca (boss)
VITA_ORSO_SPECIALE = 30  # punti vita dell'orso speciale esplosivo (più resistente)
DANNO_NORMALE = 5        # danno inflitto dai proiettili normali
DANNO_MISSILE = 30       # danno inflitto dai missili della foca
DANNO_ORCA = 10          # danno inflitto dai proiettili dell'orca
DANNO_ESPLOSIONE = 50    # danno inflitto dall'esplosione dell'orso speciale
RAGGIO_ESPLOSIONE = 800  # raggio dell'area di esplosione in pixel
VELOCITA_PROIETTILE = 9  # pixel per frame dei proiettili normali
VELOCITA_MISSILE = 100    # pixel per frame dei missili
VELOCITA_FOCA = 5        # pixel per frame del movimento verticale della foca
VELOCITA_ORSO = 2        # pixel per frame degli orsi
VELOCITA_ORCA = 2        # pixel per frame dell'orca
TEMPO_SPAWN_ORSO = 3000  # millisecondi tra uno spawn di orsi e il successivo
ORSI_INIZIALI = 6        # quanti orsi compaiono all'inizio della partita
ORSI_PER_MISSILE = 7     # ogni quanti orsi uccisi si ottiene un missile bonus
ORSI_PER_BOSS = 9        # ogni quanti orsi uccisi appare l'orca boss
# Probabilità che uno spawn generi un orso speciale (1 su N)
PROBABILITA_ORSO_SPECIALE = 5

# ── Percorsi delle immagini usate nel gioco ──
# Path.cwd() restituisce la cartella in cui si trova il file .py in esecuzione
IMMAGINE_FOCA          = Path.cwd() / "foca2.png"
IMMAGINE_ORSO          = Path.cwd() / "orso21.png"
IMMAGINE_ORSO_SPECIALE = Path.cwd() / "orsobomba.png"  # <-- aggiungi questo file!
IMMAGINE_ORCA          = Path.cwd() / "orca2.png"
IMMAGINE_SFONDO        = Path.cwd() / "sfondo.png"

# Percorso del file JSON dove vengono salvati i punteggi
FILE_CLASSIFICA = Path.cwd() / "classifica.json"


# ──────────────────────────────────────────────
# GESTIONE CLASSIFICA
# ──────────────────────────────────────────────

def carica_classifica():
    """Legge il file JSON della classifica e restituisce la lista dei punteggi.
    Se il file non esiste o è corrotto, restituisce una lista vuota."""
    if FILE_CLASSIFICA.exists():  # controlla se il file esiste prima di aprirlo
        try:
            with open(FILE_CLASSIFICA, "r", encoding="utf-8") as f:
                return json.load(f)  # converte il JSON in una lista Python
        except Exception:
            pass  # se c'è un errore (file corrotto ecc.), ignora e continua
    return []  # classifica vuota come valore di default


def salva_classifica(classifica):
    """Scrive la lista della classifica nel file JSON sul disco."""
    try:
        with open(FILE_CLASSIFICA, "w", encoding="utf-8") as f:
            json.dump(classifica, f, ensure_ascii=False, indent=2)
            # ensure_ascii=False: permette caratteri speciali italiani (à, è, ecc.)
            # indent=2: formatta il JSON con indentazione per renderlo leggibile
    except Exception:
        pass  # se il salvataggio fallisce (es. permessi), ignora silenziosamente


def aggiungi_a_classifica(nome, punteggio, orsi_uccisi, orche_uccise):
    """Aggiunge un nuovo risultato alla classifica, la ordina e tiene solo i primi 10."""
    classifica = carica_classifica()
    classifica.append({        # aggiunge un dizionario con i dati del giocatore
        "nome": nome,
        "punteggio": punteggio,
        "orsi": orsi_uccisi,
        "orche": orche_uccise
    })
    # Ordina dal punteggio più alto al più basso usando una lambda come chiave
    classifica.sort(key=lambda x: x["punteggio"], reverse=True)
    classifica = classifica[:10]   # taglia la lista ai primi 10 elementi
    salva_classifica(classifica)
    return classifica


# ──────────────────────────────────────────────
# CARICAMENTO IMMAGINI
# ──────────────────────────────────────────────

def carica_immagine(percorso, larghezza, altezza, tipo):
    """Carica un'immagine da file e la ridimensiona.
    Se il file non esiste, disegna un personaggio di riserva con forme geometriche."""
    if os.path.exists(percorso):  # controlla se il file immagine è presente
        try:
            img = pygame.image.load(percorso)                        # carica l'immagine
            return pygame.transform.scale(img, (larghezza, altezza)) # ridimensiona
        except:
            pass  # se il caricamento fallisce, passa al disegno di riserva
    
    # ── Fallback: disegna il personaggio con primitive geometriche ──
    s = pygame.Surface((larghezza, altezza))  # crea una superficie vuota
    s.fill(BIANCO)                            # riempie di bianco come sfondo
    if tipo == "foca":
        pygame.draw.ellipse(s, GRIGIO, (10, 20, 80, 50))    # corpo della foca
        pygame.draw.circle(s, GRIGIO, (100, 40), 25)         # testa
        pygame.draw.circle(s, NERO, (110, 35), 4)            # occhio
    elif tipo == "orso":
        pygame.draw.ellipse(s, (180, 180, 180), (10, 20, 80, 50))  # corpo orso
        pygame.draw.circle(s, (200, 200, 200), (20, 35), 20)        # testa
        pygame.draw.circle(s, ROSSO, (12, 33), 4)                   # occhio
    elif tipo == "orso_speciale":
        # Fallback orso speciale: simile all'orso normale ma con colori diversi
        pygame.draw.ellipse(s, (255, 80, 0), (10, 20, 80, 50))   # corpo arancione
        pygame.draw.circle(s, (255, 120, 0), (20, 35), 20)        # testa arancione
        pygame.draw.circle(s, GIALLO, (12, 33), 4)                # occhio giallo
        # Disegna una piccola "bomba" sul corpo per indicare il pericolo
        pygame.draw.circle(s, NERO, (70, 45), 12)
        pygame.draw.line(s, GIALLO, (70, 33), (78, 25), 2)
    elif tipo == "orca":
        pygame.draw.ellipse(s, NERO, (0, 10, 130, 70))       # corpo orca
        pygame.draw.ellipse(s, BIANCO, (15, 30, 35, 25))     # macchia bianca tipica
        pygame.draw.circle(s, ROSSO, (25, 40), 5)             # occhio
        pygame.draw.polygon(s, NERO, [(130, 45), (150, 20), (150, 70)])  # pinna caudale
    return s


def carica_sfondo(percorso):
    """Carica l'immagine di sfondo e la ridimensiona alla risoluzione del gioco.
    Restituisce None se il file non esiste (verrà usato uno sfondo stellato procedurale)."""
    if os.path.exists(percorso):
        try:
            img = pygame.image.load(percorso)
            return pygame.transform.scale(img, (LARGHEZZA, ALTEZZA))
        except:
            pass
    return None  # None = sfondo non disponibile, il gioco userà quello generato


# ──────────────────────────────────────────────
# ENTITÀ DI GIOCO (rappresentate come dizionari)
# ──────────────────────────────────────────────

def nuovo_orso():
    """Crea un dizionario che rappresenta un nuovo orso nemico.
    Gli orsi appaiono fuori dallo schermo a destra e si muovono verso sinistra."""
    return {
        'x': LARGHEZZA + 10,                        # parte appena fuori dal bordo destro
        'y': random.randint(50, ALTEZZA - 180),     # altezza casuale
        'w': 150, 'h': 130,                         # dimensioni hitbox
        'vita': VITA_ORSO,                           # punti vita iniziali
        'vx': -VELOCITA_ORSO,                        # velocità orizzontale (negativa = va a sinistra)
        'vy': 0,                                     # velocità verticale (cambia casualmente)
        'timer_sparo': pygame.time.get_ticks() + random.randint(500, 2000),  # quando sparerà la prima volta
        'intervallo_sparo': random.randint(1500, 3000),  # millisecondi tra uno sparo e il successivo
        'timer_move': 0,                             # contatore per cambiare direzione verticale
        'speciale': False                            # flag: NON è un orso esplosivo
    }


def nuovo_orso_speciale():
    """Crea un dizionario per l'orso speciale esplosivo.
    È più resistente dell'orso normale e quando muore esplode danneggiando
    chiunque (foca e altri orsi) si trovi entro RAGGIO_ESPLOSIONE pixel."""
    return {
        'x': LARGHEZZA + 10,
        'y': random.randint(50, ALTEZZA - 180),
        'w': 150, 'h': 130,
        'vita': VITA_ORSO_SPECIALE,                  # più resistente degli orsi normali
        'vx': -VELOCITA_ORSO,
        'vy': 0,
        'timer_sparo': pygame.time.get_ticks() + random.randint(500, 2000),
        'intervallo_sparo': random.randint(1500, 3000),
        'timer_move': 0,
        'speciale': True                             # flag: È un orso esplosivo!
    }


def nuova_orca():
    """Crea un dizionario per il boss orca. Parte da destra e si ferma a circa 2/3 dello schermo."""
    return {
        'x': LARGHEZZA + 10,
        'y': ALTEZZA // 2 - 85,       # posizione verticale centrale
        'w': 190, 'h': 170,           # più grande degli orsi
        'vita': VITA_ORCA,
        'vx': -VELOCITA_ORCA,
        'vy': 0,
        'timer_sparo': pygame.time.get_ticks() + 1000,
        'intervallo_sparo': 1000,     # spara più spesso degli orsi
        'timer_move': 0,
        'entrata': True               # flag: sta ancora entrando in scena?
    }


def crea_proiettile(x, y, direzione, tipo):
    """Crea un dizionario che rappresenta un proiettile.
    direzione: +1 = va a destra (proiettili foca), -1 = va a sinistra (proiettili nemici)."""
    if tipo == 'normale':
        return {'x': x, 'y': y, 'dir': direzione,
                'w': 10, 'h': 7,
                'colore': GIALLO if direzione > 0 else ROSSO,  # giallo per foca, rosso per nemici
                'tipo': 'normale', 'danno': DANNO_NORMALE}
    elif tipo == 'missile':
        return {'x': x, 'y': y, 'dir': 1,   # i missili vanno sempre a destra (dalla foca)
                'w': 45, 'h': 15,            # più grande dei proiettili normali
                'colore': ARANCIONE,
                'tipo': 'missile', 'danno': DANNO_MISSILE}
    elif tipo == 'orca':
        return {'x': x, 'y': y, 'dir': -1,  # i proiettili dell'orca vanno a sinistra
                'w': 10, 'h': 10,
                'colore': (255, 0, 255),     # magenta per distinguerli
                'tipo': 'orca', 'danno': DANNO_ORCA}


def aggiorna_proiettile(p):
    """Sposta il proiettile nella sua direzione e restituisce True se è ancora sullo schermo.
    Usata in una list comprehension per rimuovere automaticamente i proiettili usciti."""
    v = VELOCITA_MISSILE if p['tipo'] == 'missile' else VELOCITA_PROIETTILE
    p['x'] += v * p['dir']  # aggiorna posizione: positivo = destra, negativo = sinistra
    return -50 < p['x'] < LARGHEZZA + 50  # True se è ancora vicino allo schermo


def disegna_proiettile(schermo, p):
    """Disegna il proiettile come un rettangolo colorato.
    I missili hanno un cerchio giallo davanti per sembrare più realistici."""
    pygame.draw.rect(schermo, p['colore'], (p['x'], p['y'], p['w'], p['h']))
    if p['tipo'] == 'missile':
        pygame.draw.circle(schermo, GIALLO, (int(p['x']), int(p['y'] + 7)), 5)  # punta del missile


def rect_collide(ax, ay, aw, ah, bx, by, bw, bh):
    """Controlla la collisione tra due rettangoli con l'algoritmo AABB
    (Axis-Aligned Bounding Box). Restituisce True se i rettangoli si sovrappongono."""
    return ax < bx + bw and ax + aw > bx and ay < by + bh and ay + ah > by


# ──────────────────────────────────────────────
# ESPLOSIONE
# ──────────────────────────────────────────────

def applica_esplosione(cx, cy, foca, orsi, orca, esplosioni):
    """Gestisce l'effetto esplosione quando muore un orso speciale.

    Parametri:
        cx, cy   -- coordinate del centro dell'esplosione
        foca     -- dizionario della foca (può subire danno)
        orsi     -- lista degli orsi (quelli nel raggio vengono danneggiati/uccisi)
        orca     -- dizionario dell'orca boss oppure None
        esplosioni -- lista degli effetti visivi attivi (ci aggiunge la nuova esplosione)

    Restituisce una tupla (foca_morta, orsi_uccisi_da_esplosione, orca_uccisa):
        foca_morta               -- True se la foca è morta per l'esplosione
        orsi_uccisi_da_esplosione -- lista di orsi eliminati dall'esplosione
        orca_uccisa              -- True se l'orca boss è morta per l'esplosione
    """
    # Area di esplosione: rettangolo centrato in (cx, cy)
    # Larghezza = 10 pixel, Altezza = 10 pixel (come da specifiche)
    exp_w = 10
    exp_h = 10
    exp_x = cx - exp_w // 2
    exp_y = cy - exp_h // 2

    # Aggiunge effetto visivo nella lista (verrà disegnato e poi rimosso dopo qualche frame)
    esplosioni.append({
        'x': exp_x, 'y': exp_y,
        'w': exp_w, 'h': exp_h,
        'timer': 400   # durata in ms dell'effetto visivo (più lunga dell'area per visibilità)
    })

    foca_morta = False
    orsi_uccisi_da_esplosione = []
    orca_uccisa = False

    # ── Controlla se la foca è nell'area di esplosione ──
    foca_cx = foca['x'] + foca['w'] // 2
    foca_cy = foca['y'] + foca['h'] // 2
    if rect_collide(exp_x, exp_y, exp_w, exp_h,
                    foca['x'], foca['y'], foca['w'], foca['h']):
        foca['vita'] -= DANNO_ESPLOSIONE
        if foca['vita'] <= 0:
            foca['vita'] = 0
            foca_morta = True

    # ── Controlla se altri orsi sono nell'area di esplosione ──
    for orso in orsi:
        if rect_collide(exp_x, exp_y, exp_w, exp_h,
                        orso['x'], orso['y'], orso['w'], orso['h']):
            orso['vita'] -= DANNO_ESPLOSIONE
            if orso['vita'] <= 0:
                orsi_uccisi_da_esplosione.append(orso)

    # ── Controlla se l'orca boss è nell'area di esplosione ──
    if orca and rect_collide(exp_x, exp_y, exp_w, exp_h,
                              orca['x'], orca['y'], orca['w'], orca['h']):
        orca['vita'] -= DANNO_ESPLOSIONE
        if orca['vita'] <= 0:
            orca_uccisa = True

    return foca_morta, orsi_uccisi_da_esplosione, orca_uccisa


def disegna_esplosioni(schermo, esplosioni, dt):
    """Disegna le esplosioni attive e aggiorna i loro timer.
    Un'esplosione viene rimossa dalla lista quando il suo timer scende a 0.

    L'effetto visivo mostra cerchi concentrici che si espandono e sbiadiscono
    nel tempo per simulare un'onda d'urto."""
    da_rimuovere = []
    for exp in esplosioni:
        exp['timer'] -= dt
        if exp['timer'] <= 0:
            da_rimuovere.append(exp)
            continue

        # Centro dell'esplosione (centro del rettangolo area)
        cx = int(exp['x'] + exp['w'] // 2)
        cy = int(exp['y'] + exp['h'] // 2)

        # Calcola il progresso dell'animazione: da 1.0 (appena esploso) a 0.0 (svanito)
        progress = exp['timer'] / 400.0

        # Raggio visivo che si espande: parte piccolo e cresce nel tempo
        # (nota: visivamente più grande del rettangolo danno di 10x10 per essere visibile)
        raggio_visivo = int((1.0 - progress) * 120 + 10)

        # Alpha (trasparenza): inizia pieno e si dissolve
        alpha = int(progress * 230)

        # Disegna su una superficie trasparente per supportare la trasparenza
        surf_exp = pygame.Surface((raggio_visivo * 2 + 4, raggio_visivo * 2 + 4), pygame.SRCALPHA)

        # Cerchio esterno: arancione
        pygame.draw.circle(surf_exp, (*ARANCIONE, alpha),
                           (raggio_visivo + 2, raggio_visivo + 2), raggio_visivo)
        # Cerchio interno: giallo più luminoso
        pygame.draw.circle(surf_exp, (*GIALLO, min(255, alpha + 40)),
                           (raggio_visivo + 2, raggio_visivo + 2), max(1, raggio_visivo // 2))
        # Nucleo bianco al centro
        pygame.draw.circle(surf_exp, (255, 255, 255, min(255, alpha + 80)),
                           (raggio_visivo + 2, raggio_visivo + 2), max(1, raggio_visivo // 5))

        schermo.blit(surf_exp, (cx - raggio_visivo - 2, cy - raggio_visivo - 2))

        # Disegna il rettangolo dell'area di danno reale (10x10) come contorno rosso
        # visibile solo nei primi 200ms per debug/feedback al giocatore
        if exp['timer'] > 200:
            pygame.draw.rect(schermo, ROSSO,
                             (exp['x'], exp['y'], exp['w'], exp['h']), 2)

    for exp in da_rimuovere:
        esplosioni.remove(exp)


# ──────────────────────────────────────────────
# SCHERMATA: INSERIMENTO NOME
# ──────────────────────────────────────────────

def schermata_nome(schermo, clock, img_sfondo, stelle):
    """Mostra un campo di testo dove il giocatore inserisce il proprio nome.
    Gestisce il cursore lampeggiante e restituisce il nome inserito (o None se ESC)."""
    font_title = pygame.font.Font(None, 72)
    font_label = pygame.font.Font(None, 42)
    font_input = pygame.font.Font(None, 54)
    font_hint  = pygame.font.Font(None, 30)

    nome = ""             # stringa che accumula i caratteri digitati
    cursore_visible = True
    cursore_timer = 0     # contatore per far lampeggiare il cursore

    while True:
        dt = clock.tick(FPS)       # dt = milliseconds dall'ultimo frame
        cursore_timer += dt
        if cursore_timer >= 500:   # ogni 500ms cambia visibilità del cursore
            cursore_visible = not cursore_visible
            cursore_timer = 0

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_RETURN and nome.strip():  # INVIO con nome non vuoto
                    return nome.strip()
                elif ev.key == pygame.K_BACKSPACE:
                    nome = nome[:-1]           # cancella l'ultimo carattere
                elif ev.key == pygame.K_ESCAPE:
                    return None                # ESC = annulla, torna al menù
                elif len(nome) < 16 and ev.unicode.isprintable():  # max 16 caratteri
                    nome += ev.unicode         # aggiunge il carattere digitato

        # ── Disegno sfondo ──
        if img_sfondo:
            schermo.blit(img_sfondo, (0, 0))
        else:
            schermo.fill(BLU_SCURO)
            for sx, sy in stelle:
                pygame.draw.circle(schermo, BIANCO, (sx, sy), 1)

        # Overlay scuro semitrasparente sopra lo sfondo
        overlay = pygame.Surface((LARGHEZZA, ALTEZZA), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))   # RGBA: 160 = 62% opacità
        schermo.blit(overlay, (0, 0))

        titolo = font_title.render("INSERISCI IL TUO NOME", True, ORO)
        schermo.blit(titolo, (LARGHEZZA // 2 - titolo.get_width() // 2, 250))

        # Box di input: rettangolo bianco con bordo blu
        box_x, box_y, box_w, box_h = LARGHEZZA // 2 - 250, 370, 500, 60
        pygame.draw.rect(schermo, BIANCO, (box_x, box_y, box_w, box_h), border_radius=8)
        pygame.draw.rect(schermo, BLU_CHIARO, (box_x, box_y, box_w, box_h), 3, border_radius=8)

        # Testo del nome + cursore lampeggiante "|" o spazio invisibile
        testo_input = font_input.render(nome + ("|" if cursore_visible else " "), True, NERO)
        schermo.blit(testo_input, (box_x + 15, box_y + 8))

        hint = font_hint.render("INVIO per confermare  |  ESC per tornare al menù", True, GRIGIO)
        schermo.blit(hint, (LARGHEZZA // 2 - hint.get_width() // 2, 460))

        pygame.display.flip()  # aggiorna lo schermo (mostra il frame disegnato)


# ──────────────────────────────────────────────
# SCHERMATA: CLASSIFICA
# ──────────────────────────────────────────────

def schermata_classifica(schermo, clock, img_sfondo, stelle):
    """Mostra la classifica dei migliori 10 punteggi letti dal file JSON."""
    font_title  = pygame.font.Font(None, 72)
    font_header = pygame.font.Font(None, 36)
    font_row    = pygame.font.Font(None, 32)
    font_hint   = pygame.font.Font(None, 30)

    classifica = carica_classifica()  # legge i dati dal file

    while True:
        clock.tick(FPS)

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if ev.type == pygame.KEYDOWN:
                if ev.key in (pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_BACKSPACE):
                    return  # qualsiasi di questi tasti chiude la classifica

        # Sfondo
        if img_sfondo:
            schermo.blit(img_sfondo, (0, 0))
        else:
            schermo.fill(BLU_SCURO)
            for sx, sy in stelle:
                pygame.draw.circle(schermo, BLU_SCURO, (sx, sy), 1)

        overlay = pygame.Surface((LARGHEZZA, ALTEZZA), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 170))
        schermo.blit(overlay, (0, 0))

        titolo = font_title.render("🏆 CLASSIFICA", True, ORO)
        schermo.blit(titolo, (LARGHEZZA // 2 - titolo.get_width() // 2, 40))

        # Posizioni x delle colonne della tabella
        col_pos  = [120, 380, 650, 880, 1100]
        headers  = ["#", "NOME", "PUNTEGGIO", "ORSI", "ORCHE"]
        for i, h in enumerate(headers):
            surf = font_header.render(h, True, BLU_CHIARO)
            schermo.blit(surf, (col_pos[i], 140))

        # Linea separatrice sotto le intestazioni
        pygame.draw.line(schermo, GRIGIO, (100, 175), (LARGHEZZA - 100, 175), 2)

        if not classifica:
            msg = font_row.render("Nessun punteggio registrato ancora.", True, GRIGIO)
            schermo.blit(msg, (LARGHEZZA // 2 - msg.get_width() // 2, 250))
        else:
            for idx, entry in enumerate(classifica):
                y = 190 + idx * 55  # ogni riga è distanziata di 55 pixel verticalmente
                # Il primo in classifica è oro, le righe pari sono nere, le dispari grigio chiaro
                colore = ORO if idx == 0 else (NERO if idx % 2 == 0 else (200, 200, 200))

                # Sfondo alternato per migliorare la leggibilità delle righe
                if idx % 2 == 0:
                    pygame.draw.rect(schermo, (255, 255, 255, 15),
                                     (100, y - 5, LARGHEZZA - 200, 45))

                # Dati della riga: posizione, nome, punteggio, orsi, orche
                dati = [
                    str(idx + 1),
                    entry.get("nome", "???"),
                    str(entry.get("punteggio", 0)),
                    str(entry.get("orsi", 0)),
                    str(entry.get("orche", 0))
                ]
                for i, testo in enumerate(dati):
                    surf = font_row.render(testo, True, colore)
                    schermo.blit(surf, (col_pos[i], y))

        hint = font_hint.render("Premi ESC o INVIO per tornare al menù", True, BIANCO)
        schermo.blit(hint, (LARGHEZZA // 2 - hint.get_width() // 2, ALTEZZA - 50))

        pygame.display.flip()


# ──────────────────────────────────────────────
# SCHERMATA: MENÙ PRINCIPALE
# ──────────────────────────────────────────────

def schermata_menu(schermo, clock, img_sfondo, stelle):
    """Mostra il menù principale con navigazione da tastiera e mouse.
    Restituisce la stringa dell'opzione scelta: 'GIOCA', 'CLASSIFICA' o 'ESCI'."""
    font_title   = pygame.font.Font(None, 90)
    font_sub     = pygame.font.Font(None, 36)
    font_option  = pygame.font.Font(None, 56)

    opzioni      = ["GIOCA", "CLASSIFICA", "ESCI"]
    selezionata  = 0  # indice dell'opzione attualmente evidenziata

    while True:
        clock.tick(FPS)

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            if ev.type == pygame.KEYDOWN:
                if ev.key in (pygame.K_UP, pygame.K_w):
                    selezionata = (selezionata - 1) % len(opzioni)   # va su, con wrap
                elif ev.key in (pygame.K_DOWN, pygame.K_s):
                    selezionata = (selezionata + 1) % len(opzioni)   # va giù, con wrap
                elif ev.key == pygame.K_RETURN:
                    return opzioni[selezionata]  # conferma la scelta

            # Gestione click del mouse: controlla se il click è dentro un pulsante
            if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                mx, my = ev.pos
                for i in range(len(opzioni)):
                    oy = 420 + i * 90   # posizione y del pulsante i-esimo
                    if LARGHEZZA // 2 - 200 < mx < LARGHEZZA // 2 + 200 and oy - 5 < my < oy + 55:
                        return opzioni[i]

        # Hover col mouse: aggiorna la voce selezionata in base alla posizione del cursore
        mx, my = pygame.mouse.get_pos()
        for i in range(len(opzioni)):
            oy = 420 + i * 90
            if LARGHEZZA // 2 - 200 < mx < LARGHEZZA // 2 + 200 and oy - 5 < my < oy + 55:
                selezionata = i

        # Sfondo
        if img_sfondo:
            schermo.blit(img_sfondo, (0, 0))
        else:
            schermo.fill(BLU_SCURO)
            for sx, sy in stelle:
                pygame.draw.circle(schermo, BIANCO, (sx, sy), 1)

        overlay = pygame.Surface((LARGHEZZA, ALTEZZA), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 140))
        schermo.blit(overlay, (0, 0))

        titolo = font_title.render(" LA FOCA DRAGONE ", True, ORO)
        schermo.blit(titolo, (LARGHEZZA // 2 - titolo.get_width() // 2, 200))

        sottotitolo = font_sub.render("Il videogioco che ti farà capire che devi riprendere in mano la tua vita", True, BLU_CHIARO)
        schermo.blit(sottotitolo, (LARGHEZZA // 2 - sottotitolo.get_width() // 2, 310))

        # Disegna ogni pulsante del menù
        for i, opzione in enumerate(opzioni):
            y = 420 + i * 90
            if i == selezionata:
                # Pulsante attivo: sfondo blu chiaro, testo nero
                pygame.draw.rect(schermo, BLU_CHIARO,
                                 (LARGHEZZA // 2 - 200, y - 5, 400, 60), border_radius=10)
                colore_testo = NERO
            else:
                # Pulsante inattivo: sfondo grigio scuro con bordo
                pygame.draw.rect(schermo, (60, 60, 80),
                                 (LARGHEZZA // 2 - 200, y - 5, 400, 60), border_radius=10)
                pygame.draw.rect(schermo, GRIGIO,
                                 (LARGHEZZA // 2 - 200, y - 5, 400, 60), 2, border_radius=10)
                colore_testo = BIANCO

            surf = font_option.render(opzione, True, colore_testo)
            schermo.blit(surf, (LARGHEZZA // 2 - surf.get_width() // 2, y))

        hint = font_sub.render("↑↓ per navigare  |  INVIO per selezionare", True, GRIGIO)
        schermo.blit(hint, (LARGHEZZA // 2 - hint.get_width() // 2, ALTEZZA - 50))

        pygame.display.flip()


# ──────────────────────────────────────────────
# CICLO PRINCIPALE DI GIOCO
# ──────────────────────────────────────────────

def gioca(schermo, clock, img_foca, img_orso, img_orso_speciale, img_orca, img_sfondo, stelle, nome_giocatore):
    """Funzione principale che gestisce l'intera sessione di gioco:
    input del giocatore, movimento dei nemici, sparo, collisioni, HUD e game over."""
    font     = pygame.font.Font(None, 36)
    font_pic = pygame.font.Font(None, 24)
    font_big = pygame.font.Font(None, 72)

    gioco_attivo = True  # diventa False quando la foca muore (mostra game over)

    # Stato iniziale della foca (il giocatore)
    foca = {'x': 50, 'y': ALTEZZA // 2 - 65,
            'w': 150, 'h': 130,
            'vita': VITA_FOCA}

    # Genera gli orsi iniziali e prepara le liste di entità
    orsi = [nuovo_orso() for _ in range(ORSI_INIZIALI)]
    orca = None  # l'orca boss non è presente all'inizio

    proiettili_foca   = []  # proiettili sparati dalla foca verso i nemici
    proiettili_nemici = []  # proiettili sparati dai nemici verso la foca
    esplosioni        = []  # effetti visivi delle esplosioni attive

    punteggio         = 0
    orsi_uccisi       = 0
    orche_uccise      = 0
    missili           = 0   # missili disponibili (si guadagnano uccidendo orsi)
    ultimo_spawn_orso = pygame.time.get_ticks()  # timestamp dell'ultimo spawn di orsi
    ultimo_spawn_orca = -1  # soglia a cui è stata già generata l'orca (evita doppi spawn)

    # ── Game loop: gira continuamente finché la funzione non restituisce ──
    while True:
        dt = clock.tick(FPS)  # aspetta il prossimo frame e ottiene il tempo trascorso

        # ── Gestione eventi (tastiera, finestra) ──
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            if ev.type == pygame.KEYDOWN:
                # Tasti validi solo durante il game over
                if not gioco_attivo:
                    if ev.key == pygame.K_r:
                        return 'rigioca', nome_giocatore  # riavvia la partita
                    elif ev.key == pygame.K_ESCAPE:
                        return 'menu', None               # torna al menù principale

                # Tasti validi solo durante il gioco attivo
                if gioco_attivo:
                    if ev.key == pygame.K_SPACE:
                        # Spara un proiettile normale dalla punta destra della foca
                        proiettili_foca.append(
                            crea_proiettile(foca['x'] + foca['w'],
                                            foca['y'] + foca['h'] // 2 - 3,
                                            1, 'normale'))
                    elif ev.key == pygame.K_RETURN and missili > 0:
                        # Lancia un missile (solo se ce ne sono disponibili)
                        proiettili_foca.append(
                            crea_proiettile(foca['x'] + foca['w'],
                                            foca['y'] + foca['h'] // 2 - 7,
                                            1, 'missile'))
                        missili -= 1  # consuma un missile

        # ── Schermata di game over (se la foca è morta) ──
        if not gioco_attivo:
            if img_sfondo:
                schermo.blit(img_sfondo, (0, 0))
            else:
                schermo.fill(BLU_SCURO)
            overlay = pygame.Surface((LARGHEZZA, ALTEZZA), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            schermo.blit(overlay, (0, 0))

            schermo.blit(font_big.render("GAME OVER!", True, ROSSO),
                         (LARGHEZZA // 2 - 180, ALTEZZA // 2 - 130))
            schermo.blit(font.render(f"Giocatore: {nome_giocatore}", True, ORO),
                         (LARGHEZZA // 2 - 140, ALTEZZA // 2 - 60))
            schermo.blit(font.render(f"Punteggio: {punteggio}", True, BIANCO),
                         (LARGHEZZA // 2 - 120, ALTEZZA // 2 - 10))
            schermo.blit(font.render(f"Orsi eliminati: {orsi_uccisi}", True, BIANCO),
                         (LARGHEZZA // 2 - 130, ALTEZZA // 2 + 40))
            schermo.blit(font.render(f"Orche eliminate: {orche_uccise}", True, BIANCO),
                         (LARGHEZZA // 2 - 130, ALTEZZA // 2 + 90))
            schermo.blit(font_pic.render("R = Rigioca  |  ESC = Menù principale", True, GRIGIO),
                         (LARGHEZZA // 2 - 160, ALTEZZA // 2 + 150))
            pygame.display.flip()
            continue  # salta il resto del loop (aggiornamento fisica) e attende input

        # ── Movimento della foca con tasti freccia o WASD ──
        tasti = pygame.key.get_pressed()
        if tasti[pygame.K_w] or tasti[pygame.K_UP]:
            foca['y'] -= VELOCITA_FOCA
        if tasti[pygame.K_s] or tasti[pygame.K_DOWN]:
            foca['y'] += VELOCITA_FOCA
        # Limita la foca entro i bordi verticali dello schermo
        foca['y'] = max(0, min(ALTEZZA - foca['h'], foca['y']))

        ora = pygame.time.get_ticks()  # timestamp attuale in ms

        # ── Aggiornamento posizione e comportamento degli orsi ──
        orsi_da_rimuovere = []
        for orso in orsi:
            orso['x'] += orso['vx']       # movimento orizzontale costante verso sinistra

            # Cambia direzione verticale casualmente ogni tot millisecondi
            orso['timer_move'] -= dt
            if orso['timer_move'] <= 0:
                orso['vy'] = random.choice([-1, 0, 0, 1]) * VELOCITA_ORSO * 2  # su, fermo, giù
                orso['timer_move'] = random.randint(400, 1200)

            orso['y'] += orso['vy']
            orso['y'] = max(0, min(ALTEZZA - orso['h'], orso['y']))  # clamp verticale

            # Se l'orso è uscito dal bordo sinistro, viene marcato per la rimozione
            if orso['x'] + orso['w'] < 0:
                orsi_da_rimuovere.append(orso)
                continue

            # Sparo dell'orso se è passato abbastanza tempo dall'ultimo colpo
            if ora - orso['timer_sparo'] > orso['intervallo_sparo']:
                proiettili_nemici.append(
                    crea_proiettile(orso['x'], orso['y'] + orso['h'] // 2, -1, 'normale'))
                orso['timer_sparo'] = ora  # resetta il timer di sparo

        # Rimuove gli orsi usciti dallo schermo (non si fa dentro il loop per evitare errori)
        for o in orsi_da_rimuovere:
            orsi.remove(o)

        # ── Spawn periodico di nuovi orsi ──
        if ora - ultimo_spawn_orso > TEMPO_SPAWN_ORSO:
            # Con probabilità 1/PROBABILITA_ORSO_SPECIALE, uno dei due orsi è speciale
            if random.randint(1, PROBABILITA_ORSO_SPECIALE) == 1:
                orsi.append(nuovo_orso_speciale())
            else:
                orsi.append(nuovo_orso())
            orsi.append(nuovo_orso())  # il secondo è sempre normale
            ultimo_spawn_orso = ora

        # ── Aggiornamento dell'orca boss ──
        if orca:
            destinazione_x = int(LARGHEZZA * 0.65)  # si ferma al 65% della larghezza
            if orca.get('entrata') and orca['x'] > destinazione_x:
                orca['x'] += orca['vx']  # si avvicina verso la sua posizione di combattimento
            else:
                orca['entrata'] = False  # ha raggiunto la posizione: smette di avanzare

            # Movimento verticale casuale (identico agli orsi ma con parametri diversi)
            orca['timer_move'] -= dt
            if orca['timer_move'] <= 0:
                orca['vy'] = random.choice([-1, 0, 0, 1]) * VELOCITA_ORCA * 3
                orca['timer_move'] = random.randint(500, 1500)
            orca['y'] += orca['vy']
            orca['y'] = max(0, min(ALTEZZA - orca['h'], orca['y']))

            # Sparo dell'orca (più frequente degli orsi: ogni 1000ms)
            if ora - orca['timer_sparo'] > orca['intervallo_sparo']:
                proiettili_nemici.append(
                    crea_proiettile(orca['x'], orca['y'] + orca['h'] // 2, -1, 'orca'))
                orca['timer_sparo'] = ora

        # ── Aggiornamento proiettili: sposta e rimuove quelli usciti dallo schermo ──
        proiettili_foca   = [p for p in proiettili_foca   if aggiorna_proiettile(p)]
        proiettili_nemici = [p for p in proiettili_nemici if aggiorna_proiettile(p)]

        # ── Collisioni: proiettili della foca contro orsi ──
        for p in proiettili_foca[:]:   # copia della lista per poter rimuovere in sicurezza
            colpito = False
            for orso in orsi[:]:
                if rect_collide(p['x'], p['y'], p['w'], p['h'],
                                orso['x'], orso['y'], orso['w'], orso['h']):
                    colpito = True
                    orso['vita'] -= p['danno']

                    if orso['vita'] <= 0:
                        # ── Morte dell'orso: gestione normale e speciale ──
                        if orso['speciale']:
                            # L'orso speciale esplode! Calcola il centro del suo corpo
                            centro_x = orso['x'] + orso['w'] // 2
                            centro_y = orso['y'] + orso['h'] // 2

                            # Rimuove l'orso dalla lista PRIMA di applicare l'esplosione
                            # (altrimenti si danneggerebbe da solo nell'area explosion)
                            orsi.remove(orso)

                            # Applica danno ad area e aggiunge effetto visivo
                            foca_morta, vittime_exp, orca_uccisa_exp = applica_esplosione(
                                centro_x, centro_y, foca, orsi, orca, esplosioni)

                            # Aggiorna i contatori per gli orsi uccisi dall'esplosione
                            for vittima in vittime_exp:
                                if vittima in orsi:
                                    orsi.remove(vittima)
                                punteggio   += 10
                                orsi_uccisi += 1
                                if orsi_uccisi % ORSI_PER_MISSILE == 0:
                                    missili += 1

                            # Conta anche l'orso speciale stesso
                            punteggio   += 20  # bonus extra per aver ucciso l'orso speciale
                            orsi_uccisi += 1
                            if orsi_uccisi % ORSI_PER_MISSILE == 0:
                                missili += 1

                            # Controlla se l'orca boss è morta per l'esplosione
                            if orca_uccisa_exp and orca:
                                orca = None
                                punteggio    += 50
                                orche_uccise += 1

                            # Controlla se la foca è morta per l'esplosione
                            if foca_morta:
                                gioco_attivo = False
                                aggiungi_a_classifica(nome_giocatore, punteggio,
                                                      orsi_uccisi, orche_uccise)

                        else:
                            # Morte normale: rimuove l'orso e aggiorna punteggio
                            orsi.remove(orso)
                            punteggio   += 10
                            orsi_uccisi += 1

                            if orsi_uccisi % ORSI_PER_MISSILE == 0:
                                missili += 1

                        # Controlla se va spawnato il boss orca
                        soglia = (orsi_uccisi // ORSI_PER_BOSS) * ORSI_PER_BOSS
                        if (orsi_uccisi % ORSI_PER_BOSS == 0
                                and not orca
                                and soglia > ultimo_spawn_orca):
                            ultimo_spawn_orca = soglia
                            orca = nuova_orca()

                    break  # un proiettile colpisce solo un orso

            # Se il proiettile ha colpito qualcosa, viene rimosso
            if colpito and p in proiettili_foca:
                proiettili_foca.remove(p)

        # ── Collisioni: proiettili della foca contro orca ──
        if orca:
            for p in proiettili_foca[:]:
                if rect_collide(p['x'], p['y'], p['w'], p['h'],
                                orca['x'], orca['y'], orca['w'], orca['h']):
                    if p in proiettili_foca:
                        proiettili_foca.remove(p)
                    orca['vita'] -= p['danno']
                    if orca['vita'] <= 0:
                        orca = None         # rimuove il boss
                        punteggio    += 50  # bonus punteggio per aver sconfitto il boss
                        orche_uccise += 1
                        break

        # ── Collisioni: proiettili nemici contro la foca ──
        for p in proiettili_nemici[:]:
            if rect_collide(p['x'], p['y'], p['w'], p['h'],
                            foca['x'], foca['y'], foca['w'], foca['h']):
                proiettili_nemici.remove(p)
                foca['vita'] -= p['danno']
                if foca['vita'] <= 0:
                    foca['vita'] = 0       # non scende sotto zero per la barra vita
                    gioco_attivo = False   # attiva la schermata di game over
                    # Salva il punteggio nella classifica immediatamente
                    aggiungi_a_classifica(nome_giocatore, punteggio, orsi_uccisi, orche_uccise)

        # ══════════════════════
        # DISEGNO DEL FRAME
        # ══════════════════════

        if img_sfondo:
            schermo.blit(img_sfondo, (0, 0))
        else:
            schermo.fill(BLU_SCURO)
            for sx, sy in stelle:
                pygame.draw.circle(schermo, BIANCO, (sx, sy), 1)  # stelle procedurali

        # Disegna la foca
        schermo.blit(img_foca, (foca['x'], foca['y']))

        # Disegna ogni orso con la sua barra vita sopra
        for orso in orsi:
            # Usa l'immagine giusta in base al tipo di orso
            if orso['speciale']:
                schermo.blit(img_orso_speciale, (orso['x'], orso['y']))
                # Bordo arancione lampeggiante per segnalare il pericolo esplosione
                pygame.draw.rect(schermo, ARANCIONE,
                                 (orso['x'] - 2, orso['y'] - 2,
                                  orso['w'] + 4, orso['h'] + 4), 3)
            else:
                schermo.blit(img_orso, (orso['x'], orso['y']))

            # Barra vita: sfondo rosso + vita rimasta verde
            colore_barra = ARANCIONE if orso['speciale'] else VERDE
            vita_max = VITA_ORSO_SPECIALE if orso['speciale'] else VITA_ORSO
            pygame.draw.rect(schermo, ROSSO,  (orso['x'], orso['y'] - 12, 60, 6))
            pygame.draw.rect(schermo, colore_barra,
                             (orso['x'], orso['y'] - 12,
                              int(60 * max(0, orso['vita'] / vita_max)), 6))

            # Label "💣" sopra l'orso speciale per renderlo riconoscibile
            if orso['speciale']:
                font_warn = pygame.font.Font(None, 22)
                warn = font_warn.render("ALLAH AKBAR!", True, ARANCIONE)
                schermo.blit(warn, (orso['x'] + 35, orso['y'] - 28))

        # Disegna l'orca con barra vita e label "BOSS!"
        if orca:
            schermo.blit(img_orca, (orca['x'], orca['y']))
            pygame.draw.rect(schermo, ROSSO, (orca['x'], orca['y'] - 18, 120, 10))
            pygame.draw.rect(schermo, (255, 0, 255),
                             (orca['x'], orca['y'] - 18,
                              int(120 * max(0, orca['vita'] / VITA_ORCA)), 10))  # barra magenta
            schermo.blit(font.render("BOSS!", True, (255, 0, 255)),
                         (orca['x'] + 20, orca['y'] - 45))

        # Disegna tutti i proiettili
        for p in proiettili_foca:
            disegna_proiettile(schermo, p)
        for p in proiettili_nemici:
            disegna_proiettile(schermo, p)

        # Disegna le esplosioni attive (aggiorna anche i loro timer)
        disegna_esplosioni(schermo, esplosioni, dt)

        # ── HUD (Heads-Up Display): informazioni sovraimposte sullo schermo ──

        # Barra vita della foca: rettangolo rosso + rettangolo verde proporzionale alla vita
        bar_w = 600
        pygame.draw.rect(schermo, ROSSO, (10, 10, bar_w, 22))
        pygame.draw.rect(schermo, VERDE,
                         (10, 10, int(bar_w * max(0, foca['vita'] / VITA_FOCA)), 22))
        schermo.blit(font_pic.render(f"Vita: {max(0, foca['vita'])}", True, BIANCO), (620, 12))

        schermo.blit(font.render(f"Punteggio: {punteggio}", True, BIANCO), (10, 40))
        schermo.blit(font_pic.render(f"Orsi eliminati: {orsi_uccisi}  |  Orche: {orche_uccise}",
                                     True, BIANCO), (10, 78))

        # I missili disponibili appaiono arancione, altrimenti grigio quando sono 0
        col_m = ARANCIONE if missili > 0 else GRIGIO
        schermo.blit(font_pic.render(f"Missili: {missili}  (INVIO)", True, col_m), (10, 100))

        # Mostra quanti orsi mancano al prossimo missile
        prossimo = ORSI_PER_MISSILE - (orsi_uccisi % ORSI_PER_MISSILE)
        schermo.blit(font_pic.render(f"Prossimo missile tra: {prossimo} orsi", True, BIANCO),
                     (10, 122))

        # Nome giocatore in alto a destra
        schermo.blit(font_pic.render(f"Giocatore: {nome_giocatore}", True, ORO),
                     (LARGHEZZA - 280, 30))

        # Istruzioni comandi in alto a destra
        schermo.blit(font_pic.render("FRECCETE SU E GIU': Muovi  |  SPAZIO: Spara  |  INVIO: Missile",
                                     True, BIANCO), (LARGHEZZA - 480, 10))

        pygame.display.flip()  # mostra il frame completamente disegnato


# ──────────────────────────────────────────────
# ENTRY POINT DEL PROGRAMMA
# ──────────────────────────────────────────────

def main():
    """Funzione principale: inizializza pygame, carica le risorse e gestisce
    il flusso tra menù, classifica e partite."""
    schermo = pygame.display.set_mode((LARGHEZZA, ALTEZZA))
    pygame.display.set_caption("FOCA BAMBINA/O vs ORSI DIDDY con ORCA EPSTEIN")
    clock = pygame.time.Clock()

    # Carica tutte le immagini (con fallback procedurale se i file non ci sono)
    img_foca          = carica_immagine(IMMAGINE_FOCA,          150, 130, "foca")
    img_orso          = carica_immagine(IMMAGINE_ORSO,          150, 130, "orso")
    img_orso_speciale = carica_immagine(IMMAGINE_ORSO_SPECIALE, 150, 130, "orso_speciale")  # NUOVO
    img_orca          = carica_immagine(IMMAGINE_ORCA,          190, 170, "orca")
    img_sfondo        = carica_sfondo(IMMAGINE_SFONDO)   # None se il file non esiste

    # Genera le posizioni casuali delle stelle (sfondo procedurale di riserva)
    stelle = [(random.randint(0, LARGHEZZA), random.randint(0, ALTEZZA)) for _ in range(120)]

    nome_corrente = None  # nome del giocatore, ricordato tra una partita e l'altra

    # ── Loop principale: menù → gioca → menù → ... ──
    while True:
        scelta = schermata_menu(schermo, clock, img_sfondo, stelle)

        if scelta == "ESCI":
            pygame.quit()
            sys.exit()

        elif scelta == "CLASSIFICA":
            schermata_classifica(schermo, clock, img_sfondo, stelle)

        elif scelta == "GIOCA":
            # Chiede il nome al giocatore prima di iniziare
            nome = schermata_nome(schermo, clock, img_sfondo, stelle)
            if nome is None:
                continue  # ESC nella schermata nome → torna al menù senza giocare
            nome_corrente = nome

            # Loop interno per "Rigioca" senza tornare al menù principale
            while True:
                risultato, _ = gioca(schermo, clock, img_foca, img_orso, img_orso_speciale,
                                     img_orca, img_sfondo, stelle, nome_corrente)
                if risultato == 'rigioca':
                    # Chiede un nuovo nome per la nuova partita
                    nuovo_nome = schermata_nome(schermo, clock, img_sfondo, stelle)
                    if nuovo_nome:
                        nome_corrente = nuovo_nome
                    # Se ESC, rigioca con lo stesso nome senza cambiarlo
                else:
                    break  # risultato == 'menu': esce dal loop interno e torna al menù


# Esegue main() solo se questo file è avviato direttamente (non importato come modulo)
if __name__ == "__main__":
    main()
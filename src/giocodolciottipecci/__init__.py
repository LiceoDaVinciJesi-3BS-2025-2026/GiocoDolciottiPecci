import pygame
import random
import sys
import os
import json
from pathlib import Path

pygame.init()

LARGHEZZA = 1500
ALTEZZA = 900
FPS = 60

# colori
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

# impostazioni basi
VITA_FOCA = 400
VITA_ORSO = 20
VITA_ORCA = 100
DANNO_NORMALE = 5
DANNO_MISSILE = 30
DANNO_ORCA = 10
VELOCITA_PROIETTILE = 9
VELOCITA_MISSILE = 16
VELOCITA_FOCA = 5
VELOCITA_ORSO = 2
VELOCITA_ORCA = 2
TEMPO_SPAWN_ORSO = 3000
ORSI_INIZIALI = 6
ORSI_PER_MISSILE = 7
ORSI_PER_BOSS = 9

IMMAGINE_FOCA   = Path.cwd() / "foca2.png"
IMMAGINE_ORSO   = Path.cwd() / "orso21.png"
IMMAGINE_ORCA   = Path.cwd() / "orca2.png"
IMMAGINE_SFONDO = Path.cwd() / "sfondo.png"

FILE_CLASSIFICA = Path.cwd() / "classifica.json"


# ──────────────────────────────────────────────
# CLASSIFICA  (carica / salva su file JSON)
# ──────────────────────────────────────────────

def carica_classifica():
    if FILE_CLASSIFICA.exists():
        try:
            with open(FILE_CLASSIFICA, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return []


def salva_classifica(classifica):
    try:
        with open(FILE_CLASSIFICA, "w", encoding="utf-8") as f:
            json.dump(classifica, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


def aggiungi_a_classifica(nome, punteggio, orsi_uccisi, orche_uccise):
    classifica = carica_classifica()
    classifica.append({
        "nome": nome,
        "punteggio": punteggio,
        "orsi": orsi_uccisi,
        "orche": orche_uccise
    })
    # Ordina per punteggio decrescente, tieni i primi 10
    classifica.sort(key=lambda x: x["punteggio"], reverse=True)
    classifica = classifica[:10]
    salva_classifica(classifica)
    return classifica


# ──────────────────────────────────────────────
# CARICA IMMAGINI
# ──────────────────────────────────────────────

def carica_immagine(percorso, larghezza, altezza, tipo):
    if os.path.exists(percorso):
        try:
            img = pygame.image.load(percorso)
            return pygame.transform.scale(img, (larghezza, altezza))
        except:
            pass
    s = pygame.Surface((larghezza, altezza))
    s.fill(BIANCO)
    if tipo == "foca":
        pygame.draw.ellipse(s, GRIGIO, (10, 20, 80, 50))
        pygame.draw.circle(s, GRIGIO, (100, 40), 25)
        pygame.draw.circle(s, NERO, (110, 35), 4)
    elif tipo == "orso":
        pygame.draw.ellipse(s, (180, 180, 180), (10, 20, 80, 50))
        pygame.draw.circle(s, (200, 200, 200), (20, 35), 20)
        pygame.draw.circle(s, ROSSO, (12, 33), 4)
    elif tipo == "orca":
        pygame.draw.ellipse(s, NERO, (0, 10, 130, 70))
        pygame.draw.ellipse(s, BIANCO, (15, 30, 35, 25))
        pygame.draw.circle(s, ROSSO, (25, 40), 5)
        pygame.draw.polygon(s, NERO, [(130, 45), (150, 20), (150, 70)])
    return s


def carica_sfondo(percorso):
    if os.path.exists(percorso):
        try:
            img = pygame.image.load(percorso)
            return pygame.transform.scale(img, (LARGHEZZA, ALTEZZA))
        except:
            pass
    return None


# ──────────────────────────────────────────────
# ENTITÀ
# ──────────────────────────────────────────────

def nuovo_orso():
    return {
        'x': LARGHEZZA + 10,
        'y': random.randint(50, ALTEZZA - 180),
        'w': 150, 'h': 130,
        'vita': VITA_ORSO,
        'vx': -VELOCITA_ORSO,
        'vy': 0,
        'timer_sparo': pygame.time.get_ticks() + random.randint(500, 2000),
        'intervallo_sparo': random.randint(1500, 3000),
        'timer_move': 0
    }


def nuova_orca():
    return {
        'x': LARGHEZZA + 10,
        'y': ALTEZZA // 2 - 85,
        'w': 190, 'h': 170,
        'vita': VITA_ORCA,
        'vx': -VELOCITA_ORCA,
        'vy': 0,
        'timer_sparo': pygame.time.get_ticks() + 1000,
        'intervallo_sparo': 1000,
        'timer_move': 0,
        'entrata': True
    }


def crea_proiettile(x, y, direzione, tipo):
    if tipo == 'normale':
        return {'x': x, 'y': y, 'dir': direzione,
                'w': 10, 'h': 7,
                'colore': GIALLO if direzione > 0 else ROSSO,
                'tipo': 'normale', 'danno': DANNO_NORMALE}
    elif tipo == 'missile':
        return {'x': x, 'y': y, 'dir': 1,
                'w': 45, 'h': 15,
                'colore': ARANCIONE,
                'tipo': 'missile', 'danno': DANNO_MISSILE}
    elif tipo == 'orca':
        return {'x': x, 'y': y, 'dir': -1,
                'w': 10, 'h': 10,
                'colore': (255, 0, 255),
                'tipo': 'orca', 'danno': DANNO_ORCA}


def aggiorna_proiettile(p):
    v = VELOCITA_MISSILE if p['tipo'] == 'missile' else VELOCITA_PROIETTILE
    p['x'] += v * p['dir']
    return -50 < p['x'] < LARGHEZZA + 50


def disegna_proiettile(schermo, p):
    pygame.draw.rect(schermo, p['colore'], (p['x'], p['y'], p['w'], p['h']))
    if p['tipo'] == 'missile':
        pygame.draw.circle(schermo, GIALLO, (int(p['x']), int(p['y'] + 7)), 5)


def rect_collide(ax, ay, aw, ah, bx, by, bw, bh):
    return ax < bx + bw and ax + aw > bx and ay < by + bh and ay + ah > by


# ──────────────────────────────────────────────
# SCHERMATA: INSERIMENTO NOME
# ──────────────────────────────────────────────

def schermata_nome(schermo, clock, img_sfondo, stelle):
    font_title = pygame.font.Font(None, 72)
    font_label = pygame.font.Font(None, 42)
    font_input = pygame.font.Font(None, 54)
    font_hint  = pygame.font.Font(None, 30)

    nome = ""
    cursore_visible = True
    cursore_timer = 0

    while True:
        dt = clock.tick(FPS)
        cursore_timer += dt
        if cursore_timer >= 500:
            cursore_visible = not cursore_visible
            cursore_timer = 0

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_RETURN and nome.strip():
                    return nome.strip()
                elif ev.key == pygame.K_BACKSPACE:
                    nome = nome[:-1]
                elif ev.key == pygame.K_ESCAPE:
                    return None  # torna al menù
                elif len(nome) < 16 and ev.unicode.isprintable():
                    nome += ev.unicode

        # sfondo
        if img_sfondo:
            schermo.blit(img_sfondo, (0, 0))
        else:
            schermo.fill(BLU_SCURO)
            for sx, sy in stelle:
                pygame.draw.circle(schermo, BIANCO, (sx, sy), 1)

        overlay = pygame.Surface((LARGHEZZA, ALTEZZA), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        schermo.blit(overlay, (0, 0))

        # titolo
        titolo = font_title.render("INSERISCI IL TUO NOME", True, ORO)
        schermo.blit(titolo, (LARGHEZZA // 2 - titolo.get_width() // 2, 250))

        # box input
        box_x, box_y, box_w, box_h = LARGHEZZA // 2 - 250, 370, 500, 60
        pygame.draw.rect(schermo, BIANCO, (box_x, box_y, box_w, box_h), border_radius=8)
        pygame.draw.rect(schermo, BLU_CHIARO, (box_x, box_y, box_w, box_h), 3, border_radius=8)

        testo_input = font_input.render(nome + ("|" if cursore_visible else " "), True, NERO)
        schermo.blit(testo_input, (box_x + 15, box_y + 8))

        hint = font_hint.render("INVIO per confermare  |  ESC per tornare al menù", True, GRIGIO)
        schermo.blit(hint, (LARGHEZZA // 2 - hint.get_width() // 2, 460))

        pygame.display.flip()


# ──────────────────────────────────────────────
# SCHERMATA: CLASSIFICA
# ──────────────────────────────────────────────

def schermata_classifica(schermo, clock, img_sfondo, stelle):
    font_title  = pygame.font.Font(None, 72)
    font_header = pygame.font.Font(None, 36)
    font_row    = pygame.font.Font(None, 32)
    font_hint   = pygame.font.Font(None, 30)

    classifica = carica_classifica()

    while True:
        clock.tick(FPS)

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if ev.type == pygame.KEYDOWN:
                if ev.key in (pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_BACKSPACE):
                    return  # torna al menù

        # sfondo
        if img_sfondo:
            schermo.blit(img_sfondo, (0, 0))
        else:
            schermo.fill(BLU_SCURO)
            for sx, sy in stelle:
                pygame.draw.circle(schermo, BIANCO, (sx, sy), 1)

        overlay = pygame.Surface((LARGHEZZA, ALTEZZA), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 170))
        schermo.blit(overlay, (0, 0))

        titolo = font_title.render("🏆  CLASSIFICA", True, ORO)
        schermo.blit(titolo, (LARGHEZZA // 2 - titolo.get_width() // 2, 40))

        # intestazione colonne
        col_pos  = [120, 380, 650, 880, 1100]
        headers  = ["#", "NOME", "PUNTEGGIO", "ORSI", "ORCHE"]
        for i, h in enumerate(headers):
            surf = font_header.render(h, True, BLU_CHIARO)
            schermo.blit(surf, (col_pos[i], 140))

        pygame.draw.line(schermo, GRIGIO, (100, 175), (LARGHEZZA - 100, 175), 2)

        if not classifica:
            msg = font_row.render("Nessun punteggio registrato ancora.", True, GRIGIO)
            schermo.blit(msg, (LARGHEZZA // 2 - msg.get_width() // 2, 250))
        else:
            for idx, entry in enumerate(classifica):
                y = 190 + idx * 55
                colore = ORO if idx == 0 else (BIANCO if idx % 2 == 0 else (200, 200, 200))

                # sfondo riga alternato
                if idx % 2 == 0:
                    pygame.draw.rect(schermo, (255, 255, 255, 15),
                                     (100, y - 5, LARGHEZZA - 200, 45))

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

        hint = font_hint.render("Premi ESC o INVIO per tornare al menù", True, GRIGIO)
        schermo.blit(hint, (LARGHEZZA // 2 - hint.get_width() // 2, ALTEZZA - 50))

        pygame.display.flip()


# ──────────────────────────────────────────────
# SCHERMATA: MENÙ PRINCIPALE
# ──────────────────────────────────────────────

def schermata_menu(schermo, clock, img_sfondo, stelle):
    font_title   = pygame.font.Font(None, 90)
    font_sub     = pygame.font.Font(None, 36)
    font_option  = pygame.font.Font(None, 56)

    opzioni      = ["GIOCA", "CLASSIFICA", "ESCI"]
    selezionata  = 0

    while True:
        clock.tick(FPS)

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            if ev.type == pygame.KEYDOWN:
                if ev.key in (pygame.K_UP, pygame.K_w):
                    selezionata = (selezionata - 1) % len(opzioni)
                elif ev.key in (pygame.K_DOWN, pygame.K_s):
                    selezionata = (selezionata + 1) % len(opzioni)
                elif ev.key == pygame.K_RETURN:
                    return opzioni[selezionata]

            # click del mouse
            if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                mx, my = ev.pos
                for i in range(len(opzioni)):
                    oy = 420 + i * 90
                    if LARGHEZZA // 2 - 200 < mx < LARGHEZZA // 2 + 200 and oy - 5 < my < oy + 55:
                        return opzioni[i]

        # hover col mouse
        mx, my = pygame.mouse.get_pos()
        for i in range(len(opzioni)):
            oy = 420 + i * 90
            if LARGHEZZA // 2 - 200 < mx < LARGHEZZA // 2 + 200 and oy - 5 < my < oy + 55:
                selezionata = i

        # sfondo
        if img_sfondo:
            schermo.blit(img_sfondo, (0, 0))
        else:
            schermo.fill(BLU_SCURO)
            for sx, sy in stelle:
                pygame.draw.circle(schermo, BIANCO, (sx, sy), 1)

        overlay = pygame.Surface((LARGHEZZA, ALTEZZA), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 140))
        schermo.blit(overlay, (0, 0))

        titolo = font_title.render("FOCA vs ORSI & ORCA", True, ORO)
        schermo.blit(titolo, (LARGHEZZA // 2 - titolo.get_width() // 2, 200))

        sottotitolo = font_sub.render("Il videogioco più épico del Mare Artico", True, BLU_CHIARO)
        schermo.blit(sottotitolo, (LARGHEZZA // 2 - sottotitolo.get_width() // 2, 310))

        for i, opzione in enumerate(opzioni):
            y = 420 + i * 90
            if i == selezionata:
                # pulsante evidenziato
                pygame.draw.rect(schermo, BLU_CHIARO,
                                 (LARGHEZZA // 2 - 200, y - 5, 400, 60), border_radius=10)
                colore_testo = NERO
            else:
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
# GIOCO PRINCIPALE
# ──────────────────────────────────────────────

def gioca(schermo, clock, img_foca, img_orso, img_orca, img_sfondo, stelle, nome_giocatore):
    font     = pygame.font.Font(None, 36)
    font_pic = pygame.font.Font(None, 24)
    font_big = pygame.font.Font(None, 72)

    gioco_attivo = True

    foca = {'x': 50, 'y': ALTEZZA // 2 - 65,
            'w': 150, 'h': 130,
            'vita': VITA_FOCA}

    orsi = [nuovo_orso() for _ in range(ORSI_INIZIALI)]
    orca = None

    proiettili_foca   = []
    proiettili_nemici = []

    punteggio         = 0
    orsi_uccisi       = 0
    orche_uccise      = 0
    missili           = 0
    ultimo_spawn_orso = pygame.time.get_ticks()
    ultimo_spawn_orca = -1

    while True:
        dt = clock.tick(FPS)

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            if ev.type == pygame.KEYDOWN:
                # Dopo game over: R = rigioca, ESC = menù
                if not gioco_attivo:
                    if ev.key == pygame.K_r:
                        return 'rigioca', nome_giocatore
                    elif ev.key == pygame.K_ESCAPE:
                        return 'menu', None

                if gioco_attivo:
                    if ev.key == pygame.K_SPACE:
                        proiettili_foca.append(
                            crea_proiettile(foca['x'] + foca['w'],
                                            foca['y'] + foca['h'] // 2 - 3,
                                            1, 'normale'))
                    elif ev.key == pygame.K_RETURN and missili > 0:
                        proiettili_foca.append(
                            crea_proiettile(foca['x'] + foca['w'],
                                            foca['y'] + foca['h'] // 2 - 7,
                                            1, 'missile'))
                        missili -= 1

        # ── GAME OVER screen ──
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
            continue

        # ── input foca ──
        tasti = pygame.key.get_pressed()
        if tasti[pygame.K_w] or tasti[pygame.K_UP]:
            foca['y'] -= VELOCITA_FOCA
        if tasti[pygame.K_s] or tasti[pygame.K_DOWN]:
            foca['y'] += VELOCITA_FOCA
        foca['y'] = max(0, min(ALTEZZA - foca['h'], foca['y']))

        ora = pygame.time.get_ticks()

        # ── aggiorna orsi ──
        orsi_da_rimuovere = []
        for orso in orsi:
            orso['x'] += orso['vx']
            orso['timer_move'] -= dt
            if orso['timer_move'] <= 0:
                orso['vy'] = random.choice([-1, 0, 0, 1]) * VELOCITA_ORSO * 2
                orso['timer_move'] = random.randint(400, 1200)
            orso['y'] += orso['vy']
            orso['y'] = max(0, min(ALTEZZA - orso['h'], orso['y']))
            if orso['x'] + orso['w'] < 0:
                orsi_da_rimuovere.append(orso)
                continue
            if ora - orso['timer_sparo'] > orso['intervallo_sparo']:
                proiettili_nemici.append(
                    crea_proiettile(orso['x'], orso['y'] + orso['h'] // 2, -1, 'normale'))
                orso['timer_sparo'] = ora

        for o in orsi_da_rimuovere:
            orsi.remove(o)

        # ── spawn nuovi orsi ──
        if ora - ultimo_spawn_orso > TEMPO_SPAWN_ORSO:
            orsi.append(nuovo_orso())
            orsi.append(nuovo_orso())
            ultimo_spawn_orso = ora

        # ── aggiorna orca ──
        if orca:
            destinazione_x = int(LARGHEZZA * 0.65)
            if orca.get('entrata') and orca['x'] > destinazione_x:
                orca['x'] += orca['vx']
            else:
                orca['entrata'] = False
            orca['timer_move'] -= dt
            if orca['timer_move'] <= 0:
                orca['vy'] = random.choice([-1, 0, 0, 1]) * VELOCITA_ORCA * 3
                orca['timer_move'] = random.randint(500, 1500)
            orca['y'] += orca['vy']
            orca['y'] = max(0, min(ALTEZZA - orca['h'], orca['y']))
            if ora - orca['timer_sparo'] > orca['intervallo_sparo']:
                proiettili_nemici.append(
                    crea_proiettile(orca['x'], orca['y'] + orca['h'] // 2, -1, 'orca'))
                orca['timer_sparo'] = ora

        # ── aggiorna proiettili ──
        proiettili_foca   = [p for p in proiettili_foca   if aggiorna_proiettile(p)]
        proiettili_nemici = [p for p in proiettili_nemici if aggiorna_proiettile(p)]

        # ── collisioni proiettili foca → orsi ──
        for p in proiettili_foca[:]:
            colpito = False
            for orso in orsi[:]:
                if rect_collide(p['x'], p['y'], p['w'], p['h'],
                                orso['x'], orso['y'], orso['w'], orso['h']):
                    colpito = True
                    orso['vita'] -= p['danno']
                    if orso['vita'] <= 0:
                        orsi.remove(orso)
                        punteggio   += 10
                        orsi_uccisi += 1
                        if orsi_uccisi % ORSI_PER_MISSILE == 0:
                            missili += 1
                        soglia = (orsi_uccisi // ORSI_PER_BOSS) * ORSI_PER_BOSS
                        if (orsi_uccisi % ORSI_PER_BOSS == 0
                                and not orca
                                and soglia > ultimo_spawn_orca):
                            ultimo_spawn_orca = soglia
                            orca = nuova_orca()
                    break
            if colpito and p in proiettili_foca:
                proiettili_foca.remove(p)

        # ── collisioni proiettili foca → orca ──
        if orca:
            for p in proiettili_foca[:]:
                if rect_collide(p['x'], p['y'], p['w'], p['h'],
                                orca['x'], orca['y'], orca['w'], orca['h']):
                    if p in proiettili_foca:
                        proiettili_foca.remove(p)
                    orca['vita'] -= p['danno']
                    if orca['vita'] <= 0:
                        orca = None
                        punteggio    += 50
                        orche_uccise += 1
                        break

        # ── collisioni proiettili nemici → foca ──
        for p in proiettili_nemici[:]:
            if rect_collide(p['x'], p['y'], p['w'], p['h'],
                            foca['x'], foca['y'], foca['w'], foca['h']):
                proiettili_nemici.remove(p)
                foca['vita'] -= p['danno']
                if foca['vita'] <= 0:
                    foca['vita'] = 0
                    gioco_attivo = False
                    # salva il punteggio nella classifica al momento del game over
                    aggiungi_a_classifica(nome_giocatore, punteggio, orsi_uccisi, orche_uccise)

        # ══ DISEGNO ══
        if img_sfondo:
            schermo.blit(img_sfondo, (0, 0))
        else:
            schermo.fill(BLU_SCURO)
            for sx, sy in stelle:
                pygame.draw.circle(schermo, BIANCO, (sx, sy), 1)

        schermo.blit(img_foca, (foca['x'], foca['y']))

        for orso in orsi:
            schermo.blit(img_orso, (orso['x'], orso['y']))
            pygame.draw.rect(schermo, ROSSO,  (orso['x'], orso['y'] - 12, 60, 6))
            pygame.draw.rect(schermo, VERDE,
                             (orso['x'], orso['y'] - 12,
                              int(60 * max(0, orso['vita'] / VITA_ORSO)), 6))

        if orca:
            schermo.blit(img_orca, (orca['x'], orca['y']))
            pygame.draw.rect(schermo, ROSSO, (orca['x'], orca['y'] - 18, 120, 10))
            pygame.draw.rect(schermo, (255, 0, 255),
                             (orca['x'], orca['y'] - 18,
                              int(120 * max(0, orca['vita'] / VITA_ORCA)), 10))
            schermo.blit(font.render("BOSS!", True, (255, 0, 255)),
                         (orca['x'] + 20, orca['y'] - 45))

        for p in proiettili_foca:
            disegna_proiettile(schermo, p)
        for p in proiettili_nemici:
            disegna_proiettile(schermo, p)

        # ── HUD ──
        bar_w = 600
        pygame.draw.rect(schermo, ROSSO, (10, 10, bar_w, 22))
        pygame.draw.rect(schermo, VERDE,
                         (10, 10, int(bar_w * max(0, foca['vita'] / VITA_FOCA)), 22))
        schermo.blit(font_pic.render(f"Vita: {max(0, foca['vita'])}", True, BIANCO), (620, 12))

        schermo.blit(font.render(f"Punteggio: {punteggio}", True, BIANCO), (10, 40))
        schermo.blit(font_pic.render(f"Orsi eliminati: {orsi_uccisi}  |  Orche: {orche_uccise}",
                                     True, BIANCO), (10, 78))

        col_m = ARANCIONE if missili > 0 else GRIGIO
        schermo.blit(font_pic.render(f"Missili: {missili}  (INVIO)", True, col_m), (10, 100))

        prossimo = ORSI_PER_MISSILE - (orsi_uccisi % ORSI_PER_MISSILE)
        schermo.blit(font_pic.render(f"Prossimo missile tra: {prossimo} orsi", True, BIANCO),
                     (10, 122))

        # nome giocatore in alto a destra
        schermo.blit(font_pic.render(f"Giocatore: {nome_giocatore}", True, ORO),
                     (LARGHEZZA - 280, 30))

        schermo.blit(font_pic.render("W/S: Muovi  |  SPAZIO: Spara  |  INVIO: Missile",
                                     True, BIANCO), (LARGHEZZA - 480, 10))

        pygame.display.flip()


# ──────────────────────────────────────────────
# MAIN LOOP
# ──────────────────────────────────────────────

def main():
    schermo = pygame.display.set_mode((LARGHEZZA, ALTEZZA))
    pygame.display.set_caption("FOCA BAMBINA/O vs ORSI DIDDY con ORCA EPSTEIN")
    clock = pygame.time.Clock()

    img_foca   = carica_immagine(IMMAGINE_FOCA,   150, 130, "foca")
    img_orso   = carica_immagine(IMMAGINE_ORSO,   150, 130, "orso")
    img_orca   = carica_immagine(IMMAGINE_ORCA,   190, 170, "orca")
    img_sfondo = carica_sfondo(IMMAGINE_SFONDO)

    stelle = [(random.randint(0, LARGHEZZA), random.randint(0, ALTEZZA)) for _ in range(120)]

    nome_corrente = None

    while True:
        scelta = schermata_menu(schermo, clock, img_sfondo, stelle)

        if scelta == "ESCI":
            pygame.quit()
            sys.exit()

        elif scelta == "CLASSIFICA":
            schermata_classifica(schermo, clock, img_sfondo, stelle)

        elif scelta == "GIOCA":
            # Chiedi il nome solo se non ce l'abbiamo già
            nome = schermata_nome(schermo, clock, img_sfondo, stelle)
            if nome is None:
                continue  # ESC → torna al menù senza giocare
            nome_corrente = nome

            # Loop rigioca senza tornare al menù
            while True:
                risultato, _ = gioca(schermo, clock, img_foca, img_orso, img_orca,
                                     img_sfondo, stelle, nome_corrente)
                if risultato == 'rigioca':
                    # Chiedi il nome di nuovo per una nuova partita
                    nuovo_nome = schermata_nome(schermo, clock, img_sfondo, stelle)
                    if nuovo_nome:
                        nome_corrente = nuovo_nome
                    # Se ESC, rigioca con lo stesso nome
                else:
                    break  # 'menu' → esce dal loop interno e torna al while principale


if __name__ == "__main__":
    main()

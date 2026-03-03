import pygame
import random
import sys
import os
from pathlib import Path

pygame.init()

LARGHEZZA = 1500
ALTEZZA = 750
FPS = 60

BIANCO = (255, 255, 255)
NERO = (0, 0, 0)
ROSSO = (255, 0, 0)
VERDE = (0, 255, 0)
GRIGIO = (150, 150, 150)
GIALLO = (255, 255, 0)
ARANCIONE = (255, 165, 0)

VITA_FOCA = 400
VITA_ORSO = 35
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


def main():
    schermo = pygame.display.set_mode((LARGHEZZA, ALTEZZA))
    pygame.display.set_caption("Foca Spaziale vs Orsi Cyborg")
    clock = pygame.time.Clock()

    img_foca   = carica_immagine(IMMAGINE_FOCA,   150, 130, "foca")
    img_orso   = carica_immagine(IMMAGINE_ORSO,   150, 130, "orso")
    img_orca   = carica_immagine(IMMAGINE_ORCA,   190, 170, "orca")
    img_sfondo = carica_sfondo(IMMAGINE_SFONDO)

    stelle = [(random.randint(0, LARGHEZZA), random.randint(0, ALTEZZA)) for _ in range(120)]

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
    missili           = 0
    ultimo_spawn_orso = pygame.time.get_ticks()
    ultimo_spawn_orca = -1

    while True:
        dt = clock.tick(FPS)

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            if ev.type == pygame.KEYDOWN:
                if not gioco_attivo and ev.key == pygame.K_r:
                    return main()

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

        if not gioco_attivo:
            if img_sfondo:
                schermo.blit(img_sfondo, (0, 0))
            else:
                schermo.fill((10, 10, 30))
            overlay = pygame.Surface((LARGHEZZA, ALTEZZA), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            schermo.blit(overlay, (0, 0))
            schermo.blit(font_big.render("GAME OVER!", True, ROSSO),
                         (LARGHEZZA//2 - 180, ALTEZZA//2 - 100))
            schermo.blit(font.render(f"Punteggio: {punteggio}", True, BIANCO),
                         (LARGHEZZA//2 - 120, ALTEZZA//2))
            schermo.blit(font.render(f"Orsi eliminati: {orsi_uccisi}", True, BIANCO),
                         (LARGHEZZA//2 - 130, ALTEZZA//2 + 50))
            schermo.blit(font_pic.render("Premi R per ricominciare", True, GRIGIO),
                         (LARGHEZZA//2 - 130, ALTEZZA//2 + 100))
            pygame.display.flip()
            continue

        # --- input foca ---
        tasti = pygame.key.get_pressed()
        if tasti[pygame.K_w] or tasti[pygame.K_UP]:
            foca['y'] -= VELOCITA_FOCA
        if tasti[pygame.K_s] or tasti[pygame.K_DOWN]:
            foca['y'] += VELOCITA_FOCA
        foca['y'] = max(0, min(ALTEZZA - foca['h'], foca['y']))

        ora = pygame.time.get_ticks()

        # --- aggiorna orsi ---
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

        # --- spawn nuovi orsi ---
        if ora - ultimo_spawn_orso > TEMPO_SPAWN_ORSO:
            orsi.append(nuovo_orso())
            orsi.append(nuovo_orso())
            ultimo_spawn_orso = ora

        # --- aggiorna orca ---
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

        # --- aggiorna proiettili ---
        proiettili_foca   = [p for p in proiettili_foca   if aggiorna_proiettile(p)]
        proiettili_nemici = [p for p in proiettili_nemici if aggiorna_proiettile(p)]

        # --- collisioni proiettili foca → orsi ---
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

        # --- collisioni proiettili foca → orca ---
        if orca:
            for p in proiettili_foca[:]:
                if rect_collide(p['x'], p['y'], p['w'], p['h'],
                                orca['x'], orca['y'], orca['w'], orca['h']):
                    if p in proiettili_foca:
                        proiettili_foca.remove(p)
                    orca['vita'] -= p['danno']
                    if orca['vita'] <= 0:
                        orca = None
                        punteggio += 50
                        break

        # --- collisioni proiettili nemici → foca ---
        for p in proiettili_nemici[:]:
            if rect_collide(p['x'], p['y'], p['w'], p['h'],
                            foca['x'], foca['y'], foca['w'], foca['h']):
                proiettili_nemici.remove(p)
                foca['vita'] -= p['danno']
                if foca['vita'] <= 0:
                    foca['vita'] = 0
                    gioco_attivo = False

        # ===== DISEGNO =====
        if img_sfondo:
            schermo.blit(img_sfondo, (0, 0))
        else:
            schermo.fill((10, 10, 30))
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

        # --- HUD ---
        bar_w = 600
        pygame.draw.rect(schermo, ROSSO, (10, 10, bar_w, 22))
        pygame.draw.rect(schermo, VERDE,
                         (10, 10, int(bar_w * max(0, foca['vita'] / VITA_FOCA)), 22))
        schermo.blit(font_pic.render(f"Vita: {max(0, foca['vita'])}", True, BIANCO), (620, 12))

        schermo.blit(font.render(f"Punteggio: {punteggio}", True, BIANCO), (10, 40))
        schermo.blit(font_pic.render(f"Orsi eliminati: {orsi_uccisi}", True, BIANCO), (10, 78))

        col_m = ARANCIONE if missili > 0 else GRIGIO
        schermo.blit(font_pic.render(f"Missili: {missili}  (INVIO)", True, col_m), (10, 100))

        prossimo = ORSI_PER_MISSILE - (orsi_uccisi % ORSI_PER_MISSILE)
        schermo.blit(font_pic.render(f"Prossimo missile tra: {prossimo} orsi", True, BIANCO),
                     (10, 122))

        schermo.blit(font_pic.render("W/S: Muovi  |  SPAZIO: Spara  |  INVIO: Missile",
                                     True, BIANCO), (LARGHEZZA - 480, 10))

        pygame.display.flip()


if __name__ == "__main__":
    main()

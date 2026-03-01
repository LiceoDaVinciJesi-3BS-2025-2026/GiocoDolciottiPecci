import pygame
import random
import sys
import os
from pathlib import Path

# Inizializzazione Pygame gffdfdtgvghfhgftxrtfygfyu
pygame.init()

# Costanti
LARGHEZZA = 1500
ALTEZZA = 750
FPS = 60

# Colori
BIANCO = (255, 255, 255)
NERO = (0, 0, 0)
ROSSO = (255, 0, 0)
VERDE = (0, 255, 0)
BLU = (100, 150, 255)
GRIGIO = (150, 150, 150)
GIALLO = (255, 255, 0)
ARANCIONE = (255, 165, 0)

# Impostazioni gioco
VITA_FOCA = 400
VITA_ORSO = 35
VITA_ORCA = 100
DANNO_NORMALE = 5
DANNO_MISSILE = 100
DANNO_ORCA = 10
VELOCITA_PROIETTILE = 9
VELOCITA_MISSILE = 16
VELOCITA_FOCA = 5
VELOCITA_ORSO = 4
VELOCITA_ORCA = 5
TEMPO_SPAWN_ORSO = 3000  # 3 secondi
ORSI_INIZIALI = 6
ORSI_PER_MISSILE = 7
ORSI_PER_BOSS = 9

# ========== INSERISCI QUI I PERCORSI DELLE TUE IMMAGINI ==========
IMMAGINE_FOCA = Path.cwd() / "foca2.png"
IMMAGINE_ORSO = Path.cwd() / "orso21.png"
IMMAGINE_ORCA = Path.cwd() / "orca2.png"
IMMAGINE_SFONDO = Path.cwd() / "sfondo.png"  # <-- Metti qui il nome del tuo file sfondo
# ================================================================

def carica_immagine(percorso, larghezza, altezza, colore_default):
    """Carica un'immagine o crea un placeholder se non esiste"""
    if os.path.exists(percorso):
        try:
            img = pygame.image.load(percorso)
            img = pygame.transform.scale(img, (larghezza, altezza))
            return img
        except:
            pass
    
    # Crea placeholder se l'immagine non esiste
    superficie = pygame.Surface((larghezza, altezza))
    superficie.fill(BIANCO)
    if colore_default == "foca":
        pygame.draw.circle(superficie, GRIGIO, (15, 20), 15)
        pygame.draw.ellipse(superficie, GRIGIO, (25, 10, 30, 25))
        pygame.draw.polygon(superficie, GRIGIO, [(55, 20), (60, 15), (60, 25)])
        pygame.draw.circle(superficie, NERO, (50, 18), 3)
    elif colore_default == "orso":
        pygame.draw.circle(superficie, (200, 200, 200), (45, 20), 15)
        pygame.draw.ellipse(superficie, (180, 180, 180), (5, 10, 30, 25))
        pygame.draw.polygon(superficie, (200, 200, 200), [(5, 20), (0, 15), (0, 25)])
        pygame.draw.circle(superficie, ROSSO, (10, 18), 3)
        pygame.draw.rect(superficie, GRIGIO, (20, 15, 15, 3))
    elif colore_default == "orca":
        pygame.draw.ellipse(superficie, NERO, (0, 5, 70, 35))
        pygame.draw.ellipse(superficie, BIANCO, (10, 15, 20, 15))
        pygame.draw.circle(superficie, ROSSO, (15, 20), 4)
        pygame.draw.polygon(superficie, NERO, [(65, 20), (75, 10), (75, 30)])
    return superficie

def carica_sfondo(percorso):
    """Carica l'immagine di sfondo o restituisce None se non esiste"""
    if os.path.exists(percorso):
        try:
            img = pygame.image.load(percorso)
            img = pygame.transform.scale(img, (LARGHEZZA, ALTEZZA))
            return img
        except:
            pass
    return None

# FIX BUG: funzione per creare un orso con dizionario indipendente
def crea_orso():
    return {
        'x': LARGHEZZA - 300,
        'y': random.randint(50, ALTEZZA - 50),
        'larghezza': 150,
        'altezza': 130,
        'vita': VITA_ORSO,
        'velocita': VELOCITA_ORSO,
        'tempo_ultimo_sparo': pygame.time.get_ticks(),
        'intervallo_sparo': random.randint(1500, 3000)
    }

def crea_proiettile_normale(x, y, direzione):
    """Crea un proiettile normale"""
    return {
        'x': x,
        'y': y,
        'direzione': direzione,
        'larghezza': 6.5,
        'altezza': 6.5,
        'colore': GIALLO if direzione > 0 else ROSSO,
        'tipo': 'normale',
        'danno': DANNO_NORMALE
    }

def crea_missile(x, y):
    """Crea un missile speciale"""
    return {
        'x': x,
        'y': y,
        'direzione': 1,
        'larghezza': 45,
        'altezza': 15,
        'colore': ARANCIONE,
        'tipo': 'missile',
        'danno': DANNO_MISSILE
    }

def crea_proiettile_orca(x, y):
    """Crea un proiettile dell'orca"""
    return {
        'x': x,
        'y': y,
        'direzione': -1,
        'larghezza': 8,
        'altezza': 8,
        'colore': (255, 0, 255),
        'tipo': 'orca',
        'danno': DANNO_ORCA
    }

def aggiorna_proiettile(proiettile):
    """Aggiorna posizione proiettile"""
    velocita = VELOCITA_MISSILE if proiettile['tipo'] == 'missile' else VELOCITA_PROIETTILE
    proiettile['x'] += velocita * proiettile['direzione']
    return 0 <= proiettile['x'] <= LARGHEZZA

def disegna_proiettile(schermo, proiettile):
    """Disegna un proiettile"""
    pygame.draw.rect(schermo, proiettile['colore'], 
                     (proiettile['x'], proiettile['y'], 
                      proiettile['larghezza'], proiettile['altezza']))
    if proiettile['tipo'] == 'missile':
        # Effetto fiamma per il missile
        pygame.draw.circle(schermo, GIALLO, 
                          (int(proiettile['x']), int(proiettile['y'] + 4)), 4)

def main():
    # Inizializza schermo
    schermo = pygame.display.set_mode((LARGHEZZA, ALTEZZA))
    pygame.display.set_caption("Foca Spaziale vs Orsi Cyborg")
    orologio = pygame.time.Clock()
    
    # Carica immagini
    img_foca = carica_immagine(IMMAGINE_FOCA, 150, 130, "foca")
    img_orso = carica_immagine(IMMAGINE_ORSO, 150, 130, "orso")
    img_orca = carica_immagine(IMMAGINE_ORCA, 170, 190, "orca")
    img_sfondo = carica_sfondo(IMMAGINE_SFONDO)  # Carica sfondo

    # Stelle statiche (usate solo se l'immagine sfondo non è disponibile)
    stelle = [(random.randint(0, LARGHEZZA), random.randint(0, ALTEZZA)) for _ in range(100)]
    
    # Font
    font = pygame.font.Font(None, 36)
    font_piccolo = pygame.font.Font(None, 24)
    
    # Stato gioco
    gioco_attivo = True
    
    # Foca
    foca = {
        'x': 50,
        'y': ALTEZZA // 2,
        'larghezza': 150,
        'altezza': 130,
        'vita': VITA_FOCA,
        'velocita': VELOCITA_FOCA
    }
    
    # Liste
    orsi = []
    orca = None
    proiettili_foca = []
    proiettili_nemici = []
    
    # Statistiche
    punteggio = 0
    orsi_uccisi = 0
    orche_uccise = 0  # NUOVO: contatore orche eliminate
    missili_disponibili = 0
    tempo_ultimo_spawn = pygame.time.get_ticks()
    
    # Crea orsi iniziali
    for i in range(ORSI_INIZIALI):
        o = crea_orso()
        o['tempo_ultimo_sparo'] = pygame.time.get_ticks() + random.randint(0, 2000)
        orsi.append(o)
    
    # Loop principale
    while True:
        # Eventi
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if evento.type == pygame.KEYDOWN and gioco_attivo:
                if evento.key == pygame.K_SPACE:
                    proiettile = crea_proiettile_normale(
                        foca['x'] + foca['larghezza'], 
                        foca['y'] + foca['altezza'] // 2,
                        1
                    )
                    proiettili_foca.append(proiettile)
                
                elif evento.key == pygame.K_RETURN and missili_disponibili > 0:
                    missile = crea_missile(
                        foca['x'] + foca['larghezza'],
                        foca['y'] + foca['altezza'] // 2
                    )
                    proiettili_foca.append(missile)
                    missili_disponibili -= 1
            
            if evento.type == pygame.KEYDOWN and not gioco_attivo:
                if evento.key == pygame.K_r:
                    return main()
        
        if gioco_attivo:
            # Input movimento foca
            tasti = pygame.key.get_pressed()
            if tasti[pygame.K_w] or tasti[pygame.K_UP]:
                foca['y'] -= foca['velocita']
            if tasti[pygame.K_s] or tasti[pygame.K_DOWN]:
                foca['y'] += foca['velocita']
            
            foca['y'] = max(0, min(ALTEZZA - foca['altezza'], foca['y']))
            
            # Aggiorna orsi
            for orso in orsi:
                if random.random() < 0.02:
                    orso['y'] += random.choice([-1, 1]) * orso['velocita'] * 5
                orso['y'] = max(0, min(ALTEZZA - orso['altezza'], orso['y']))
                
                ora = pygame.time.get_ticks()
                if ora - orso['tempo_ultimo_sparo'] > orso['intervallo_sparo']:
                    proiettile = crea_proiettile_normale(
                        orso['x'],
                        orso['y'] + orso['altezza'] // 2,
                        -1
                    )
                    proiettili_nemici.append(proiettile)
                    orso['tempo_ultimo_sparo'] = ora
            
            # Aggiorna orca
            if orca:
                if random.random() < 0.03:
                    orca['y'] += random.choice([-1, 1]) * orca['velocita'] * 5
                orca['y'] = max(0, min(ALTEZZA - orca['altezza'], orca['y']))
                
                ora = pygame.time.get_ticks()
                if ora - orca['tempo_ultimo_sparo'] > orca['intervallo_sparo']:
                    proiettile = crea_proiettile_orca(
                        orca['x'],
                        orca['y'] + orca['altezza'] // 2
                    )
                    proiettili_nemici.append(proiettile)
                    orca['tempo_ultimo_sparo'] = ora
            
            # Aggiorna proiettili
            proiettili_foca = [p for p in proiettili_foca if aggiorna_proiettile(p)]
            proiettili_nemici = [p for p in proiettili_nemici if aggiorna_proiettile(p)]
            
            # Collisioni proiettili foca con orsi
            for proiettile in proiettili_foca[:]:
                for orso in orsi[:]:
                    if (orso['x'] < proiettile['x'] < orso['x'] + orso['larghezza'] and
                        orso['y'] < proiettile['y'] < orso['y'] + orso['altezza']):
                        if proiettile in proiettili_foca:
                            proiettili_foca.remove(proiettile)
                        orso['vita'] -= proiettile['danno']
                        if orso['vita'] <= 0:
                            if orso in orsi:
                                orsi.remove(orso)
                            punteggio += 10
                            orsi_uccisi += 1
                            
                            if orsi_uccisi % ORSI_PER_MISSILE == 0:
                                missili_disponibili += 1
                            
                            if orsi_uccisi % ORSI_PER_BOSS == 0 and not orca:
                                orca = {
                                    'x': LARGHEZZA - 300,
                                    'y': ALTEZZA // 2,
                                    'larghezza': 190,
                                    'altezza': 170,
                                    'vita': VITA_ORCA,
                                    'velocita': VELOCITA_ORCA,
                                    'tempo_ultimo_sparo': pygame.time.get_ticks(),
                                    'intervallo_sparo': 1000
                                }
                        break
            
            # Collisioni proiettili foca con orca
            if orca:
                for proiettile in proiettili_foca[:]:
                    if (orca['x'] < proiettile['x'] < orca['x'] + orca['larghezza'] and
                        orca['y'] < proiettile['y'] < orca['y'] + orca['altezza']):
                        if proiettile in proiettili_foca:
                            proiettili_foca.remove(proiettile)
                        orca['vita'] -= proiettile['danno']
                        if orca['vita'] <= 0:
                            orca = None
                            punteggio += 50
                            orche_uccise += 1  # NUOVO: incrementa contatore orche
            
            # Collisioni proiettili nemici con foca
            for proiettile in proiettili_nemici[:]:
                if (foca['x'] < proiettile['x'] < foca['x'] + foca['larghezza'] and
                    foca['y'] < proiettile['y'] < foca['y'] + foca['altezza']):
                    proiettili_nemici.remove(proiettile)
                    foca['vita'] -= proiettile['danno']
                    if foca['vita'] <= 0:
                        gioco_attivo = False
            
            # Spawn nuovi orsi ogni 3 secondi
            ora = pygame.time.get_ticks()
            if ora - tempo_ultimo_spawn > TEMPO_SPAWN_ORSO:
                orsi.append(crea_orso())  # FIX BUG: due dizionari separati e indipendenti
                orsi.append(crea_orso())
                tempo_ultimo_spawn = ora
        
        # ===== DISEGNO =====

        # Sfondo: immagine se disponibile, altrimenti colore scuro + stelle
        if img_sfondo:
            schermo.blit(img_sfondo, (0, 0))
        else:
            schermo.fill((10, 10, 30))
            for x, y in stelle:
                pygame.draw.circle(schermo, BIANCO, (x, y), 1)
        
        # Disegna foca
        schermo.blit(img_foca, (foca['x'], foca['y']))
        
        # Disegna orsi
        for orso in orsi:
            schermo.blit(img_orso, (orso['x'], orso['y']))
            pygame.draw.rect(schermo, ROSSO, (orso['x'], orso['y'] - 10, 60, 5))
            vita_percentuale = orso['vita'] / VITA_ORSO
            pygame.draw.rect(schermo, VERDE, (orso['x'], orso['y'] - 10, int(60 * vita_percentuale), 5))
        
        # Disegna orca
        if orca:
            schermo.blit(img_orca, (orca['x'], orca['y']))
            pygame.draw.rect(schermo, ROSSO, (orca['x'], orca['y'] - 15, 80, 8))
            vita_percentuale = orca['vita'] / VITA_ORCA
            pygame.draw.rect(schermo, (255, 0, 255), (orca['x'], orca['y'] - 15, int(80 * vita_percentuale), 8))
            testo_boss = font.render("BOSS!", True, (255, 0, 255))
            schermo.blit(testo_boss, (orca['x'] + 10, orca['y'] - 40))
        
        # Disegna proiettili
        for proiettile in proiettili_foca:
            disegna_proiettile(schermo, proiettile)
        for proiettile in proiettili_nemici:
            disegna_proiettile(schermo, proiettile)
        
        # UI
        pygame.draw.rect(schermo, ROSSO, (10, 10, 800, 20))
        pygame.draw.rect(schermo, VERDE, (10, 10, max(0, foca['vita'] * 2), 20))
        testo_vita = font_piccolo.render(f"Vita: {foca['vita']}", True, BIANCO)
        schermo.blit(testo_vita, (820, 10))
        
        testo_punteggio = font.render(f"Punteggio: {punteggio}", True, BIANCO)
        schermo.blit(testo_punteggio, (10, 40))
        
        testo_uccisi = font_piccolo.render(f"Orsi eliminati: {orsi_uccisi}", True, BIANCO)
        schermo.blit(testo_uccisi, (10, 75))
        
        colore_missile = ARANCIONE if missili_disponibili > 0 else GRIGIO
        testo_missili = font_piccolo.render(f"Missili: {missili_disponibili} (INVIO)", True, colore_missile)
        schermo.blit(testo_missili, (10, 100))
        
        orsi_per_prossimo = ORSI_PER_MISSILE - (orsi_uccisi % ORSI_PER_MISSILE)
        testo_prossimo = font_piccolo.render(f"Prossimo missile tra: {orsi_per_prossimo} orsi", True, BIANCO)
        schermo.blit(testo_prossimo, (10, 125))

        # NUOVO: contatore orche eliminate in viola
        testo_orche = font_piccolo.render(f"Orche eliminate: {orche_uccise}", True, (255, 0, 255))
        schermo.blit(testo_orche, (10, 150))
        
        testo_controlli = font_piccolo.render("W/S: Muovi | SPAZIO: Spara | INVIO: Missile", True, BIANCO)
        schermo.blit(testo_controlli, (LARGHEZZA - 450, 10))
        
        # Game Over
        if not gioco_attivo:
            overlay = pygame.Surface((LARGHEZZA, ALTEZZA))
            overlay.set_alpha(200)
            overlay.fill(NERO)
            schermo.blit(overlay, (0, 0))
            
            testo_gameover = font.render("GAME OVER!", True, ROSSO)
            testo_finale = font.render(f"Punteggio Finale: {punteggio}", True, BIANCO)
            testo_uccisi_finale = font.render(f"Orsi Eliminati: {orsi_uccisi}", True, BIANCO)
            testo_orche_finale = font.render(f"Orche Eliminate: {orche_uccise}", True, (255, 0, 255))
            testo_riavvia = font_piccolo.render("Premi R per ricominciare", True, BIANCO)
            
            schermo.blit(testo_gameover, (LARGHEZZA//2 - 100, ALTEZZA//2 - 100))
            schermo.blit(testo_finale, (LARGHEZZA//2 - 150, ALTEZZA//2 - 40))
            schermo.blit(testo_uccisi_finale, (LARGHEZZA//2 - 150, ALTEZZA//2 + 0))
            schermo.blit(testo_orche_finale, (LARGHEZZA//2 - 150, ALTEZZA//2 + 40))
            schermo.blit(testo_riavvia, (LARGHEZZA//2 - 130, ALTEZZA//2 + 80))
        
        pygame.display.flip()
        orologio.tick(FPS)

if __name__ == "__main__":
    main()
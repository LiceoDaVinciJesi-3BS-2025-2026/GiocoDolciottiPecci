def main() -> None:
    print("Hello from giocodolciottipecci!")

import pygame
import random
import sys
import os

# Inizializzazione Pygame
pygame.init()

# Costanti
LARGHEZZA = 1000
ALTEZZA = 600
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
VITA_FOCA = 100
VITA_ORSO = 70
VITA_ORCA = 200
DANNO_NORMALE = 10
DANNO_MISSILE = 30
DANNO_ORCA = 20
VELOCITA_PROIETTILE = 8
VELOCITA_MISSILE = 6
VELOCITA_FOCA = 5
VELOCITA_ORSO = 3
VELOCITA_ORCA = 2
TEMPO_SPAWN_ORSO = 15000  # 15 secondi
ORSI_INIZIALI = 5
ORSI_PER_MISSILE = 7
ORSI_PER_BOSS = 10

# ========== INSERISCI QUI I PERCORSI DELLE TUE IMMAGINI ==========
# Sostituisci questi percorsi con i tuoi file immagine
IMMAGINE_FOCA = "foca.png"  # <-- Metti qui il percorso della tua immagine foca
IMMAGINE_ORSO = "orso.png"  # <-- Metti qui il percorso della tua immagine orso
IMMAGINE_ORCA = "orca.png"  # <-- Metti qui il percorso della tua immagine orca (opzionale)
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

def crea_proiettile_normale(x, y, direzione):
    """Crea un proiettile normale"""
    return {
        'x': x,
        'y': y,
        'direzione': direzione,
        'larghezza': 10,
        'altezza': 5,
        'colore': VERDE if direzione > 0 else ROSSO,
        'tipo': 'normale',
        'danno': DANNO_NORMALE
    }

def crea_missile(x, y):
    """Crea un missile speciale"""
    return {
        'x': x,
        'y': y,
        'direzione': 1,
        'larghezza': 20,
        'altezza': 8,
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
        'larghezza': 12,
        'altezza': 6,
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
    img_foca = carica_immagine(IMMAGINE_FOCA, 60, 40, "foca")
    img_orso = carica_immagine(IMMAGINE_ORSO, 60, 40, "orso")
    img_orca = carica_immagine(IMMAGINE_ORCA, 80, 50, "orca")
    
    # Font
    font = pygame.font.Font(None, 36)
    font_piccolo = pygame.font.Font(None, 24)
    
    # Stato gioco
    gioco_attivo = True
    
    # Foca
    foca = {
        'x': 50,
        'y': ALTEZZA // 2,
        'larghezza': 60,
        'altezza': 40,
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
    missili_disponibili = 0
    tempo_ultimo_spawn = pygame.time.get_ticks()
    
    # Crea orsi iniziali
    for i in range(ORSI_INIZIALI):
        orso = {
            'x': LARGHEZZA - 50,
            'y': random.randint(50, ALTEZZA - 50),
            'larghezza': 60,
            'altezza': 40,
            'vita': VITA_ORSO,
            'velocita': VELOCITA_ORSO,
            'tempo_ultimo_sparo': pygame.time.get_ticks() + random.randint(0, 2000),
            'intervallo_sparo': random.randint(1500, 3000)
        }
        orsi.append(orso)
    
    # Loop principale
    while True:
        # Eventi
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if evento.type == pygame.KEYDOWN and gioco_attivo:
                if evento.key == pygame.K_SPACE:
                    # Sparo normale - MODIFICATO: aggiunto parametro direzione
                    proiettile = crea_proiettile_normale(
                        foca['x'] + foca['larghezza'], 
                        foca['y'] + foca['altezza'] // 2,
                        1  # direzione verso destra
                    )
                    proiettili_foca.append(proiettile)
                
                elif evento.key == pygame.K_RETURN and missili_disponibili > 0:
                    # Sparo missile
                    missile = crea_missile(
                        foca['x'] + foca['larghezza'],
                        foca['y'] + foca['altezza'] // 2
                    )
                    proiettili_foca.append(missile)
                    missili_disponibili -= 1
            
            if evento.type == pygame.KEYDOWN and not gioco_attivo:
                if evento.key == pygame.K_r:
                    # Riavvia il gioco
                    return main()
        
        if gioco_attivo:
            # Input movimento foca
            tasti = pygame.key.get_pressed()
            if tasti[pygame.K_w] or tasti[pygame.K_UP]:
                foca['y'] -= foca['velocita']
            if tasti[pygame.K_s] or tasti[pygame.K_DOWN]:
                foca['y'] += foca['velocita']
            
            # Limiti foca
            foca['y'] = max(0, min(ALTEZZA - foca['altezza'], foca['y']))
            
            # Aggiorna orsi
            for orso in orsi:
                # Movimento casuale
                if random.random() < 0.02:
                    orso['y'] += random.choice([-1, 1]) * orso['velocita'] * 5
                orso['y'] = max(0, min(ALTEZZA - orso['altezza'], orso['y']))
                
                # Sparo orso
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
                # Movimento orca
                if random.random() < 0.03:
                    orca['y'] += random.choice([-1, 1]) * orca['velocita'] * 5
                orca['y'] = max(0, min(ALTEZZA - orca['altezza'], orca['y']))
                
                # Sparo orca (più frequente)
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
                            orsi.remove(orso)
                            punteggio += 10
                            orsi_uccisi += 1
                            
                            # Sblocca missile ogni 7 orsi
                            if orsi_uccisi % ORSI_PER_MISSILE == 0:
                                missili_disponibili += 1
                            
                            # Spawn boss ogni 10 orsi
                            if orsi_uccisi % ORSI_PER_BOSS == 0 and not orca:
                                orca = {
                                    'x': LARGHEZZA - 100,
                                    'y': ALTEZZA // 2,
                                    'larghezza': 80,
                                    'altezza': 50,
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
            
            # Collisioni proiettili nemici con foca
            for proiettile in proiettili_nemici[:]:
                if (foca['x'] < proiettile['x'] < foca['x'] + foca['larghezza'] and
                    foca['y'] < proiettile['y'] < foca['y'] + foca['altezza']):
                    proiettili_nemici.remove(proiettile)
                    foca['vita'] -= proiettile['danno']
                    if foca['vita'] <= 0:
                        gioco_attivo = False
            
            # Spawn nuovi orsi ogni 15 secondi
            ora = pygame.time.get_ticks()
            if ora - tempo_ultimo_spawn > TEMPO_SPAWN_ORSO:
                orso = {
                    'x': LARGHEZZA - 50,
                    'y': random.randint(50, ALTEZZA - 50),
                    'larghezza': 60,
                    'altezza': 40,
                    'vita': VITA_ORSO,
                    'velocita': VELOCITA_ORSO,
                    'tempo_ultimo_sparo': pygame.time.get_ticks(),
                    'intervallo_sparo': random.randint(1500, 3000)
                }
                orsi.append(orso)
                tempo_ultimo_spawn = ora
        
        # ===== DISEGNO =====
        # Sfondo spaziale
        schermo.fill((10, 10, 30))
        
        # Stelle
        for _ in range(100):
            x = random.randint(0, LARGHEZZA)
            y = random.randint(0, ALTEZZA)
            pygame.draw.circle(schermo, BIANCO, (x, y), 1)
        
        # Disegna foca
        schermo.blit(img_foca, (foca['x'], foca['y']))
        
        # Disegna orsi
        for orso in orsi:
            schermo.blit(img_orso, (orso['x'], orso['y']))
            # Barra vita orso
            pygame.draw.rect(schermo, ROSSO, (orso['x'], orso['y'] - 10, 60, 5))
            vita_percentuale = orso['vita'] / VITA_ORSO
            pygame.draw.rect(schermo, VERDE, (orso['x'], orso['y'] - 10, int(60 * vita_percentuale), 5))
        
        # Disegna orca
        if orca:
            schermo.blit(img_orca, (orca['x'], orca['y']))
            # Barra vita orca
            pygame.draw.rect(schermo, ROSSO, (orca['x'], orca['y'] - 15, 80, 8))
            vita_percentuale = orca['vita'] / VITA_ORCA
            pygame.draw.rect(schermo, (255, 0, 255), (orca['x'], orca['y'] - 15, int(80 * vita_percentuale), 8))
            # Etichetta BOSS
            testo_boss = font.render("BOSS!", True, (255, 0, 255))
            schermo.blit(testo_boss, (orca['x'] + 10, orca['y'] - 40))
        
        # Disegna proiettili
        for proiettile in proiettili_foca:
            disegna_proiettile(schermo, proiettile)
        for proiettile in proiettili_nemici:
            disegna_proiettile(schermo, proiettile)
        
        # UI
        # Barra vita foca
        pygame.draw.rect(schermo, ROSSO, (10, 10, 200, 20))
        pygame.draw.rect(schermo, VERDE, (10, 10, max(0, foca['vita'] * 2), 20))
        testo_vita = font_piccolo.render(f"Vita: {foca['vita']}", True, BIANCO)
        schermo.blit(testo_vita, (220, 10))
        
        # Punteggio
        testo_punteggio = font.render(f"Punteggio: {punteggio}", True, BIANCO)
        schermo.blit(testo_punteggio, (10, 40))
        
        # Orsi uccisi
        testo_uccisi = font_piccolo.render(f"Orsi eliminati: {orsi_uccisi}", True, BIANCO)
        schermo.blit(testo_uccisi, (10, 75))
        
        # Missili disponibili
        colore_missile = ARANCIONE if missili_disponibili > 0 else GRIGIO
        testo_missili = font_piccolo.render(f"Missili: {missili_disponibili} (INVIO)", True, colore_missile)
        schermo.blit(testo_missili, (10, 100))
        
        # Prossimo missile
        orsi_per_prossimo = ORSI_PER_MISSILE - (orsi_uccisi % ORSI_PER_MISSILE)
        testo_prossimo = font_piccolo.render(f"Prossimo missile tra: {orsi_per_prossimo} orsi", True, BIANCO)
        schermo.blit(testo_prossimo, (10, 125))
        
        # Controlli
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
            testo_riavvia = font_piccolo.render("Premi R per ricominciare", True, BIANCO)
            
            schermo.blit(testo_gameover, (LARGHEZZA//2 - 100, ALTEZZA//2 - 80))
            schermo.blit(testo_finale, (LARGHEZZA//2 - 150, ALTEZZA//2 - 20))
            schermo.blit(testo_uccisi_finale, (LARGHEZZA//2 - 150, ALTEZZA//2 + 20))
            schermo.blit(testo_riavvia, (LARGHEZZA//2 - 130, ALTEZZA//2 + 60))
        
        pygame.display.flip()
        orologio.tick(FPS)

if __name__ == "__main__":
    main()

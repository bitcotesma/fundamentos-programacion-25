import pygame                                           
import random                                           

pygame.init() 
pygame.mixer.init()
pygame.mixer.music.load("All I Ever Wanted.mp3")
pygame.mixer.music.play (-1)

ancho = 400
altura = 600
ventana = pygame.display.set_mode((ancho, altura))       #dimensiones de la ventana

pygame.display.set_caption('Dance Dance Revolution')    #nombre de la ventana
fps = pygame.time.Clock()
fps.tick(60)                                            #frames por segundo


negro = (0,0,0)                                         #colores
blanco = (255,255,255)
gris = (200,200,200)
rojo = (255, 0, 0)
verde = (0,255,0)

impacto = 100                                           #zona de impacto de flechas
velocidad = 5                                           #tiempo de render de flechas en fps
imagenFlecha = {
    "arriba": pygame.image.load("flechaarriba.png"),
    "abajo": pygame.image.load("flechaabajo.png"),
    "izquierda": pygame.image.load("flechaizquierda.png"),
    "derecha": pygame.image.load("flechaderecha.png")
}
flechas = []                                            #abro una lista vacia para las flechas
def flechaAparece ():                                   #declaro funcion para hacer aparecer las flechas
    direccion = random.choice(["arriba","abajo","izquierda","derecha"]) #elige al azar una direccion de flecha
    posicionX = {"arriba" :120,"abajo":220,"izquierda":20,"derecha":320}[direccion] #posicion en el eje x donde aparecen las flechas
    flechas.append({"dir": direccion, "x" : posicionX, "y" : altura}) #añado a la lista direccion y posicion

jugando = True 
puntaje = 0
vidas = 10
tiempoDeSpawn = 0
fuente = pygame.font.SysFont(None, 36)

while jugando:  #el loop principal, para que corra
    ventana.fill(negro)

    for evento in pygame.event.get(): #para salir del juego
        if evento.type == pygame.QUIT:
            jugando = False
    tiempoDeSpawn += fps.get_time() #tiempo entre flecha y flecha (modificar para dificultad)
    if tiempoDeSpawn > 460:
        flechaAparece()
        tiempoDeSpawn = 0

    apretar = pygame.key.get_pressed()

    for flecha in flechas[:]: #dibuja el movimiento de las flechas
        flecha["y"] -= velocidad
        ventana.blit(imagenFlecha[flecha["dir"]], (flecha["x"], flecha["y"]))

        # Verificar si está en la zona de impacto
        if impacto - 10 < flecha["y"] < impacto + 10: #si la flecha esta en zona de impacto y imput correcto
            if (flecha["dir"] == "arriba" and (apretar[pygame.K_UP]) or apretar[pygame.K_w]) or \
               (flecha["dir"] == "abajo" and (apretar[pygame.K_DOWN]) or apretar[pygame.K_s]) or \
               (flecha["dir"] == "izquierda" and (apretar[pygame.K_LEFT]) or apretar[pygame.K_a]) or \
               (flecha["dir"] == "derecha" and (apretar[pygame.K_RIGHT] or apretar[pygame.K_d])):
                flechas.remove(flecha)
                puntaje += 1

        
        elif flecha["y"] < 0:       #  flechas que pasaron
            flechas.remove(flecha) 
            vidas -= 1              #remueve vidas
            if vidas <= 0 :         #game over
                jugando = False

    # Dibujar zona de impacto
    pygame.draw.line(ventana, gris, (0, impacto), (altura, impacto), 2) #zona de impacto linea 1
    pygame.draw.line(ventana, gris, (0, impacto+64), (altura, impacto+64), 2) #zona de impacto linea 2 
   
    textoPuntaje = fuente.render(f"Puntaje: {puntaje}", True, blanco) 
    ventana.blit(textoPuntaje, (10, 10))
    textoVidas = fuente.render(f"Vidas: {vidas}", True, verde)
    ventana.blit(textoVidas, (10, 50))
    pygame.display.flip()
    fps.tick(60)

ventana.fill(negro)
gameOver = fuente.render(f"Puntaje final: {puntaje}", True, rojo)
ventana.blit(gameOver, (ancho/2 - 100 , altura/2))
pygame.display.flip()
pygame.time.wait(3000)
jugando = False

pygame.quit()
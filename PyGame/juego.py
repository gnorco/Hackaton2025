import pygame
import random
import sys
import os # ⭐ Importación esencial para manejo de rutas de archivos

# --- 1. Inicialización de Pygame y Carga de Recursos ---
pygame.init()

# Definición de colores
NEGRO = (0, 0, 0)
BLANCO = (255, 255, 255)
GRIS_OSCURO = (50, 50, 50)
AZUL_CIELO = (135, 206, 235)
ROJO = (255, 0, 0)

# Configuración de la pantalla
ANCHO_PANTALLA = 800
ALTO_PANTALLA = 600
pantalla = pygame.display.set_mode((ANCHO_PANTALLA, ALTO_PANTALLA))
pygame.display.set_caption("EcoCleaner: ¡Tu misión es un aire puro!")


reloj = pygame.time.Clock()
FPS = 30
fuente = pygame.font.Font(None, 36)
fuente_pequena = pygame.font.Font(None, 24)

# ⭐ DEFINICIÓN DE RUTA ABSOLUTA Y CARGA DE IMÁGENES
# Esto resuelve los errores NameError y FileNotFoundError
try:
    # 1. Obtiene la ruta de la carpeta donde se encuentra este script (juego.py)
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__)) 
    
    # 2. Carga las imágenes desde la subcarpeta 'img'
    IMAGEN_SPARKY = pygame.image.load(os.path.join(SCRIPT_DIR, "img", "sparky_robot.png")).convert_alpha() 
    IMAGEN_NUBE_CO = pygame.image.load(os.path.join(SCRIPT_DIR, "img", "nube_sucia.png")).convert_alpha()
    IMAGEN_NUBE_PURA = pygame.image.load(os.path.join(SCRIPT_DIR, "img", "nube_limpia.png")).convert_alpha()

    
except pygame.error as e:
    print(f"Error al cargar la imagen: {e}.")
    print("Asegúrate de que los archivos estén en la carpeta 'img' y los nombres sean correctos.")
    # Fallback: si las imágenes fallan, usamos None para que las clases usen el dibujo simple.
    IMAGEN_SPARKY = None 
    IMAGEN_NUBE_CO = None
    IMAGEN_NUBE_PURA = None
    
# Variable global para el gestor de juego
gestor_juego = None 

# --- 2. Clases del Juego ---

class Sparky(pygame.sprite.Sprite):
    """El personaje principal con la aspiradora."""
    def __init__(self):
        super().__init__()
        
        # Uso de la imagen si está disponible
        if IMAGEN_SPARKY:
            self.image = pygame.transform.scale(IMAGEN_SPARKY, (60, 60))
        else:
            # Dibujo simple (fallback)
            self.image = pygame.Surface([50, 50])
            self.image.fill(BLANCO)
            pygame.draw.circle(self.image, (0, 150, 255), (25, 25), 20)
            
        self.rect = self.image.get_rect()
        self.rect.centerx = ANCHO_PANTALLA // 2
        self.rect.bottom = ALTO_PANTALLA - 10
        self.velocidad_x = 0

    def update(self):
        self.rect.x += self.velocidad_x
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > ANCHO_PANTALLA:
            self.rect.right = ANCHO_PANTALLA

    def mover(self, direccion):
        if direccion == "izquierda":
            self.velocidad_x = -10
        elif direccion == "derecha":
            self.velocidad_x = 10
        elif direccion == "parar":
            self.velocidad_x = 0

class NubeCO(pygame.sprite.Sprite):
    """Representa una nube de Monóxido de Carbono (CO)."""
    def __init__(self):
        super().__init__()
        
        # Uso de la imagen si está disponible
        if IMAGEN_NUBE_CO:
            self.image = pygame.transform.scale(IMAGEN_NUBE_CO, (50, 50))
        else:
            # Dibujo simple (fallback)
            self.image = pygame.Surface([40, 40])
            self.image.fill(NEGRO) 
            pygame.draw.circle(self.image, (50, 50, 50), (20, 20), 20)
            self.image.set_colorkey(NEGRO) 
            
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(ANCHO_PANTALLA - self.rect.width)
        self.rect.y = random.randrange(-100, -40)
        
        # Velocidad de caída reducida (para menos CO)
        self.velocidad_y = random.randrange(1, 3) 

    def update(self):
        self.rect.y += self.velocidad_y
        
        # ⭐ Lógica de pérdida de vida y reseteo
        if self.rect.top > ALTO_PANTALLA:
            global gestor_juego
            if gestor_juego:
                gestor_juego.vidas -= 1
                gestor_juego.nivel_co += 1 # Sube CO por fallar

            # Reseteo de la nube
            self.rect.x = random.randrange(ANCHO_PANTALLA - self.rect.width)
            self.rect.y = random.randrange(-100, -40)
            self.velocidad_y = random.randrange(1, 3) 


class NubePura(pygame.sprite.Sprite):
    """Representa una nube de aire purificado (blanca)."""
    def __init__(self, posicion_x, posicion_y):
        super().__init__()

        # Uso de la imagen si está disponible
        if IMAGEN_NUBE_PURA:
            self.image = pygame.transform.scale(IMAGEN_NUBE_PURA, (60, 60))
        else:
            # Dibujo simple (fallback)
            self.image = pygame.Surface([50, 50])
            self.image.fill(NEGRO)
            pygame.draw.circle(self.image, BLANCO, (25, 25), 20)
            self.image.set_colorkey(NEGRO)
        
        self.rect = self.image.get_rect()
        self.rect.centerx = posicion_x
        self.rect.centery = posicion_y
        self.tiempo_vida = 60

    def update(self):
        self.rect.y -= 2
        self.tiempo_vida -= 1
        if self.tiempo_vida <= 0:
            self.kill()

class GestorJuego:
    """Clase para manejar el estado del juego, puntuación y CO."""
    def __init__(self):
        self.puntuacion = 0
        self.nivel_co = 0
        self.max_co = 100
        self.vidas = 3 # Inicialización de vidas
        self.juego_terminado = False
        self.mensaje_alerta = ""
        self.tiempo_mensaje = 0

    def mostrar_alerta(self, mensaje):
        self.mensaje_alerta = mensaje
        self.tiempo_mensaje = 180

    def dibujar_interfaz(self, pantalla):
        # Puntuación
        texto_puntuacion = fuente.render(f"Puntos: {self.puntuacion}", True, NEGRO)
        pantalla.blit(texto_puntuacion, [10, 10])

        # Vidas
        texto_vidas = fuente.render(f"Vidas: {self.vidas}", True, ROJO)
        pantalla.blit(texto_vidas, [10, 40])

        # Medidor de CO (Barra de progreso)
        pygame.draw.rect(pantalla, NEGRO, [ANCHO_PANTALLA - 210, 10, 200, 30], 2)
        ancho_co = (self.nivel_co / self.max_co) * 200
        
        color_co = (0, 200, 0)
        if self.nivel_co > 50:
            color_co = (255, 255, 0)
        if self.nivel_co > 80:
            color_co = (255, 0, 0)

        pygame.draw.rect(pantalla, color_co, [ANCHO_PANTALLA - 210, 10, ancho_co, 30])
        
        texto_co = fuente_pequena.render(f"Nivel CO: {self.nivel_co}%", True, NEGRO)
        pantalla.blit(texto_co, [ANCHO_PANTALLA - 190, 15])
        
        # Mensaje de Alerta
        if self.tiempo_mensaje > 0:
            texto_alerta = fuente.render(self.mensaje_alerta, True, (255, 50, 50))
            rect_alerta = texto_alerta.get_rect(center=(ANCHO_PANTALLA // 2, 50))
            pygame.draw.rect(pantalla, BLANCO, rect_alerta.inflate(20, 10))
            pantalla.blit(texto_alerta, rect_alerta)
            self.tiempo_mensaje -= 1

# --- 3. Grupos de Sprites y Configuración Inicial ---
gestor_juego = GestorJuego()
todos_los_sprites = pygame.sprite.Group()
nubes_co = pygame.sprite.Group()
nubes_puras = pygame.sprite.Group()

sparky = Sparky()
todos_los_sprites.add(sparky)

# Crear nubes iniciales (reducido a 10)
for i in range(10): 
    nube = NubeCO()
    todos_los_sprites.add(nube)
    nubes_co.add(nube)

# --- 4. Bucle Principal del Juego ---
jugando = True
while jugando:
    # Manejo de eventos
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            jugando = False
        
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_LEFT:
                sparky.mover("izquierda")
            if evento.key == pygame.K_RIGHT:
                sparky.mover("derecha")
        
        if evento.type == pygame.KEYUP:
            if evento.key == pygame.K_LEFT and sparky.velocidad_x < 0:
                sparky.mover("parar")
            if evento.key == pygame.K_RIGHT and sparky.velocidad_x > 0:
                sparky.mover("parar")

    if gestor_juego.juego_terminado:
        for evento in pygame.event.get(): 
            if evento.type == pygame.QUIT or evento.type == pygame.KEYDOWN:
                jugando = False
        
    if not gestor_juego.juego_terminado:

        # 5. Lógica de Actualización
        todos_los_sprites.update()
        
        # 6. Colisiones (Sparky absorbe CO)
        nubes_golpeadas = pygame.sprite.spritecollide(sparky, nubes_co, True)
        
        for nube_golpeada in nubes_golpeadas:
            gestor_juego.puntuacion += 10
            gestor_juego.nivel_co = max(0, gestor_juego.nivel_co - 5)
            
            nube_pura = NubePura(nube_golpeada.rect.centerx, nube_golpeada.rect.centery)
            todos_los_sprites.add(nube_pura)
            nubes_puras.add(nube_pura)
            
            mensajes = [
                "¡Aire Puro! Recuerda ventilar los ambientes.",
                "¡CO absorbido! El CO es inodoro e invisible.",
                "¡Muy bien! Un detector de CO salva vidas."
            ]
            if random.random() < 0.2:
                gestor_juego.mostrar_alerta(random.choice(mensajes))
            
            # ⭐ Reaparición: Solo reaparece el 60% de las veces (para menos CO)
            if random.random() < 0.6: 
                nube = NubeCO()
                todos_los_sprites.add(nube)
                nubes_co.add(nube)
            
        # 7. Control de Fin del Juego
        if gestor_juego.vidas <= 0:
             gestor_juego.juego_terminado = True
             gestor_juego.mostrar_alerta("¡Te has quedado sin vidas! Juego Terminado.")

        if gestor_juego.nivel_co >= gestor_juego.max_co and not gestor_juego.juego_terminado:
            gestor_juego.juego_terminado = True
            gestor_juego.mostrar_alerta("¡Nivel de CO Crítico! Juego Terminado.")
            
        if gestor_juego.juego_terminado:
             for nube in nubes_co:
                nube.velocidad_y = 0


        # 8. Dibujado / Renderizado
        pantalla.fill(AZUL_CIELO)
        todos_los_sprites.draw(pantalla)
        gestor_juego.dibujar_interfaz(pantalla)
    
    # Pantalla de Juego Terminado (se dibuja si gestor_juego.juego_terminado es True)
    if gestor_juego.juego_terminado:
        texto_final = fuente.render("JUEGO TERMINADO", True, NEGRO)
        rect_final = texto_final.get_rect(center=(ANCHO_PANTALLA // 2, ALTO_PANTALLA // 2 - 50))
        pantalla.blit(texto_final, rect_final)
        
        texto_puntos = fuente.render(f"Puntuación Final: {gestor_juego.puntuacion}", True, NEGRO)
        rect_puntos = texto_puntos.get_rect(center=(ANCHO_PANTALLA // 2, ALTO_PANTALLA // 2))
        pantalla.blit(texto_puntos, rect_puntos)


    # Actualizar la pantalla
    pygame.display.flip()

    # Control de la velocidad
    reloj.tick(FPS)

# --- 9. Salida del Juego ---
pygame.quit()
sys.exit()
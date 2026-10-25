"""
Simulación del Juego Clásico Yahtzee (2 Jugadores) mediante el Método de Montecarlo.
Materia: Simulación - Ingeniería de Software y Datos.
Distribución de probabilidad base: Uniforme Discreta U{1, 6}.
"""

import random
import statistics
from collections import Counter
from typing import List, Dict, Optional, Tuple


class DadoUniforme:
    """
    Representa un dado convencional de 6 caras gobernado por una
    distribución de probabilidad uniforme discreta P(X = x) = 1/6.
    """
    @staticmethod
    def lanzar(cantidad: int = 5) -> List[int]:
        # Uso de generador uniforme continuo U(0,1) transformado a discreto {1..6}
        return [int(random.random() * 6) + 1 for _ in range(cantidad)]


class EvaluadorYahtzee:
    """
    Evalúa los vectores de 5 dados y calcula el puntaje correspondiente
    para cada una de las 13 categorías del juego Yahtzee clásico.
    """
    CATEGORIAS_SUPERIORES = ["Unos", "Doses", "Treses", "Cuatros", "Cincos", "Seises"]
    CATEGORIAS_INFERIORES = [
        "Tres Iguales", "Cuatro Iguales", "Full House",
        "Escalera Pequeña", "Escalera Grande", "Yahtzee", "Chance"
    ]
    TODAS_LAS_CATEGORIAS = CATEGORIAS_SUPERIORES + CATEGORIAS_INFERIORES

    @staticmethod
    def calcular_puntaje(dados: List[int], categoria: str) -> int:
        conteo = Counter(dados)
        suma_total = sum(dados)
        valores_unicos = set(dados)

        # Sección Superior
        mapa_superior = {
            "Unos": 1, "Doses": 2, "Treses": 3,
            "Cuatros": 4, "Cincos": 5, "Seises": 6
        }
        if categoria in mapa_superior:
            cara = mapa_superior[categoria]
            return conteo[cara] * cara

        # Sección Inferior
        frecuencias = sorted(conteo.values(), reverse=True)

        if categoria == "Tres Iguales":
            return suma_total if frecuencias[0] >= 3 else 0
        elif categoria == "Cuatro Iguales":
            return suma_total if frecuencias[0] >= 4 else 0
        elif categoria == "Full House":
            return 25 if (frecuencias == [3, 2] or frecuencias == [5]) else 0
        elif categoria == "Escalera Pequeña":
            escaleras_peq = [{1, 2, 3, 4}, {2, 3, 4, 5}, {3, 4, 5, 6}]
            return 30 if any(esc.issubset(valores_unicos) for esc in escaleras_peq) else 0
        elif categoria == "Escalera Grande":
            return 40 if valores_unicos in [{1, 2, 3, 4, 5}, {2, 3, 4, 5, 6}] else 0
        elif categoria == "Yahtzee":
            return 50 if frecuencias[0] == 5 else 0
        elif categoria == "Chance":
            return suma_total

        return 0


class Jugador:
    """
    Estructura de datos que gestiona la tarjeta de puntuación (Scorecard)
    y la política de decisiones (transición de estados entre lanzamientos) de un jugador.
    """
    def __init__(self, nombre: str):
        self.nombre = nombre
        # Diccionario para gestionar las 13 categorías (None = disponible)
        self.tarjeta: Dict[str, Optional[int]] = {
            cat: None for cat in EvaluadorYahtzee.TODAS_LAS_CATEGORIAS
        }

    def categorias_disponibles(self) -> List[str]:
        return [cat for cat, pts in self.tarjeta.items() if pts is None]

    def decidir_retencion(self, dados: List[int]) -> List[int]:
        """
        Política heurística (Modelo de transición de estados):
        Determina qué dados conservar entre lanzamientos para maximizar
        la probabilidad de alcanzar estados de mayor puntuación.
        """
        conteo = Counter(dados)
        valores_unicos = sorted(list(set(dados)))

        # Si ya tiene Yahtzee, Escalera Grande o Full House, conserva todos los dados
        if len(conteo) == 1:
            return dados
        if set(dados) in [{1, 2, 3, 4, 5}, {2, 3, 4, 5, 6}]:
            return dados
        if sorted(conteo.values()) == [2, 3] and self.tarjeta["Full House"] is None:
            return dados

        # Verificar si está a un dado de una Escalera Grande y aún está disponible
        if self.tarjeta["Escalera Grande"] is None or self.tarjeta["Escalera Pequeña"] is None:
            for esc in [{1, 2, 3, 4}, {2, 3, 4, 5}, {3, 4, 5, 6}]:
                if esc.issubset(set(dados)):
                    return list(esc)

        # Por defecto: conservar el valor o valores con mayor frecuencia (buscar iguales)
        cara_mas_frecuente, freq_max = conteo.most_common(1)[0]
        if freq_max >= 2:
            return [d for d in dados if d == cara_mas_frecuente]

        # Si todos son distintos, conservar el dado de mayor valor nominal
        return [max(dados)]

    def jugar_turno(self, mostrar_traza: bool = False) -> Tuple[str, int, List[int]]:
        """
        Simula hasta 3 lanzamientos de 5 dados en un turno y registra el puntaje óptimo.
        """
        dados_actuales = DadoUniforme.lanzar(5)
        if mostrar_traza:
            print(f"    Lanzamiento 1: {dados_actuales}")

        # Lanzamientos 2 y 3
        for num_tiro in range(2, 4):
            retenidos = self.decidir_retencion(dados_actuales)
            if len(retenidos) == 5:
                break  # Se plantó antes de agotar los 3 tiros
            nuevos = DadoUniforme.lanzar(5 - len(retenidos))
            dados_actuales = retenidos + nuevos
            if mostrar_traza:
                print(f"    Lanzamiento {num_tiro} (Retuvo {retenidos}): {dados_actuales}")

        # Selección de la mejor categoría disponible
        mejor_cat = None
        mejor_puntaje = -1

        for cat in self.categorias_disponibles():
            pts = EvaluadorYahtzee.calcular_puntaje(dados_actuales, cat)
            # Pequeño peso heurístico para no malgastar Yahtzee en 0 puntos si hay otra opción
            peso = pts
            if cat == "Yahtzee" and pts == 0 and len(self.categorias_disponibles()) > 1:
                peso = -0.5

            if peso > mejor_puntaje:
                mejor_puntaje = pts
                mejor_cat = cat

        # En caso de que solo quede Yahtzee con 0 puntos
        if mejor_cat is None:
            mejor_cat = self.categorias_disponibles()[0]
            mejor_puntaje = EvaluadorYahtzee.calcular_puntaje(dados_actuales, mejor_cat)

        self.tarjeta[mejor_cat] = mejor_puntaje
        return mejor_cat, mejor_puntaje, dados_actuales

    def puntaje_seccion_superior(self) -> int:
        return sum(self.tarjeta[cat] or 0 for cat in EvaluadorYahtzee.CATEGORIAS_SUPERIORES)

    def bono_superior(self) -> int:
        return 35 if self.puntaje_seccion_superior() >= 63 else 0

    def puntaje_seccion_inferior(self) -> int:
        return sum(self.tarjeta[cat] or 0 for cat in EvaluadorYahtzee.CATEGORIAS_INFERIORES)

    def puntaje_total(self) -> int:
        return self.puntaje_seccion_superior() + self.bono_superior() + self.puntaje_seccion_inferior()


def simular_partida(mostrar_detalle: bool = False) -> Tuple[Jugador, Jugador]:
    """Ejecuta una partida completa de Yahtzee (13 rondas) entre 2 jugadores."""
    j1 = Jugador("Jugador 1")
    j2 = Jugador("Jugador 2")

    if mostrar_detalle:
        print("=" * 75)
        print("SIMULACIÓN DE PARTIDA DETALLADA DE YAHTZEE (2 JUGADORES)")
        print("=" * 75)

    for ronda in range(1, 14):
        if mostrar_detalle:
            print(f"\n--- RONDA {ronda} ---")
        for jugador in (j1, j2):
            if mostrar_detalle:
                print(f"  Turno de {jugador.nombre}:")
            cat, pts, dados_finales = jugador.jugar_turno(mostrar_traza=mostrar_detalle)
            if mostrar_detalle:
                print(f"  -> Asigna '{cat}' con {pts} puntos (Dados finales: {dados_finales})")

    if mostrar_detalle:
        imprimir_resumen_partida(j1, j2)

    return j1, j2


def imprimir_resumen_partida(j1: Jugador, j2: Jugador) -> None:
    print("\n" + "=" * 75)
    print(f"{'CATEGORÍA':<25} | {j1.nombre:^20} | {j2.nombre:^20}")
    print("-" * 75)
    for cat in EvaluadorYahtzee.TODAS_LAS_CATEGORIAS:
        print(f"{cat:<25} | {j1.tarjeta[cat]:^20} | {j2.tarjeta[cat]:^20}")
    print("-" * 75)
    print(f"{'Subtotal Superior':<25} | {j1.puntaje_seccion_superior():^20} | {j2.puntaje_seccion_superior():^20}")
    print(f"{'Bono Superior (>=63)':<25} | {j1.bono_superior():^20} | {j2.bono_superior():^20}")
    print(f"{'Subtotal Inferior':<25} | {j1.puntaje_seccion_inferior():^20} | {j2.puntaje_seccion_inferior():^20}")
    print("=" * 75)
    print(f"{'PUNTAJE TOTAL FINAL':<25} | {j1.puntaje_total():^20} | {j2.puntaje_total():^20}")
    print("=" * 75)

    if j1.puntaje_total() > j2.puntaje_total():
        print(f"GANADOR DE LA PARTIDA: {j1.nombre} ({j1.puntaje_total()} vs {j2.puntaje_total()})")
    elif j2.puntaje_total() > j1.puntaje_total():
        print(f"GANADOR DE LA PARTIDA: {j2.nombre} ({j2.puntaje_total()} vs {j1.puntaje_total()})")
    else:
        print(f"RESULTADO: Empate técnico a {j1.puntaje_total()} puntos.")


def experimento_montecarlo(num_partidas: int = 5000) -> None:
    """
    Explotación de resultados mediante el Método de Montecarlo.
    Ejecuta N partidas para estimar probabilidades, medias y convergencia.
    """
    print("\n" + "#" * 75)
    print(f"EJECUTANDO EXPERIMENTO DE MONTECARLO ({num_partidas} PARTIDAS SIMULADAS)...")
    print("#" * 75)

    puntajes_totales = []
    victorias_j1 = 0
    victorias_j2 = 0
    empates = 0
    yahtzees_logrados = 0
    bonos_logrados = 0

    for _ in range(num_partidas):
        j1, j2 = simular_partida(mostrar_detalle=False)
        pts1, pts2 = j1.puntaje_total(), j2.puntaje_total()
        puntajes_totales.extend([pts1, pts2])

        if pts1 > pts2:
            victorias_j1 += 1
        elif pts2 > pts1:
            victorias_j2 += 1
        else:
            empates += 1

        for j in (j1, j2):
            if j.tarjeta["Yahtzee"] == 50:
                yahtzees_logrados += 1
            if j.bono_superior() == 35:
                bonos_logrados += 1

    total_jugadores_evaluados = num_partidas * 2
    media = statistics.mean(puntajes_totales)
    desviacion = statistics.stdev(puntajes_totales)

    print(f"\nRESULTADOS ESTADÍSTICOS DE MONTECARLO (Muestra = {total_jugadores_evaluados} tarjetas):")
    print(f"  * Puntaje Promedio Esperado (Media):   {media:.2f} pts")
    print(f"  * Desviación Estándar:                 {desviacion:.2f} pts")
    print(f"  * Puntaje Mínimo / Máximo registrado:  {min(puntajes_totales)} pts / {max(puntajes_totales)} pts")
    print(f"  * Tasa de Victoria Jugador 1:          {(victorias_j1 / num_partidas) * 100:.2f}%")
    print(f"  * Tasa de Victoria Jugador 2:          {(victorias_j2 / num_partidas) * 100:.2f}%")
    print(f"  * Tasa de Empates:                     {(empates / num_partidas) * 100:.2f}%")
    print(f"  * Probabilidad de lograr Yahtzee:      {(yahtzees_logrados / total_jugadores_evaluados) * 100:.2f}%")
    print(f"  * Probabilidad de Bono Superior:       {(bonos_logrados / total_jugadores_evaluados) * 100:.2f}%")
    print("#" * 75)


if __name__ == "__main__":
    # Semilla opcional para reproducibilidad de pruebas (descomentar si se desea fijar)
    # random.seed(42)

    # 1. Simular una partida interactiva/detallada entre 2 jugadores
    simular_partida(mostrar_detalle=True)

    # 2. Explotación estadística de Montecarlo con 5,000 partidas
    experimento_montecarlo(num_partidas=5000)
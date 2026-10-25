# 🎲 Simulación de Yahtzee Clásico mediante el Método de Montecarlo

Repositorio correspondiente a la **Actividad Didáctica 2 - Módulo 1** de la asignatura **Simulación** (Ingeniería de Software y Datos).

## 🎯 Objetivo del Proyecto
Comprender y aplicar el **Método de Montecarlo** y las **Cadenas de Markov** en una aplicación computacional que simula el juego clásico de Yahtzee para 2 jugadores bajo una distribución de probabilidad uniforme discreta, permitiendo la explotación estadística de los resultados aleatorios obtenidos.

## 🧮 Fundamento Matemático
1. **Distribución Uniforme Discreta:** Cada cara de los 5 dados se modela como una variable aleatoria independiente $X \sim U\{1, 6\}$ con probabilidad $P(X=x) = \frac{1}{6}$.

2. **Transición de Estados (Modelo de Markov):** Cada turno consta de hasta 3 lanzamientos. La transición entre el lanzamiento $t$ y $t+1$ depende exclusivamente del vector de dados actual y de la política de retención aplicada por el jugador.

3. **Simulación de Montecarlo:** Ejecución de $N$ miles de partidas completas para estimar por la Ley de los Grandes Números el puntaje medio esperado, varianza y probabilidades empíricas de jugadas complejas.

## 🛠️ Estructuras de Datos Utilizadas
* `list`: Vectores dinámicos para almacenar el estado de los 5 dados en cada tiro.

* `dict`: Tablas hash para gestionar la tarjeta de puntuación (*Scorecard*) de 13 categorías por jugador.

* `collections.Counter`: Árboles/mapas de frecuencias para evaluar combinaciones en tiempo $O(n)$.

## 🚀 Requisitos y Ejecución
El proyecto está desarrollado en **Python 3.8+** utilizando únicamente librerías estándar (`random`, `statistics`, `collections`, `typing`).

Para ejecutar la simulación detallada de 1 partida (2 jugadores) seguida del experimento de Montecarlo:

```bash
git clone https://github.com/wtrianav/simulacion-yahtzee-montecarlo.git
cd simulacion-yahtzee-montecarlo
python src/yahtzee_montecarlo.py
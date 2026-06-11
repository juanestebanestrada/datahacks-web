import numpy as np
import pandas as pd
from scipy.stats import poisson


class ExpectedPointsSimulator:
    def __init__(self, simulations=10000, max_goals=10):
        """
        Calculadora de Expectativa de Puntos usando Distribución de Poisson Bivariada.
        El método analítico (np.outer) es determinista y equivalente a Monte Carlo
        con un número infinito de simulaciones.
        """
        self.simulations = simulations
        self.max_goals = max_goals

    def calculate_match_probabilities(self, home_xg, away_xg):
        """
        Genera la matriz bivariada de Poisson para calcular
        Victoria Local, Empate y Victoria Visitante.
        """
        home_poisson = [poisson.pmf(i, home_xg) for i in range(self.max_goals)]
        away_poisson = [poisson.pmf(i, away_xg) for i in range(self.max_goals)]

        # Producto exterior → matriz de probabilidad cruzada O(max_goals²)
        # match_matrix[i, j] = P(Local=i goles) × P(Visitante=j goles)
        match_matrix = np.outer(home_poisson, away_poisson)

        home_win_prob = np.sum(np.tril(match_matrix, -1))
        draw_prob     = np.sum(np.diag(match_matrix))
        away_win_prob = np.sum(np.triu(match_matrix, 1))

        # Normalizar para compensar la cola derecha (goles > max_goals)
        total_prob     = home_win_prob + draw_prob + away_win_prob
        home_win_prob /= total_prob
        draw_prob     /= total_prob
        away_win_prob /= total_prob

        return {
            'Home_Win': round(home_win_prob, 4),
            'Draw':     round(draw_prob, 4),
            'Away_Win': round(away_win_prob, 4)
        }

    def compute_xpts(self, home_xg, away_xg):
        """Calcula los xPts de cada equipo según las probabilidades de Poisson."""
        probs = self.calculate_match_probabilities(home_xg, away_xg)
        home_xpts = (probs['Home_Win'] * 3) + (probs['Draw'] * 1)
        away_xpts = (probs['Away_Win'] * 3) + (probs['Draw'] * 1)
        return {
            'Home_xPts': round(home_xpts, 2),
            'Away_xPts': round(away_xpts, 2),
            'Win_Probabilities': probs
        }

    def monte_carlo_xpts(self, home_xg, away_xg):
        """
        FASE 6: Validación estocástica de la solución analítica.
        Simula N partidos con muestras de Poisson aleatorias.
        La convergencia entre este método y compute_xpts valida el modelo.
        """
        rng = np.random.default_rng(42)  # Reproducible
        home_goals = rng.poisson(home_xg, self.simulations)
        away_goals = rng.poisson(away_xg, self.simulations)
        home_wins  = np.sum(home_goals > away_goals) / self.simulations
        draws      = np.sum(home_goals == away_goals) / self.simulations
        away_wins  = np.sum(away_goals > home_goals) / self.simulations
        return {
            'MC_Home_Win': round(home_wins, 4),
            'MC_Draw':     round(draws, 4),
            'MC_Away_Win': round(away_wins, 4)
        }

    def generate_justice_table(self, match_data_df):
        """
        Acepta DataFrame con ['Team_Home', 'Team_Away', 'xG_Home', 'xG_Away'].
        Retorna la 'Tabla de Justicia Matemática' con xPts acumulados.
        """
        teams = set(match_data_df['Team_Home']).union(set(match_data_df['Team_Away']))
        table = {team: 0.0 for team in teams}

        for _, row in match_data_df.iterrows():
            res = self.compute_xpts(row['xG_Home'], row['xG_Away'])
            table[row['Team_Home']] += res['Home_xPts']
            table[row['Team_Away']] += res['Away_xPts']

        justice_df = pd.DataFrame(list(table.items()), columns=['Team', 'Expected_Points'])
        return justice_df.sort_values(by='Expected_Points', ascending=False).reset_index(drop=True)


if __name__ == "__main__":
    sim = ExpectedPointsSimulator()
    print("Test: Portugal (2.4 xG) vs Colombia (1.2 xG)")
    analytic = sim.compute_xpts(2.4, 1.2)
    mc       = sim.monte_carlo_xpts(2.4, 1.2)
    print(f"Analítico: {analytic['Win_Probabilities']}")
    print(f"Monte Carlo: {mc}")
    diff = abs(mc['MC_Home_Win'] - analytic['Win_Probabilities']['Home_Win'])
    print(f"Convergencia Δ: {diff:.4f} ({'✅ OK' if diff < 0.01 else '⚠️ Revisar'})")

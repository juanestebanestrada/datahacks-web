import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.metrics.pairwise import cosine_similarity


class ScoutingGenerativeSimilarity:
    """
    Motor comparativo de perfiles usando métricas base p90.
    Usa similitud coseno vectorizada (sklearn) en lugar de loop O(n).
    Escalado estándar Z-Score para normalizar unidades dispares.
    Optimizado para datasets de +1000 jugadores.
    """

    def __init__(self, stats_df: pd.DataFrame):
        if 'player_name' not in stats_df.columns:
            raise ValueError("El dataset debe contener la columna 'player_name'.")

        self.raw_df      = stats_df.dropna()
        self.players     = self.raw_df['player_name'].values
        self.features_df = self.raw_df.drop(columns=['player_name']).select_dtypes(include=[np.number])

        # Z-Score: normaliza escala para que 'Goles' no domine sobre 'Toques de balón'
        self.scaler   = StandardScaler()
        self.z_matrix = self.scaler.fit_transform(self.features_df)

        # Matriz de similitud precalculada (O(n²) una sola vez en __init__)
        self._sim_matrix = cosine_similarity(self.z_matrix)

    def find_most_similar(self, target_player_name: str, top_n: int = 3):
        """
        Calcula similitud coseno en una sola operación matricial (vectorizado).
        O(1) por llamada tras la precalculación en __init__.
        """
        if target_player_name not in self.players:
            return {"error": f"Jugador '{target_player_name}' no encontrado."}

        target_idx = np.where(self.players == target_player_name)[0][0]
        sims = self._sim_matrix[target_idx].copy()
        sims[target_idx] = -1  # Excluir al propio jugador

        top_indices = np.argsort(sims)[::-1][:top_n]
        top_matches = [(self.players[i], round(sims[i] * 100, 2)) for i in top_indices]

        return self._format_ai_prompt(target_player_name, top_matches)

    def get_similarity_scores(self, target_player_name: str) -> pd.DataFrame:
        """
        Retorna un DataFrame ordenado de todos los jugadores por similitud.
        Útil para visualizaciones externas o exportación a NotebookLM.
        """
        if target_player_name not in self.players:
            return pd.DataFrame()

        target_idx = np.where(self.players == target_player_name)[0][0]
        sims = self._sim_matrix[target_idx].copy()
        df = pd.DataFrame({
            'player': self.players,
            'similarity_pct': np.round(sims * 100, 2)
        })
        df = df[df['player'] != target_player_name]
        return df.sort_values('similarity_pct', ascending=False).reset_index(drop=True)

    def _format_ai_prompt(self, target: str, matches: list) -> str:
        """Formatea resultado para el Registro de Prompting de NotebookLM."""
        prompt  = "Analiza esta similitud detectada por el modelo algorítmico:\n"
        prompt += f"El radar de scouting indica que {target} tiene un perfil matemáticamente similar a:\n"
        for rank, (player, score) in enumerate(matches, 1):
            prompt += f"{rank}. {player} (Similitud Coseno: {score}%)\n"
        prompt += "\nNotebookLM: genera un informe táctico argumentando en qué aspectos en cancha se parecen estos perfiles."
        return prompt


if __name__ == "__main__":
    mock_data = pd.DataFrame({
        'player_name':    ['James Rodriguez', 'Bruno Fernandes', 'Abbosbek', 'Joao Felix', 'Defensa Z'],
        'xA_p90':         [0.4, 0.42, 0.1, 0.38, 0.01],
        'key_passes_p90': [3.1, 3.2, 0.5, 2.9, 0.1],
        'tackles_p90':    [0.5, 0.8, 3.0, 0.7, 4.5]
    })
    scout = ScoutingGenerativeSimilarity(mock_data)
    print(scout.find_most_similar('James Rodriguez', top_n=2))
    print(scout.get_similarity_scores('James Rodriguez'))

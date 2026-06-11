import pandas as pd
import numpy as np

class TacticalExpectedThreat:
    """
    Motor Táctico de Expected Threat (xT) y posesiones progresivas (xGChain).
    Basado en los frameworks analíticos introducidos por estudios avanzados de Footbal Analytics.
    """
    def __init__(self, pitch_length=120, pitch_width=80, cell_x=12, cell_y=8):
        # Grilla para mapear coords al algoritmo de Markov
        self.pitch_length = pitch_length
        self.pitch_width = pitch_width
        self.cell_x = cell_x
        self.cell_y = cell_y
        
        # Array simulado de Probabilidad de Tiro + Probabilidad de Moverse a celda i, j
        # En producción esto se extrae del baseline de las 5 grandes ligas (K. Singh o S. Karunakar).
        self.xt_grid = np.random.uniform(0.001, 0.25, (self.cell_y, self.cell_x))
        # Ajustamos artificialmente la grilla: Mayor xT cerca de la portería rival (derecha, en SB)
        self.xt_grid[:, int(self.cell_x/2):] *= 2.5 

    def _get_cell_indexes(self, x, y):
        """Conversor de Coordenadas continuas a Celdas Discretas de la Grilla xT"""
        x_idx = int(np.clip(x / (self.pitch_length / self.cell_x), 0, self.cell_x - 1))
        y_idx = int(np.clip(y / (self.pitch_width / self.cell_y), 0, self.cell_y - 1))
        return x_idx, y_idx

    def calculate_xt_added(self, start_x, start_y, end_x, end_y):
        """
        Diferencial de xT: Cuánto peligro añadió la acción de pase o conducción.
        (xT Celda Final - xT Celda Inicial)
        """
        sx, sy = self._get_cell_indexes(start_x, start_y)
        ex, ey = self._get_cell_indexes(end_x, end_y)
        
        xt_start = self.xt_grid[sy, sx]
        xt_end = self.xt_grid[ey, ex]
        
        xt_added = xt_end - xt_start
        # Si retrocede, el xT es negativo (se pierde peligro posicional).
        return xt_added

    def process_match_xt(self, events_df):
        """
        Ingiere un DataFrame puro de StatsBomb o similar y calcula el Threat
        generado por cada jugador.
        """
        # Filtrar solo Pases y Conducciones (Carries) con éxito
        actions = events_df[
            (events_df['type'].isin(['Pass', 'Carry'])) & 
            (events_df['outcome'].isnull() | (events_df['outcome'] == 'Complete'))
        ].copy()
        
        xt_values = []
        for _, row in actions.iterrows():
            loc = row.get('location', [0, 0])
            end_loc = row.get('pass_end_location') if row['type'] == 'Pass' else row.get('carry_end_location')
            
            if type(loc) == list and type(end_loc) == list:
                xt_add = self.calculate_xt_added(loc[0], loc[1], end_loc[0], end_loc[1])
                xt_values.append(xt_add)
            else:
                xt_values.append(0.0)
                
        actions['xT_Added'] = xt_values
        
        # Agrupar por jugador para descubrir al "Top Threat Creator"
        threat_creators = actions.groupby('player_name')['xT_Added'].sum().reset_index()
        return threat_creators.sort_values(by='xT_Added', ascending=False)

if __name__ == "__main__":
    extractor = TacticalExpectedThreat()
    # Demo Mocks de Coordenadas SB
    print("xT Añadido Pase cruzado: ", extractor.calculate_xt_added(40, 20, 105, 45))

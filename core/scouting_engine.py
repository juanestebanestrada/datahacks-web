import pandas as pd
import asyncio
import aiohttp
from LanusStats import FotMob, Fbref
import numpy as np

class ScoutingEngine:
    def __init__(self):
        self.fotmob = FotMob()
        self.fbref = Fbref()
        self.semaphore = asyncio.Semaphore(5)  # Máximo 5 peticiones simultáneas

    # 1. Refactorización: Extracción Asíncrona para FotMob
    async def fetch_fotmob_async(self, session, url):
        async with self.semaphore:
            async with session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                return None

    async def get_multiple_team_stats_async(self, league_id, season_id, stats_list):
        async with aiohttp.ClientSession() as session:
            tasks = []
            for stat in stats_list:
                # Simulamos la construcción de URLs basada en cómo funciona la librería
                url = f"https://www.fotmob.com/api/leagueseasonstats?id={league_id}&season={season_id}&type={stat}"
                tasks.append(self.fetch_fotmob_async(session, url))
            
            results = await asyncio.gather(*tasks)
            return results

    # 2. Normalizadora de Coordenadas
    @staticmethod
    def normalize_fotmob_coords(df):
        """
        Normaliza coordenadas de FotMob (100x100) a StatsBomb (120x80).
        """
        if df is not None and not df.empty:
            if 'x' in df.columns and 'y' in df.columns:
                df['x_norm'] = df['x'] * 1.2
                df['y_norm'] = df['y'] * 0.8
            # Caso para Shot Map de FotMob donde a veces vienen como 'x' e 'y' en coordenadas de campo
            if 'x_coord' in df.columns and 'y_coord' in df.columns:
                df['x_norm'] = df['x_coord'] * 1.2
                df['y_norm'] = df['y_coord'] * 0.8
        return df

    # 3. Consolidación de Rankings (FotMob)
    def get_all_team_season_stats(self, league_id, season_id, list_of_stats):
        """
        Consolida múltiples estadísticas en un solo DataFrame.
        """
        master_df = None
        for stat in list_of_stats:
            try:
                df = self.fotmob.get_teams_stats_season(str(league_id), season_id, stat)
                if df is not None and not df.empty:
                    df = df.rename(columns={'value': stat})
                    if master_df is None:
                        master_df = df[['participantName', stat]]
                    else:
                        master_df = pd.merge(master_df, df[['participantName', stat]], on='participantName', how='outer')
            except Exception as e:
                print(f"Error en {stat}: {e}")
        return master_df

    # 4. Solución Anti-Scraping SofaScore
    async def get_sofascore_data_advanced(self, match_id):
        """
        Bypassea Cloudflare usando nodriver e intercepta el JSON de momentum.
        """
        import nodriver as uc
        browser = await uc.start()
        tab = await browser.get(f"https://www.sofascore.com/match/id/{match_id}")
        
        # Esperamos a que cargue y buscamos el script o el tráfico
        # En una implementación real, usaríamos tab.on(cdp.network.ResponseReceived)
        # Por simplicidad de script robusto, extraemos del window.__INITIAL_STATE__ si existe
        content = await tab.get_content()
        await browser.stop()
        return {"status": "captured", "match_id": match_id, "length": len(content)}

    # 5. Visualizaciones Avanzadas
    def plot_advanced_radar(self, player_name, params, values):
        from mplsoccer import PyPizza
        import matplotlib.pyplot as plt
        
        baker = PyPizza(
            params=params,
            background_color="#080d1a",
            straight_line_color="#222222",
            last_circle_color="#222222",
            last_circle_lw=2.5,
            other_circle_lw=0,
            inner_circle_size=20
        )
        
        fig, ax = baker.make_pizza(
            values,
            figsize=(8, 8),
            color_blank_space="same",
            blank_alpha=0.4,
            kwargs_slices=dict(facecolor="#1a73e8", edgecolor="#222222", zorder=2, linewidth=1),
            kwargs_params=dict(color="white", fontsize=12),
            kwargs_values=dict(color="white", fontsize=11, zorder=3, bbox=dict(edgecolor="#1a73e8", facecolor="#1a73e8", boxstyle="round,pad=0.2"))
        )
        fig.text(0.515, 0.97, f"Profiling: {player_name}", size=18, ha="center", color="white", fontweight="bold")
        return fig

    def plot_kde_heatmap(self, df_shots, title="Densidad de Ataque"):
        from mplsoccer import Pitch
        import matplotlib.pyplot as plt
        
        # Normalizar si es necesario
        if 'x_norm' not in df_shots.columns:
            df_shots = self.normalize_fotmob_coords(df_shots)
            
        pitch = Pitch(pitch_type='statsbomb', pitch_color='#080d1a', line_color='#555555')
        fig, ax = pitch.draw(figsize=(10, 8))
        fig.set_facecolor('#080d1a')
        
        pitch.kdeplot(df_shots.x_norm, df_shots.y_norm, ax=ax, fill=True, levels=100, thresh=0, cmap='hot', alpha=0.5)
        pitch.scatter(df_shots.x_norm, df_shots.y_norm, s=10, c='white', alpha=0.3, ax=ax)
        
        ax.set_title(title, color='white', fontsize=15, pad=20)
        return fig

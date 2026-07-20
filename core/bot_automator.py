import tweepy
import dataframe_image as dfi
import pandas as pd
import os

class TwitterContentFactory:
    """
    Motor de Automatización de Distribución para Redes Sociales.
    Basado en el sistema de Lanus Stats para publicar tablas auto-generadas al instante.
    """
    def __init__(self, use_mock_offline=True):
        """
        Para protección, setear 'use_mock_offline' evitará que explote por falta 
        de credenciales reales en fase de pruebas locales.
        """
        self.offline_mode = use_mock_offline
        
        # Estas variables debes llenarlas en producción obteniéndolas de tu Portal Developer de X.
        self.api_key = "TU_API_KEY_AQUI"
        self.api_secret = "TU_API_SECRET_AQUI"
        self.access_token = "TU_ACCESS_TOKEN_AQUI"
        self.access_token_secret = "TU_TOKEN_SECRET_AQUI"
        self.client = None
        self.api = None
        
        if not self.offline_mode:
            try:
                # Auth Tweepy v2 and v1.1 (Para subir media requerimos v1.1)
                auth = tweepy.OAuth1UserHandler(self.api_key, self.api_secret, self.access_token, self.access_token_secret)
                self.api = tweepy.API(auth)
                self.client = tweepy.Client(
                    consumer_key=self.api_key, consumer_secret=self.api_secret,
                    access_token=self.access_token, access_token_secret=self.access_token_secret
                )
            except Exception as e:
                print(f"[X-Bot Error]: Fallo autenticación -> {e}")

    def export_dataframe_to_image(self, df: pd.DataFrame, output_path="assets/temp_table.png"):
        """
        Toma una 'Justice League Table' (xPts) o cualquier Dataframe,
        le inserta estilos CSS bellísimos y lo vuelve PNG HD.
        """
        # Estilos Pandas Premium
        styled_df = df.style.background_gradient(cmap='Blues') \
                            .set_properties(**{'text-align': 'center', 'font-family': 'Inter'}) \
                            .set_table_styles([{'selector': 'th', 'props': [('background-color', '#111827'), ('color', 'white')]}])
        
        try:
            # table_conversion='chrome' utiliza el motor V8 para renderizar a imagen sin perder calidad de fuente
            dfi.export(styled_df, output_path, table_conversion="matplotlib")
            return output_path
        except Exception as e:
            print(f"[Export Error]: {e}. Asegúrate de tener instalado dataframe_image")
            return None

    def post_thread_with_media(self, md_text_array, image_path=None):
        """
        Iterador para publicar hilos basados en un arreglo de strings (los tweets individuales).
        """
        if self.offline_mode:
            print("🚀 MODO OFFLINE: Simulación de Publicación.")
            print(f"📷 Media a subir: {image_path}")
            for t in md_text_array:
                print(f"🐦 Tuit -> {t}\n")
            return True
            
        try:
            media_id = None
            if image_path and os.path.exists(image_path):
                # Subir la imagen primero al servidor V1.1
                media = self.api.media_upload(image_path)
                media_id = media.media_id
            
            # Postear el primer Tuit (el padre)
            first_tweet = md_text_array[0]
            if media_id:
                response = self.client.create_tweet(text=first_tweet, media_ids=[media_id])
            else:
                response = self.client.create_tweet(text=first_tweet)
                
            previous_id = response.data['id']
            
            # Postear el resto como respuestas (el hilo)
            for subsequent_tweet in md_text_array[1:]:
                response = self.client.create_tweet(text=subsequent_tweet, in_reply_to_tweet_id=previous_id)
                previous_id = response.data['id']
                
            print("✅ Hilo Publicado Mágicamente!")
            return True
            
        except Exception as e:
            print(f"❌ Error lanzando el hilo a X: {e}")
            return False

if __name__ == "__main__":
    # Test
    bot = TwitterContentFactory(use_mock_offline=True)
    mock_xpts = pd.DataFrame({'Team': ['Portugal', 'Colombia'], 'Expected_Pts': [2.89, 1.45]})
    bot.export_dataframe_to_image(mock_xpts)
    bot.post_thread_with_media(["1/2 Prueba de posteo de IA.", "2/2 Fin de prueba con imagen insertada."], "assets/temp_table.png")

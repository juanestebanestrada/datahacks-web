import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os

class NotebookLMAutomator:
    """
    Automatizador para Google NotebookLM usando undetected-chromedriver.
    Permite subir fuentes y disparar la generación de Audio Overview.
    """
    def __init__(self, notebook_url, user_data_dir=None):
        self.notebook_url = notebook_url
        self.user_data_dir = user_data_dir or os.path.join(os.getcwd(), "chrome_profile")
        self.driver = None

    def start_driver(self, headless=False):
        options = uc.ChromeOptions()
        if headless:
            # --headless=new es el estándar actual y soluciona el error 'session not created'
            options.add_argument("--headless=new")
        
        # Banderas de estabilidad para Linux
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-software-rasterizer")
        
        # Usar perfil persistente
        options.add_argument(f"--user-data-dir={self.user_data_dir}")
        
        # Limpieza preventiva de bloqueos de Chrome en Linux
        try:
            lock_path = os.path.join(self.user_data_dir, "SingletonLock")
            if os.path.islink(lock_path) or os.path.exists(lock_path):
                print(f"Limpiando bloqueo previo en {lock_path}")
                os.unlink(lock_path)
        except Exception as e:
            print(f"Aviso: No se pudo eliminar el archivo de bloqueo: {e}")
        
        # Forzar resolución para evitar screenshots de 0x0 en modo headless
        if self.driver:
            try:
                self.driver.set_window_size(1280, 900)
            except Exception:
                pass
        
        try:
            # Intentar iniciar el driver con un timeout
            self.driver = uc.Chrome(options=options)
            # Forzar tamaño de ventana inmediatamente para evitar screenshots vacíos
            self.driver.set_window_size(1280, 900)
            return True, "Driver iniciado con éxito"
        except Exception as e:
            error_msg = str(e)
            print(f"Error iniciando driver: {error_msg}")
            if "singleton" in error_msg.lower() or "lock" in error_msg.lower():
                return False, "El perfil de Chrome sigue bloqueado. Por favor, usa el botón 'Limpiar Sesión' e intenta de nuevo."
            return False, f"Fallo al conectar con Chrome: {error_msg[:100]}..."

    def navigate_and_login(self):
        """Abre la página y espera a que el usuario esté logueado si es necesario."""
        print(f"Navegando a: {self.notebook_url}")
        self.driver.get(self.notebook_url)
        
        # Primer check rápido: si la URL ya contiene notebooklm y no hay redirect a accounts.google.com
        # esperamos a que la página cargue algo antes de analizar
        import time as _time
        _time.sleep(4)
        
        # ── CHECK 1: URL-based (más confiable) ──
        current_url = self.driver.current_url
        print(f"URL actual: {current_url}")
        if "accounts.google.com" in current_url or "signin" in current_url.lower():
            print("Detectado: Página de login de Google. Se requiere Paso 1.")
            return False
        if "notebooklm.google.com" in current_url:
            print("URL confirma: estamos en NotebookLM.")
            return True
        
        # ── CHECK 2: Buscar elementos de la UI (inglés Y español) ──
        selectors_es = [
            "//div[contains(text(), 'Fuentes')]",
            "//button[contains(., 'Subir una fuente')]",
            "//p[contains(text(), 'Agrega una fuente')]",
            "//div[contains(text(), 'Notebook guide')]",
        ]
        selectors_en = [
            "//div[contains(text(), 'Sources')]",
            "//button[contains(., 'Add source')]",
            "//button[contains(@aria-label, 'Add source')]",
            "//div[contains(text(), 'Notebook guide')]",
        ]
        xpath_query = " | ".join(selectors_es + selectors_en)
        
        try:
            WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.XPATH, xpath_query))
            )
            print("Login detectado por selector de UI.")
            return True
        except Exception as e:
            print(f"Selectores de UI no encontrados: {e}")
            self.take_screenshot("error_login.png")
            return False

    def upload_source(self, file_path):
        """Sube un archivo Markdown como fuente al notebook."""
        try:
            # 1. Clic en 'Add source'
            add_btn = WebDriverWait(self.driver, 20).until(
                EC.element_to_be_clickable((By.XPATH, "//button[.//span[contains(text(), 'Add source')]] | //button[contains(@aria-label, 'Add source')]"))
            )
            add_btn.click()
            time.sleep(2)

            # 2. Seleccionar 'Upload from computer' (esto varía en el UI de NotebookLM, a veces es un input directo)
            # Buscamos el input de tipo file que suele estar oculto
            file_input = self.driver.find_element(By.CSS_SELECTOR, "input[type='file']")
            file_input.send_keys(os.path.abspath(file_path))
            
            print(f"Archivo {file_path} subido. Esperando procesamiento...")
            time.sleep(10) # Esperar a que NotebookLM procese el documento
            return True
        except Exception as e:
            print(f"Error subiendo fuente: {e}")
            return False

    def generate_audio_overview(self):
        """Dispara la generación del pódcast (Audio Overview)."""
        try:
            # 1. NotebookLM suele requerir abrir el 'Notebook guide' primero para ver el botón de audio
            print("Buscando panel de 'Notebook guide'...")
            guide_btns = self.driver.find_elements(By.XPATH, "//button[contains(., 'Notebook guide')] | //div[contains(text(), 'Notebook guide')]")
            if guide_btns:
                guide_btns[0].click()
                time.sleep(3)
            
            # 2. Buscar el botón de Generate específicamente para Audio Overview
            # A veces el texto es 'Generate' o 'Load'
            print("Buscando botón 'Generate' en el panel de audio...")
            gen_btn = WebDriverWait(self.driver, 15).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Generate')] | //button[contains(., 'Deep dive')]"))
            )
            gen_btn.click()
            print("Generación de Audio Overview iniciada.")
            return True
        except Exception as e:
            print(f"Error iniciando generación de audio: {e}")
            self.take_screenshot("error_generacion.png")
            return False

    def take_screenshot(self, filename="bot_debug.png"):
        """Captura lo que el bot está viendo para depuración."""
        if not self.driver:
            return None
        
        _os_makedirs = os.makedirs
        _os_makedirs("assets", exist_ok=True)
        path = os.path.join("assets", filename)
        
        try:
            # Esperar a que la página tenga algo visible
            time.sleep(2)
            # Asegurar tamaño de ventana antes de capturar
            self.driver.set_window_size(1280, 900)
            time.sleep(0.5)
            self.driver.save_screenshot(path)
            
            # Validar que el archivo tiene contenido real
            if os.path.exists(path) and os.path.getsize(path) > 1000:
                return path
            else:
                print(f"Screenshot vacío o inválido: {os.path.getsize(path) if os.path.exists(path) else 0} bytes")
                return None
        except Exception as e:
            print(f"Error tomando screenshot: {e}")
            return None

    def close(self):
        if self.driver:
            self.driver.quit()

if __name__ == "__main__":
    # Ejemplo de uso manual
    URL = "https://notebooklm.google.com/" # Reemplazar con URL real del notebook
    bot = NotebookLMAutomator(URL)
    if bot.start_driver():
        bot.navigate_and_login()
        # bot.upload_source("Reporte_NotebookLM_Colombia.md")
        # bot.generate_audio_overview()

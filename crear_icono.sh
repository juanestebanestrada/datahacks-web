#!/bin/bash

# Detectar la carpeta del escritorio (Desktop o Escritorio)
if [ -d "$HOME/Escritorio" ]; then
    DESKTOP_DIR="$HOME/Escritorio"
elif [ -d "$HOME/Desktop" ]; then
    DESKTOP_DIR="$HOME/Desktop"
else
    DESKTOP_DIR="$HOME"
fi

ICON_PATH="$DESKTOP_DIR/Mundial2026.desktop"

# Crear el archivo .desktop
cat <<EOF > "$ICON_PATH"
[Desktop Entry]
Version=1.0
Name=Mundial 2026
Comment=App de Análisis de Fútbol
Exec=bash -c "cd /home/esteban/Documentos/AntigravityPruebas/Mundial2026 && source venv/bin/activate && streamlit run app.py"
Icon=applications-internet
Terminal=true
Type=Application
Categories=Utility;
EOF

# Darle permisos de ejecución al ícono
chmod +x "$ICON_PATH"

echo "¡Ícono creado exitosamente en tu escritorio! ($ICON_PATH)"

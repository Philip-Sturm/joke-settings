#!/usr/bin/env bash

set -e

echo "================================="
echo " Joke Settings Installer"
echo "================================="
echo

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

INSTALL_DIR="$HOME/.local/share/joke-settings"
APPLICATION_DIR="$HOME/.local/share/applications"
SYSTEMD_DIR="$HOME/.config/systemd/user"

echo "[1/7] Installiere benötigte Fedora-Pakete ..."

sudo dnf install -y \
    python3 \
    python3-pyside6

echo
echo "[2/7] Erstelle Verzeichnisse ..."

mkdir -p "$INSTALL_DIR"
mkdir -p "$APPLICATION_DIR"
mkdir -p "$SYSTEMD_DIR"
mkdir -p "$HOME/.local/share/jokes"
mkdir -p "$HOME/.config/programming-jokes"

echo
echo "[3/7] Installiere Joke Settings ..."

cp "$SCRIPT_DIR/joke_settings.py" "$INSTALL_DIR/"
cp "$SCRIPT_DIR/update_jokes.py" "$INSTALL_DIR/"

chmod +x "$INSTALL_DIR/joke_settings.py"
chmod +x "$INSTALL_DIR/update_jokes.py"

echo
echo "[4/7] Erstelle systemd-Service ..."

cat > "$SYSTEMD_DIR/programming-jokes.service" <<EOF
[Unit]
Description=Update jokes from JokeAPI
After=network-online.target

[Service]
Type=oneshot
ExecStart=/usr/bin/python3 $INSTALL_DIR/update_jokes.py
EOF

echo
echo "[5/7] Erstelle täglichen Timer ..."

cat > "$SYSTEMD_DIR/programming-jokes.timer" <<'EOF'
[Unit]
Description=Daily Programming Joke Update

[Timer]
OnCalendar=daily
Persistent=true

[Install]
WantedBy=timers.target
EOF

echo
echo "[6/7] Erstelle KDE-Menüeintrag ..."

cat > "$APPLICATION_DIR/joke-settings.desktop" <<EOF
[Desktop Entry]
Type=Application
Name=Joke Settings
Comment=JokeAPI Einstellungen verwalten
Exec=/usr/bin/python3 $INSTALL_DIR/joke_settings.py
Icon=face-smile
Terminal=false
Categories=Utility;Settings;
EOF

chmod +x "$APPLICATION_DIR/joke-settings.desktop"

echo
echo "[7/7] Aktiviere automatische Aktualisierung ..."

systemctl --user daemon-reload
systemctl --user enable --now programming-jokes.timer

if command -v kbuildsycoca6 >/dev/null 2>&1; then
    kbuildsycoca6 >/dev/null 2>&1 || true
fi

echo
echo "Lade erste Witzsammlung ..."

if /usr/bin/python3 "$INSTALL_DIR/update_jokes.py"; then
    echo
    echo "Erste Witzsammlung erfolgreich erstellt."
else
    echo
    echo "Warnung: JokeAPI konnte momentan nicht erreicht werden."
    echo "Die Installation selbst wurde trotzdem abgeschlossen."
fi

echo
echo "================================="
echo " Installation abgeschlossen"
echo "================================="
echo
echo "Du kannst jetzt im KDE-Anwendungsmenü nach"
echo
echo "    Joke Settings"
echo
echo "suchen."
echo
echo "Witzdatei:"
echo "    $HOME/.local/share/jokes/programming-jokes.txt"
echo
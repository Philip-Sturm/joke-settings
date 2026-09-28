#!/usr/bin/env bash

set -e

INSTALL_DIR="$HOME/.local/share/joke-settings"
APPLICATION_FILE="$HOME/.local/share/applications/joke-settings.desktop"
SYSTEMD_DIR="$HOME/.config/systemd/user"

echo "Deinstalliere Joke Settings ..."

systemctl --user disable --now programming-jokes.timer 2>/dev/null || true

rm -f "$SYSTEMD_DIR/programming-jokes.service"
rm -f "$SYSTEMD_DIR/programming-jokes.timer"

systemctl --user daemon-reload

rm -f "$APPLICATION_FILE"
rm -rf "$INSTALL_DIR"

if command -v kbuildsycoca6 >/dev/null 2>&1; then
    kbuildsycoca6 >/dev/null 2>&1 || true
fi

echo
echo "Joke Settings wurde deinstalliert."
echo
echo "Deine Einstellungen und Witzsammlung wurden NICHT gelöscht:"
echo
echo "  ~/.config/programming-jokes/"
echo "  ~/.local/share/jokes/"
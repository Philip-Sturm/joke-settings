#!/usr/bin/env python3

import json
import sys
from datetime import datetime
from pathlib import Path

from PySide6.QtCore import QProcess
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QFormLayout,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)


CONFIG_DIR = Path.home() / ".config" / "programming-jokes"
CONFIG_FILE = CONFIG_DIR / "config.json"

JOKE_FILE = (
    Path.home()
    / ".local"
    / "share"
    / "jokes"
    / "programming-jokes.txt"
)

UPDATER_FILE = Path(__file__).with_name("update_jokes.py")


DEFAULT_CONFIG = {
    "languages": ["en", "de"],
    "categories": ["Programming"],
    "blacklist": [],
    "safe_mode": False,
    "amount_per_request": 10,
    "requests_per_language": 5,
}


class JokeSettingsWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Joke Settings")
        self.resize(520, 650)

        self.process = None

        self.language_boxes = {}
        self.category_boxes = {}
        self.blacklist_boxes = {}

        self.create_ui()
        self.load_settings()
        self.refresh_status()

    def create_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)

        #
        # Sprachen
        #

        language_group = QGroupBox("Sprachen")
        language_layout = QGridLayout(language_group)

        languages = {
            "en": "English",
            "de": "Deutsch",
        }

        for column, (code, name) in enumerate(languages.items()):
            checkbox = QCheckBox(name)

            self.language_boxes[code] = checkbox
            language_layout.addWidget(checkbox, 0, column)

        main_layout.addWidget(language_group)

        #
        # Kategorien
        #

        category_group = QGroupBox("Kategorien")
        category_layout = QGridLayout(category_group)

        categories = [
            "Programming",
            "Pun",
            "Misc",
            "Dark",
            "Spooky",
            "Christmas",
        ]

        for index, category in enumerate(categories):
            checkbox = QCheckBox(category)

            self.category_boxes[category] = checkbox

            row = index // 2
            column = index % 2

            category_layout.addWidget(checkbox, row, column)

        main_layout.addWidget(category_group)

        #
        # Blacklist
        #

        self.blacklist_group = QGroupBox("Blacklist")
        blacklist_layout = QGridLayout(self.blacklist_group)

        blacklist_flags = [
            "nsfw",
            "religious",
            "political",
            "racist",
            "sexist",
            "explicit",
        ]

        display_names = {
            "nsfw": "NSFW",
            "religious": "Religious",
            "political": "Political",
            "racist": "Racist",
            "sexist": "Sexist",
            "explicit": "Explicit",
        }

        for index, flag in enumerate(blacklist_flags):
            checkbox = QCheckBox(display_names[flag])

            self.blacklist_boxes[flag] = checkbox

            row = index // 2
            column = index % 2

            blacklist_layout.addWidget(checkbox, row, column)

        main_layout.addWidget(self.blacklist_group)

        #
        # Safe Mode
        #

        safe_group = QGroupBox("Sicherheit")
        safe_layout = QVBoxLayout(safe_group)

        self.safe_mode_checkbox = QCheckBox(
            "Safe Mode aktivieren"
        )

        self.safe_mode_checkbox.setToolTip(
            "JokeAPI filtert problematische Inhalte automatisch."
        )

        self.safe_mode_checkbox.toggled.connect(
            self.safe_mode_changed
        )

        safe_layout.addWidget(self.safe_mode_checkbox)

        main_layout.addWidget(safe_group)

        #
        # Abrufeinstellungen
        #

        request_group = QGroupBox("Abrufeinstellungen")
        request_layout = QFormLayout(request_group)

        self.amount_spinbox = QSpinBox()
        self.amount_spinbox.setRange(1, 10)
        self.amount_spinbox.setValue(10)

        self.amount_spinbox.setToolTip(
            "Wie viele Witze JokeAPI pro Anfrage liefern soll."
        )

        request_layout.addRow(
            "Witze pro API-Abruf:",
            self.amount_spinbox,
        )

        self.requests_spinbox = QSpinBox()
        self.requests_spinbox.setRange(1, 20)
        self.requests_spinbox.setValue(5)

        self.requests_spinbox.setToolTip(
            "Wie oft pro ausgewählter Sprache bei JokeAPI "
            "angefragt wird."
        )

        request_layout.addRow(
            "Abrufe pro Sprache:",
            self.requests_spinbox,
        )

        main_layout.addWidget(request_group)

        #
        # Status
        #

        status_group = QGroupBox("Status")
        status_layout = QFormLayout(status_group)

        self.joke_count_label = QLabel("–")
        self.last_update_label = QLabel("–")

        status_layout.addRow(
            "Witze in der Sammlung:",
            self.joke_count_label,
        )

        status_layout.addRow(
            "Letzte Aktualisierung:",
            self.last_update_label,
        )

        self.file_label = QLabel(str(JOKE_FILE))
        self.file_label.setWordWrap(True)

        status_layout.addRow(
            "Witzdatei:",
            self.file_label,
        )

        main_layout.addWidget(status_group)

        #
        # Prozessstatus
        #

        self.process_status_label = QLabel("")
        self.process_status_label.setWordWrap(True)

        main_layout.addWidget(self.process_status_label)

        #
        # Buttons
        #

        button_layout = QHBoxLayout()

        self.save_button = QPushButton("Speichern")
        self.update_button = QPushButton("Jetzt aktualisieren")
        self.close_button = QPushButton("Schließen")

        self.save_button.clicked.connect(
            self.save_settings_clicked
        )

        self.update_button.clicked.connect(
            self.update_jokes
        )

        self.close_button.clicked.connect(
            self.close
        )

        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.update_button)
        button_layout.addStretch()
        button_layout.addWidget(self.close_button)

        main_layout.addLayout(button_layout)

    def safe_mode_changed(self, checked):
        self.blacklist_group.setEnabled(not checked)

    def load_settings(self):
        config = DEFAULT_CONFIG.copy()

        if CONFIG_FILE.exists():
            try:
                with CONFIG_FILE.open(
                    "r",
                    encoding="utf-8",
                ) as file:
                    saved_config = json.load(file)

                config.update(saved_config)

            except (json.JSONDecodeError, OSError) as error:
                QMessageBox.warning(
                    self,
                    "Konfiguration",
                    f"Die gespeicherte Konfiguration konnte "
                    f"nicht gelesen werden:\n\n{error}",
                )

        selected_languages = config.get(
            "languages",
            ["en", "de"],
        )

        for code, checkbox in self.language_boxes.items():
            checkbox.setChecked(
                code in selected_languages
            )

        selected_categories = config.get(
            "categories",
            ["Programming"],
        )

        for category, checkbox in self.category_boxes.items():
            checkbox.setChecked(
                category in selected_categories
            )

        selected_blacklist = config.get(
            "blacklist",
            [],
        )

        for flag, checkbox in self.blacklist_boxes.items():
            checkbox.setChecked(
                flag in selected_blacklist
            )

        safe_mode = config.get(
            "safe_mode",
            False,
        )

        self.safe_mode_checkbox.setChecked(safe_mode)

        self.amount_spinbox.setValue(
            config.get(
                "amount_per_request",
                10,
            )
        )

        self.requests_spinbox.setValue(
            config.get(
                "requests_per_language",
                5,
            )
        )

        self.safe_mode_changed(safe_mode)

    def get_current_settings(self):
        languages = [
            code
            for code, checkbox
            in self.language_boxes.items()
            if checkbox.isChecked()
        ]

        categories = [
            category
            for category, checkbox
            in self.category_boxes.items()
            if checkbox.isChecked()
        ]

        blacklist = [
            flag
            for flag, checkbox
            in self.blacklist_boxes.items()
            if checkbox.isChecked()
        ]

        return {
            "languages": languages,
            "categories": categories,
            "blacklist": blacklist,
            "safe_mode": (
                self.safe_mode_checkbox.isChecked()
            ),
            "amount_per_request": (
                self.amount_spinbox.value()
            ),
            "requests_per_language": (
                self.requests_spinbox.value()
            ),
        }

    def save_settings(self):
        config = self.get_current_settings()

        if not config["languages"]:
            QMessageBox.warning(
                self,
                "Keine Sprache",
                "Bitte mindestens eine Sprache auswählen.",
            )

            return False

        if not config["categories"]:
            QMessageBox.warning(
                self,
                "Keine Kategorie",
                "Bitte mindestens eine Kategorie auswählen.",
            )

            return False

        CONFIG_DIR.mkdir(
            parents=True,
            exist_ok=True,
        )

        temp_file = CONFIG_FILE.with_suffix(".tmp")

        try:
            with temp_file.open(
                "w",
                encoding="utf-8",
            ) as file:
                json.dump(
                    config,
                    file,
                    indent=4,
                    ensure_ascii=False,
                )

            temp_file.replace(CONFIG_FILE)

        except OSError as error:
            QMessageBox.critical(
                self,
                "Fehler",
                f"Die Einstellungen konnten nicht "
                f"gespeichert werden:\n\n{error}",
            )

            return False

        return True

    def save_settings_clicked(self):
        if self.save_settings():
            self.process_status_label.setText(
                "Einstellungen gespeichert."
            )

    def update_jokes(self):
        if not self.save_settings():
            return

        if not UPDATER_FILE.exists():
            QMessageBox.critical(
                self,
                "Updater nicht gefunden",
                f"Die Datei wurde nicht gefunden:\n\n"
                f"{UPDATER_FILE}",
            )

            return

        self.update_button.setEnabled(False)
        self.save_button.setEnabled(False)

        self.process_status_label.setText(
            "Witze werden von JokeAPI geladen …"
        )

        self.process = QProcess(self)

        self.process.finished.connect(
            self.update_finished
        )

        self.process.errorOccurred.connect(
            self.update_process_error
        )

        self.process.setProgram(sys.executable)
        self.process.setArguments(
            [str(UPDATER_FILE)]
        )

        self.process.start()

    def update_finished(self, exit_code, exit_status):
        stdout = bytes(
            self.process.readAllStandardOutput()
        ).decode(
            "utf-8",
            errors="replace",
        )

        stderr = bytes(
            self.process.readAllStandardError()
        ).decode(
            "utf-8",
            errors="replace",
        )

        self.update_button.setEnabled(True)
        self.save_button.setEnabled(True)

        self.refresh_status()

        if exit_code == 0:
            self.process_status_label.setText(
                "Aktualisierung erfolgreich abgeschlossen."
            )

        else:
            self.process_status_label.setText(
                "Aktualisierung fehlgeschlagen."
            )

            error_text = stderr.strip()

            if not error_text:
                error_text = stdout.strip()

            QMessageBox.critical(
                self,
                "Aktualisierung fehlgeschlagen",
                error_text or "Unbekannter Fehler",
            )

        self.process = None

    def update_process_error(self, error):
        self.update_button.setEnabled(True)
        self.save_button.setEnabled(True)

        self.process_status_label.setText(
            "Der Aktualisierungsprozess konnte "
            "nicht gestartet werden."
        )

    def refresh_status(self):
        if not JOKE_FILE.exists():
            self.joke_count_label.setText("0")
            self.last_update_label.setText(
                "Noch keine Aktualisierung"
            )

            return

        try:
            count = 0

            with JOKE_FILE.open(
                "r",
                encoding="utf-8",
            ) as file:
                for line in file:
                    if line.strip() == "%":
                        count += 1

            self.joke_count_label.setText(
                str(count)
            )

            modification_time = datetime.fromtimestamp(
                JOKE_FILE.stat().st_mtime
            )

            self.last_update_label.setText(
                modification_time.strftime(
                    "%d.%m.%Y %H:%M:%S"
                )
            )

        except OSError as error:
            self.joke_count_label.setText("Fehler")
            self.last_update_label.setText(
                str(error)
            )


def main():
    app = QApplication(sys.argv)

    window = JokeSettingsWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
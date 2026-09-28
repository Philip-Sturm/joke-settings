# Joke Settings for KDE Plasma

A small graphical application for Fedora KDE Plasma that downloads random jokes from [JokeAPI](https://v2.jokeapi.dev/) and makes them available to the KDE **Quote of the Day** desktop widget.

The result is a joke directly on your KDE desktop that changes automatically at a configurable interval.

The application supports:

- English and German jokes
- Multiple joke categories
- JokeAPI blacklist filters
- Safe Mode
- Configurable number of API requests
- Manual refresh
- Automatic daily refresh using a systemd user timer
- Display of the current number of jokes
- Display of the last update time

---

# What it looks like

The setup consists of two parts:

```text
Joke Settings
      │
      │ downloads jokes
      ▼
    JokeAPI
      │
      ▼
~/.local/share/jokes/programming-jokes.txt
      │
      ▼
KDE "Quote of the Day" Widget
      │
      ▼
Random joke on your desktop
```

The joke collection is refreshed automatically once per day.

The KDE widget can then display a different joke, for example every 15 minutes.

---

# Requirements

This project is intended for:

- Fedora Linux
- KDE Plasma 6
- Python 3
- PySide6 / Qt 6

It has been tested with Fedora KDE Plasma 6.

The installer automatically installs the required Python packages.

---

# Installation

## 1. Download the repository

Open a terminal.

Clone this repository:

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
```

Then enter the directory:

```bash
cd joke-settings
```

If you downloaded the project as a ZIP file instead, extract it and open a terminal inside the extracted `joke-settings` directory.

---

## 2. Run the installer

Make the installer executable:

```bash
chmod +x install.sh
```

Then run:

```bash
./install.sh
```

The installer will:

- install Python and PySide6 if necessary
- install Joke Settings into your user directory
- create the KDE application launcher entry
- create a systemd user service
- create a daily systemd timer
- download the first joke collection

You may be asked for your password because Fedora packages are installed using `dnf`.

After the installation you should be able to find:

```text
Joke Settings
```

in the KDE application launcher.

---

# KDE Desktop Setup

The Python application downloads and manages the jokes.

To actually display them on the KDE desktop, install the **Quote of the Day** Plasma widget.

## 1. Enter KDE edit mode

Right-click an empty area of the desktop.

Select:

```text
Enter Edit Mode
```

or:

```text
Bearbeitungsmodus starten
```

depending on your system language.

---

## 2. Open the widget browser

Select:

```text
Add Widgets...
```

or:

```text
Miniprogramme hinzufügen...
```

---

## 3. Download the Quote of the Day widget

In the widget browser, select:

```text
Get New Widgets...
```

and then:

```text
Download New Plasma Widgets...
```

Search for:

```text
Quote of the Day
```

Install the Plasma 6 compatible **Quote of the Day** widget.

After installation, close the download window.

---

## 4. Add Quote of the Day to the desktop

Search for:

```text
Quote of the Day
```

in the normal widget list.

Drag the widget onto your desktop.

You can position and resize it like any other KDE Plasma widget.

At first it may display one of its default quotes.

---

# Connect the widget to Joke Settings

The generated joke file is located at:

```text
~/.local/share/jokes/programming-jokes.txt
```

The full path is usually:

```text
/home/YOUR_USERNAME/.local/share/jokes/programming-jokes.txt
```

For example:

```text
/home/philipsturm/.local/share/jokes/programming-jokes.txt
```

Do not copy the example username. Use your own home directory.

---

## 1. Open the widget settings

Right-click the **Quote of the Day** widget.

Select:

```text
Configure Quote of the Day...
```

or the corresponding German configuration option.

---

## 2. Add the joke file

In the widget configuration, find the section containing the quote files.

Select:

```text
Add File...
```

Navigate to:

```text
.local
└── share
    └── jokes
        └── programming-jokes.txt
```

The `.local` directory is hidden.

If it is not visible in the KDE file picker, press:

```text
Ctrl + H
```

to show hidden files.

Select:

```text
programming-jokes.txt
```

and confirm.

---

## 3. Remove the default quote files

The widget may already contain several quote files.

Select the default files one after another and use:

```text
Remove File
```

until only:

```text
programming-jokes.txt
```

remains.

This ensures that only the jokes downloaded by Joke Settings are displayed.

---

## 4. Set the refresh interval

Set:

```text
Update quote every
```

to your preferred interval.

For the setup this project was designed for, the recommended value is:

```text
15 minutes
```

The widget will then select another joke from the local collection every 15 minutes.

Click:

```text
Apply
```

and then:

```text
OK
```

You should now see a joke on the desktop.

---

# Configure the jokes

Open the KDE application launcher and search for:

```text
Joke Settings
```

The application allows you to configure the JokeAPI request without editing any files manually.

---

## Languages

Currently supported by the graphical interface:

- English
- Deutsch

You can enable both at the same time.

When both are enabled, the local joke collection contains English and German jokes.

At least one language must be selected.

---

## Categories

Available JokeAPI categories include:

- Programming
- Pun
- Misc
- Dark
- Spooky
- Christmas

Multiple categories can be selected at the same time.

For a programming-oriented desktop, simply enable:

```text
Programming
```

---

## Blacklist

Individual JokeAPI content flags can be excluded:

- NSFW
- Religious
- Political
- Racist
- Sexist
- Explicit

For example, enabling:

```text
Racist
Sexist
```

means jokes marked with these flags will not be downloaded.

---

## Safe Mode

You can alternatively enable:

```text
Safe Mode
```

Safe Mode tells JokeAPI to use its built-in safe-content filtering.

When Safe Mode is enabled, the individual blacklist settings are disabled in the application.

---

# Refresh the joke collection manually

Inside **Joke Settings**, click:

```text
Jetzt aktualisieren
```

or:

```text
Update Now
```

depending on the application version.

The application will:

1. save the current settings
2. contact JokeAPI
3. download a new selection of jokes
4. remove duplicates
5. replace the local joke collection
6. update the displayed joke count
7. update the last-update timestamp

The KDE widget continues using the same file, so no KDE reconfiguration is necessary.

---

# Automatic updates

The installer creates a systemd user timer:

```text
programming-jokes.timer
```

It updates the joke collection once per day.

Check the timer with:

```bash
systemctl --user status programming-jokes.timer
```

A normal running timer should contain something similar to:

```text
Active: active (waiting)
```

You can also list the next scheduled execution with:

```bash
systemctl --user list-timers programming-jokes.timer
```

---

# Run an update manually from the terminal

You normally do not need this because the graphical application has an update button.

If required, you can manually start the systemd service:

```bash
systemctl --user start programming-jokes.service
```

Check its result with:

```bash
systemctl --user status programming-jokes.service
```

Because this is a `oneshot` service, it is normal for the service to show:

```text
inactive (dead)
```

after a successful execution.

The important part is that the service completed successfully and is not shown as `failed`.

---

# Joke collection

The generated fortune-style joke file is stored here:

```text
~/.local/share/jokes/programming-jokes.txt
```

Individual jokes are separated using:

```text
%
```

Example:

```text
Why are modern programming languages so materialistic?

Because they are object-oriented.
%
Was ist die Lieblingsbeschäftigung von Bits?

Busfahren.
%
Debugging: Removing the needles from the haystack.
%
```

This format is understood by the Quote of the Day Plasma widget.

---

# Configuration file

Joke Settings stores its configuration in:

```text
~/.config/programming-jokes/config.json
```

Example:

```json
{
    "languages": [
        "en",
        "de"
    ],
    "categories": [
        "Programming"
    ],
    "blacklist": [],
    "safe_mode": false,
    "amount_per_request": 10,
    "requests_per_language": 5
}
```

Normally there is no reason to edit this file manually.

Use the graphical **Joke Settings** application instead.

---

# Files installed by the project

Application:

```text
~/.local/share/joke-settings/
```

KDE application launcher:

```text
~/.local/share/applications/joke-settings.desktop
```

systemd service:

```text
~/.config/systemd/user/programming-jokes.service
```

systemd timer:

```text
~/.config/systemd/user/programming-jokes.timer
```

Configuration:

```text
~/.config/programming-jokes/
```

Generated jokes:

```text
~/.local/share/jokes/
```

---

# Troubleshooting

## Joke Settings does not appear in the KDE application launcher

Run:

```bash
kbuildsycoca6
```

Then search again for:

```text
Joke Settings
```

---

## The Quote of the Day widget cannot find `.local`

Directories beginning with a dot are hidden on Linux.

Inside the KDE file picker press:

```text
Ctrl + H
```

Then navigate to:

```text
~/.local/share/jokes/programming-jokes.txt
```

---

## No joke file exists

Open **Joke Settings** and click:

```text
Jetzt aktualisieren
```

Or run:

```bash
systemctl --user start programming-jokes.service
```

Then check:

```bash
ls -l ~/.local/share/jokes/
```

You should see:

```text
programming-jokes.txt
```

---

## Check how many jokes are currently stored

Run:

```bash
grep -c '^%$' ~/.local/share/jokes/programming-jokes.txt
```

For example:

```text
52
```

means the current collection contains 52 jokes.

The exact number varies because JokeAPI returns random jokes and this application removes duplicates.

---

## Check the automatic updater

Run:

```bash
systemctl --user status programming-jokes.timer
```

If necessary, restart and enable it with:

```bash
systemctl --user enable --now programming-jokes.timer
```

---

## Check update errors

Run:

```bash
journalctl --user -u programming-jokes.service
```

To show only recent messages:

```bash
journalctl --user -u programming-jokes.service -n 50
```

---

# Uninstall

From the cloned repository, make the uninstall script executable if necessary:

```bash
chmod +x uninstall.sh
```

Then run:

```bash
./uninstall.sh
```

The application, KDE launcher and systemd integration will be removed.

The following personal files are intentionally kept:

```text
~/.config/programming-jokes/
~/.local/share/jokes/
```

This prevents your settings and joke collection from being deleted accidentally.

If you also want to delete these files:

```bash
rm -rf ~/.config/programming-jokes
rm -rf ~/.local/share/jokes
```

You can also remove the **Quote of the Day** widget manually from your KDE desktop.

---

# Updating the application

If the repository was cloned with Git, enter the repository directory:

```bash
cd joke-settings
```

Download the latest changes:

```bash
git pull
```

Then run the installer again:

```bash
./install.sh
```

The existing installation will be updated.

Your Joke Settings configuration is stored separately and will not be overwritten.

---

# Quick Installation Summary

For experienced users, the complete process is:

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd joke-settings
chmod +x install.sh
./install.sh
```

Then in KDE:

```text
Right-click Desktop
→ Enter Edit Mode
→ Add Widgets
→ Get New Widgets
→ Search "Quote of the Day"
→ Install
→ Add it to the desktop
→ Configure Quote of the Day
→ Add File
→ ~/.local/share/jokes/programming-jokes.txt
→ Remove the default quote files
→ Set update interval to 15 minutes
→ Apply
```

After that, open:

```text
Joke Settings
```

from the KDE application launcher whenever you want to change languages, categories, blacklist filters or update the joke collection manually.

---

# API

Jokes are provided by:

[JokeAPI](https://v2.jokeapi.dev/)

No API key is required.
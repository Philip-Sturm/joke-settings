#!/usr/bin/env python3

import json
import os
import random
import sys
import tempfile
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path


CONFIG_DIR = Path.home() / ".config" / "programming-jokes"
CONFIG_FILE = CONFIG_DIR / "config.json"

OUTPUT_DIR = Path.home() / ".local" / "share" / "jokes"
OUTPUT_FILE = OUTPUT_DIR / "programming-jokes.txt"

API_BASE = "https://v2.jokeapi.dev/joke"


DEFAULT_CONFIG = {
    "languages": ["en", "de"],
    "categories": ["Programming"],
    "blacklist": [],
    "safe_mode": False,
    "amount_per_request": 10,
    "requests_per_language": 5,
}


def load_config():
    config = DEFAULT_CONFIG.copy()

    if CONFIG_FILE.exists():
        try:
            with CONFIG_FILE.open("r", encoding="utf-8") as file:
                saved_config = json.load(file)

            config.update(saved_config)

        except (json.JSONDecodeError, OSError) as error:
            print(
                f"Warnung: Konfiguration konnte nicht gelesen werden: {error}",
                file=sys.stderr,
            )

    return config


def build_api_url(config, language):
    categories = config.get("categories", ["Programming"])
    blacklist = config.get("blacklist", [])
    safe_mode = config.get("safe_mode", False)
    amount = config.get("amount_per_request", 10)

    if not categories:
        categories = ["Programming"]

    category_path = ",".join(categories)

    params = {
        "lang": language,
        "amount": amount,
    }

    if blacklist:
        params["blacklistFlags"] = ",".join(blacklist)

    query = urllib.parse.urlencode(params)

    if safe_mode:
        query += "&safe-mode"

    return f"{API_BASE}/{category_path}?{query}"


def fetch_jokes(url):
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Fedora-Joke-Settings/1.0"
        },
    )

    with urllib.request.urlopen(request, timeout=15) as response:
        data = json.load(response)

    if data.get("error"):
        message = data.get("message", "Unbekannter JokeAPI-Fehler")
        raise RuntimeError(message)

    if "jokes" in data:
        return data["jokes"]

    return [data]


def format_joke(joke):
    joke_type = joke.get("type")

    if joke_type == "single":
        text = joke.get("joke", "")

    elif joke_type == "twopart":
        setup = joke.get("setup", "")
        delivery = joke.get("delivery", "")

        text = f"{setup}\n\n{delivery}"

    else:
        return None

    text = text.strip()

    if not text:
        return None

    return text


def collect_jokes(config):
    languages = config.get("languages", ["en"])
    requests_per_language = config.get("requests_per_language", 5)

    if not languages:
        raise RuntimeError("Es wurde keine Sprache ausgewählt.")

    collected = []
    seen = set()
    successful_requests = 0

    for language in languages:
        for request_number in range(requests_per_language):
            url = build_api_url(config, language)

            try:
                jokes = fetch_jokes(url)
                successful_requests += 1

            except (
                urllib.error.URLError,
                urllib.error.HTTPError,
                TimeoutError,
                RuntimeError,
                json.JSONDecodeError,
            ) as error:
                print(
                    f"Warnung bei {language}, Abruf "
                    f"{request_number + 1}/{requests_per_language}: {error}",
                    file=sys.stderr,
                )
                continue

            for joke in jokes:
                text = format_joke(joke)

                if text and text not in seen:
                    seen.add(text)
                    collected.append(text)

    if successful_requests == 0:
        raise RuntimeError(
            "Keine Verbindung zu JokeAPI möglich. "
            "Die vorhandene Witzdatei wurde nicht verändert."
        )

    if not collected:
        raise RuntimeError(
            "JokeAPI hat keine verwendbaren Witze geliefert. "
            "Die vorhandene Witzdatei wurde nicht verändert."
        )

    random.shuffle(collected)

    return collected


def write_jokes(jokes):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    with tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        dir=OUTPUT_DIR,
        delete=False,
    ) as temp_file:

        temp_path = Path(temp_file.name)

        for joke in jokes:
            temp_file.write(joke)
            temp_file.write("\n%\n")

    os.replace(temp_path, OUTPUT_FILE)


def main():
    try:
        config = load_config()
        jokes = collect_jokes(config)
        write_jokes(jokes)

    except Exception as error:
        print(f"Fehler: {error}", file=sys.stderr)
        return 1

    print(f"Witzdatei aktualisiert: {OUTPUT_FILE}")
    print(f"Anzahl der Witze: {len(jokes)}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
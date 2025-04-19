import requests
import json
from datetime import datetime
from pathlib import Path

API_URL = "https://store-site-backend-static-ipv4.ak.epicgames.com/freeGamesPromotions?locale=en-US&country=US&allowCountries=US"
GAMES_JSON = "games.json"
README_FILE = "README.md"

def fetch_games():
    print("🚀 Fetching free games from Epic Games...")
    res = requests.get(API_URL)
    data = res.json()
    elements = data["data"]["Catalog"]["searchStore"]["elements"]
    free_games = []

    for offer in elements:
        promotions = offer.get("promotions")
        if not promotions:
            print(f"Skipping {offer['title']} - No promotions")
            continue

        # Check current and upcoming promo blocks
        current = promotions.get("promotionalOffers", [])
        upcoming = promotions.get("upcomingPromotionalOffers", [])

        promo = None
        if current and current[0]["promotionalOffers"]:
            promo = current[0]["promotionalOffers"][0]
        elif upcoming and upcoming[0]["promotionalOffers"]:
            promo = upcoming[0]["promotionalOffers"][0]
        else:
            print(f"Skipping {offer['title']} - No promotional offers")
            continue

        if promo["discountSetting"]["discountPercentage"] != 0:
            continue

        start = promo["startDate"][:10]
        end = promo["endDate"][:10]

        game = {
            "title": offer["title"],
            "description": offer.get("description", "No description provided."),
            "url": f"https://store.epicgames.com/en-US/p/{offer.get('urlSlug', '')}",
            "startDate": start,
            "endDate": end
        }

        print(f"Found free game: {game['title']}")
        free_games.append(game)

    return free_games

def load_existing():
    if not Path(GAMES_JSON).exists():
        return []
    with open(GAMES_JSON, "r") as f:
        return json.load(f)

def save_games(games):
    with open(GAMES_JSON, "w") as f:
        json.dump(games, f, indent=2)
    print(f"[✓] Saved {len(games)} entries to {GAMES_JSON}")

def update_readme(games):
    with open(README_FILE, "r", encoding="utf-8") as f:
        readme = f.read()

    start_marker = "<!-- BEGIN_GAMES_TABLE -->"
    end_marker = "<!-- END_GAMES_TABLE -->"

    table = "| 🎮 Game | 🗓️ Duration | 🔗 Link |\n|--------|--------------|---------|\n"
    for g in games:
        duration = f"{g['startDate']} → {g['endDate']}"
        link = f"[Store Page]({g['url']})"
        table += f"| {g['title']} | {duration} | {link} |\n"

    updated = readme.split(start_marker)[0] + start_marker + "\n" + table + "\n" + end_marker + readme.split(end_marker)[1]
    updated = updated.replace(
        "Last updated: 2025-04-19",
        f"Last updated: {datetime.utcnow().strftime('%Y-%m-%d')}"
    )

    with open(README_FILE, "w", encoding="utf-8") as f:
        f.write(updated)

    print(f"[✓] README updated with {len(games)} games.")

def main():
    games = fetch_games()
    save_games(games)
    update_readme(games)

if __name__ == "__main__":
    main()

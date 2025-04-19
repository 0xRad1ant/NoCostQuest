import requests
import json
from datetime import datetime

# URL for the Epic Games free promotions
URL = "https://store-site-backend-static-ipv4.ak.epicgames.com/freeGamesPromotions?locale=en-US&country=US&allowCountries=US"
README_PATH = "README.md"
DATA_PATH = "games.json"

# Get the offers from Epic Games
def getOffers():
    r = requests.get(URL)
    data = r.json()
    # Return the offers data
    return data["data"]["Catalog"]["searchStore"]["elements"]

# Filters only free games (100% off)
def getFree():
    offers = getOffers()
    return list(filter(filterFunct, offers))

# Filter function to check if the game is free (100% off)
def filterFunct(offer):
    try:
        # Check if 'promotions' key exists and contains offers
        if offer.get('promotions') is None:
            return False
        
        promotions = offer['promotions']['promotionalOffers']
        
        # If no promotional offers exist, return False
        if len(promotions) <= 0:
            return False
        
        # Check the first promotional offer discount percentage
        discountPercentage = promotions[0]['promotionalOffers'][0]['discountSetting']['discountPercentage']
        
        # Only return True if the discount is 100% (i.e., the game is free)
        if discountPercentage == 100:
            return True
        
        return False
    except Exception as e:
        print(f"Error processing offer: {e}")
        return False

# Convert offer to a string (display title)
def offerToString(offer):
    return offer['title']

# Update README with free games list
def update_readme(games):
    with open(README_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    # Build new table rows
    new_rows = "\n".join(
        f"| {g['title']} | {g['start']} → {g['end']} | [Claim Now]({g['url']}) |"
        for g in games
    )

    # Replace the table section using markers
    start_tag = "<!-- BEGIN_GAMES_TABLE -->"
    end_tag = "<!-- END_GAMES_TABLE -->"

    if start_tag not in content or end_tag not in content:
        raise ValueError("README is missing required table markers.")

    before = content.split(start_tag)[0] + start_tag + "\n"
    after = "\n" + end_tag + content.split(end_tag)[1]
    new_table = "| 🎮 Game | 🗓️ Duration | 🔗 Link |\n|--------|--------------|---------|\n" + new_rows

    # Replace the section between markers
    content = before + new_table + after

    # Replace update date
    today = datetime.utcnow().strftime("%Y-%m-%d")
    content = content.replace("{{UPDATE_DATE}}", today)

    # Write back to README
    with open(README_PATH, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"[✓] README updated with {len(games)} games.")

# Save free games to a JSON file
def save_json(games):
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(games, f, indent=2)
    print(f"[✓] Saved {len(games)} entries to {DATA_PATH}")

def main():
    # Get the free games
    free_games = getFree()

    # Prepare games data for updating README and saving as JSON
    games_data = []
    for game in free_games:
        title = game.get('title', 'Unknown')
        slug = game.get('productSlug', '')
        price_info = game.get('price', {}).get('totalPrice', {}).get('discountPrice', None)

        # Validate promotions and gather data
        promotions = game.get('promotions', {})
        offers = promotions.get('promotionalOffers', [])
        if offers and offers[0].get('promotionalOffers'):
            offer = offers[0]['promotionalOffers'][0]
            try:
                start = offer['startDate'][:10]
                end = offer['endDate'][:10]
            except (KeyError, IndexError):
                print(f"[!] Skipping {title}: Invalid offer structure")
                continue

            if price_info == 0:
                games_data.append({
                    "title": title,
                    "url": f"https://store.epicgames.com/p/{slug}",
                    "start": start,
                    "end": end
                })
                print(f"[+] Found free game: {title} ({start} → {end})")

    # Update README and save to JSON
    update_readme(games_data)
    save_json(games_data)

if __name__ == "__main__":
    main()

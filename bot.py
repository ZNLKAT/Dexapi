import requests, time
from telegram import Bot

# Telegram-Daten
bot_token = '7583456108:AAGi-14xgS1KcA3vBQnpTJuBS05khu1czzw'
chat_id = '1093230583'
bot = Bot(token=bot_token)

# Chains die gescannt werden
chains = ['solana', 'ethereum']
already_alerted = set()

def scan_tokens():
    for chain in chains:
        url = f"https://api.dexscreener.com/latest/dex/pairs/{chain}"
        try:
            response = requests.get(url)
            data = response.json()
        except Exception as e:
            print(f"Fehler beim Abruf {chain}:", e)
            continue

        for pair in data["pairs"]:
            address = pair["pairAddress"]
            if address in already_alerted:
                continue

            try:
                price_change = float(pair["priceChange"]["m5"])
                volume = float(pair["volume"]["h1"])
                liquidity = float(pair["liquidity"]["usd"])
                created = int(pair["pairCreatedAt"]) / 1000
                age_minutes = (time.time() - created) / 60

                # Nur neue Token mit Pump
                if price_change > 20 and volume > 5000 and liquidity > 8000 and age_minutes < 60:
                    
                    # HONEYPOT CHECK NUR FÜR SOLANA
                    if chain == 'solana':
                        try:
                            check = requests.get(f"https://api.rugcheck.xyz/tokens/solana/{address}").json()
                            if check.get("is_honeypot") is True:
                                continue
                        except:
                            continue

                    name = pair["baseToken"]["name"]
                    symbol = pair["baseToken"]["symbol"]
                    link = pair["url"]

                    msg = (
                        f"🚨 *Pump auf {chain.upper()}*\n"
                        f"*{name} ({symbol})*\n"
                        f"📈 +{price_change}% in 5min\n"
                        f"💧 Liquidity: {liquidity} USD\n"
                        f"📊 Vol (1h): {volume} USD\n"
                        f"🔗 [Zum Chart]({link})"
                    )

                    bot.send_message(chat_id=chat_id, text=msg, parse_mode='Markdown')
                    already_alerted.add(address)

            except Exception as e:
                print("Fehler:", e)

# Dauerhaft ausführen
while True:
    scan_tokens()
    time.sleep(60)

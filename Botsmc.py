import os
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

TOKEN = os.environ.get("TOKEN")

def ambil_candle():
    url = "https://query1.finance.yahoo.com/v8/finance/chart/GC=F?interval=1h&range=5d"
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(url, headers=headers, timeout=15).json()
    res = r['chart']['result'][0]
    h = res['indicators']['quote'][0]['high']
    l = res['indicators']['quote'][0]['low']
    c = res['indicators']['quote'][0]['close']
    data = []
    for i in range(len(c)):
        if h[i] and l[i] and c[i]:
            data.append({'high': h[i], 'low': l[i], 'close': c[i]})
    return data

def analisa_smc(data):
    harga = data[-1]['close']
    highs = [x['high'] for x in data[-30:]]
    lows = [x['low'] for x in data[-30:]]
    res = max(highs)
    sup = min(lows)
    fvg_bull = None
    fvg_bear = None
    for i in range(len(data)-3, 2, -1):
        if data[i+1]['low'] > data[i-1]['high']:
            fvg_bull = (data[i-1]['high'], data[i+1]['low'])
            break
        if data[i+1]['high'] < data[i-1]['low']:
            fvg_bear = (data[i+1]['high'], data[i-1]['low'])
            break
    ob_bull = None
    ob_bear = None
    for i in range(len(data)-1, len(data)-10, -1):
        if data[i]['close'] - data[i-1]['close'] > 5:
            ob_bull = (data[i-1]['low'], data[i-1]['high'])
            break
        if data[i-1]['close'] - data[i]['close'] > 5:
            ob_bear = (data[i-1]['low'], data[i-1]['high'])
            break
    return harga, sup, res, fvg_bull, fvg_bear, ob_bull, ob_bear

def bikin_pesan_analisa():
    data = ambil_candle()
    harga, sup, res, fvg_bull, fvg_bear, ob_bull, ob_bear = analisa_smc(data)
    pesan = f"📊 ANALISA SMC XAUUSD (H1)\n\nHarga Sekarang: {harga:.2f}\n\n🟢 SUPPORT (Demand): {sup:.2f}\n🔴 RESISTANCE (Supply): {res:.2f}\n\n"
    if fvg_bull:
        pesan += f"📈 FVG BULLISH: {fvg_bull[0]:.2f} - {fvg_bull[1]:.2f}\n"
    if fvg_bear:
        pesan += f"📉 FVG BEARISH: {fvg_bear[0]:.2f} - {fvg_bear[1]:.2f}\n"
    if ob_bull:
        pesan += f"🧱 OB BUY: {ob_bull[0]:.2f} - {ob_bull[1]:.2f}\n"
    if ob_bear:
        pesan += f"🧱 OB SELL: {ob_bear[0]:.2f} - {ob_bear[1]:.2f}\n"
    pesan += "\nKetik 'analisa' lagi buat update terbaru bor!"
    return pesan

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if "user_list" not in context.bot_data:
        context.bot_data["user_list"] = []
    if chat_id not in context.bot_data["user_list"]:
        context.bot_data["user_list"].append(chat_id)
    await update.message.reply_text("Bot SMC udah jalan 24 jam bor! 🔥\nGue bakal nyapa lo tiap 1 jam.\nKetik aja 'analisa' tanpa / juga bisa!")

async def analisa(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Sabar bor, gue lagi analisa SMC...")
    try:
        pesan = bikin_pesan_analisa()
        await update.message.reply_text(pesan)
    except Exception as e:
        await update.message.reply_text(f"Error bor: {e}")

async def balas_chat_biasa(update: Update, context: ContextTypes.DEFAULT_TYPE):
    teks = update.message.text.lower()
    if "analisa" in teks or "smc" in teks or "harga" in teks or "gold" in teks or "xau" in teks or "buy" in teks or "sell" in teks:
        await analisa(update, context)
    elif "halo" in teks or "hai" in teks or "hi" in teks or "woy" in teks:
        await update.message.reply_text("Halo juga bor! 🔥 Mau analisa? Ketik aja 'analisa'")
    else:
        await update.message.reply_text("Siap bor! Ketik aja 'analisa' buat liat SMC XAUUSD.")

async def kirim_otomatis(context: ContextTypes.DEFAULT_TYPE):
    for chat_id in context.bot_data.get("user_list", []):
        try:
            pesan = "📢 BOT SMC NYAPA LO BOR!\n\n" + bikin_pesan_analisa()
            await context.bot.send_message(chat_id=chat_id, text=pesan)
        except:
            pass

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("analisa", analisa))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, balas_chat_biasa))
    app.job_queue.run_repeating(kirim_otomatis, interval=3600, first=10)
    print("Bot SMC Render jalan...")
    app.run_polling()

if __name__ == "__main__":
    main()

from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse, Response, HTMLResponse
from fastapi.templating import Jinja2Templates
import asyncio
import random
import base64
import json
import urllib.parse
from typing import List, Set
from telegram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import aiohttp
import time
import os

app = FastAPI(title="Hivo Configs - پنل حرفه‌ای")
templates = Jinja2Templates(directory="templates")

# جایگذاری توکن و کانال تو
BOT_TOKEN = os.getenv("BOT_TOKEN")  # در Railway اضافه می‌کنی
CHANNEL_ID = os.getenv("CHANNEL_ID", "@HivoConfigs")

SOURCES = [
    "https://raw.githubusercontent.com/barry-far/V2ray-Config/main/All_Configs_Sub.txt",
    "https://raw.githubusercontent.com/barry-far/V2ray-Config/main/All_Configs_base64_Sub.txt",
    "https://raw.githubusercontent.com/barry-far/V2ray-Config/main/Sub1.txt",
    "https://raw.githubusercontent.com/barry-far/V2ray-Config/main/Sub2.txt",
    "https://raw.githubusercontent.com/Epodonios/v2ray-configs/main/All_Configs_Sub.txt",
    "https://raw.githubusercontent.com/Epodonios/v2ray-configs/main/All_Configs_base64_Sub.txt",
    "https://raw.githubusercontent.com/Epodonios/v2ray-configs/main/Splitted-By-Protocol/vless.txt",
    "https://raw.githubusercontent.com/Epodonios/v2ray-configs/main/Splitted-By-Protocol/vmess.txt",
    "https://raw.githubusercontent.com/Epodonios/v2ray-configs/main/Splitted-By-Protocol/trojan.txt",
    "https://raw.githubusercontent.com/MatinGhanbari/v2ray-configs/main/subscriptions/v2ray/all_sub.txt",
    "https://raw.githubusercontent.com/MatinGhanbari/v2ray-configs/main/subscriptions/v2ray/super-sub.txt",
    "https://raw.githubusercontent.com/mohamadfg-dev/telegram-v2ray-configs-collector/main/category/vless.txt",
    "https://raw.githubusercontent.com/mohamadfg-dev/telegram-v2ray-configs-collector/main/category/vmess.txt",
    "https://raw.githubusercontent.com/mohamadfg-dev/telegram-v2ray-configs-collector/main/category/trojan.txt",
    "https://raw.githubusercontent.com/mohamadfg-dev/telegram-v2ray-configs-collector/main/category/ss.txt",
    "https://raw.githubusercontent.com/icho53/TelegramV2rayCollector/main/sub/mix",
    "https://raw.githubusercontent.com/icho53/TelegramV2rayCollector/main/sub/mix_base64",
    "https://raw.githubusercontent.com/icho53/TelegramV2rayCollector/main/sub/vless",
    "https://raw.githubusercontent.com/icho53/TelegramV2rayCollector/main/sub/vmess",
    "https://raw.githubusercontent.com/icho53/TelegramV2rayCollector/main/sub/trojan",
    "https://raw.githubusercontent.com/hamedcode/port-based-v2ray-configs/main/sub/port_443.txt",
    "https://raw.githubusercontent.com/hamedcode/port-based-v2ray-configs/main/sub/port_80.txt",
    "https://raw.githubusercontent.com/ebrasha/free-v2ray-public-list/main/all_extracted_configs.txt",
    "https://raw.githubusercontent.com/sevcator/5ubscrpt10n/main/protocols/vl.txt",
    "https://raw.githubusercontent.com/sevcator/5ubscrpt10n/main/protocols/vm.txt",
    "https://raw.githubusercontent.com/sevcator/5ubscrpt10n/main/protocols/tr.txt",
    "https://raw.githubusercontent.com/sevcator/5ubscrpt10n/main/protocols/ss.txt",
    "https://raw.githubusercontent.com/Surfboardv2ray/TGParse/main/splitted/vless",
    "https://raw.githubusercontent.com/Surfboardv2ray/TGParse/main/splitted/vmess",
    "https://raw.githubusercontent.com/Surfboardv2ray/TGParse/main/splitted/trojan",
    "https://raw.githubusercontent.com/vorz1k/v2box/main/supreme_vpns_1.txt",
    "https://raw.githubusercontent.com/vorz1k/v2box/main/supreme_vpns_2.txt",
    "https://raw.githubusercontent.com/SoliSpirit/v2ray-configs/main/all_configs.txt",
    "https://raw.githubusercontent.com/NiREvil/vless/main/sub.txt",
    # اگر بیشتر خواستی، بگو تا اضافه کنم
]

CAPTIONS_POOL = [
    "🌟 هویو کانفیگ تازه رسید! سرعتش دیوونه‌کننده‌ست، برو حالشو ببر 🚀💨",
    "🔥 Hivo Configs جدید! امنیت بالا + پینگ عالی، همین الان وصل شو 😍",
    "💎 با Hivo Configs آزاد باش، سریع باش، خوش باش... محدودیت؟ دیگه چی بود؟ ✨",
    "⚡ این یکی از بهترین‌های امروز Hivo هست! تست کردی هنوز؟ 🔥",
    "❤️ تیم Hivo براتون بهترین‌ها رو جمع کرد – مرسی که همراهید عزیزام 💕",
    "🌈 اینترنت بدون مرز منتظرته... فقط یک کلیک با Hivo Configs 😊",
    "🎉 بروزرسانی ویژه Hivo! امروز رو با آزادی کامل جشن بگیر 🎊",
    "🛡️ امنیت الماسی + سرعت نور = Hivo Configs امروز! برو وصل شو 💪",
    "✨ Hivo همیشه بهترین کانفیگ‌ها رو براتون داره... جادوی آزادی شروع شد! 🌟",
    "😍 پینگ پایین، دانلود بی‌نهایت، Hivo Configs جادو می‌کنه! 🚀",
    "🔥 تازه و داغ از Hivo! این کانفیگ منتظر توئه، امتحانش کن 😏",
    "💫 با Hivo Configs دنیا رو بدون فیلتر ببین... حس آزادی فوق‌العاده‌ست! 🌍",
    "🌟 Hivo Configs: جایی که سرعت و امنیت دست به دست هم می‌دن... لذت ببر! 😎",
    "🚀 سرعتش خفنه! Hivo دوباره بهترین‌ها رو آورد، برو چک کن 🔥",
    "❤️ از طرف Hivo به تو: بهترین کانفیگ روز برای بهترین کاربر 💙",
    "⚡ Hivo Configs آماده اتصال فوری! امروز رو متفاوت کن ✨",
    "🎯 این کانفیگ Hivo فوق‌العاده پایداره... تست کردی؟ نتیجه‌شو بگو! 😄",
    "🌌 شب‌ها با Hivo Configs روشن‌تره... اینترنت آزاد شبانه‌روزی! 🌙",
    "💥 انفجار سرعت با Hivo! کانفیگ جدید رسید، منتظر چی هستی؟ 🚀",
    "😘 Hivo Configs مثل همیشه عالی... مرسی که با مایی عزیز دل 💖",
]

posted_configs = set()

bot = Bot(token=BOT_TOKEN) if BOT_TOKEN else None

def change_remark(config: str, new_remark: str = "Hivo Configs") -> str:
    if not config.strip():
        return config
    protocol = config.split('://', 1)[0].lower() + '://'
    rest = config[len(protocol):]
    if protocol.startswith('vmess://'):
        try:
            decoded = base64.urlsafe_b64decode(rest + '===').decode('utf-8')
            data = json.loads(decoded)
            data['ps'] = new_remark
            new_json = json.dumps(data, separators=(',', ':'))
            new_b64 = base64.urlsafe_b64encode(new_json.encode('utf-8')).decode('utf-8').rstrip('=')
            return 'vmess://' + new_b64
        except:
            return config
    elif protocol in ('vless://', 'trojan://', 'ss://'):
        if '#' in rest:
            main, _ = rest.rsplit('#', 1)
            return protocol + main + '#' + urllib.parse.quote(new_remark)
        return protocol + rest + '#' + urllib.parse.quote(new_remark)
    return config

async def fetch_configs() -> List[str]:
    all_configs = set()
    async with aiohttp.ClientSession() as session:
        for url in SOURCES:
            try:
                async with session.get(url, timeout=15) as resp:
                    if resp.status == 200:
                        text = await resp.text()
                        lines = text.strip().splitlines()
                        for line in lines:
                            line = line.strip()
                            if line and line.startswith(("vmess://", "vless://", "trojan://", "ss://")):
                                all_configs.add(line)
            except Exception as e:
                print(f"خطا منبع {url}: {e}")
    return list(all_configs)

async def post_new_configs():
    if not bot:
        print("BOT_TOKEN تنظیم نشده – پست خودکار غیرفعال")
        return
    configs = await fetch_configs()
    new_posts = 0
    for cfg in configs:
        if cfg in posted_configs:
            continue
        customized = change_remark(cfg)
        caption = random.choice(CAPTIONS_POOL)
        try:
            await bot.send_message(
                chat_id=CHANNEL_ID,
                text=f"{caption}\n\n`{customized}`",
                parse_mode="Markdown",
                disable_web_page_preview=True
            )
            posted_configs.add(cfg)
            new_posts += 1
            await asyncio.sleep(random.uniform(8, 20))  # ضد flood تلگرام
        except Exception as e:
            print(f"خطا در پست کانفیگ: {e}")
            break
    print(f"پایان پست: {new_posts} کانفیگ جدید ارسال شد")

scheduler = AsyncIOScheduler()
scheduler.add_job(post_new_configs, 'interval', minutes=30)
scheduler.start()

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    configs = await fetch_configs()
    unique = len(set(configs))
    stats = {
        "unique_configs": f"{unique:,}".replace(",", "،"),
        "sources": len(SOURCES),
        "remark": "Hivo Configs",
        "update_interval": "هر ۳۰ دقیقه پست (اگر BOT_TOKEN باشه)",
        "last_check": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    return templates.TemplateResponse("index.html", {"request": request, "stats": stats})

@app.get("/sub", response_class=PlainTextResponse)
async def sub():
    configs = await fetch_configs()
    customized = [change_remark(c) for c in configs]
    return "\n".join(customized)

@app.get("/sub64")
async def sub64():
    content = await sub()
    encoded = base64.b64encode(content.encode('utf-8')).decode('utf-8')
    return Response(content=encoded, media_type="text/plain")

@app.get("/health")
async def health():
    return {"status": "alive"}

@app.on_event("startup")
async def startup():
    if bot:
        domain = os.getenv('RAILWAY_PUBLIC_DOMAIN', 'your-domain.up.railway.app')
        webhook_url = f"https://{domain}/webhook"
        try:
            await bot.set_webhook(url=webhook_url)
            print(f"Webhook ست شد: {webhook_url}")
        except Exception as e:
            print(f"خطا در ست webhook: {e}")

@app.post("/webhook")
async def webhook(request: Request):
    if bot:
        update = await request.json()
        # فعلاً ساده – اگر نیاز به هندل پیام داشتی، بگو اضافه کنیم
        return {"ok": True}
    return {"ok": False}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))

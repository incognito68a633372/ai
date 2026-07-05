import streamlit as st
import openai
import json
import asyncio
import os
import io
import base64
import subprocess
import psutil
import time
import random
import string
import hashlib
import urllib.parse
import urllib.request
from pathlib import Path
from datetime import datetime, timedelta
from typing import Tuple, Optional
import requests
from bs4 import BeautifulSoup
import pyautogui
import pyperclip
from PIL import Image, ImageDraw, ImageFont
import qrcode
from pydub import AudioSegment
from langdetect import detect
import edge_tts
from streamlit_mic_recorder import mic_recorder

# ==================== تنظیمات صفحه ====================
st.set_page_config(page_title="JARVIS AI Agent", layout="wide", page_icon="🧠", initial_sidebar_state="expanded")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Vazirmatn:wght@300;400;700&display=swap');
* { font-family: 'Vazirmatn', 'Segoe UI', sans-serif !important; }
.stApp {
    background: linear-gradient(135deg, #000428 0%, #004e92 50%, #000428 100%);
    background-attachment: fixed;
}
.main .block-container { max-width: 1000px; padding: 2rem 1rem; }
[data-testid="stSidebar"] {
    background: rgba(0, 4, 40, 0.95) !important;
    backdrop-filter: blur(20px);
    border-right: 1px solid rgba(0, 255, 255, 0.1);
}
.stChatMessage {
    background: rgba(0, 255, 255, 0.03) !important;
    border: 1px solid rgba(0, 255, 255, 0.08) !important;
    border-radius: 20px !important;
    margin-bottom: 12px !important;
    backdrop-filter: blur(10px);
    transition: all 0.3s ease;
}
.stChatMessage:hover { border-color: rgba(0, 255, 255, 0.2) !important; box-shadow: 0 0 20px rgba(0, 255, 255, 0.1); }
.stTextInput > div > div > input, .stSelectbox > div > div {
    background: rgba(0, 255, 255, 0.05) !important;
    border: 1px solid rgba(0, 255, 255, 0.15) !important;
    border-radius: 12px !important;
    color: white !important;
}
.stButton > button {
    background: linear-gradient(135deg, #00d2ff 0%, #3a7bd5 100%) !important;
    border: none !important; border-radius: 12px !important;
    color: white !important; font-weight: 700 !important;
    text-transform: uppercase !important; letter-spacing: 1px !important;
}
.stButton > button:hover { transform: translateY(-2px); box-shadow: 0 8px 30px rgba(0, 210, 255, 0.4); }
.stInfo { background: rgba(0, 210, 255, 0.08) !important; border: 1px solid rgba(0, 210, 255, 0.3) !important; border-radius: 12px; }
.stSuccess { background: rgba(0, 255, 136, 0.08) !important; border: 1px solid rgba(0, 255, 136, 0.3) !important; border-radius: 12px; }
.stError { background: rgba(255, 50, 50, 0.08) !important; border: 1px solid rgba(255, 50, 50, 0.3) !important; border-radius: 12px; }
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: rgba(0,0,0,0.3); }
::-webkit-scrollbar-thumb { background: rgba(0, 210, 255, 0.3); border-radius: 3px; }
.jarvis-title {
    font-family: 'Orbitron', sans-serif !important;
    background: linear-gradient(90deg, #00d2ff, #3a7bd5, #00d2ff);
    background-size: 200% auto;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    animation: shine 3s linear infinite;
}
@keyframes shine { to { background-position: 200% center; } }
.pulse-ring {
    width: 60px; height: 60px; border-radius: 50%;
    background: radial-gradient(circle, rgba(0,210,255,0.3) 0%, transparent 70%);
    animation: pulse 2s ease-out infinite;
}
@keyframes pulse { 0% { transform: scale(0.8); opacity: 1; } 100% { transform: scale(2); opacity: 0; } }
</style>
""", unsafe_allow_html=True)

# ==================== Sidebar ====================
with st.sidebar:
    st.markdown('<h1 class="jarvis-title" style="text-align:center;">⚙️ JARVIS CORE</h1>', unsafe_allow_html=True)
    base_url = st.text_input("🔌 Base URL", "http://localhost:20128/v1")
    api_key = st.text_input("🔑 API Key", type="password")
    model = st.selectbox("🧠 مدل", [
        "openrouter/nvidia/nemotron-3-super-120b-a12b:free",
        "openrouter/nvidia/nemotron-3-nano-30b-a3b:free",
        "gc/gemini-3.1-pro-preview", "gc/gemini-3-pro-preview", "all", "a", "mmf/mimo-auto",
        "cf/@cf/moonshotai/kimi-k2.7-code", "@cf/moonshotai/kimi-k2.7-code", "@cf/zai-org/glm-5.2", "@cf/openai/gpt-oss-120b", "@cf/meta/llama-3.2-1b-instruct", "@cf/meta/llama-3.2-3b-instruct", "@cf/meta/llama-3.1-8b-instruct-fp8-fast", "@cf/meta/llama-3.1-8b-instruct-awq", "@cf/mistralai/mistral-small-3.1-24b-instruct", "@cf/meta/llama-3.1-70b-instruct-fp8-fast", "@cf/meta/llama-3.3-70b-instruct-fp8-fast", "@cf/deepseek-ai/deepseek-r1-distill-qwen-32b", "@cf/moonshotai/kimi-k2.5", "@cf/moonshotai/kimi-k2.6", "@cf/zai-org/glm-4.7-flash", "@cf/qwen/qwq-32b", "@cf/qwen/qwen2.5-coder-32b-instruct"
    ], index=0)
    st.markdown("---")
    chrome_path = st.text_input("🌐 Chrome Path", r"C:\Program Files\Google\Chrome\Application\chrome.exe")
    st.markdown("---")
    st.info("🎙️ دستورات:\n• برام github.com رو توی کروم باز کن\n• کروم رو ببند\n• همه کروم رو ببند\n• notepad رو ببند\n• فایل test.txt بساز\n• اسکرین‌شات بگیر\n• موس رو ببر 500 500\n• کلیک کن\n• تایپ کن Hello\n• صدا رو کم کن\n• خاموش شو\n• ...")

client = openai.OpenAI(base_url=base_url, api_key=api_key, timeout=60.0, max_retries=2)

# ==================== VOICE MAP (همه زبان‌ها) ====================
VOICE_MAP = {
    'fa': 'fa-IR-DilaraNeural', 'en': 'en-US-AriaNeural', 'fr': 'fr-FR-DeniseNeural',
    'es': 'es-ES-ElviraNeural', 'de': 'de-DE-KatjaNeural', 'it': 'it-IT-ElsaNeural',
    'ja': 'ja-JP-NanamiNeural', 'ko': 'ko-KR-SunHiNeural', 'ar': 'ar-SA-ZariyahNeural',
    'ru': 'ru-RU-SvetlanaNeural', 'tr': 'tr-TR-EmelNeural', 'pt': 'pt-BR-FranciscaNeural',
    'nl': 'nl-NL-ColetteNeural', 'pl': 'pl-PL-AgnieszkaNeural', 'sv': 'sv-SE-SofieNeural',
    'hi': 'hi-IN-SwaraNeural', 'th': 'th-TH-PremwadeeNeural', 'vi': 'vi-VN-HoaiMyNeural',
    'id': 'id-ID-GadisNeural', 'zh': 'zh-CN-XiaoxiaoNeural', 'el': 'el-GR-AthinaNeural',
    'he': 'he-IL-HilaNeural', 'ro': 'ro-RO-AlinaNeural', 'hu': 'hu-HU-NoemiNeural',
    'cs': 'cs-CZ-VlastaNeural', 'sk': 'sk-SK-ViktoriaNeural', 'uk': 'uk-UA-PolinaNeural',
    'bg': 'bg-BG-KalinaNeural', 'hr': 'hr-HR-GabrijelaNeural', 'sl': 'sl-SI-PetraNeural',
    'lt': 'lt-LT-OnaNeural', 'lv': 'lv-LV-EveritaNeural', 'et': 'et-EE-AnuNeural',
    'fi': 'fi-FI-SelmaNeural', 'no': 'nb-NO-PernilleNeural', 'da': 'da-DK-ChristelNeural',
    'ca': 'ca-ES-JoanaNeural', 'ta': 'ta-IN-PallaviNeural', 'te': 'te-IN-ShrutiNeural',
    'mr': 'mr-IN-AarohiNeural', 'bn': 'bn-IN-TanishaaNeural', 'ur': 'ur-IN-GulNeural',
    'sw': 'sw-KE-ZuriNeural', 'ms': 'ms-MY-YasminNeural', 'tl': 'fil-PH-BlessicaNeural',
}

# ==================== WHISPER (تشخیص صدای همه زبان) ====================
@st.cache_resource
def load_whisper():
    try:
        from faster_whisper import WhisperModel
        return WhisperModel("base", device="cpu", compute_type="int8")
    except Exception:
        return None

whisper_model = load_whisper()

def transcribe_audio(audio_data) -> Tuple[str, str]:
    """تشخیص صدای همه زبان‌ها با Whisper"""
    if audio_data is None:
        return "❌ صدایی ضبط نشد.", ""

    raw = audio_data.get("bytes") if isinstance(audio_data, dict) else audio_data
    if raw is None:
        return "❌ داده صدا موجود نیست.", ""

    if isinstance(raw, str):
        try: audio_bytes = base64.b64decode(raw)
        except: return "❌ فرمت صدا نامعتبر.", ""
    elif isinstance(raw, bytes): audio_bytes = raw
    else: return f"❌ نوع داده ناشناخته: {type(raw)}", ""

    if len(audio_bytes) < 500:
        return f"❌ صدای خیلی کوتاه ({len(audio_bytes)} بایت).", ""

    # ذخیره موقت
    with open("temp_input.webm", "wb") as f:
        f.write(audio_bytes)

    # تبدیل به wav با ffmpeg
    ret = os.system("ffmpeg -y -i temp_input.webm temp_rec.wav -loglevel quiet 2>nul")

    if whisper_model:
        try:
            segments, info = whisper_model.transcribe("temp_rec.wav")
            text = " ".join([s.text for s in segments])
            lang = info.language
            return text, lang
        except Exception as e:
            return f"❌ Whisper error: {e}", ""
    else:
        # Fallback: speech_recognition
        import speech_recognition as sr
        r = sr.Recognizer()
        try:
            with sr.AudioFile("temp_rec.wav") as source:
                audio = r.record(source)
            text = r.recognize_google(audio, language="auto")
            return text, "auto"
        except Exception as e:
            return f"❌ خطا: {e}", ""

# ==================== TTS (همه زبان‌ها) ====================
def run_tts(text: str, lang: str) -> str:
    voice = VOICE_MAP.get(lang, VOICE_MAP.get('en'))
    output = f"resp_{int(time.time())}.mp3"
    communicate = edge_tts.Communicate(text, voice)
    asyncio.run(communicate.save(output))
    return output

# ==================== LLM ====================
def ask_llm(messages, tools=None):
    try:
        return client.chat.completions.create(model=model, messages=messages, tools=tools,
            tool_choice="auto", temperature=0.7, max_tokens=4000)
    except Exception as e:
        st.error(f"❌ LLM Error: {str(e)[:200]}")
        return None

# ==================== 100 قابلیت (توابع) ====================

def open_chrome(url: str) -> str:
    if not url.startswith("http"): url = "https://" + url
    paths = [chrome_path, r"C:\Program Files\Google\Chrome\Application\chrome.exe",
             r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"]
    for p in paths:
        if os.path.exists(os.path.expandvars(p)):
            try:
                proc = subprocess.Popen([os.path.expandvars(p), "--new-window", url],
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
                if "chrome_pids" not in st.session_state: st.session_state.chrome_pids = []
                st.session_state.chrome_pids.append(proc.pid)
                return f"✅ Chrome باز شد: {url}"
            except Exception as e: return f"❌ {e}"
    return "❌ Chrome پیدا نشد."

def close_last_chrome() -> str:
    if not st.session_state.get("chrome_pids"): return "❌ کرومی باز نشده."
    pid = st.session_state.chrome_pids.pop()
    try:
        p = psutil.Process(pid); p.terminate(); psutil.wait_procs([p], timeout=3)
        return f"✅ Chrome بسته شد."
    except: return "⚠️ قبلاً بسته بود."

def close_all_chrome() -> str:
    c = 0
    for proc in psutil.process_iter(['pid','name']):
        try:
            if proc.info['name'] and 'chrome' in proc.info['name'].lower():
                p = psutil.Process(proc.info['pid']); p.terminate(); psutil.wait_procs([p], timeout=2); c += 1
        except: pass
    st.session_state.chrome_pids = []
    return f"✅ {c} Chrome بسته شد."

def close_program(name: str) -> str:
    c = 0; nl = name.lower().replace('.exe','')
    for proc in psutil.process_iter(['pid','name']):
        try:
            if nl in (proc.info['name'] or '').lower():
                p = psutil.Process(proc.info['pid']); p.terminate(); psutil.wait_procs([p], timeout=2); c += 1
        except: pass
    return f"✅ {c} '{name}' بسته شد." if c else f"⚠️ '{name}' پیدا نشد."

def create_file(path: str, content: str) -> str:
    try:
        dp = os.path.dirname(path)
        if dp and not os.path.exists(dp): os.makedirs(dp, exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f: f.write(content)
        return f"✅ فایل ساخته شد: {path}"
    except Exception as e: return f"❌ {e}"

def read_file(path: str) -> str:
    try:
        with open(path, 'r', encoding='utf-8') as f: return f.read()
    except Exception as e: return f"❌ {e}"

def delete_file(path: str) -> str:
    try: os.remove(path); return f"✅ حذف شد: {path}"
    except Exception as e: return f"❌ {e}"

def list_files(directory: str = ".") -> str:
    try: return "📁 " + "\n".join([f"• {f}" for f in os.listdir(directory)[:50]])
    except Exception as e: return f"❌ {e}"

def create_folder(path: str) -> str:
    try: os.makedirs(path, exist_ok=True); return f"✅ پوشه ساخته شد: {path}"
    except Exception as e: return f"❌ {e}"

def delete_folder(path: str) -> str:
    try: import shutil; shutil.rmtree(path); return f"✅ پوشه حذف شد: {path}"
    except Exception as e: return f"❌ {e}"

def copy_file(src: str, dst: str) -> str:
    try: import shutil; shutil.copy2(src, dst); return f"✅ کپی شد: {src} → {dst}"
    except Exception as e: return f"❌ {e}"

def move_file(src: str, dst: str) -> str:
    try: import shutil; shutil.move(src, dst); return f"✅ انتقال شد: {src} → {dst}"
    except Exception as e: return f"❌ {e}"

def rename_file(old: str, new: str) -> str:
    try: os.rename(old, new); return f"✅ تغییر نام: {old} → {new}"
    except Exception as e: return f"❌ {e}"

def take_screenshot() -> str:
    try:
        img = pyautogui.screenshot()
        img.save("screenshot.png")
        return "✅ اسکرین‌شات گرفته شد."
    except Exception as e: return f"❌ {e}"

def type_text(text: str) -> str:
    try: pyautogui.typewrite(text, interval=0.01); return f"✅ تایپ شد: {text}"
    except Exception as e: return f"❌ {e}"

def press_key(key: str) -> str:
    try: pyautogui.press(key); return f"✅ کلید {key} زده شد."
    except Exception as e: return f"❌ {e}"

def click_mouse(x: int = None, y: int = None) -> str:
    try:
        if x is not None and y is not None: pyautogui.click(x, y)
        else: pyautogui.click()
        return f"✅ کلیک در {x},{y}" if x else "✅ کلیک شد."
    except Exception as e: return f"❌ {e}"

def move_mouse(x: int, y: int) -> str:
    try: pyautogui.moveTo(x, y); return f"✅ موس رفت {x},{y}"
    except Exception as e: return f"❌ {e}"

def scroll_mouse(amount: int) -> str:
    try: pyautogui.scroll(amount); return f"✅ اسکرول {amount}"
    except Exception as e: return f"❌ {e}"

def get_time() -> str: return f"🕐 {datetime.now().strftime('%H:%M:%S')}"

def get_date() -> str: return f"📅 {datetime.now().strftime('%Y-%m-%d %A')}"

def get_datetime() -> str: return f"🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

def calculator(expression: str) -> str:
    try:
        safe = {"__builtins__": None}
        safe.update({k: v for k, v in vars(__import__('math')).items() if not k.startswith('_')})
        result = eval(expression, safe)
        return f"🧮 {expression} = {result}"
    except Exception as e: return f"❌ خطا: {e}"

def random_number(min_val: int = 0, max_val: int = 100) -> str:
    return f"🎲 {random.randint(min_val, max_val)}"

def password_generator(length: int = 12) -> str:
    chars = string.ascii_letters + string.digits + "!@#$%^&*"
    return f"🔐 {''.join(random.choice(chars) for _ in range(length))}"

def coin_flip() -> str: return f"🪙 {'شیر' if random.choice([True, False]) else 'خط'}"

def dice_roll(sides: int = 6) -> str: return f"🎲 {random.randint(1, sides)}"

def encode_base64(text: str) -> str: return f"🔢 {base64.b64encode(text.encode()).decode()}"

def decode_base64(text: str) -> str:
    try: return f"🔢 {base64.b64decode(text.encode()).decode()}"
    except Exception as e: return f"❌ {e}"

def hash_md5(text: str) -> str: return f"🔐 MD5: {hashlib.md5(text.encode()).hexdigest()}"

def hash_sha256(text: str) -> str: return f"🔐 SHA256: {hashlib.sha256(text.encode()).hexdigest()}"

def generate_qr(data: str) -> str:
    try: img = qrcode.make(data); img.save("qr.png"); return f"✅ QR ساخته شد: qr.png"
    except Exception as e: return f"❌ {e}"

def shorten_url(url: str) -> str:
    try:
        r = requests.get(f"https://tinyurl.com/api-create.php?url={urllib.parse.quote(url)}", timeout=10)
        return f"🔗 کوتاه‌شده: {r.text}"
    except Exception as e: return f"❌ {e}"

def get_ip() -> str:
    try:
        r = requests.get("https://api.ipify.org?format=json", timeout=10)
        return f"🌐 IP: {r.json()['ip']}"
    except Exception as e: return f"❌ {e}"

def ping(host: str) -> str:
    try:
        ret = subprocess.run(["ping", "-n", "1", host], capture_output=True, text=True, timeout=10)
        return f"📡 Ping {host}:\n{ret.stdout[:500]}"
    except Exception as e: return f"❌ {e}"

def system_info() -> str:
    try:
        return (f"💻 سیستم:\n• CPU: {psutil.cpu_percent()}%\n• RAM: {psutil.virtual_memory().percent}%\n• Disk: {psutil.disk_usage('/').percent}%\n• Boot: {datetime.fromtimestamp(psutil.boot_time()).strftime('%Y-%m-%d %H:%M')}")
    except Exception as e: return f"❌ {e}"

def battery_status() -> str:
    try:
        bat = psutil.sensors_battery()
        return f"🔋 {bat.percent}% {'⚡ شارژ' if bat.power_plugged else '🔌 باتری'}"
    except: return "⚠️ اطلاعات باتری در دسترس نیست."

def volume_up() -> str:
    try: os.system("nircmd.exe changesysvolume 2000"); return "🔊 صدا زیاد شد."
    except: return "⚠️ از کیبورد استفاده کنید."

def volume_down() -> str:
    try: os.system("nircmd.exe changesysvolume -2000"); return "🔉 صدا کم شد."
    except: return "⚠️ از کیبورد استفاده کنید."

def volume_mute() -> str:
    try: os.system("nircmd.exe mutesysvolume 1"); return "🔇 صدا قطع شد."
    except: return "⚠️ از کیبورد استفاده کنید."

def shutdown() -> str:
    try: os.system("shutdown /s /t 60"); return "⏻ خاموش شدن در 60 ثانیه..."
    except Exception as e: return f"❌ {e}"

def restart() -> str:
    try: os.system("shutdown /r /t 60"); return "🔄 ری‌استارت در 60 ثانیه..."
    except Exception as e: return f"❌ {e}"

def sleep_pc() -> str:
    try: os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0"); return "💤 Sleep..."
    except Exception as e: return f"❌ {e}"

def abort_shutdown() -> str:
    try: os.system("shutdown /a"); return "✅ خاموش شدن لغو شد."
    except Exception as e: return f"❌ {e}"

def open_app(name: str) -> str:
    try: os.startfile(name); return f"✅ {name} باز شد."
    except Exception as e: return f"❌ {e}"

def open_folder(path: str) -> str:
    try: os.startfile(path); return f"✅ پوشه باز شد: {path}"
    except Exception as e: return f"❌ {e}"

def read_clipboard() -> str:
    try: return f"📋 {pyperclip.paste()}"
    except Exception as e: return f"❌ {e}"

def write_clipboard(text: str) -> str:
    try: pyperclip.copy(text); return f"✅ کلیپ‌برد: {text[:50]}..."
    except Exception as e: return f"❌ {e}"

def minimize_window() -> str:
    try: pyautogui.keyDown('win'); pyautogui.keyDown('down'); pyautogui.keyUp('down'); pyautogui.keyUp('win'); return "✅ minimized"
    except Exception as e: return f"❌ {e}"

def maximize_window() -> str:
    try: pyautogui.keyDown('win'); pyautogui.keyDown('up'); pyautogui.keyUp('up'); pyautogui.keyUp('win'); return "✅ maximized"
    except Exception as e: return f"❌ {e}"

def close_window() -> str:
    try: pyautogui.keyDown('alt'); pyautogui.keyDown('f4'); pyautogui.keyUp('f4'); pyautogui.keyUp('alt'); return "✅ پنجره بسته شد."
    except Exception as e: return f"❌ {e}"

def switch_window() -> str:
    try: pyautogui.keyDown('alt'); pyautogui.keyDown('tab'); pyautogui.keyUp('tab'); pyautogui.keyUp('alt'); return "✅ switched"
    except Exception as e: return f"❌ {e}"

def search_google(query: str) -> str:
    try: open_chrome(f"https://www.google.com/search?q={urllib.parse.quote(query)}"); return f"🔍 گوگل: {query}"
    except Exception as e: return f"❌ {e}"

def search_youtube(query: str) -> str:
    try: open_chrome(f"https://www.youtube.com/results?search_query={urllib.parse.quote(query)}"); return f"📺 یوتیوب: {query}"
    except Exception as e: return f"❌ {e}"

def play_music(query: str) -> str:
    try: open_chrome(f"https://www.youtube.com/results?search_query={urllib.parse.quote(query + ' music')}"); return f"🎵 در حال پخش: {query}"
    except Exception as e: return f"❌ {e}"

def weather(city: str) -> str:
    try:
        url = f"https://wttr.in/{city}?format=%C+%t+%h+%w"
        r = requests.get(url, timeout=10)
        return f"🌤️ {city}: {r.text}"
    except Exception as e: return f"❌ {e}"

def translate(text: str, target: str = "en") -> str:
    try:
        # استفاده از MyMemory API (رایگان)
        url = f"https://api.mymemory.translated.net/get?q={urllib.parse.quote(text)}&langpair=auto|{target}"
        r = requests.get(url, timeout=10).json()
        return f"🌐 ترجمه: {r['responseData']['translatedText']}"
    except Exception as e: return f"❌ {e}"

def news() -> str:
    try:
        r = requests.get("https://feeds.bbci.co.uk/news/rss.xml", timeout=10)
        soup = BeautifulSoup(r.content, 'xml')
        items = soup.find_all('item')[:5]
        return "📰 اخبار:\n" + "\n".join([f"• {i.title.text}" for i in items])
    except Exception as e: return f"❌ {e}"

def joke() -> str:
    try:
        r = requests.get("https://v2.jokeapi.dev/joke/Any?type=single", timeout=10)
        return f"😂 {r.json()['joke']}"
    except Exception as e: return f"❌ {e}"

def quote() -> str:
    try:
        r = requests.get("https://api.quotable.io/random", timeout=10)
        d = r.json()
        return f"💬 {d['content']} — {d['author']}"
    except Exception as e: return f"❌ {e}"

def fact() -> str:
    try:
        r = requests.get("https://uselessfacts.jsph.pl/random.json?language=en", timeout=10)
        return f"🤯 {r.json()['text']}"
    except Exception as e: return f"❌ {e}"

def word_count(text: str) -> str: return f"📝 {len(text.split())} کلمه"

def char_count(text: str) -> str: return f"📝 {len(text)} کاراکتر"

def line_count(text: str) -> str: return f"📝 {len(text.splitlines())} خط"

def reverse_text(text: str) -> str: return f"🔄 {text[::-1]}"

def upper_text(text: str) -> str: return f"🔠 {text.upper()}"

def lower_text(text: str) -> str: return f"🔡 {text.lower()}"

def capitalize_text(text: str) -> str: return f"🔤 {text.title()}"

def remove_spaces(text: str) -> str: return f"✂️ {text.replace(' ', '')}"

def trim_text(text: str) -> str: return f"✂️ {text.strip()}"

def replace_text(text: str, old: str, new: str) -> str: return f"🔄 {text.replace(old, new)}"

def split_text(text: str, delimiter: str = " ") -> str: return f"📎 {text.split(delimiter)}"

def join_text(items: str, delimiter: str = " ") -> str: return f"📎 {delimiter.join(items.split(','))}"

def find_text(text: str, substring: str) -> str:
    idx = text.find(substring)
    return f"🔍 پیدا شد در ایندکس {idx}" if idx != -1 else "🔍 پیدا نشد."

def count_substring(text: str, substring: str) -> str: return f"🔢 {text.count(substring)} بار"

def starts_with(text: str, prefix: str) -> str: return f"✅ بله" if text.startswith(prefix) else "❌ خیر"

def ends_with(text: str, suffix: str) -> str: return f"✅ بله" if text.endswith(suffix) else "❌ خیر"

def is_palindrome(text: str) -> str:
    t = text.replace(" ", "").lower()
    return f"✅ پالیندروم است" if t == t[::-1] else "❌ پالیندروم نیست"

def extract_numbers(text: str) -> str:
    import re
    nums = re.findall(r'\d+', text)
    return f"🔢 {', '.join(nums)}" if nums else "🔢 عددی پیدا نشد."

def extract_emails(text: str) -> str:
    import re
    emails = re.findall(r'[\w\.-]+@[\w\.-]+', text)
    return f"📧 {', '.join(emails)}" if emails else "📧 ایمیلی پیدا نشد."

def extract_urls(text: str) -> str:
    import re
    urls = re.findall(r'https?://[^\s]+', text)
    return f"🔗 {', '.join(urls)}" if urls else "🔗 لینکی پیدا نشد."

def json_pretty(text: str) -> str:
    try: return json.dumps(json.loads(text), indent=2, ensure_ascii=False)
    except Exception as e: return f"❌ JSON نامعتبر: {e}"

def csv_to_table(text: str) -> str:
    lines = text.strip().split('\n')
    return "📊 " + "\n".join([" | ".join(line.split(',')) for line in lines[:20]])

def sort_lines(text: str) -> str: return "\n".join(sorted(text.splitlines()))

def shuffle_lines(text: str) -> str:
    lines = text.splitlines(); random.shuffle(lines); return "\n".join(lines)

def unique_lines(text: str) -> str: return "\n".join(list(dict.fromkeys(text.splitlines())))

def duplicate_lines(text: str) -> str: return "\n".join([line for line in text.splitlines() for _ in range(2)])

def repeat_text(text: str, times: int = 2) -> str: return text * times

def pad_left(text: str, length: int, char: str = " ") -> str: return text.rjust(length, char)

def pad_right(text: str, length: int, char: str = " ") -> str: return text.ljust(length, char)

def center_text(text: str, length: int) -> str: return text.center(length)

def wrap_text(text: str, width: int = 40) -> str:
    import textwrap
    return "\n".join(textwrap.wrap(text, width))

def truncate_text(text: str, length: int = 50) -> str: return text[:length] + "..." if len(text) > length else text

def slugify(text: str) -> str:
    import re
    return re.sub(r'[^\w\s-]', '', text).strip().lower().replace(' ', '-')

def camel_case(text: str) -> str:
    words = text.split()
    return words[0].lower() + ''.join(w.capitalize() for w in words[1:])

def snake_case(text: str) -> str: return text.replace(' ', '_').lower()

def kebab_case(text: str) -> str: return text.replace(' ', '-').lower()

def pascal_case(text: str) -> str: return ''.join(w.capitalize() for w in text.split())

def leet_speak(text: str) -> str:
    trans = str.maketrans('aAeEoOtTiIsS', '443300771155')
    return text.translate(trans)

def morse_encode(text: str) -> str:
    MORSE = {'A':'.-','B':'-...','C':'-.-.','D':'-..','E':'.','F':'..-.','G':'--.','H':'....','I':'..','J':'.---','K':'-.-','L':'.-..','M':'--','N':'-.','O':'---','P':'.--.','Q':'--.-','R':'.-.','S':'...','T':'-','U':'..-','V':'...-','W':'.--','X':'-..-','Y':'-.--','Z':'--..','1':'.----','2':'..---','3':'...--','4':'....-','5':'.....','6':'-....','7':'--...','8':'---..','9':'----.','0':'-----',' ':'/'}
    return ' '.join(MORSE.get(c.upper(), c) for c in text)

def caesar_cipher(text: str, shift: int = 3) -> str:
    result = ""
    for c in text:
        if c.isalpha():
            base = ord('A') if c.isupper() else ord('a')
            result += chr((ord(c) - base + shift) % 26 + base)
        else: result += c
    return result

def rot13(text: str) -> str: return caesar_cipher(text, 13)

def hex_encode(text: str) -> str: return text.encode().hex()

def hex_decode(text: str) -> str:
    try: return bytes.fromhex(text).decode()
    except: return "❌ hex نامعتبر"

def binary_encode(text: str) -> str: return ' '.join(format(ord(c), '08b') for c in text)

def binary_decode(text: str) -> str:
    try: return ''.join(chr(int(b, 2)) for b in text.split())
    except: return "❌ binary نامعتبر"

def url_encode(text: str) -> str: return urllib.parse.quote(text)

def url_decode(text: str) -> str: return urllib.parse.unquote(text)

def html_encode(text: str) -> str: return text.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')

def html_decode(text: str) -> str: return text.replace('&lt;','<').replace('&gt;','>').replace('&amp;','&')

def markdown_to_text(text: str) -> str:
    import re
    t = re.sub(r'[#*`_~\[\]\(\)!]', '', text)
    return re.sub(r'\n+', '\n', t).strip()

def lorem_ipsum(words: int = 50) -> str:
    lorem = "lorem ipsum dolor sit amet consectetur adipiscing elit sed do eiusmod tempor incididunt ut labore et dolore magna aliqua ut enim ad minim veniam quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur excepteur sint occaecat cupidatat non proident sunt in culpa qui officia deserunt mollit anim id est laborum"
    return ' '.join((lorem.split() * ((words // 20) + 1))[:words])

def uuid_generator() -> str:
    import uuid
    return f"🔑 {uuid.uuid4()}"

def guid_generator() -> str: return uuid_generator()

def color_random() -> str:
    c = "#{:06x}".format(random.randint(0, 0xFFFFFF))
    return f"🎨 {c}"

def color_rgb(r: int, g: int, b: int) -> str: return f"🎨 RGB({r},{g},{b}) = #{r:02x}{g:02x}{b:02x}"

def days_between(date1: str, date2: str) -> str:
    try:
        d1 = datetime.strptime(date1, "%Y-%m-%d")
        d2 = datetime.strptime(date2, "%Y-%m-%d")
        return f"📅 {abs((d2-d1).days)} روز"
    except Exception as e: return f"❌ {e}"

def add_days(date_str: str, days: int) -> str:
    try:
        d = datetime.strptime(date_str, "%Y-%m-%d") + timedelta(days=days)
        return f"📅 {d.strftime('%Y-%m-%d')}"
    except Exception as e: return f"❌ {e}"

def age_calculator(birthdate: str) -> str:
    try:
        birth = datetime.strptime(birthdate, "%Y-%m-%d")
        today = datetime.today()
        years = today.year - birth.year - ((today.month, today.day) < (birth.month, birth.day))
        return f"🎂 {years} سال"
    except Exception as e: return f"❌ {e}"

def timer(seconds: int) -> str: return f"⏱️ تایمر {seconds} ثانیه تنظیم شد."

def stopwatch_start() -> str: return f"⏱️ کرنومتر شروع: {datetime.now().strftime('%H:%M:%S')}"

def world_clock(city: str = "UTC") -> str:
    try:
        import pytz
        tz = pytz.timezone(city)
        return f"🌍 {city}: {datetime.now(tz).strftime('%H:%M:%S')}"
    except: return f"🌍 {datetime.utcnow().strftime('%H:%M:%S')} UTC"

def currency_converter(amount: float, from_curr: str = "USD", to_curr: str = "EUR") -> str:
    try:
        # نرخ ثابت تقریبی (برای offline)
        rates = {"USD":1,"EUR":0.92,"GBP":0.79,"JPY":150,"IRR":42000,"TRY":32,"AED":3.67,"CAD":1.36,"AUD":1.52,"CHF":0.88,"CNY":7.2,"INR":83,"RUB":92,"KRW":1330,"BRL":4.95}
        result = amount / rates[from_curr.upper()] * rates[to_curr.upper()]
        return f"💱 {amount} {from_curr.upper()} = {result:.2f} {to_curr.upper()}"
    except Exception as e: return f"❌ {e}"

def unit_converter(value: float, from_unit: str, to_unit: str) -> str:
    # متر به فوت
    conversions = {("m","ft"):3.28084, ("ft","m"):0.3048, ("km","mi"):0.621371, ("mi","km"):1.60934,
                   ("kg","lb"):2.20462, ("lb","kg"):0.453592, ("c","f"):None, ("f","c"):None}
    if (from_unit.lower(), to_unit.lower()) in conversions:
        rate = conversions[(from_unit.lower(), to_unit.lower())]
        if rate is None:
            if from_unit.lower() == "c": return f"🌡️ {value}°C = {(value*9/5)+32:.1f}°F"
            else: return f"🌡️ {value}°F = {(value-32)*5/9:.1f}°C"
        return f"📏 {value} {from_unit} = {value*rate:.2f} {to_unit}"
    return "⚠️ واحد پشتیبانی نمی‌شود."

def wifi_list() -> str:
    try:
        ret = subprocess.run(["netsh", "wlan", "show", "profiles"], capture_output=True, text=True)
        return f"📶 شبکه‌ها:\n{ret.stdout[:1000]}"
    except Exception as e: return f"❌ {e}"

def speed_test() -> str:
    return "⚡ برای تست سرعت از speedtest.net استفاده کنید یا دستور 'speedtest' را در ترمینال اجرا کنید."

def dns_lookup(domain: str) -> str:
    try:
        import socket
        ip = socket.gethostbyname(domain)
        return f"🌐 {domain} → {ip}"
    except Exception as e: return f"❌ {e}"

def whois_lookup(domain: str) -> str:
    try:
        r = requests.get(f"https://whois.verisign.com/whois/whois.jsp?domain={domain}", timeout=10)
        return f"🌐 WHOIS {domain}:\n{r.text[:500]}"
    except Exception as e: return f"❌ {e}"

def port_scan(host: str, ports: str = "80,443,8080") -> str:
    import socket
    results = []
    for port in map(int, ports.split(',')):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(1)
            result = s.connect_ex((host, port))
            status = "✅ باز" if result == 0 else "❌ بسته"
            results.append(f"Port {port}: {status}")
            s.close()
        except: results.append(f"Port {port}: ❌ خطا")
    return "\n".join(results)

def download_file(url: str, path: str = None) -> str:
    try:
        if not path: path = url.split('/')[-1]
        urllib.request.urlretrieve(url, path)
        return f"✅ دانلود شد: {path}"
    except Exception as e: return f"❌ {e}"

def upload_file(path: str) -> str:
    return f"📤 برای آپلود فایل {path} از رابط کاربری استفاده کنید."

def compress_image(path: str, quality: int = 70) -> str:
    try:
        img = Image.open(path)
        out = f"compressed_{os.path.basename(path)}"
        img.save(out, quality=quality, optimize=True)
        return f"✅ فشرده شد: {out}"
    except Exception as e: return f"❌ {e}"

def resize_image(path: str, width: int, height: int) -> str:
    try:
        img = Image.open(path)
        img = img.resize((width, height))
        out = f"resized_{os.path.basename(path)}"
        img.save(out)
        return f"✅ تغییر سایز: {out}"
    except Exception as e: return f"❌ {e}"

def convert_image(path: str, fmt: str = "png") -> str:
    try:
        img = Image.open(path)
        out = f"converted.{fmt}"
        img.save(out, fmt.upper())
        return f"✅ تبدیل: {out}"
    except Exception as e: return f"❌ {e}"

def pdf_to_text(path: str) -> str:
    try:
        import PyPDF2
        with open(path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            text = "\n".join([page.extract_text() for page in reader.pages[:5]])
            return f"📄 {text[:2000]}"
    except Exception as e: return f"❌ {e}"

def text_to_pdf(text: str, path: str) -> str:
    try:
        from fpdf import FPDF
        pdf = FPDF(); pdf.add_page(); pdf.set_font('Arial', '', 12)
        for line in text.split('\n'): pdf.cell(0, 10, line.encode('latin-1', 'replace').decode('latin-1'), ln=True)
        pdf.output(path)
        return f"✅ PDF ساخته شد: {path}"
    except Exception as e: return f"❌ {e}"

def merge_pdfs(files: str, output: str = "merged.pdf") -> str:
    try:
        import PyPDF2
        merger = PyPDF2.PdfMerger()
        for f in files.split(','): merger.append(f.strip())
        merger.write(output); merger.close()
        return f"✅ PDF ادغام شد: {output}"
    except Exception as e: return f"❌ {e}"

def extract_zip(path: str, dest: str = ".") -> str:
    try:
        import zipfile
        with zipfile.ZipFile(path, 'r') as z: z.extractall(dest)
        return f"✅ استخراج شد: {dest}"
    except Exception as e: return f"❌ {e}"

def create_zip(files: str, output: str = "archive.zip") -> str:
    try:
        import zipfile
        with zipfile.ZipFile(output, 'w') as z:
            for f in files.split(','): z.write(f.strip())
        return f"✅ ZIP ساخته شد: {output}"
    except Exception as e: return f"❌ {e}"

# ==================== تعریف Tool Schema برای LLM ====================
ALL_TOOLS = [
    {"type": "function", "function": {"name": "open_chrome", "description": "باز کردن سایت در Chrome", "parameters": {"type": "object", "properties": {"url": {"type": "string"}}, "required": ["url"]}}},
    {"type": "function", "function": {"name": "close_last_chrome", "description": "بستن آخرین Chrome", "parameters": {"type": "object", "properties": {}}}},
    {"type": "function", "function": {"name": "close_all_chrome", "description": "بستن همه Chrome", "parameters": {"type": "object", "properties": {}}}},
    {"type": "function", "function": {"name": "close_program", "description": "بستن برنامه", "parameters": {"type": "object", "properties": {"name": {"type": "string"}}, "required": ["name"]}}},
    {"type": "function", "function": {"name": "create_file", "description": "ساخت فایل", "parameters": {"type": "object", "properties": {"path": {"type": "string"}, "content": {"type": "string"}}, "required": ["path", "content"]}}},
    {"type": "function", "function": {"name": "read_file", "description": "خواندن فایل", "parameters": {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]}}},
    {"type": "function", "function": {"name": "delete_file", "description": "حذف فایل", "parameters": {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]}}},
    {"type": "function", "function": {"name": "list_files", "description": "لیست فایل‌ها", "parameters": {"type": "object", "properties": {"directory": {"type": "string"}}}}},
    {"type": "function", "function": {"name": "create_folder", "description": "ساخت پوشه", "parameters": {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]}}},
    {"type": "function", "function": {"name": "delete_folder", "description": "حذف پوشه", "parameters": {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]}}},
    {"type": "function", "function": {"name": "copy_file", "description": "کپی فایل", "parameters": {"type": "object", "properties": {"src": {"type": "string"}, "dst": {"type": "string"}}, "required": ["src", "dst"]}}},
    {"type": "function", "function": {"name": "move_file", "description": "انتقال فایل", "parameters": {"type": "object", "properties": {"src": {"type": "string"}, "dst": {"type": "string"}}, "required": ["src", "dst"]}}},
    {"type": "function", "function": {"name": "rename_file", "description": "تغییر نام", "parameters": {"type": "object", "properties": {"old": {"type": "string"}, "new": {"type": "string"}}, "required": ["old", "new"]}}},
    {"type": "function", "function": {"name": "take_screenshot", "description": "اسکرین‌شات", "parameters": {"type": "object", "properties": {}}}},
    {"type": "function", "function": {"name": "type_text", "description": "تایپ متن", "parameters": {"type": "object", "properties": {"text": {"type": "string"}}, "required": ["text"]}}},
    {"type": "function", "function": {"name": "press_key", "description": "زدن کلید", "parameters": {"type": "object", "properties": {"key": {"type": "string"}}, "required": ["key"]}}},
    {"type": "function", "function": {"name": "click_mouse", "description": "کلیک موس", "parameters": {"type": "object", "properties": {"x": {"type": "integer"}, "y": {"type": "integer"}}}}},
    {"type": "function", "function": {"name": "move_mouse", "description": "حرکت موس", "parameters": {"type": "object", "properties": {"x": {"type": "integer"}, "y": {"type": "integer"}}, "required": ["x", "y"]}}},
    {"type": "function", "function": {"name": "scroll_mouse", "description": "اسکرول", "parameters": {"type": "object", "properties": {"amount": {"type": "integer"}}, "required": ["amount"]}}},
    {"type": "function", "function": {"name": "get_time", "description": "ساعت", "parameters": {"type": "object", "properties": {}}}},
    {"type": "function", "function": {"name": "get_date", "description": "تاریخ", "parameters": {"type": "object", "properties": {}}}},
    {"type": "function", "function": {"name": "calculator", "description": "ماشین‌حساب", "parameters": {"type": "object", "properties": {"expression": {"type": "string"}}, "required": ["expression"]}}},
    {"type": "function", "function": {"name": "random_number", "description": "عدد تصادفی", "parameters": {"type": "object", "properties": {"min_val": {"type": "integer"}, "max_val": {"type": "integer"}}}}},
    {"type": "function", "function": {"name": "password_generator", "description": "پسورد", "parameters": {"type": "object", "properties": {"length": {"type": "integer"}}}}},
    {"type": "function", "function": {"name": "coin_flip", "description": "شیرخط", "parameters": {"type": "object", "properties": {}}}},
    {"type": "function", "function": {"name": "dice_roll", "description": "تاس", "parameters": {"type": "object", "properties": {"sides": {"type": "integer"}}}}},
    {"type": "function", "function": {"name": "encode_base64", "description": "Base64 encode", "parameters": {"type": "object", "properties": {"text": {"type": "string"}}, "required": ["text"]}}},
    {"type": "function", "function": {"name": "decode_base64", "description": "Base64 decode", "parameters": {"type": "object", "properties": {"text": {"type": "string"}}, "required": ["text"]}}},
    {"type": "function", "function": {"name": "hash_md5", "description": "MD5", "parameters": {"type": "object", "properties": {"text": {"type": "string"}}, "required": ["text"]}}},
    {"type": "function", "function": {"name": "hash_sha256", "description": "SHA256", "parameters": {"type": "object", "properties": {"text": {"type": "string"}}, "required": ["text"]}}},
    {"type": "function", "function": {"name": "generate_qr", "description": "QR Code", "parameters": {"type": "object", "properties": {"data": {"type": "string"}}, "required": ["data"]}}},
    {"type": "function", "function": {"name": "shorten_url", "description": "کوتاه‌کننده لینک", "parameters": {"type": "object", "properties": {"url": {"type": "string"}}, "required": ["url"]}}},
    {"type": "function", "function": {"name": "get_ip", "description": "IP", "parameters": {"type": "object", "properties": {}}}},
    {"type": "function", "function": {"name": "ping", "description": "Ping", "parameters": {"type": "object", "properties": {"host": {"type": "string"}}, "required": ["host"]}}},
    {"type": "function", "function": {"name": "system_info", "description": "اطلاعات سیستم", "parameters": {"type": "object", "properties": {}}}},
    {"type": "function", "function": {"name": "battery_status", "description": "باتری", "parameters": {"type": "object", "properties": {}}}},
    {"type": "function", "function": {"name": "volume_up", "description": "زیاد کردن صدا", "parameters": {"type": "object", "properties": {}}}},
    {"type": "function", "function": {"name": "volume_down", "description": "کم کردن صدا", "parameters": {"type": "object", "properties": {}}}},
    {"type": "function", "function": {"name": "volume_mute", "description": "قطع صدا", "parameters": {"type": "object", "properties": {}}}},
    {"type": "function", "function": {"name": "shutdown", "description": "خاموش کردن", "parameters": {"type": "object", "properties": {}}}},
    {"type": "function", "function": {"name": "restart", "description": "ری‌استارت", "parameters": {"type": "object", "properties": {}}}},
    {"type": "function", "function": {"name": "sleep_pc", "description": "Sleep", "parameters": {"type": "object", "properties": {}}}},
    {"type": "function", "function": {"name": "abort_shutdown", "description": "لغو خاموشی", "parameters": {"type": "object", "properties": {}}}},
    {"type": "function", "function": {"name": "open_app", "description": "باز کردن برنامه", "parameters": {"type": "object", "properties": {"name": {"type": "string"}}, "required": ["name"]}}},
    {"type": "function", "function": {"name": "open_folder", "description": "باز کردن پوشه", "parameters": {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]}}},
    {"type": "function", "function": {"name": "read_clipboard", "description": "خواندن کلیپ‌برد", "parameters": {"type": "object", "properties": {}}}},
    {"type": "function", "function": {"name": "write_clipboard", "description": "نوشتن کلیپ‌برد", "parameters": {"type": "object", "properties": {"text": {"type": "string"}}, "required": ["text"]}}},
    {"type": "function", "function": {"name": "minimize_window", "description": "Minimize", "parameters": {"type": "object", "properties": {}}}},
    {"type": "function", "function": {"name": "maximize_window", "description": "Maximize", "parameters": {"type": "object", "properties": {}}}},
    {"type": "function", "function": {"name": "close_window", "description": "بستن پنجره", "parameters": {"type": "object", "properties": {}}}},
    {"type": "function", "function": {"name": "switch_window", "description": "Alt+Tab", "parameters": {"type": "object", "properties": {}}}},
    {"type": "function", "function": {"name": "search_google", "description": "جستجوی گوگل", "parameters": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]}}},
    {"type": "function", "function": {"name": "search_youtube", "description": "جستجوی یوتیوب", "parameters": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]}}},
    {"type": "function", "function": {"name": "play_music", "description": "پخش موزیک", "parameters": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]}}},
    {"type": "function", "function": {"name": "weather", "description": "آب‌وهوا", "parameters": {"type": "object", "properties": {"city": {"type": "string"}}, "required": ["city"]}}},
    {"type": "function", "function": {"name": "translate", "description": "ترجمه", "parameters": {"type": "object", "properties": {"text": {"type": "string"}, "target": {"type": "string"}}, "required": ["text"]}}},
    {"type": "function", "function": {"name": "news", "description": "اخبار", "parameters": {"type": "object", "properties": {}}}},
    {"type": "function", "function": {"name": "joke", "description": "جوک", "parameters": {"type": "object", "properties": {}}}},
    {"type": "function", "function": {"name": "quote", "description": "سخن بزرگان", "parameters": {"type": "object", "properties": {}}}},
    {"type": "function", "function": {"name": "fact", "description": "دانستنی", "parameters": {"type": "object", "properties": {}}}},
    {"type": "function", "function": {"name": "word_count", "description": "شمارش کلمات", "parameters": {"type": "object", "properties": {"text": {"type": "string"}}, "required": ["text"]}}},
    {"type": "function", "function": {"name": "char_count", "description": "شمارش کاراکتر", "parameters": {"type": "object", "properties": {"text": {"type": "string"}}, "required": ["text"]}}},
    {"type": "function", "function": {"name": "reverse_text", "description": "معکوس", "parameters": {"type": "object", "properties": {"text": {"type": "string"}}, "required": ["text"]}}},
    {"type": "function", "function": {"name": "upper_text", "description": "حروف بزرگ", "parameters": {"type": "object", "properties": {"text": {"type": "string"}}, "required": ["text"]}}},
    {"type": "function", "function": {"name": "lower_text", "description": "حروف کوچک", "parameters": {"type": "object", "properties": {"text": {"type": "string"}}, "required": ["text"]}}},
    {"type": "function", "function": {"name": "capitalize_text", "description": "Capitalize", "parameters": {"type": "object", "properties": {"text": {"type": "string"}}, "required": ["text"]}}},
    {"type": "function", "function": {"name": "remove_spaces", "description": "حذف فاصله", "parameters": {"type": "object", "properties": {"text": {"type": "string"}}, "required": ["text"]}}},
    {"type": "function", "function": {"name": "trim_text", "description": "Trim", "parameters": {"type": "object", "properties": {"text": {"type": "string"}}, "required": ["text"]}}},
    {"type": "function", "function": {"name": "replace_text", "description": "جایگزینی", "parameters": {"type": "object", "properties": {"text": {"type": "string"}, "old": {"type": "string"}, "new": {"type": "string"}}, "required": ["text", "old", "new"]}}},
    {"type": "function", "function": {"name": "find_text", "description": "جستجو", "parameters": {"type": "object", "properties": {"text": {"type": "string"}, "substring": {"type": "string"}}, "required": ["text", "substring"]}}},
    {"type": "function", "function": {"name": "is_palindrome", "description": "پالیندروم", "parameters": {"type": "object", "properties": {"text": {"type": "string"}}, "required": ["text"]}}},
    {"type": "function", "function": {"name": "extract_numbers", "description": "استخراج اعداد", "parameters": {"type": "object", "properties": {"text": {"type": "string"}}, "required": ["text"]}}},
    {"type": "function", "function": {"name": "extract_emails", "description": "استخراج ایمیل", "parameters": {"type": "object", "properties": {"text": {"type": "string"}}, "required": ["text"]}}},
    {"type": "function", "function": {"name": "extract_urls", "description": "استخراج لینک", "parameters": {"type": "object", "properties": {"text": {"type": "string"}}, "required": ["text"]}}},
    {"type": "function", "function": {"name": "json_pretty", "description": "زیباسازی JSON", "parameters": {"type": "object", "properties": {"text": {"type": "string"}}, "required": ["text"]}}},
    {"type": "function", "function": {"name": "sort_lines", "description": "مرتب‌سازی خطوط", "parameters": {"type": "object", "properties": {"text": {"type": "string"}}, "required": ["text"]}}},
    {"type": "function", "function": {"name": "unique_lines", "description": "حذف تکراری", "parameters": {"type": "object", "properties": {"text": {"type": "string"}}, "required": ["text"]}}},
    {"type": "function", "function": {"name": "repeat_text", "description": "تکرار", "parameters": {"type": "object", "properties": {"text": {"type": "string"}, "times": {"type": "integer"}}, "required": ["text"]}}},
    {"type": "function", "function": {"name": "wrap_text", "description": "شکستن خط", "parameters": {"type": "object", "properties": {"text": {"type": "string"}, "width": {"type": "integer"}}, "required": ["text"]}}},
    {"type": "function", "function": {"name": "truncate_text", "description": "بریدن", "parameters": {"type": "object", "properties": {"text": {"type": "string"}, "length": {"type": "integer"}}, "required": ["text"]}}},
    {"type": "function", "function": {"name": "slugify", "description": "Slug", "parameters": {"type": "object", "properties": {"text": {"type": "string"}}, "required": ["text"]}}},
    {"type": "function", "function": {"name": "camel_case", "description": "camelCase", "parameters": {"type": "object", "properties": {"text": {"type": "string"}}, "required": ["text"]}}},
    {"type": "function", "function": {"name": "snake_case", "description": "snake_case", "parameters": {"type": "object", "properties": {"text": {"type": "string"}}, "required": ["text"]}}},
    {"type": "function", "function": {"name": "kebab_case", "description": "kebab-case", "parameters": {"type": "object", "properties": {"text": {"type": "string"}}, "required": ["text"]}}},
    {"type": "function", "function": {"name": "pascal_case", "description": "PascalCase", "parameters": {"type": "object", "properties": {"text": {"type": "string"}}, "required": ["text"]}}},
    {"type": "function", "function": {"name": "leet_speak", "description": "Leet speak", "parameters": {"type": "object", "properties": {"text": {"type": "string"}}, "required": ["text"]}}},
    {"type": "function", "function": {"name": "morse_encode", "description": "Morse", "parameters": {"type": "object", "properties": {"text": {"type": "string"}}, "required": ["text"]}}},
    {"type": "function", "function": {"name": "caesar_cipher", "description": "Caesar", "parameters": {"type": "object", "properties": {"text": {"type": "string"}, "shift": {"type": "integer"}}, "required": ["text"]}}},
    {"type": "function", "function": {"name": "rot13", "description": "ROT13", "parameters": {"type": "object", "properties": {"text": {"type": "string"}}, "required": ["text"]}}},
    {"type": "function", "function": {"name": "hex_encode", "description": "Hex encode", "parameters": {"type": "object", "properties": {"text": {"type": "string"}}, "required": ["text"]}}},
    {"type": "function", "function": {"name": "hex_decode", "description": "Hex decode", "parameters": {"type": "object", "properties": {"text": {"type": "string"}}, "required": ["text"]}}},
    {"type": "function", "function": {"name": "binary_encode", "description": "Binary", "parameters": {"type": "object", "properties": {"text": {"type": "string"}}, "required": ["text"]}}},
    {"type": "function", "function": {"name": "binary_decode", "description": "Binary decode", "parameters": {"type": "object", "properties": {"text": {"type": "string"}}, "required": ["text"]}}},
    {"type": "function", "function": {"name": "url_encode", "description": "URL encode", "parameters": {"type": "object", "properties": {"text": {"type": "string"}}, "required": ["text"]}}},
    {"type": "function", "function": {"name": "url_decode", "description": "URL decode", "parameters": {"type": "object", "properties": {"text": {"type": "string"}}, "required": ["text"]}}},
    {"type": "function", "function": {"name": "html_encode", "description": "HTML encode", "parameters": {"type": "object", "properties": {"text": {"type": "string"}}, "required": ["text"]}}},
    {"type": "function", "function": {"name": "html_decode", "description": "HTML decode", "parameters": {"type": "object", "properties": {"text": {"type": "string"}}, "required": ["text"]}}},
    {"type": "function", "function": {"name": "markdown_to_text", "description": "MD to text", "parameters": {"type": "object", "properties": {"text": {"type": "string"}}, "required": ["text"]}}},
    {"type": "function", "function": {"name": "lorem_ipsum", "description": "Lorem ipsum", "parameters": {"type": "object", "properties": {"words": {"type": "integer"}}}}},
    {"type": "function", "function": {"name": "uuid_generator", "description": "UUID", "parameters": {"type": "object", "properties": {}}}},
    {"type": "function", "function": {"name": "color_random", "description": "رنگ تصادفی", "parameters": {"type": "object", "properties": {}}}},
    {"type": "function", "function": {"name": "color_rgb", "description": "RGB to HEX", "parameters": {"type": "object", "properties": {"r": {"type": "integer"}, "g": {"type": "integer"}, "b": {"type": "integer"}}, "required": ["r", "g", "b"]}}},
    {"type": "function", "function": {"name": "days_between", "description": "فاصله روزها", "parameters": {"type": "object", "properties": {"date1": {"type": "string"}, "date2": {"type": "string"}}, "required": ["date1", "date2"]}}},
    {"type": "function", "function": {"name": "add_days", "description": "اضافه کردن روز", "parameters": {"type": "object", "properties": {"date_str": {"type": "string"}, "days": {"type": "integer"}}, "required": ["date_str", "days"]}}},
    {"type": "function", "function": {"name": "age_calculator", "description": "محاسبه سن", "parameters": {"type": "object", "properties": {"birthdate": {"type": "string"}}, "required": ["birthdate"]}}},
    {"type": "function", "function": {"name": "timer", "description": "تایمر", "parameters": {"type": "object", "properties": {"seconds": {"type": "integer"}}, "required": ["seconds"]}}},
    {"type": "function", "function": {"name": "stopwatch_start", "description": "کرنومتر", "parameters": {"type": "object", "properties": {}}}},
    {"type": "function", "function": {"name": "world_clock", "description": "ساعت جهانی", "parameters": {"type": "object", "properties": {"city": {"type": "string"}}}}},
    {"type": "function", "function": {"name": "currency_converter", "description": "تبدیل ارز", "parameters": {"type": "object", "properties": {"amount": {"type": "number"}, "from_curr": {"type": "string"}, "to_curr": {"type": "string"}}, "required": ["amount"]}}},
    {"type": "function", "function": {"name": "unit_converter", "description": "تبدیل واحد", "parameters": {"type": "object", "properties": {"value": {"type": "number"}, "from_unit": {"type": "string"}, "to_unit": {"type": "string"}}, "required": ["value", "from_unit", "to_unit"]}}},
    {"type": "function", "function": {"name": "wifi_list", "description": "لیست WiFi", "parameters": {"type": "object", "properties": {}}}},
    {"type": "function", "function": {"name": "speed_test", "description": "تست سرعت", "parameters": {"type": "object", "properties": {}}}},
    {"type": "function", "function": {"name": "dns_lookup", "description": "DNS", "parameters": {"type": "object", "properties": {"domain": {"type": "string"}}, "required": ["domain"]}}},
    {"type": "function", "function": {"name": "whois_lookup", "description": "WHOIS", "parameters": {"type": "object", "properties": {"domain": {"type": "string"}}, "required": ["domain"]}}},
    {"type": "function", "function": {"name": "port_scan", "description": "Port scan", "parameters": {"type": "object", "properties": {"host": {"type": "string"}, "ports": {"type": "string"}}, "required": ["host"]}}},
    {"type": "function", "function": {"name": "download_file", "description": "دانلود", "parameters": {"type": "object", "properties": {"url": {"type": "string"}, "path": {"type": "string"}}, "required": ["url"]}}},
    {"type": "function", "function": {"name": "compress_image", "description": "فشرده‌سازی عکس", "parameters": {"type": "object", "properties": {"path": {"type": "string"}, "quality": {"type": "integer"}}, "required": ["path"]}}},
    {"type": "function", "function": {"name": "resize_image", "description": "تغییر سایز عکس", "parameters": {"type": "object", "properties": {"path": {"type": "string"}, "width": {"type": "integer"}, "height": {"type": "integer"}}, "required": ["path", "width", "height"]}}},
    {"type": "function", "function": {"name": "convert_image", "description": "تبدیل فرمت عکس", "parameters": {"type": "object", "properties": {"path": {"type": "string"}, "fmt": {"type": "string"}}, "required": ["path"]}}},
    {"type": "function", "function": {"name": "pdf_to_text", "description": "PDF به متن", "parameters": {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]}}},
    {"type": "function", "function": {"name": "text_to_pdf", "description": "متن به PDF", "parameters": {"type": "object", "properties": {"text": {"type": "string"}, "path": {"type": "string"}}, "required": ["text", "path"]}}},
    {"type": "function", "function": {"name": "merge_pdfs", "description": "ادغام PDF", "parameters": {"type": "object", "properties": {"files": {"type": "string"}, "output": {"type": "string"}}, "required": ["files"]}}},
    {"type": "function", "function": {"name": "extract_zip", "description": "استخراج ZIP", "parameters": {"type": "object", "properties": {"path": {"type": "string"}, "dest": {"type": "string"}}, "required": ["path"]}}},
    {"type": "function", "function": {"name": "create_zip", "description": "ساخت ZIP", "parameters": {"type": "object", "properties": {"files": {"type": "string"}, "output": {"type": "string"}}, "required": ["files"]}}},
]

# ==================== Dispatcher ====================
FUNCTION_MAP = {
    "open_chrome": open_chrome, "close_last_chrome": close_last_chrome, "close_all_chrome": close_all_chrome,
    "close_program": close_program, "create_file": create_file, "read_file": read_file, "delete_file": delete_file,
    "list_files": list_files, "create_folder": create_folder, "delete_folder": delete_folder, "copy_file": copy_file,
    "move_file": move_file, "rename_file": rename_file, "take_screenshot": take_screenshot, "type_text": type_text,
    "press_key": press_key, "click_mouse": click_mouse, "move_mouse": move_mouse, "scroll_mouse": scroll_mouse,
    "get_time": get_time, "get_date": get_date, "get_datetime": get_datetime, "calculator": calculator,
    "random_number": random_number, "password_generator": password_generator, "coin_flip": coin_flip,
    "dice_roll": dice_roll, "encode_base64": encode_base64, "decode_base64": decode_base64,
    "hash_md5": hash_md5, "hash_sha256": hash_sha256, "generate_qr": generate_qr, "shorten_url": shorten_url,
    "get_ip": get_ip, "ping": ping, "system_info": system_info, "battery_status": battery_status,
    "volume_up": volume_up, "volume_down": volume_down, "volume_mute": volume_mute, "shutdown": shutdown,
    "restart": restart, "sleep_pc": sleep_pc, "abort_shutdown": abort_shutdown, "open_app": open_app,
    "open_folder": open_folder, "read_clipboard": read_clipboard, "write_clipboard": write_clipboard,
    "minimize_window": minimize_window, "maximize_window": maximize_window, "close_window": close_window,
    "switch_window": switch_window, "search_google": search_google, "search_youtube": search_youtube,
    "play_music": play_music, "weather": weather, "translate": translate, "news": news, "joke": joke,
    "quote": quote, "fact": fact, "word_count": word_count, "char_count": char_count, "line_count": line_count,
    "reverse_text": reverse_text, "upper_text": upper_text, "lower_text": lower_text, "capitalize_text": capitalize_text,
    "remove_spaces": remove_spaces, "trim_text": trim_text, "replace_text": replace_text, "split_text": split_text,
    "join_text": join_text, "find_text": find_text, "count_substring": count_substring, "starts_with": starts_with,
    "ends_with": ends_with, "is_palindrome": is_palindrome, "extract_numbers": extract_numbers,
    "extract_emails": extract_emails, "extract_urls": extract_urls, "json_pretty": json_pretty,
    "csv_to_table": csv_to_table, "sort_lines": sort_lines, "shuffle_lines": shuffle_lines, "unique_lines": unique_lines,
    "duplicate_lines": duplicate_lines, "repeat_text": repeat_text, "pad_left": pad_left, "pad_right": pad_right,
    "center_text": center_text, "wrap_text": wrap_text, "truncate_text": truncate_text, "slugify": slugify,
    "camel_case": camel_case, "snake_case": snake_case, "kebab_case": kebab_case, "pascal_case": pascal_case,
    "leet_speak": leet_speak, "morse_encode": morse_encode, "caesar_cipher": caesar_cipher, "rot13": rot13,
    "hex_encode": hex_encode, "hex_decode": hex_decode, "binary_encode": binary_encode, "binary_decode": binary_decode,
    "url_encode": url_encode, "url_decode": url_decode, "html_encode": html_encode, "html_decode": html_decode,
    "markdown_to_text": markdown_to_text, "lorem_ipsum": lorem_ipsum, "uuid_generator": uuid_generator,
    "guid_generator": guid_generator, "color_random": color_random, "color_rgb": color_rgb,
    "days_between": days_between, "add_days": add_days, "age_calculator": age_calculator, "timer": timer,
    "stopwatch_start": stopwatch_start, "world_clock": world_clock, "currency_converter": currency_converter,
    "unit_converter": unit_converter, "wifi_list": wifi_list, "speed_test": speed_test, "dns_lookup": dns_lookup,
    "whois_lookup": whois_lookup, "port_scan": port_scan, "download_file": download_file, "upload_file": upload_file,
    "compress_image": compress_image, "resize_image": resize_image, "convert_image": convert_image,
    "pdf_to_text": pdf_to_text, "text_to_pdf": text_to_pdf, "merge_pdfs": merge_pdfs, "extract_zip": extract_zip,
    "create_zip": create_zip,
}

# ==================== UI ====================
st.markdown('<h1 class="jarvis-title" style="text-align:center; font-size:3rem;">🧠 JARVIS AI AGENT</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align:center; color:rgba(0,210,255,0.6); font-size:1.1rem;">Just A Rather Very Intelligent System</p>', unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = [{
        "role": "system",
        "content": "You are JARVIS — a powerful multilingual AI assistant with 100+ capabilities. You can control Chrome, files, system, mouse/keyboard, calculate, convert, encode, and much more. Always respond in the SAME LANGUAGE as the user. Be concise, helpful, and proactive."
    }]
if "chrome_pids" not in st.session_state: st.session_state.chrome_pids = []

for msg in st.session_state.messages[1:]:
    with st.chat_message(msg["role"], avatar="🧑‍💻" if msg["role"]=="user" else "🤖"):
        st.write(msg["content"])
        if msg.get("audio"): st.audio(msg["audio"], format="audio/mp3")
        if msg.get("screenshot"): st.image(msg["screenshot"], caption="📸")

st.markdown("### 🎤 صدا")
audio = mic_recorder(start_prompt="🎙️", stop_prompt="⏹️", just_once=True, key="mic_jarvis")
user_text = st.chat_input("پیام تایپ کنید...")

if audio is not None:
    with st.spinner("🎙️ در حال تشخیص صدا..."):
        recognized, detected_lang = transcribe_audio(audio)
    if not recognized.startswith("❌"):
        st.success(f"🎙️ [{detected_lang}] {recognized}")
        user_text = recognized
        if detected_lang: st.session_state.last_lang = detected_lang
    else:
        st.error(recognized)
        user_text = None

if user_text:
    st.session_state.messages.append({"role": "user", "content": user_text})
    with st.chat_message("user", avatar="🧑‍💻"): st.write(user_text)

    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("🤖 JARVIS در حال پردازش..."):
            response = ask_llm(st.session_state.messages, ALL_TOOLS)
        if not response:
            st.write("❌ خطا در اتصال به LLM.")
            st.stop()

        msg = response.choices[0].message

        if msg.tool_calls:
            for tool in msg.tool_calls:
                func_name = tool.function.name
                args = json.loads(tool.function.arguments)
                st.info(f"🔧 {func_name}")

                if func_name in FUNCTION_MAP:
                    try:
                        result = FUNCTION_MAP[func_name](**args)
                    except Exception as e:
                        result = f"❌ خطا در اجرا: {e}"
                else:
                    result = f"❌ تابع ناشناخته: {func_name}"

                st.write(f"📋 {result}")
                st.session_state.messages.append({"role": "tool", "tool_call_id": tool.id, "content": result})

            final = ask_llm(st.session_state.messages)
            reply = final.choices[0].message.content if final else "✅ انجام شد."
        else:
            reply = msg.content

        st.write(reply)
        st.session_state.messages.append({"role": "assistant", "content": reply})

        # TTS با تشخیص زبان
        try:
            lang = st.session_state.get("last_lang", "")
            if not lang:
                try: lang = detect(reply)
                except: lang = "en"
            if lang not in VOICE_MAP: lang = "en"
            with st.spinner("🔊"):
                audio_path = run_tts(reply, lang)
            st.audio(audio_path, format="audio/mp3")
            st.session_state.messages[-1]["audio"] = audio_path
        except Exception as e:
            st.warning(f"⚠️ TTS: {e}")

st.markdown("---")
st.caption("🚀 JARVIS AI Agent | 100+ قابلیت | 50+ زبان | 9Router + Whisper + Edge-TTS")
from dotenv import load_dotenv
import os

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
# .env dan olingan ma'lumot har doim matn (string) bo'ladi, 
# shuning uchun uni songa (int) aylantiramiz
ADMIN_ID = int(os.getenv("ADMIN_ID"))
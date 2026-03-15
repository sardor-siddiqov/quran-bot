import asyncio
import logging
import sqlite3
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

# --- 1. SOZLAMALAR ---
BOT_TOKEN = "8726258891:AAH1cHcLUaKLzipyCX3UoUI0p_Fcb4JnTcs"
ADMIN_ID = 6603429654  # O'zingizning Telegram ID-ingiz
logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


# --- 2. BAZA BILAN ISHLASH (SQLITE) ---
def init_db():
    conn = sqlite3.connect("quran_bot.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            full_name TEXT
        )
    """)
    conn.commit()
    conn.close()


def add_user(user_id, username, full_name):
    conn = sqlite3.connect("quran_bot.db")
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO users VALUES (?, ?, ?)", (user_id, username, full_name))
    conn.commit()
    conn.close()


def get_stats():
    conn = sqlite3.connect("quran_bot.db")
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users")
    count = cursor.fetchone()[0]
    conn.close()
    return count


def get_all_users():
    conn = sqlite3.connect("quran_bot.db")
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, full_name FROM users")
    users = cursor.fetchall()
    conn.close()
    return users


# --- 3. SURALAR RO'YXATI (114 TA) ---
SURA_NAMES = {
    1: "Fotiha", 2: "Baqara", 3: "Oli Imron", 4: "Niso", 5: "Moida", 6: "An'om", 7: "A'rof", 8: "Anfol", 9: "Tavba",
    10: "Yunus", 11: "Hud", 12: "Yusuf", 13: "Ra'd", 14: "Ibrohim", 15: "Hijr", 16: "Nahl", 17: "Isro", 18: "Kahf",
    19: "Maryam", 20: "Toha", 21: "Anbiyo", 22: "Haj", 23: "Mo'minun", 24: "Nur", 25: "Furqon", 26: "Shuaro",
    27: "Naml", 28: "Qasas", 29: "Ankabut", 30: "Rum", 31: "Luqmon", 32: "Sajda", 33: "Ahzob", 34: "Saba",
    35: "Fotir", 36: "Yosin", 37: "Saffot", 38: "Sod", 39: "Zumar", 40: "G'ofir", 41: "Fussilat", 42: "Sho'ro",
    43: "Zuhruf", 44: "Duxon", 45: "Josiya", 46: "Ahqof", 47: "Muhammad", 48: "Fath", 49: "Hujurot", 50: "Qof",
    51: "Zariyat", 52: "Tur", 53: "Najm", 54: "Qamar", 55: "Rahmon", 56: "Voqea", 57: "Hadid", 58: "Mujodala",
    59: "Hashr", 60: "Mumtahana", 61: "Saff", 62: "Juma", 63: "Munofiqun", 64: "Tag'obun", 65: "Taloq",
    66: "Tahrim", 67: "Mulk", 68: "Qalam", 69: "Haqqa", 70: "Maorij", 71: "Nuh", 72: "Jin", 73: "Muzzammil",
    74: "Muddassir", 75: "Qiyomat", 76: "Inson", 77: "Mursalat", 78: "Naba", 79: "Nazi'at", 80: "Abasa",
    81: "Takvir", 82: "Infitor", 83: "Mutaffifun", 84: "Inshiqoq", 85: "Buruj", 86: "Toriq", 87: "A'lo",
    88: "G'oshiya", 89: "Fajr", 90: "Balad", 91: "Shams", 92: "Layl", 93: "Zuho", 94: "Sharh", 95: "Tiyn",
    96: "Alaq", 97: "Qadr", 98: "Bayyina", 99: "Zalzala", 100: "Odiyat", 101: "Qoria", 102: "Takasur",
    103: "Asr", 104: "Humaza", 105: "Fil", 106: "Quraysh", 107: "Ma'un", 108: "Kavsar", 109: "Kofirun",
    110: "Nasr", 111: "Masad", 112: "Ixlos", 113: "Falaq", 114: "Nos"
}

# --- 4. AUDIO ID BAZASI (SIZ YUBORGAN IDLAR) ---
AUDIOS = {
    "tilovat": {
        1: "CQACAgQAAxkBAAMLabbjr6LKLkn2SOdpBY1jnga4wzwAAkAOAAMTEFJHFDA3s_1hgDoE",
        2: "CQACAgUAAxkBAAMZabbn7NxB27Rsp_nlVdUpJgIlIYQAAqsEAALlTtIDMP6g9t6kf9c6BA",
        3: "CQACAgUAAxkBAAMiabbo1ZS1ZSe0e5UCM3wl1CzK4t0AAqwEAALlTtIDLkd41RH7ldA6BA",
        4: "CQACAgIAAxkBAAMjabbo1axSHhuGA83fFfbHgnsoEukAAvMNAAKeQ6BIPK_Fpge9KEo6BA",
        5: "CQACAgIAAxkBAAMkabbo1XlxAAFXfup6fn-8nvWZzXFeAAL0DQACnkOgSJmtzNzq2mIuOgQ",
        6: "CQACAgIAAxkBAAMlabbo1e4x074ElSXOkHmh65Xv2w8AAvUNAAKeQ6BIdIMEBHs5S2o6BA",
        7: "CQACAgIAAxkBAAMmabbo1fQKKupn_bUkT0i2W6eOcb4AAvYNAAKeQ6BIPywwSfol7IQ6BA",
        8: "CQACAgIAAxkBAAMnabbo1Xn3nEa34yLDj6P4WaPdqq8AAvcNAAKeQ6BIiyMannVjZeA6BA",
        9: "CQACAgIAAxkBAAMoabbo1QolNGJyBtphNoszhsskrK4AAvgNAAKeQ6BIDEwAAbfEv4-NOgQ",
        10: "CQACAgIAAxkBAAMpabbo1aCzukNZBAoLR8TiBaWFcKIAAvkNAAKeQ6BICUixeQm5Q4E6BA",
        11: "CQACAgIAAxkBAANDabbqK_Achza5xhTymCo0OhnXIZAAAvoNAAKeQ6BIq_e9dNNr3NU6BA",
        12: "CQACAgIAAxkBAANEabbqKwaccNe8FfTIaG-YGP0sEnIAAvwNAAKeQ6BI6-kryjcUErc6BA",
        13: "CQACAgIAAxkBAANFabbqK5u0wN7oxWzSFm68UW0Ct80AAv0NAAKeQ6BIlD4ezphnzZc6BA",
        14: "CQACAgIAAxkBAANGabbqK9OLH1up56JM1mkNeRPEaVQAAv4NAAKeQ6BICcmScH6Q1o46BA",
        15: "CQACAgIAAxkBAANHabbqKzktBlM5OmUDzcbIyBsPIpEAAv8NAAKeQ6BIHujvQO2LggQ6BA",
        16: "CQACAgIAAxkBAANIabbqK0kyYvHrBzecba1bZCN-0SoAAgIOAAKeQ6BId0b0pwi5cn46BA",
        17: "CQACAgIAAxkBAANJabbqK0sMFEUiT5VDrzDiGw2MwB8AAgMOAAKeQ6BIDw8zAVZQt346BA",
        18: "CQACAgIAAxkBAANKabbqKzowGSDvP5E0PzTQfcZLF8EAAgQOAAKeQ6BIRJjrDXSS0xc6BA",
        19: "CQACAgIAAxkBAANLabbqKzEQg4AH732lZyeFi2-5y9QAAgUOAAKeQ6BI5srOEkLVd9k6BA",
        20: "CQACAgIAAxkBAANMabbqK4QarB-qutBd1ECo-_Hwr-YAAgYOAAKeQ6BI2B_3wrm8tmc6BA",
        21: "CQACAgIAAxkBAANXabbqXU7apPmJDk7bDu6Y9jHbY3YAAgcOAAKeQ6BINKbwqAyPl2U6BA",
        22: "CQACAgIAAxkBAANYabbqXYcV3ATrRQfiSHA5gLnvu08AAggOAAKeQ6BILaLo_MIp3_o6BA",
        23: "CQACAgIAAxkBAANZabbqXTNZswfZUHE_X0BuOQ5gZpYAAgkOAAKeQ6BIhk6Z3EffF7E6BA",
        24: "CQACAgIAAxkBAANaabbqXcY0gTvWhJUig34aClUAAfZ2AAIKDgACnkOgSERwkGQmgDSAOgQ",
        25: "CQACAgIAAxkBAANbabbqXVbkxwEpVSGhkU7uDCGQhqUAAgsOAAKeQ6BIHkdY_RJpb_U6BA",
        26: "CQACAgIAAxkBAANcabbqXZX2606LRGwHDdhWbel9Nl4AAgwOAAKeQ6BI4TUdKz8e3aY6BA",
        27: "CQACAgIAAxkBAANdabbqXWyrjoPLYJZC_tc2_mAyPFcAAg4OAAKeQ6BI-fFUI6JTVi46BA",
        28: "CQACAgIAAxkBAANeabbqXUwnv-h3mCdSTtH49Eh6QDYAAg8OAAKeQ6BIg_O0L-iUPtY6BA",
        29: "CQACAgIAAxkBAANfabbqXejgTKu1OZStAiBt6i9J2pEAAhAOAAKeQ6BIq3fzyaeixZ06BA",
        30: "CQACAgIAAxkBAANgabbqXdhY1gIpDeQ-ueVt1yuHF8cAAhEOAAKeQ6BIIPX-0wwj-fc6BA",
        31: "CQACAgIAAxkBAANrabbqhVI2xvEL3Nd9n7Lr43kDSxUAAhIOAAKeQ6BIGF9Jt_7vKWI6BA",
        32: "CQACAgIAAxkBAANsabbqhRyeLKDLFx36V43y2i4e9wIAAhMOAAKeQ6BIzEGDuoCNXlE6BA",
        33: "CQACAgIAAxkBAANtabbqhc8i2lKEZp3uxzQTsUjMLnIAAhQOAAKeQ6BI5ZhFCj-LtrQ6BA",
        34: "CQACAgIAAxkBAANuabbqhXZ4eg7LGZS083o-e57wB_4AAhUOAAKeQ6BILiSwWP-7o2o6BA",
        35: "CQACAgIAAxkBAANvabbqhRHoECRAvVMbne3IYxrb73AAAhYOAAKeQ6BIHLQE-Ni9XjA6BA",
        36: "CQACAgIAAxkBAANwabbqhbHrUURanUwpZEdV-sBlmnAAAhcOAAKeQ6BIPl_1OVGnnkE6BA",
        37: "CQACAgIAAxkBAANxabbqhZh4QYUTlRu7p4PICPR3GRsAAhgOAAKeQ6BIf3ivn6MRAq06BA",
        38: "CQACAgIAAxkBAANyabbqhREyy3nFKLdhk3lojYhvSyYAAhkOAAKeQ6BIP8G1Qca_DKU6BA",
        39: "CQACAgIAAxkBAANzabbqhUm8bKUNuZPSU6LRFGiK4RkAAhoOAAKeQ6BI9E5Yw_ogIZk6BA",
        40: "CQACAgIAAxkBAAN0abbqhSkzKSMDZrSVf68ftY6T0QwAAhsOAAKeQ6BIX4F6-nBDI3Q6BA",
        41: "CQACAgIAAxkBAAN_abbqtqZh5UQV2FpkLRay9DoidSkAAhwOAAKeQ6BI4g0vICryrvs6BA",
        42: "CQACAgIAAxkBAAOAabbqth-pcO9Z31iFmXviMy6wi2YAAh0OAAKeQ6BI8NtUiOQaiJ86BA",
        43: "CQACAgIAAxkBAAOBabbqtu4Xfy1qDluaoLhU5idnJ6oAAh4OAAKeQ6BIQHEozD7ukVw6BA",
        44: "CQACAgIAAxkBAAOCabbqtp5KeFkxj3IhRvMka_rALpsAAh8OAAKeQ6BIEnKI-fp6l886BA",
        45: "CQACAgIAAxkBAAODabbqtgVMNjdulHkDE6Ag1qYRjB0AAiAOAAKeQ6BIsSJfTnfIwbw6BA",
        46: "CQACAgIAAxkBAAOEabbqtnpaWqOQQn3Umih0wNhqI3sAAiEOAAKeQ6BIuFjo6FWK2Gk6BA",
        47: "CQACAgIAAxkBAAOFabbqtsSU4gRGBYiuoJ12Bmvp7q0AAiIOAAKeQ6BIPiCjG-w0q5I6BA",
        48: "CQACAgIAAxkBAAOGabbqtkfk7bR2V_pH7OwAAUCU04UUAAIjDgACnkOgSLXMF9Ik4X9uOgQ",
        49: "CQACAgIAAxkBAAOHabbqtm5kT8lkFlUpNyO1IQs79akAAiQOAAKeQ6BI1Tqdiohyx5k6BA",
        50: "CQACAgIAAxkBAAOIabbqtmjUnv9pirPSGUWJapys0kkAAiUOAAKeQ6BIT1V4O9n0rlU6BA",
        51: "CQACAgIAAxkBAAOTabbq4I9UliGzKpsnf18uQD43xbcAAiYOAAKeQ6BIv3pEhaUc5Bk6BA",
        52: "CQACAgIAAxkBAAOUabbq4Bnc4iSZwm7d-adZxbn6KUoAAicOAAKeQ6BIc4b7JvMpi4Q6BA",
        53: "CQACAgIAAxkBAAOVabbq4OcQ6EMOU163IMSuxO-CzN0AAigOAAKeQ6BIwcwGp39d6UM6BA",
        54: "CQACAgIAAxkBAAOWabbq4F-W9hd9MnoEFmf5V1LypLMAAikOAAKeQ6BITusdl2sS0P46BA",
        55: "CQACAgIAAxkBAAOXabbq4H248Xmdo7CbofiH5vgHVXsAAioOAAKeQ6BIoEt_akptKRk6BA",
        56: "CQACAgIAAxkBAAOYabbq4CyXiTYdmxWwTo6nzXkrbhAAAisOAAKeQ6BI9GRP6BF5Inw6BA",
        57: "CQACAgIAAxkBAAOZabbq4CaEqB6OrDPywy8-UNIzw54AAiwOAAKeQ6BI1Ovkmucts2E6BA",
        58: "CQACAgIAAxkBAAOaabbq4NbCRkjgYyl0WKV4qgiqg3AAAi0OAAKeQ6BIb7keNDj8t506BA",
        59: "CQACAgIAAxkBAAObabbq4LIsGVlJOFqRHt5ExO9peO0AAi4OAAKeQ6BIrOYyx7FFNxA6BA",
        60: "CQACAgIAAxkBAAOcabbq4C1J1L9PqHHdFCv-VkW9m-MAAi8OAAKeQ6BI2EJe_OurgSo6BA",
        61: "CQACAgIAAxkBAAOnabbrCzIgopqmCFsZEYRdKzWzS_8AAjAOAAKeQ6BI9b2pO21QSYM6BA",
        62: "CQACAgIAAxkBAAOoabbrC1IJvcwcHxYZukXYPXvnG0wAAjEOAAKeQ6BIR_Ic2sTeONU6BA",
        63: "CQACAgIAAxkBAAOpabbrC2tb3IRHMX8_yWK-lcNtrKQAAjIOAAKeQ6BIjyu5-izrGjM6BA",
        64: "CQACAgIAAxkBAAOqabbrC5Ufp2ozt2UgDQcqttijrToAAjMOAAKeQ6BIJvTebVfAZuY6BA",
        65: "CQACAgIAAxkBAAOrabbrC_zNOgABlq5J6zmCyDeOQ3O4AAI0DgACnkOgSKz5K7aUE-6JOgQ",
        66: "CQACAgIAAxkBAAOsabbrC1BQj_DJel93xJn8jyLmti8AAjUOAAKeQ6BID3rbe3MjTIs6BA",
        67: "CQACAgIAAxkBAAOtabbrC2juwJubztq3sXnt1beHv3YAAjYOAAKeQ6BIkOP3nn5XTfI6BA",
        68: "CQACAgIAAxkBAAOuabbrC4qhhVxENVLc-ou3kfdQYXYAAjcOAAKeQ6BIg9ASavQZg-06BA",
        69: "CQACAgIAAxkBAAOvabbrC9fFsmaue9AVb8PzAem72CUAAjgOAAKeQ6BIS6cKKIjK22s6BA",
        70: "CQACAgIAAxkBAAOwabbrC7izVCAchu2wSMaMhJlUPIUAAjkOAAKeQ6BIh3fvXFihC_U6BA",
        71: "CQACAgIAAxkBAAO7abbrLutmBKwzUFaQZ7f3DXGnA3cAAjoOAAKeQ6BILob-t_lThCI6BA",
        72: "CQACAgIAAxkBAAO8abbrLnltP4Kr23ijCgqIdF5KEP4AAjsOAAKeQ6BI4VoEEwXeGCk6BA",
        73: "CQACAgIAAxkBAAO9abbrLot_Us019dMP2B5ZwVHmWFQAAjwOAAKeQ6BILOFc9q2m9pQ6BA",
        74: "CQACAgIAAxkBAAO-abbrLnO1QRebIvXvkdhC31p1LBkAAj0OAAKeQ6BIXFdi3gk9ns06BA",
        75: "CQACAgIAAxkBAAO_abbrLkieRdf0KAT3066L73RJ_UUAAj4OAAKeQ6BIt5woBRJmKaA6BA",
        76: "CQACAgIAAxkBAAPAabbrLj0KOKwFqNjKRgHazRtd4ZwAAj8OAAKeQ6BINTACzLlnNSs6BA",
        77: "CQACAgIAAxkBAAPBabbrLorImSR0G3Lj8rTgf3m_yjoAAkAOAAKeQ6BIoS8RnUJ7k_I6BA",
        78: "CQACAgIAAxkBAAPCabbrLt4bX3xEJPYW304j_d7pAfEAAkEOAAKeQ6BIpR-bRV5Dsik6BA",
        79: "CQACAgIAAxkBAAPDabbrLtfpCx-pOJt28mnG3AGIZWYAAkIOAAKeQ6BIGSwVQ3ttPvg6BA",
        80: "CQACAgIAAxkBAAPEabbrLrkwP231f-9Y0-3ovFPT6mwAAkMOAAKeQ6BI6IEW74q55zM6BA",
        81: "CQACAgIAAxkBAAPPabbre3LQDlO9hGQmjymDh4temJwAAkQOAAKeQ6BIf-eFQ3YAAS-SOgQ",
        82: "CQACAgIAAxkBAAPQabbre_kPqxi8ucqspO15t0hr1KgAAkYOAAKeQ6BIBXGY3kcTo406BA",
        83: "CQACAgIAAxkBAAPRabbrewHjQC2ArSiwjmXus3mq6foAAkcOAAKeQ6BIgAABUoMg-5-pOgQ",
        84: "CQACAgIAAxkBAAPSabbre-7kPuoqXhIMvDTmdP9_o_EAAkgOAAKeQ6BIF0h5y9hh63E6BA",
        85: "CQACAgIAAxkBAAPTabbre8gQ_CQ4FPMsmi3aeeORkpMAAkkOAAKeQ6BI8eUAAZu9H-RtOgQ",
        86: "CQACAgIAAxkBAAPUabbreyz1w4pr2kZh8oel_RfqghUAAkoOAAKeQ6BIYa5YFnHFLxs6BA",
        87: "CQACAgIAAxkBAAPVabbrezENwbi3yKg374dkU5k8tkEAAksOAAKeQ6BIBdboNmgM87A6BA",
        88: "CQACAgIAAxkBAAPWabbre2hRwdDcAQ8XiFjoeveCI2QAAkwOAAKeQ6BIljhOWIIv2lM6BA",
        89: "CQACAgIAAxkBAAPXabbre07mVCizbg65cSGZTFY_XygAAk0OAAKeQ6BIXAsyJxJEAv86BA",
        90: "CQACAgIAAxkBAAPYabbre3Z9TlLpTTRzMJsB3b2imywAAk4OAAKeQ6BIBMTLxsyxS3s6BA",
        91: "CQACAgIAAxkBAAPjabbrts5v-67AMNpcprEWy1EVUHAAAk8OAAKeQ6BIwL-4O7gsxjg6BA",
        92: "CQACAgIAAxkBAAPkabbrtoS_mlEQ6iT9i3CJFVBoBuEAAlEOAAKeQ6BIE7BaMKg1h486BA",
        93: "CQACAgIAAxkBAAPlabbrtqyNuhrdFBAEIAjVScq5J0kAAlAOAAKeQ6BIYueoqRbV4hE6BA",
        94: "CQACAgIAAxkBAAPmabbrtpc1HUvhVndN__WvwGySvuMAAlMOAAKeQ6BIKMkRCeQzBfs6BA",
        95: "CQACAgIAAxkBAAPnabbrtpc1HUvhVndN__WvwGySvuMAAlMOAAKeQ6BIKMkRCeQzBfs6BA",
        96: "CQACAgIAAxkBAAPoabbrtu5fPkgyzGsn2Wf30QaB7AwAAlQOAAKeQ6BIprPV4NY53os6BA",
        97: "CQACAgIAAxkBAAPpabbrtlDa79_R1PCRYypovf7Tll8AAlUOAAKeQ6BIb6NI8kYSKI46BA",
        98: "CQACAgIAAxkBAAPqabbrtliXw9E1zf85t1lyLxXE7EoAAlYOAAKeQ6BIvuryKxrOopA6BA",
        99: "CQACAgIAAxkBAAPrabbrtgz7GdxDOXBkJ_jYeOh6mGUAAlcOAAKeQ6BIIJ43ubHruDw6BA",
        100: "CQACAgIAAxkBAAPsabbrtiBTIHhhWRhY6Fpd0EpXt0sAAlgOAAKeQ6BIY9MB6eUW2TI6BA",
        101: "CQACAgIAAxkBAAP2abbsBqiNoUPtI9aIOCeGk4rq6_UAAlkOAAKeQ6BI0Oz0Ol6yU0c6BA",
        102: "CQACAgIAAxkBAAP3abbsBoyVLOlxSya4jAUyOnHnKv8AAloOAAKeQ6BIwwABKEaiHSC8OgQ",
        103: "CQACAgIAAxkBAAP4abbsBkXyIc_xxDQiHqiaPh2cAw0AAlsOAAKeQ6BIWL2UG2TgHCY6BA",
        104: "CQACAgIAAxkBAAP5abbsBtap22Go-gIERVgEIphz74IAAlwOAAKeQ6BIWUUkRLrTBb46BA",
        105: "CQACAgIAAxkBAAP6abbsBiP8oAl625Od8Eo3SThSwScAAl0OAAKeQ6BIK5EI8zLExXU6BA",
        106: "CQACAgIAAxkBAAP7abbsBnFYyG5R-D6PIMDBXBgan5QAAl4OAAKeQ6BIIbwDp13z3GY6BA",
        107: "CQACAgIAAxkBAAP8abbsBo6drXOPwGZ8ELUyuqeTNTUAAl8OAAKeQ6BIjuyu5AAB4x11OgQ",
        108: "CQACAgIAAxkBAAP9abbsBjsMVDzuDy7ZfA2b9Kq4E-cAAmAOAAKeQ6BI9Vh3Ys4qz-Q6BA",
        109: "CQACAgIAAxkBAAP-abbsBs5wk4hqRQM6_rEPbLWZjToAAmEOAAKeQ6BI7UaTe1lV4A46BA",
        110: "CQACAgIAAxkBAAP_abbsBrqHO3zpbMpD0r5MukBZWYcAAmIOAAKeQ6BIkng-dsrpZ946BA",
        111: "CQACAgIAAxkBAAIBCmm27CHly4CN-FUHNqdY5dDf0UDYAAJjDgACnkOgSP8zCOIt-mmfOgQ",
        112: "CQACAgIAAxkBAAIBC2m27CFUKctCfqwEJ1V32aiknvp9AAJlDgACnkOgSFJN0if0k5urOgQ",
        113: "CQACAgIAAxkBAAIBDGm27CFCVrZf_4Nb6kggbi0Zd4qtAAJmDgACnkOgSINptk3sE0wnOgQ",
        114: "CQACAgIAAxkBAAIBDWm27CHPp-jddTHapjEtypbOp1r_AAJnDgACnkOgSCHil1RoJN49OgQ",
    },
    "tafsir": {
        1: "CQACAgIAAxkBAAIBGmm273T1-teu3SUQPC86SaEQSPG3AAJDDQACEToJS0FN19lDgV1OOgQ",
        2: "CQACAgIAAxkBAAIBG2m273QkGaX5rD8YuvkmsB_aElNLAAJFDQACEToJS5FItdIV8XJqOgQ",
        3: "CQACAgIAAxkBAAIBHGm273Ruk6z3exEQNg71kKwOdeFEAAJIDQACEToJS3mnV96h6iR5OgQ",
        4: "CQACAgIAAxkBAAIBHWm273Q4SrG6wAM32G7P96zFXUqOAAJKDQACEToJS3YvQoRtjWjEOgQ",
        5: "CQACAgIAAxkBAAIBHmm273Q9_fuwLEaeqNVAeQABvmZr7QACTQ0AAhE6CUs_i7SHZeUaNzoE",
        6: "CQACAgIAAxkBAAIBH2m273RZGS_bvk3JpbPpixE-vC8oAAJPDQACEToJS1eA_ri6YC_iOgQ",
        7: "CQACAgIAAxkBAAIBIGm273R8ib--7sm5Lm-5LcGaCZqfAAJSDQACEToJS5lghHbylbLSOgQ",
        8: "CQACAgIAAxkBAAIBIWm273QdYeKkaqAzJIpHsI-RBh9lAAJTDQACEToJSws1Yv9N9_C8OgQ",
        9: "CQACAgIAAxkBAAIBImm273SbNe0-0mmxDvewSXV2nsbZAAJUDQACEToJSx3YrLQ05WiDOgQ",
        10: "CQACAgIAAxkBAAIBI2m273QHlq4ry-kVShjqZJmfAi-WAAJVDQACEToJS-qH7tRlwFePOgQ",
        11: "CQACAgIAAxkBAAIBJ2m273SAUX_ecNbjKv6afM6XzS8_AAJWDQACEToJS0UflM-5rnSmOgQ",
        12: "CQACAgIAAxkBAAIBJGm273TyCleVMeHXTtMSwFCLDOVhAAJXDQACEToJSzbAJZFZzcA-OgQ",
        13: "CQACAgIAAxkBAAIBJWm273T6GgW244C49PLrVimt7TveAAJYDQACEToJSyeL9ZN9Bs8xOgQ",
        14: "CQACAgIAAxkBAAIBJmm273QvKCecYR7wQOLUVMJTYfsRAAJZDQACEToJS5xoPxDfLdPUOgQ",
        15: "CQACAgIAAxkBAAIBKGm273SAkZjj4V0INHNeiLJ4GPsLAAJaDQACEToJS09bN01Pkwg0OgQ",
        16: "CQACAgIAAxkBAAIBKmm273RxMn0iyRtAQ50vIE3a8TAmAAJbDQACEToJS3G7WnjPkBzaOgQ",
        17: "CQACAgIAAxkBAAIBK2m273QCXR4GGMRouXHQSb8XWZsGAAJcDQACEToJSxPECfMYbXAbOgQ",
        18: "CQACAgIAAxkBAAICqWm28q7EgEG1AaNALmB3YwvUY97tAAJeDQACEToJS8FMv-y1WFheOgQ",
        19: "CQACAgIAAxkBAAIBKWm273RwcFsuaG5Wwj39v1otxZQDAAJhDQACEToJS9_R5XUkdN41OgQ",
        20: "CQACAgIAAxkBAAIBLmm273R2kvTrHTqCsTJeMvPG84rSAAJiDQACEToJS7b8XapRik0hOgQ",
        21: "CQACAgIAAxkBAAIBLGm273RFU8bzfTr9rO2Z6c4scTXUAAJjDQACEToJS5DDrEXdtGAcOgQ",
        22: "CQACAgIAAxkBAAIBLWm273REx02a_GdzSimMQ1spr0PFAAJkDQACEToJS1TDMKDAQtEWOgQ",
        23: "CQACAgIAAxkBAAIBL2m273QB8H0wZS_-KVI33UEUvw0nAAJlDQACEToJS0pcBXKoBRlbOgQ",
        24: "CQACAgIAAxkBAAIBMGm273RGAVrmHI6j9SEMlPZH45urAAJmDQACEToJSw_lTa72iNIGOgQ",
        25: "CQACAgIAAxkBAAIBMWm273TCauQ4_kHLpnWy4Rpe_dA3AAJoDQACEToJS9-96vwoGTmzOgQ",
        26: "CQACAgIAAxkBAAIBMmm273R5kvjckq57AlEEAn7dwXzUAAJpDQACEToJS_djVpBsOzLLOgQ",
        27: "CQACAgIAAxkBAAIBM2m273QanpdoD-kkH_KYyipVFGiOAAJqDQACEToJS4MG58jLvrwHOgQ",
        28: "CQACAgIAAxkBAAIBNGm273SUlXEiTHkSMiFwftI7MKoZAAJrDQACEToJS5xUQ1bgviKNOgQ",
        29: "CQACAgIAAxkBAAIBOGm273QHq2dJvLIXPf2kCA6sp5cMAAJsDQACEToJS6GbpQXA6JvoOgQ",
        30: "CQACAgIAAxkBAAIBNWm273RsrUl_XtoNPORaS-9cLkHSAAJtDQACEToJS5QMjHNSARlsOgQ",
        31: "CQACAgIAAxkBAAIBNmm273QrVVfbuR1RiDE56IML7uMKAAJuDQACEToJSyYJtvr9x6nLOgQ",
        32: "CQACAgIAAxkBAAIBN2m273Q46DPM81fKrcnb1U78a-0UAAJvDQACEToJSwJxIbw1Zi66OgQ",
        33: "CQACAgIAAxkBAAIBOWm273RVrFkt3a-OxwABwFnU7ThLbQACcA0AAhE6CUtKGYcXEIq8lToE",
        34: "CQACAgIAAxkBAAIBPGm273RIjffNyhaeQvM9jQ8vhH9KAAJxDQACEToJSzgEptIpT4M4OgQ",
        35: "CQACAgIAAxkBAAIBPmm273SWvpio6naj7QG1dJJlCD9TAAJyDQACEToJS0_V2k6pjBSkOgQ",
        36: "CQACAgIAAxkBAAIBP2m273SvZfQXrThJkFbs_DRMm3YzAAJzDQACEToJSybsWEejX4WJOgQ",
        37: "CQACAgIAAxkBAAIBOmm273QeG3yLvv17GXSRaD_RO3hnAAJ0DQACEToJS3K4Nfiee5I0OgQ",
        38: "CQACAgIAAxkBAAIBO2m273QUbngdHU1Yi4E3oYL1yCVZAAJ1DQACEToJS1hoiGRnhallOgQ",
        39: "CQACAgIAAxkBAAIBPWm273TmIraZwwwpaI6-jhHuXN81AAJ2DQACEToJS_1bXg1xPpaaOgQ",
        40: "CQACAgIAAxkBAAIBQGm273TGEmHiFHpGAAEozm52rGsWrQACdw0AAhE6CUuXSfFUHzzXnjoE",
        41: "CQACAgIAAxkBAAIBQWm273TmhN2y3D2ztYR-7Y0MCCQiAAJ4DQACEToJS4t5BsbwOPNlOgQ",
        42: "CQACAgIAAxkBAAIBQmm273QSjfI8I8dRtH9dDX3hmX3AAAJ5DQACEToJS2WJv45_Cwf2OgQ",
        43: "CQACAgIAAxkBAAIBQ2m273QwnZj_YKNACbKpkvyyjjwtAAJ7DQACEToJS3FM6_wYCkKjOgQ",
        44: "CQACAgIAAxkBAAIBRGm273TwJu_z-htNN91pyzbNkA3wAAJ8DQACEToJS2z24VIuBWaSOgQ",
        45: "CQACAgIAAxkBAAIBRWm273Sb7BQ9XpWyEjoF6oZ4nGQhAAJ-DQACEToJSzQemR_-CrCoOgQ",
        46: "CQACAgIAAxkBAAIBRmm273TAfc8ggka25G2ZpKhl0MY3AAKADQACEToJS_ZRHpNMchXtOgQ",
        47: "CQACAgIAAxkBAAIBR2m273TiSm3JjJ1oaE-sCo1_39yrAAKBDQACEToJS_ve3HsjdgvTOgQ",
        48: "CQACAgIAAxkBAAIBSGm273Q7rl7EP6lNgQQbOrC-oD_8AAKCDQACEToJS2G4cpcKy-s3OgQ",
        49: "CQACAgIAAxkBAAIBSWm273R3VKPFQSeIjEZ-8QkwmZQkAAKDDQACEToJS4z5Zmv5MOk0OgQ",
        50: "CQACAgIAAxkBAAIBSmm273T0lQmLKZuYp4Qk5J68yeEhAAKEDQACEToJS6--y1iVdkR1OgQ",
        51: "CQACAgIAAxkBAAIBTmm273SgP4OSWMwlNaDlL3cF2cjeAAKGDQACEToJS3IOtKCs-JTpOgQ",
        52: "CQACAgIAAxkBAAIBUGm273R_2jagLksN0BY8OkZi4NCXAAKHDQACEToJSzAa1_YFAg2UOgQ",
        53: "CQACAgIAAxkBAAIBS2m273QYppdeOZjSTZ5zwevnQ3LSAAKKDQACEToJS__5yrHNVpR-OgQ",
        54: "CQACAgIAAxkBAAIBTGm273QAAa93qoCN_0kplaUu2i2YMAACiw0AAhE6CUt3q506Ol-khzoE",
        55: "CQACAgIAAxkBAAIBTWm273S-DtcNr-19XiMta_l2knenAAKMDQACEToJS0Ui7ieIpOioOgQ",
        56: "CQACAgIAAxkBAAIBT2m273TcZy_D-RY-MxxixU2PlIGEAAKNDQACEToJS7ZQwj-1vKhPOgQ",
        57: "CQACAgIAAxkBAAIBUWm273Q38rHZP01-NJ2gl8Rxhs0tAAKODQACEToJS6K_JBBqurGqOgQ",
        58: "CQACAgIAAxkBAAIBUmm273Qql5ZqNUMB9iqmasYEw4zsAAKPDQACEToJSwGbNbxtfNLgOgQ",
        59: "CQACAgIAAxkBAAIBU2m273SsicYuVB0KIWHFTgwlTkQZAAKQDQACEToJSwVjYldp1yH0OgQ",
        60: "CQACAgIAAxkBAAIBVGm273Qays1Ze0g79e5LxBrYBPPyAAKSDQACEToJSysjh8IGyM41OgQ",
        61: "CQACAgIAAxkBAAIBVWm273Qc4qNfk47n6UM4EjzOHJo6AAKTDQACEToJSwohZIj8v62xOgQ",
        62: "CQACAgIAAxkBAAIBVmm273T38XQDVdB_fv96aK33RWe5AAKUDQACEToJS-dGCHS8wlbROgQ",
        63: "CQACAgIAAxkBAAIBV2m273QT2BExzOxO2d0NdA8ehveIAAKVDQACEToJSwgWvN0deBIwOgQ",
        64: "CQACAgIAAxkBAAIBWGm273SbLxjOjEbTkfG3mfw8NKHrAAKWDQACEToJS-Z_lwXCd978OgQ",
        65: "CQACAgIAAxkBAAIBWWm273Qz8fXAmvYK_KmpHTl3oVRbAAKXDQACEToJSwvlJ3lwJ_iuOgQ",
        66: "CQACAgIAAxkBAAIBWmm273TXaCQfIr9EhLNf08h_HtwyAAKZDQACEToJSzZq-9bAhVv3OgQ",
        67: "CQACAgIAAxkBAAIBW2m273TQsdCmO9T9zc2XW33iSkypAAKaDQACEToJS-xrGcdLuca9OgQ",
        68: "CQACAgIAAxkBAAIBXGm273ThnX-_MG_591JzqpAAAeH2BgACmw0AAhE6CUtr3_fFMxCtDDoE",
        69: "CQACAgIAAxkBAAIBXWm273QT1uCU2TYiAYYkEPRwJE1QAAKdDQACEToJS_0z9dw2KygdOgQ",
        70: "CQACAgIAAxkBAAIBXmm273SEjGXWeOdxGc99iqKdau73AAKeDQACEToJSweWC4O59QqGOgQ",
        71: "CQACAgIAAxkBAAIBX2m273SPI5y__o70qryPcwqSp6FnAAKfDQACEToJSxOMKI41ztYrOgQ",
        72: "CQACAgIAAxkBAAIBYGm273RoltmtjCifUoz78_Rg-ug1AAKgDQACEToJSzCEt9o6GzRwOgQ",
        73: "CQACAgIAAxkBAAIBYWm273Q1mlb3WqNsNBPfW_WwBFYOAAKhDQACEToJS6oJVNgz8YuROgQ",
        74: "CQACAgIAAxkBAAIBZWm273TPEvlO3wjHUdOwhYHHJtA_AAKiDQACEToJS_j7BcM46qZiOgQ",
        75: "CQACAgIAAxkBAAIBYmm273TxLCafD7UiBqoS-1hBrWi7AAKkDQACEToJS_owJt0Rq71yOgQ",
        76: "CQACAgIAAxkBAAIBY2m273RcLSLAS6HHUQk9FdVm3H94AAKlDQACEToJS94MQO7Ar-BzOgQ",
        77: "CQACAgIAAxkBAAIBZGm273Tjf2ZyD4FUwJvbJZuazaNWAAKmDQACEToJS4RXW9mcpc3OOgQ",
        78: "CQACAgIAAxkBAAIBZmm273RYRVq9k7b9qX0BGND9uGIxAAKnDQACEToJSzKwDw2Wwvb7OgQ",
        79: "CQACAgIAAxkBAAIBZ2m273TkYdu84WiTGoL26hZf_jFwAAKoDQACEToJSyz5hQmPytJuOgQ",
        80: "CQACAgIAAxkBAAIBaGm273T4oG-oEjdwaHPFjVMsUETzAAKqDQACEToJS3bcLnw_NCYROgQ",
        81: "CQACAgIAAxkBAAIBaWm273QxTlMVZVAElo40-rM8VWSdAAKrDQACEToJS1FeimzCCptOOgQ",
        82: "CQACAgIAAxkBAAIBamm273RQdxBzc2_GzqybkaCW7m-RAAKsDQACEToJSwOvlQoy4vSiOgQ",
        83: "CQACAgIAAxkBAAIBa2m273SCQKbiIe24tlr-M8r0zkgfAAKuDQACEToJSz2OhpUUNjLSOgQ",
        84: "CQACAgIAAxkBAAIBbGm273RYzrS-f3qSQeAeiK3I8yEVAAKvDQACEToJS7FkqibuaXTTOgQ",
        85: "CQACAgIAAxkBAAIBbWm273RCchSqMV612VR0YDya8ASVAAKwDQACEToJS9WyIq2wj2fHOgQ",
        86: "CQACAgIAAxkBAAIBcWm273RxZ6v-76XQHq-WUrHScB4cAAKxDQACEToJSyk6FQxU1bJ0OgQ",
        87: "CQACAgIAAxkBAAIBbmm273S5si3ngHQV4eomCOYFG2ApAAKyDQACEToJS3TlRd3Slq-oOgQ",
        88: "CQACAgIAAxkBAAIBb2m273S3_jf4lfsPCcCfi52xmpbHAAKzDQACEToJSwQj0XI7y_21OgQ",
        89: "CQACAgIAAxkBAAIBcGm273Q7UmffA2a0_tbWs5gZIZawAAK0DQACEToJS68_kKcUpoGoOgQ",
        90: "CQACAgIAAxkBAAIBcmm273Qk3bWbhhdgGlOpBLwXhQZgAAK1DQACEToJSz1UsR_LAYtgOgQ",
        91: "CQACAgIAAxkBAAIBdWm273R9jrbHAUhWgj_iRonL0cbaAAK2DQACEToJS6VGNUJhlwK2OgQ",
        92: "CQACAgIAAxkBAAIBd2m273QuGRyipnXFj7ujgHYFfl7JAAK4DQACEToJS0EaZOfakvLWOgQ",
        93: "CQACAgIAAxkBAAIBc2m273RdlP-w0kl6dU0Tk0rzrz7wAAK5DQACEToJS-H_CMGmUjSaOgQ",
        94: "CQACAgIAAxkBAAIBdGm273Tysn_ijNYVabr32YqobWbJAAK6DQACEToJSyG-LxwnmxIEOgQ",
        95: "CQACAgIAAxkBAAIBdmm273RFOZZ5D7G3uHhrzVISpy41AAK7DQACEToJS5Yecw4G2fWBOgQ",
        96: "CQACAgIAAxkBAAIBemm273SH-dvQVmLvJw1kLzZwIoqgAAK8DQACEToJS96JV2DSBAGROgQ",
        97: "CQACAgIAAxkBAAIBeWm273SQRv9vkW-V_AABRwKwmtouzAACvQ0AAhE6CUsEW1x9NmsXNToE",
        98: "CQACAgIAAxkBAAIBe2m273SlWwdRrIZjSZkmeoVY5eNTAAK-DQACEToJS1HQtjc6sKxPOgQ",
        99: "CQACAgIAAxkBAAIBeGm273RieLvIjDXQRXJW1_t2BsybAAK_DQACEToJS619EYS9axoqOgQ",
        100: "CQACAgIAAxkBAAIBfGm273T9p2bq46b3qRg6gkOYWykXAALBDQACEToJS80AATvBi8-lwToE",
        101: "CQACAgIAAxkBAAIBfWm273Q4Tu6_ynRYTzOPb2DFcfEZAALCDQACEToJS3DQhYR9VC-cOgQ",
        102: "CQACAgIAAxkBAAIBvWm274_p3h_ykR8QDcFqsAuIE8uNAALDDQACEToJSx2Kjb-KI1TBOgQ",
        103: "CQACAgIAAxkBAAIBvmm274-R2SMZ4H2xc14LiZkSYvaAAALEDQACEToJS5ZADJQyBdsqOgQ",
        104: "CQACAgIAAxkBAAIBv2m2748OlJc4UlMBCcv8XLsoIOkzAALFDQACEToJSxtEd3Cr9_uzOgQ",
        105: "CQACAgIAAxkBAAIBw2m2749ViDWgbKrSo1wpNaeTCLSzAALGDQACEToJS6m1kn5q0jcOgQ",
        106: "CQACAgIAAxkBAAIBwGm2749lbSaVjhVXlcIxIH9nXriSAALHDQACEToJS3vcP2CRlqPhOgQ",
        107: "CQACAgIAAxkBAAIBwWm274-DFbVdfL5OpU5B72lySa8WAALIDQACEToJS7DmASPWHmqIOgQ",
        108: "CQACAgIAAxkBAAIBwmm274_fd8OwFmXH-XqWUFkygNNEAALJDQACEToJS2vKKBDjxaPsOgQ",
        109: "CQACAgIAAxkBAAIBxGm274-H2ZbW5djapNCw_u_ppJIXAALKDQACEToJS29344WkGvO_OgQ",
        110: "CQACAgIAAxkBAAIBx2m2748Z9aAqLYoaRpwtr0Fc8CI2AALLDQACEToJS3LnEweencd8OgQ",
        111: "CQACAgIAAxkBAAIByGm274_Pgy-hWnStQ8dtCDaIOL-oALMDQACEToJS9v0tcg9J7KpOgQ",
        112: "CQACAgIAAxkBAAIBxWm2749UM5WK-X2ZfhBw1uGMwk3NAALNDQACEToJS2_qrHHQjiGGOgQ",
        113: "CQACAgIAAxkBAAIBxmm274-d53L6jzOr6T54UxL5hMkqAALODQACEToJS-1Sx7Pfgck-OgQ",
        114: "CQACAgIAAxkBAAIBDWm27CHPp-jddTHapjEtypbOp1r_AAJnDgACnkOgSCHil1RoJN49OgQ"
    }
}


# --- 5. KEYBOARDLAR ---
def main_menu():
    builder = InlineKeyboardBuilder()
    builder.row(
        types.InlineKeyboardButton(text="🎧 Qur'on tinglash", callback_data="list_tilovat_0"),
        types.InlineKeyboardButton(text=" 🎧 Qur'on tafsiri", callback_data="list_tafsir_0")
    )
    return builder.as_markup()


def admin_menu():
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="📊 Statistika", callback_data="admin_stats"))
    builder.row(types.InlineKeyboardButton(text="🆔 Foydalanuvchilar", callback_data="admin_users"))
    return builder.as_markup()


def get_surah_list_keyboard(type_name, page=0):
    builder = InlineKeyboardBuilder()
    items_per_page = 20
    surah_ids = list(SURA_NAMES.keys())
    start = page * items_per_page
    end = start + items_per_page
    current_surahs = surah_ids[start:end]

    for s_id in current_surahs:
        prefix = "🎧" if type_name == "tilovat" else "🎧"
        builder.add(types.InlineKeyboardButton(
            text=f"{prefix} {s_id:02d}-{SURA_NAMES[s_id]}",
            callback_data=f"play_{type_name}_{s_id}")
        )
    builder.adjust(2)

    nav_row = []
    if page > 0:
        nav_row.append(types.InlineKeyboardButton(text="⏪", callback_data=f"list_{type_name}_{page - 1}"))
    if end < len(surah_ids):
        nav_row.append(types.InlineKeyboardButton(text="⏩", callback_data=f"list_{type_name}_{page + 1}"))

    if nav_row:
        builder.row(*nav_row)
    builder.row(types.InlineKeyboardButton(text="Asosiy sahifa ♻️", callback_data="back_to_main"))
    return builder.as_markup()


# --- 6. HANDLERLAR ---

@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    # Foydalanuvchini bazaga qo'shish
    add_user(message.from_user.id, message.from_user.username, message.from_user.full_name)

    start_text = (
        "🌟 Assalomu alaykum va rahmatullohi va barakatuh,\n\n"
        "📖 Qur'on tilovati botiga xush kelibsiz!\n\n"
        "✅ Botda Qur'on so'zlarini va tafsirini tinglash imkoniyatlari mavjud.\n\n"

    )

    await message.answer(start_text, reply_markup=main_menu())


@dp.message(Command("admin"))
async def admin_panel_cmd(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        await message.answer("🛠 Admin Panel:", reply_markup=admin_menu())
    else:
        await message.answer("Kechirasiz, bu buyruq faqat bot admini uchun.")


@dp.callback_query(F.data == "admin_stats")
async def show_stats(callback: types.CallbackQuery):
    if callback.from_user.id == ADMIN_ID:
        count = get_stats()
        await callback.message.answer(f"📊 Botdan foydalanuvchilar soni: {count} ta")
        await callback.answer()


@dp.callback_query(F.data == "admin_users")
async def show_users_list(callback: types.CallbackQuery):
    if callback.from_user.id == ADMIN_ID:
        users = get_all_users()
        if not users:
            await callback.message.answer("Baza bo'sh.")
        else:
            text = "👤 Foydalanuvchilar ro'yxati:\n\n"
            for u_id, name in users:
                text += f"🔹 {name} (ID: {u_id})\n"
            await callback.message.answer(text[:4000])
        await callback.answer()


@dp.callback_query(F.data.startswith("list_"))
async def show_list(callback: types.CallbackQuery):
    _, type_name, page = callback.data.split("_")
    page = int(page)
    text = "🎧 Qur'on tinglash bo'limi:" if type_name == "tilovat" else "🎧 Qur'on Tafsiri bo'limi:"
    await callback.message.edit_text(text, reply_markup=get_surah_list_keyboard(type_name, page))


@dp.callback_query(F.data == "back_to_main")
async def back_to_main(callback: types.CallbackQuery):
    await callback.message.edit_text("Asosiy bo'limni tanlang:", reply_markup=main_menu())


@dp.callback_query(F.data.startswith("play_"))
async def play_audio_handler(callback: types.CallbackQuery):
    _, type_name, s_id = callback.data.split("_")
    s_id = int(s_id)
    file_id = AUDIOS.get(type_name, {}).get(s_id)

    if file_id:
        caption_text = f" {SURA_NAMES[s_id]} surasi\n\n✨Manfaatli bo'lsin: @sakinatli_bot"
        try:
            await callback.message.answer_audio(audio=file_id, caption=caption_text)
            await callback.answer()
        except Exception as e:
            await callback.answer("Audio yuborishda xatolik yuz berdi.", show_alert=True)
    else:
        await callback.answer("Bu audio hali yuklanmagan.", show_alert=True)


@dp.message(F.audio)
async def get_audio_id(message: types.Message):
    await message.reply(f"Fayl: {message.audio.file_name}\nID: {message.audio.file_id}")


# --- 7. ISHGA TUSHIRISH ---
async def main():
    init_db()
    print("Bot muvaffaqiyatli ishga tushdi...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("Bot to'xtatildi.")
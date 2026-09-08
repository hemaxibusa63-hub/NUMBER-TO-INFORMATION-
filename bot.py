import os
import re
import asyncio
from collections import defaultdict

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# ============================================================
# CONFIG
# ============================================================

BOT_TOKEN = "8994031713:AAEiPqhls2JZTrFmEEK-v5penqX0rsweSYk"

DATA_FILES = [
    "data/test_records_1.txt",
    "data/test_records_2.txt",
]

TITLE = "🛡️ KRUTIK CYBER EXPERT"

INDEX = defaultdict(list)


# ============================================================
# DATABASE / FILE INDEX
# ============================================================

def build_index():
    print()
    print("╔════════════════════════════════════╗")
    print("║          TEST LOOKUP BOT           ║")
    print("║        DATABASE INITIALIZER        ║")
    print("╚════════════════════════════════════╝")
    print()

    total_indexed = 0

    for data_file in DATA_FILES:
        print(f"📂 Loading: {data_file}")

        if not os.path.isfile(data_file):
            print(f"⚠️ File not found: {data_file}")
            continue

        try:
            with open(
                data_file,
                "r",
                encoding="utf-8",
                errors="ignore",
                buffering=1024 * 1024,
            ) as f:
                content = f.read()

        except Exception as e:
            print(f"❌ Error: {e}")
            continue

        records = re.split(
            r"\n(?=Record\s+\d+)",
            content
        )

        file_count = 0

        for record in records:
            record = record.strip()

            if not record:
                continue

            mobile_match = re.search(
                r"📱\s*Mobile:\s*(\d+)",
                record
            )

            if not mobile_match:
                continue

            mobile = mobile_match.group(1)

            if len(mobile) != 10:
                continue

            INDEX[mobile].append(record)

            file_count += 1
            total_indexed += 1

        print(f"   ✅ Indexed: {file_count:,}")

    print()
    print("╔════════════════════════════════════╗")
    print("║            INDEX READY             ║")
    print("╠════════════════════════════════════╣")
    print(f"║ 📊 Records : {total_indexed:,}")
    print(f"║ 📱 Mobiles : {len(INDEX):,}")
    print(f"║ 📁 Files   : {len(DATA_FILES)}")
    print("╚════════════════════════════════════╝")
    print()


# ============================================================
# ANIMATION
# ============================================================

async def animate(message):
    frames = [
        "⚡ Initializing...",
        "🔐 Secure connection...",
        "📡 Connecting test database...",
        "🔎 Searching test records...",
        "🧠 Matching number...",
        "⚙️ Processing result...",
    ]

    for frame in frames:
        try:
            await message.edit_text(
                f"{TITLE}\n\n{frame}"
            )
            await asyncio.sleep(0.35)

        except Exception:
            break


# ============================================================
# /START
# ============================================================

async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    if not update.message:
        return

    await update.message.reply_text(
        f"{TITLE}\n\n"
        "╭────────────────────╮\n"
        "│  🚀 SYSTEM ONLINE  │\n"
        "╰────────────────────╯\n\n"
        "🔐 Test lookup system ready.\n\n"
        "📱 Send a 10-digit test number.\n\n"
        "Example:\n"
        "➜ `1234567890`"
    )


# ============================================================
# /STATUS
# ============================================================

async def status(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    if not update.message:
        return

    total = sum(
        len(v)
        for v in INDEX.values()
    )

    await update.message.reply_text(
        f"{TITLE}\n\n"
        "╔══════════════════════════╗\n"
        "║      🟢 SYSTEM ONLINE   ║\n"
        "╠══════════════════════════╣\n"
        f"║ 📊 Records : {total:,}\n"
        f"║ 📱 Mobiles : {len(INDEX):,}\n"
        f"║ 📁 Files   : {len(DATA_FILES)}\n"
        "║ ⚡ Search  : READY\n"
        "╚══════════════════════════╝\n\n"
        "🔐 Access: DM + Groups"
    )


# ============================================================
# /ID
# ============================================================

async def show_id(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    chat = update.effective_chat

    if chat is None or not update.message:
        return

    await update.message.reply_text(
        f"{TITLE}\n\n"
        "🆔 CHAT INFORMATION\n\n"
        f"Chat ID:\n`{chat.id}`"
    )


# ============================================================
# SEARCH
# ============================================================

async def search(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    if not update.message:
        return

    text = update.message.text.strip()

    mobile = re.sub(
        r"\D",
        "",
        text
    )

    if len(mobile) != 10:
        await update.message.reply_text(
            f"{TITLE}\n\n"
            "╭────────────────────╮\n"
            "│  ❌ INVALID INPUT   │\n"
            "╰────────────────────╯\n\n"
            "📱 Please send exactly 10 digits."
        )
        return

    loading = await update.message.reply_text(
        f"{TITLE}\n\n"
        "⚡ Initializing..."
    )

    await animate(loading)

    results = INDEX.get(
        mobile,
        []
    )

    if not results:
        await loading.edit_text(
            f"{TITLE}\n\n"
            "╔══════════════════════════╗\n"
            "║      ❌ NO MATCH        ║\n"
            "╚══════════════════════════╝\n\n"
            f"📱 Test Mobile: `{mobile}`\n\n"
            "🔎 No matching test record found."
        )
        return

    header = (
        f"{TITLE}\n\n"
        "╔══════════════════════════╗\n"
        "║      ✅ MATCH FOUND      ║\n"
        "╚══════════════════════════╝\n\n"
        f"📱 Test Mobile: `{mobile}`\n"
        f"📊 Total records: {len(results)}\n\n"
    )

    output = header

    for number, record in enumerate(results, 1):
        record = re.sub(
            r"Record\s+\d+",
            f"Record {number}",
            record,
            count=1
        )

        output += (
            "━━━━━━━━━━━━━━━━━━━━\n"
            f"🔹 RESULT #{number}\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            f"{record}\n\n"
        )

    output += (
        "━━━━━━━━━━━━━━━━━━━━\n"
        "🛡️ KRUTIK LOOKUP BOT\n"
        "⚡ SEARCH COMPLETE"
    )

    try:
        await loading.delete()
    except Exception:
        pass

    MAX_LENGTH = 3900

    for start_pos in range(
        0,
        len(output),
        MAX_LENGTH
    ):
        chunk = output[
            start_pos:start_pos + MAX_LENGTH
        ]

        await update.message.reply_text(
            chunk
        )


# ============================================================
# ERROR HANDLER
# ============================================================

async def error_handler(
    update: object,
    context: ContextTypes.DEFAULT_TYPE
):
    print(
        "❌ ERROR:",
        context.error
    )


# ============================================================
# MAIN
# ============================================================

def main():

    if not BOT_TOKEN or BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        raise RuntimeError(
            "BOT_TOKEN code mein set karo."
        )

    build_index()

    app = (
        Application
        .builder()
        .token(BOT_TOKEN)
        .build()
    )

    app.add_handler(
        CommandHandler("start", start)
    )

    app.add_handler(
        CommandHandler("status", status)
    )

    app.add_handler(
        CommandHandler("id", show_id)
    )

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            search
        )
    )

    app.add_error_handler(
        error_handler
    )

    print()
    print("🛡️ KRUTIK CYBER EXPERT")
    print("🤖 BOT STARTED")
    print("👤 DM: ENABLED")
    print("👥 GROUPS: ENABLED")
    print("⚡ Waiting for messages...")
    print()

    app.run_polling()


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    main()

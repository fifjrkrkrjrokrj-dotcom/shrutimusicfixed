import asyncio
import re
from time import time
from datetime import datetime
from pyrogram import filters, types, enums
from ShrutiMusic import app

user_last_message_time = {}
user_command_count = {}
SPAM_THRESHOLD = 2
SPAM_WINDOW_SECONDS = 5

async def userstatus(user_id):
    try:
        user = await app.get_users(user_id)
        status = user.status
        if status == enums.UserStatus.RECENTLY:
            return "ʀᴇᴄᴇɴᴛʟʏ ᴀᴄᴛɪᴠᴇ"
        elif status == enums.UserStatus.LAST_WEEK:
            return "ʟᴀsᴛ ᴡᴇᴇᴋ"
        elif status == enums.UserStatus.LONG_AGO:
            return "ʟᴏɴɢ ᴛɪᴍᴇ ᴀɢᴏ"
        elif status == enums.UserStatus.OFFLINE:
            return "ᴏғғʟɪɴᴇ"
        elif status == enums.UserStatus.ONLINE:
            return "ᴏɴʟɪɴᴇ ɴᴏᴡ"
        else:
            return "ᴜɴᴋɴᴏᴡɴ"
    except:
        return "ᴜɴᴋɴᴏᴡɴ"

INFO_CAPTION = """
<b>👤 ᴜsᴇʀ ɪɴғᴏʀᴍᴀᴛɪᴏɴ</b>

<b>🆔 ɪᴅ:</b> <code>{}</code>
<b>👨‍💻 ɴᴀᴍᴇ:</b> {}
<b>🏷 ᴜsᴇʀɴᴀᴍᴇ:</b> {}
<b>🔗 ᴍᴇɴᴛɪᴏɴ:</b> {}
<b>📡 ᴅᴄ ɪᴅ:</b> {}
<b>💎 ᴘʀᴇᴍɪᴜᴍ:</b> {}
<b>💬 ʙɪᴏ:</b> {}
<b>👥 ᴍᴜᴛᴜᴀʟ ɢʀᴏᴜᴘs:</b> {}
<b>📅 ᴊᴏɪɴᴇᴅ:</b> {}
<b>📶 sᴛᴀᴛᴜs:</b> {}
"""

@app.on_message(filters.command(["info", "userinfo"], prefixes=["/", "!", "%", ",", ".", "@", "#"]))
async def userinfo(_, message):
    user_id = message.from_user.id
    current_time = time()

    last_message_time = user_last_message_time.get(user_id, 0)
    if current_time - last_message_time < SPAM_WINDOW_SECONDS:
        user_command_count[user_id] = user_command_count.get(user_id, 0) + 1
        if user_command_count[user_id] > SPAM_THRESHOLD:
            warn = await message.reply_text(
                f"⚠️ {message.from_user.mention}, ᴅᴏɴ'ᴛ sᴘᴀᴍ. ᴛʀʏ ᴀɢᴀɪɴ ᴀғᴛᴇʀ ᴀ ᴍᴏᴍᴇɴᴛ."
            )
            await asyncio.sleep(3)
            return await warn.delete()
    else:
        user_command_count[user_id] = 1
        user_last_message_time[user_id] = current_time

    if message.reply_to_message:
        target = message.reply_to_message.from_user
    elif len(message.command) > 1:
        try:
            target = await app.get_users(message.text.split(None, 1)[1])
        except Exception as e:
            return await message.reply_text(f"⚠️ {e}")
    else:
        target = message.from_user

    try:
        user_info = await app.get_chat(target.id)
        status = await userstatus(target.id)

        user_id = target.id
        name = f"{user_info.first_name or ''} {user_info.last_name or ''}".strip() or "ɴᴏ ɴᴀᴍᴇ"
        username = f"@{user_info.username}" if user_info.username else "ɴᴏ ᴜsᴇʀɴᴀᴍᴇ"
        mention = target.mention
        dc_id = getattr(target, "dc_id", "ᴜɴᴋɴᴏᴡɴ")
        premium = "✅ ʏᴇs" if getattr(target, "is_premium", False) else "❌ ɴᴏ"

        bio_raw = user_info.bio or ""
        if not bio_raw:
            bio = "ɴᴏ ʙɪᴏ sᴇᴛ"
        elif re.search(r"(t\.me|https?://|@)", bio_raw, re.IGNORECASE):
            if "@" in bio_raw:
                bio = "ᴜsᴇʀ ʜᴀs ᴀ ᴜsᴇʀɴᴀᴍᴇ ɪɴ ʙɪᴏ 🪄"
            else:
                bio = "ᴜsᴇʀ ʜᴀs ᴀ ʟɪɴᴋ ɪɴ ʙɪᴏ 🌐"
        else:
            bio = bio_raw

        try:
            mutual_chats = await app.get_common_chats(target.id)
            mutual_count = len(mutual_chats)
        except:
            mutual_count = "ᴜɴᴀᴠᴀɪʟᴀʙʟᴇ"

        join_date = getattr(target, "added_to_attachment_menu_date", None)
        join_str = join_date.strftime("%d %b %Y") if join_date else "ᴜɴᴀᴠᴀɪʟᴀʙʟᴇ"

        caption = INFO_CAPTION.format(
            user_id, name, username, mention, dc_id, premium, bio, mutual_count, join_str, status
        )

        btn = [
            [
                types.InlineKeyboardButton(
                    "🌐 ᴠɪᴇᴡ ᴘʀᴏғɪʟᴇ",
                    url=f"https://t.me/{target.username}" if target.username else "https://t.me/",
                )
            ]
        ]

        await message.reply_text(
            caption,
            reply_markup=types.InlineKeyboardMarkup(btn),
            disable_web_page_preview=True,
        )

    except Exception as e:
        await message.reply_text(f"⚠️ ᴇʀʀᴏʀ: {e}")

__MODULE__ = "Usᴇʀ ɪɴғᴏ"
__HELP__ = """
/ɪɴғᴏ [ᴜsᴇʀ_ɪᴅ] - sʜᴏᴡ ᴜsᴇʀ ɪɴғᴏʀᴍᴀᴛɪᴏɴ 💫  
/ᴜsᴇʀɪɴғᴏ [ᴜsᴇʀ_ɪᴅ] - sᴀᴍᴇ ᴀs /ɪɴғᴏ
"""

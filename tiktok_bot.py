import datetime
import os
import httpx
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

API_URL = "https://www.tikwm.com/api/user/info?unique_id={username}"

# دالة async لجلب المعلومات من API بسرعة وكفاءة
async def fetch_user_info(username: str):
    async with httpx.AsyncClient(timeout=10) as client:
        try:
            response = await client.get(API_URL.format(username=username))
            response.raise_for_status()
            return response.json()
        except httpx.RequestError as e:
            return {"error": f"خطأ في الاتصال: {e}"}
        except httpx.HTTPStatusError as e:
            return {"error": f"رد HTTP غير صالح: {e}"}
        except Exception as e:
            return {"error": f"خطأ غير متوقع: {e}"}

# دالة لتحويل الطابع الزمني unix إلى نص مقروء
def format_timestamp(ts):
    try:
        if ts and ts > 0:
            return datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
    except:
        pass
    return "غير متوفر"

# دالة لبناء نص المعلومات بشكل مرتب مع الهروب لـ MarkdownV2
def build_info_text(user_info):
    def escape_md(text):
        # الهروب من رموز MarkdownV2
        escape_chars = r"\_*[]()~`>#+-=|{}.!"
        for ch in escape_chars:
            text = text.replace(ch, f"\\{ch}")
        return text

    unique_id = escape_md(user_info.get('uniqueId', 'N/A'))
    nickname = escape_md(user_info.get('nickname', 'N/A'))
    user_id = user_info.get('id', 'N/A')
    follower_count = user_info.get('followerCount', 0)
    following_count = user_info.get('followingCount', 0)
    heart_count = user_info.get('heartCount', 0)
    video_count = user_info.get('videoCount', 0)
    signature = escape_md(user_info.get('signature', 'لا يوجد'))

    create_time = format_timestamp(user_info.get('createTime'))
    modify_unique_id_time = format_timestamp(user_info.get('modifyUniqueIdTime'))
    modify_nickname_time = format_timestamp(user_info.get('modifyNicknameTime'))
    country = escape_md(user_info.get('country', 'غير متوفر'))

    text = (
        f"✅ *تم العثور على معلومات @{unique_id}*\n\n"
        f"👤 *الاسم:* {nickname}\n"
        f"🆔 *المعرّف (ID):* `{user_id}`\n\n"
        f"❤️ *المتابعون:* {follower_count:,}\n"
        f"↗️ *يتابع:* {following_count:,}\n"
        f"👍 *الإعجابات:* {heart_count:,}\n"
        f"🎥 *الفيديوهات:* {video_count:,}\n\n"
        f"📅 *تاريخ إنشاء الحساب:* {create_time}\n"
        f"✏️ *تعديل اسم المستخدم:* {modify_unique_id_time}\n"
        f"✏️ *تعديل الاسم:* {modify_nickname_time}\n"
        f"🌍 *الدولة:* {country}\n\n"
        f"📝 *البايو:*\n{signature}"
    )
    return text

# أمر /start
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("أهلاً بك في بوت كشف معلومات تيك توك الاحترافي. أرسل لي أي يوزر.")

# التعامل مع الرسائل النصية (اسم المستخدم)
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = update.message.text.replace('@', '').strip()
    if not username:
        await update.message.reply_text("⚠️ الرجاء إرسال اسم مستخدم صالح.")
        return

    loading_msg = await update.message.reply_text("⏳ جاري البحث عن معلومات متقدمة...")

    data = await fetch_user_info(username)

    if "error" in data:
        await loading_msg.edit_text(f"❌ حدث خطأ:\n{data['error']}")
        return

    if data.get('code') != 0 or 'data' not in data:
        await loading_msg.edit_text(f"❌ لم يتم العثور على المستخدم أو حدث خطأ. الرسالة:\n{data.get('msg', 'غير معروف')}")
        return

    user_info = data['data']
    text = build_info_text(user_info)
    avatar_url = user_info.get('avatarLarger')

    # أرسل الصورة أولاً إذا موجودة، ثم الرسالة
    if avatar_url:
        try:
            await update.message.reply_photo(photo=avatar_url)
        except:
            # لو حصل خطأ بالإرسال، نرسل الرسالة فقط
            pass

    await loading_msg.edit_text(text, parse_mode='MarkdownV2')

def main():
    BOT_TOKEN = os.environ.get("BOT_TOKEN")
    if not BOT_TOKEN:
        print("خطأ: لم يتم العثور على توكن البوت. تأكد من ضبط متغير البيئة BOT_TOKEN")
        return

    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🚀 بدء تشغيل بوت تيك توك المتقدم...")
    application.run_polling()

if __name__ == "__main__":
    main()

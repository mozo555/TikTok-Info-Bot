# tiktok_bot.py (v2.0 - Professional Edition)
import requests
import datetime
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# --- الدالة الرئيسية لجلب المعلومات المتقدمة ---
def get_advanced_user_info(username):
    try:
        # استخدام API غير رسمي ولكنه قوي جداً
        url = f"https://www.tikwm.com/api/user/info?unique_id={username}"
        response = requests.get(url)
        response.raise_for_status()  # للتأكد من نجاح الطلب
        data = response.json()

        if data.get("code") == 0 and "data" in data:
            user_info = data['data']
            
            # --- تحويل التواريخ من صيغة Unix إلى صيغة مقروءة ---
            create_time = datetime.datetime.fromtimestamp(user_info.get('createTime', 0)).strftime('%Y-%m-%d %H:%M:%S')
            
            # --- تجهيز رسالة النتائج الاحترافية ---
            info_text = (
                f"✅ **تم العثور على معلومات @{user_info.get('uniqueId', 'N/A')}**\n\n"
                f"👤 **الاسم:** {user_info.get('nickname', 'N/A')}\n"
                f"🆔 **المعرّف (ID):** `{user_info.get('id', 'N/A')}`\n\n"
                f"❤️ **المتابعون:** {user_info.get('followerCount', 0):,}\n"
                f"↗️ **يتابع:** {user_info.get('followingCount', 0):,}\n"
                f"👍 **اللايكات:** {user_info.get('heartCount', 0):,}\n"
                f"🎥 **الفيديوهات:** {user_info.get('videoCount', 0):,}\n\n"
                f"📅 **تاريخ إنشاء الحساب:**\n`{create_time}`\n\n"
                f"📝 **البايو:**\n{user_info.get('signature', 'لا يوجد')}"
            )
            return info_text
        else:
            return f"❌ **خطأ:** لم يتم العثور على اليوزر. (السبب: {data.get('msg', 'غير معروف')})"

    except requests.exceptions.RequestException as e:
        return f"❌ **خطأ في الاتصال بالـ API:**\n`{e}`"
    except Exception as e:
        return f"❌ **حدث خطأ غير متوقع:**\n`{e}`"

# --- أوامر البوت ---
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("أهلاً بك في بوت كشف معلومات تيك توك الاحترافي. أرسل لي أي يوزر.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = update.message.text.replace('@', '').strip()
    processing_message = await update.message.reply_text("⏳ جاري البحث عن معلومات متقدمة...")

    result_text = get_advanced_user_info(username)
    
    await processing_message.edit_text(text=result_text, parse_mode='Markdown')

# --- الدالة الرئيسية لتشغيل البوت ---
def main():
    BOT_TOKEN = os.environ.get("BOT_TOKEN")  # تأكد من ضبط متغير البيئة BOT_TOKEN بقيمة التوكن
    if not BOT_TOKEN:
        print("خطأ: لم يتم العثور على توكن البوت. تأكد من ضبط متغير البيئة BOT_TOKEN")
        return

    print("--- بدء تشغيل بوت تيك توك الاحترافي ---")
    application = Application.builder().token(BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    application.run_polling()

if __name__ == "__main__":
    main()

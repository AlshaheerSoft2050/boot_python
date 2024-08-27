from telethon import TelegramClient, events
from telethon.errors import SessionPasswordNeededError
from telethon.tl.types import PeerChannel, PeerChat, PeerUser
import asyncio

# تعريف بيانات الاعتماد
accounts = [
    {'api_id': '22416938', 'api_hash': 'ba64c6cd8384a198a61df4b05713c297', 'phone_number': '+967770312744'},
    {'api_id': '20446329', 'api_hash': '7c151b125b2a34febd6116ef40381b4c', 'phone_number': '+967776155452'},
    {'api_id': '25035277', 'api_hash': '37b8dc4c609f7ce8fb5ed4a583e87af2', 'phone_number': '+967781336037'},
]

clients = []

# تعريف الكلمات المراقبة
tracked_words = [
    'يحل', 'مشاريع', 'يعمل', 'يسوي', 'يعرف', 'أبي أحد', 'ابغى أحد', 
    'مشروع تخرج', 'عندي واجب', 'يصاّم', 'بوستر', 'مونتاج', 'يصمم فديو',
    'برمجه', 'يشرح', 'خصوصي', 'تقرير تعاوني', 'ابغى حد', 'يفهم', 'أحد فاهم', 
    'الذي يعرف يجي خاص', 'تصميم موقع', 'جافا', 'خوارزميات', 'تشفير', 'لينكس', 
    'ماتلاب', 'اختبار حاسوب', 'يسوي تقرير', 'تقرير تدريب', 'بحث', 'عرض بوربيونت', 
    'برزنتيشن', 'سيرة ذاتية', 'cv', 'تمارين اكسل', 'محاسبة', 'إدارة أعمال', 
    'رياضيات', 'حظر', 'يفتح الحظر', 'تحليل بيانات', 'ذكاء اصطناعي', 'تعلم آلي',
    'شبكات', 'قواعد بيانات', 'تطبيقات موبايل', 'أندرويد', 'آيفون', 'تطوير ويب', 
    'CSS', 'HTML', 'JavaScript','flutter', 'فلاتر','موقع','يشرح لي','kali','metasploite','React', 'Angular', 'Vue', 'Python', 'C++', 
    'C#', 'SQL', 'تحليل نظم', 'حاسوب', 'اختبار برمجيات', 'مشروع بحثي', 
    'تدريب عملي', 'إحصاء', 'اقتصاد', 'مالية', 'إدارة مشاريع', 'نظم معلومات', 
    'هندسة برمجيات', 'هندسة كهربائية', 'هندسة', 'روبوتات', 'تحليل وتصميم الأنظمة', 
    'تصميم', 'جغرافيا', 'علم نفس', 'علوم اجتماعية', 'أدب', 'بسرعه'
]

# قائمة المجموعات الوجهة
destination_groups = ['shaheersolve']  # أضف أسماء المجموعات التي سيتم إرسال الرسائل إليها

# قائمة لتتبع معرفات الرسائل المرسلة
sent_messages = set()
async def handle_message(client, event):
    message = event.message.message
    sender = await event.get_sender()
    chat = await event.get_chat()
    chat_id = chat.id
    message_id = event.message.id

    if 'رابط الرسالة' in message:
        return

    if any(word.lower() in message.lower() for word in tracked_words):
        if len(message) > 150:
            return

        try:
            chat_name = chat.title if hasattr(chat, 'title') else 'غير محدد'
        except Exception as e:
            chat_name = 'غير محدد'
            print(f"تعذر الحصول على اسم المجموعة: {e}")

        message_link = f"https://t.me/c/{chat_id}/{message_id}"

        sender_first_name = sender.first_name if sender and sender.first_name else 'مجهول'
        sender_username = sender.username if sender and sender.username else 'مجهول'
        formatted_message = (f"من: {sender_first_name} (@{sender_username})\n"
                             f"من المجموعة: {chat_name}\n"
                             f"الرسالة: {message}\n"
                             f"رابط الرسالة: {message_link}")

        if (chat_id, message_id) in sent_messages:
            return

        sent_messages.add((chat_id, message_id))
        for group in destination_groups:
            if chat_name != group:
                try:
                    await client.send_message(group, formatted_message)
                except Exception as e:
                    print(f"فشل إرسال الرسالة إلى {group}: {e}")

async def login_and_start(account):
    session_file = f'session_{account["phone_number"]}'
    client = TelegramClient(session_file, account['api_id'], account['api_hash'])

    print(f"تسجيل الدخول باستخدام {account['phone_number']}.")
    await client.connect()

    if not await client.is_user_authorized():
        await client.send_code_request(account['phone_number'])
        code = input(f"أدخل الرمز المرسل إلى {account['phone_number']}: ")

        try:
            await client.sign_in(account['phone_number'], code)
        except SessionPasswordNeededError:
            password = input("أدخل كلمة المرور للتحقق الثنائي: ")
            await client.sign_in(password=password)

    @client.on(events.NewMessage)
    async def handler(event):
        await handle_message(client, event)

    await client.run_until_disconnected()

async def main():
    tasks = []
    for account in accounts:
        task = asyncio.create_task(login_and_start(account))
        tasks.append(task)
        await asyncio.sleep(2)  # تأخير صغير لضمان بدء تسجيل الدخول للحساب الأول قبل الحساب الثاني
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"حدث خطأ غير متوقع: {e}")

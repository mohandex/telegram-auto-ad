# Translation system for multi-language bot support
# Supports Persian (fa), Russian (ru), and English (en)

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

TRANSLATIONS = {
    # Language selection
    "select_language": {
        "fa": "🌐 لطفاً زبان خود را انتخاب کنید:",
        "ru": "🌐 Пожалуйста, выберите ваш язык:",
        "en": "🌐 Please select your language:"
    },
    "language_persian": {
        "fa": "🇮🇷 فارسی",
        "ru": "🇮🇷 Персидский",
        "en": "🇮🇷 Persian"
    },
    "language_russian": {
        "fa": "🇷🇺 روسی",
        "ru": "🇷🇺 Русский",
        "en": "🇷🇺 Russian"
    },
    "language_english": {
        "fa": "🇺🇸 انگلیسی",
        "ru": "🇺🇸 Английский",
        "en": "🇺🇸 English"
    },
    "language_selected": {
        "fa": "✅ زبان شما تنظیم شد!",
        "ru": "✅ Ваш язык установлен!",
        "en": "✅ Your language has been set!"
    },
    
    # Welcome messages
    "welcome_message": {
        "fa": "🎉 به ربات آگهی‌های گیفت خوش آمدید!\n\n📝 برای ثبت آگهی جدید، روی دکمه زیر کلیک کنید.",
        "ru": "🎉 Добро пожаловать в бот объявлений подарков!\n\n📝 Чтобы разместить новое объявление, нажмите кнопку ниже.",
        "en": "🎉 Welcome to the Gift Ads Bot!\n\n📝 To post a new ad, click the button below."
    },
    "new_ad_button": {
        "fa": "📝 ثبت آگهی جدید",
        "ru": "📝 Разместить новое объявление",
        "en": "📝 Post New Ad"
    },
    "support_button": {
        "fa": "🆘 پشتیبانی",
        "ru": "🆘 Поддержка",
        "en": "🆘 Support"
    },
    "my_ads_button": {
        "fa": "📋 آگهی‌های من",
        "ru": "📋 Мои объявления",
        "en": "📋 My Ads"
    },
    "back_to_menu_button": {
        "fa": "🔙 بازگشت به منو",
        "ru": "🔙 Вернуться в меню",
        "en": "🔙 Back to Menu"
    },
    "back_button": {
        "fa": "🔙 بازگشت",
        "ru": "🔙 Назад",
        "en": "🔙 Back"
    },
    "change_language_button": {
        "fa": "🌐 تغییر زبان",
        "ru": "🌐 Изменить язык",
        "en": "🌐 Change Language"
    },
    
    # Ad creation process
    "gift_link_request": {
        "fa": "🎁 لطفاً لینک گیفت یا کانال تلگرام خود را ارسال کنید:",
        "ru": "🎁 Пожалуйста, отправьте ссылку на ваш подарок или телеграм канал:",
        "en": "🎁 Please send your gift link or Telegram channel:"
    },
    "description_request": {
        "fa": "📝 لطفاً توضیحات اضافی برای آگهی خود وارد کنید (مثل تگ‌ها، مقدار گیفت، یا جزئیات کانال):\n\n💡 اگر توضیحی ندارید، 'بدون توضیح' بنویسید:",
        "ru": "📝 Пожалуйста, введите дополнительное описание для вашего объявления (например, теги, количество подарков или детали канала):\n\n💡 Если у вас нет описания, напишите 'без описания':",
        "en": "📝 Please enter additional description for your ad (like tags, gift amount, or channel details):\n\n💡 If you have no description, write 'no description':"
    },
    "price_request": {
        "fa": "💰 لطفاً قیمت آگهی خود را وارد کنید (به تون):",
        "ru": "💰 Пожалуйста, введите цену вашего объявления (в тонах):",
        "en": "💰 Please enter your ad price (in TON):"
    },
    "invalid_price": {
        "fa": "❌ قیمت وارد شده معتبر نیست. لطفاً یک عدد وارد کنید.",
        "ru": "❌ Введенная цена недействительна. Пожалуйста, введите число.",
        "en": "❌ Invalid price entered. Please enter a number."
    },
    "invalid_link": {
        "fa": "❌ لینک وارد شده معتبر نیست. لطفاً لینک صحیح گیفت یا کانال تلگرام ارسال کنید.",
        "ru": "❌ Введенная ссылка недействительна. Пожалуйста, отправьте правильную ссылку на подарок или телеграм канал.",
        "en": "❌ Invalid link entered. Please send a valid gift link or Telegram channel."
    },
    "invalid_photo": {
        "fa": "❌ عکس ارسالی معتبر نیست. لطفاً یک عکس صحیح ارسال کنید یا 'بدون عکس' بنویسید.",
        "ru": "❌ Отправленное фото недействительно. Пожалуйста, отправьте правильное фото или напишите 'без фото'.",
        "en": "❌ Invalid photo sent. Please send a valid photo or write 'no photo'."
    },
    "error_restart": {
        "fa": "❌ خطایی رخ داد. لطفاً دوباره شروع کنید.",
        "ru": "❌ Произошла ошибка. Пожалуйста, начните заново.",
        "en": "❌ An error occurred. Please start again."
    },
    "payment_title": {
        "fa": "پرداخت آگهی",
        "ru": "Оплата объявления",
        "en": "Ad Payment"
    },
    "payment_description": {
        "fa": "پرداخت {0} ستاره برای انتشار آگهی",
        "ru": "Оплата {0} звезд для публикации объявления",
        "en": "Pay {0} stars to publish your ad"
    },
    "payment_label": {
        "fa": "پرداخت آگهی",
        "ru": "Оплата объявления",
        "en": "Ad Payment"
    },
    "payment_error": {
        "fa": "❌ خطا در پرداخت. لطفاً دوباره تلاش کنید.",
        "ru": "❌ Ошибка платежа. Пожалуйста, попробуйте еще раз.",
        "en": "❌ Payment error. Please try again."
    },
    "payment_message": {
        "fa": "💳 برای تایید آگهی، لطفاً مبلغ {amount} ستاره پرداخت کنید:",
        "ru": "💳 Для подтверждения объявления, пожалуйста, оплатите {amount} звезд:",
        "en": "💳 To confirm your ad, please pay {amount} stars:"
    },
    "pay_button": {
        "fa": "💳 پرداخت",
        "ru": "💳 Оплатить",
        "en": "💳 Pay"
    },
    "payment_sent": {
        "fa": "💳 صورتحساب پرداخت ارسال شد. لطفاً پرداخت را تکمیل کنید.",
        "ru": "💳 Счет для оплаты отправлен. Пожалуйста, завершите платеж.",
        "en": "💳 Payment invoice sent. Please complete the payment."
    },
    "ad_submitted": {
        "fa": "✅ آگهی شما با موفقیت ثبت شد و برای بررسی ارسال شد.",
        "ru": "✅ Ваше объявление успешно отправлено на рассмотрение.",
        "en": "✅ Your ad has been successfully submitted for review."
    },
    "ad_approved": {
        "fa": "🎉 آگهی شما تایید و در کانال {channel_name} منتشر شد!",
        "ru": "🎉 Ваше объявление одобрено и опубликовано в канале {channel_name}!",
        "en": "🎉 Your ad has been approved and published in the {channel_name} channel!"
    },
    "ad_rejected": {
        "fa": "❌ متأسفانه آگهی شما رد شد.",
        "ru": "❌ К сожалению, ваше объявление было отклонено.",
        "en": "❌ Unfortunately, your ad has been rejected."
    },
    
    # Support messages
    "support_message": {
        "fa": "🆘 پشتیبانی\n\nلطفاً پیام خود را ارسال کنید:",
        "ru": "🆘 Поддержка\n\nПожалуйста, отправьте ваше сообщение:",
        "en": "🆘 Support\n\nPlease send your message:"
    },
    "support_request": {
        "fa": "🆘 لطفاً پیام خود را برای پشتیبانی ارسال کنید:",
        "ru": "🆘 Пожалуйста, отправьте ваше сообщение в службу поддержки:",
        "en": "🆘 Please send your message to support:"
    },
    "support_sent": {
        "fa": "✅ پیام شما برای پشتیبانی ارسال شد. به زودی پاسخ دریافت خواهید کرد.",
        "ru": "✅ Ваше сообщение отправлено в службу поддержки. Вы скоро получите ответ.",
        "en": "✅ Your message has been sent to support. You will receive a response soon."
    },
    "admin_response_request": {
        "fa": "💬 لطفاً پاسخ خود را وارد کنید:",
        "ru": "💬 Пожалуйста, введите ваш ответ:",
        "en": "💬 Please enter your response:"
    },
    "response_sent": {
        "fa": "✅ پاسخ شما ارسال شد.",
        "ru": "✅ Ваш ответ отправлен.",
        "en": "✅ Your response has been sent."
    },
    "admin_response_title": {
        "fa": "پاسخ پشتیبانی",
        "ru": "Ответ поддержки",
        "en": "Support Response"
    },
    "error_sending_response": {
        "fa": "❌ خطا در ارسال پاسخ.",
        "ru": "❌ Ошибка отправки ответа.",
        "en": "❌ Error sending response."
    },
    
    # Admin panels
    "support_admin_panel": {
        "fa": "🔧 پنل ادمین پشتیبانی",
        "ru": "🔧 Панель администратора поддержки",
        "en": "🔧 Support Admin Panel"
    },
    "pending_ads_count": {
        "fa": "آگهی‌های در انتظار",
        "ru": "Ожидающие объявления",
        "en": "Pending Ads"
    },
    "pending_support_count": {
        "fa": "درخواست‌های پشتیبانی",
        "ru": "Запросы поддержки",
        "en": "Support Requests"
    },
    "super_admin_panel": {
        "fa": "👑 پنل سوپر ادمین",
        "ru": "👑 Панель супер администратора",
        "en": "👑 Super Admin Panel"
    },
    "view_pending_ads": {
        "fa": "📋 مشاهده آگهی‌های در انتظار",
        "ru": "📋 Просмотр ожидающих объявлений",
        "en": "📋 View Pending Ads"
    },
    "view_support_requests": {
        "fa": "💬 مشاهده درخواست‌های پشتیبانی",
        "ru": "💬 Просмотр запросов поддержки",
        "en": "💬 View Support Requests"
    },
    "list_users": {
        "fa": "👥 لیست کاربران",
        "ru": "👥 Список пользователей",
        "en": "👥 List Users"
    },
    "search_user": {
        "fa": "🔍 جستجوی کاربر",
        "ru": "🔍 Поиск пользователя",
        "en": "🔍 Search User"
    },
    "statistics": {
        "fa": "📊 آمار",
        "ru": "📊 Статистика",
        "en": "📊 Statistics"
    },
    
    # Admin actions
    "approve_button": {
        "fa": "✅ تایید",
        "ru": "✅ Одобрить",
        "en": "✅ Approve"
    },
    "reject_button": {
        "fa": "❌ رد",
        "ru": "❌ Отклонить",
        "en": "❌ Reject"
    },
    "respond_button": {
        "fa": "💬 پاسخ",
        "ru": "💬 Ответить",
        "en": "💬 Respond"
    },
    "no_permission": {
        "fa": "شما مجاز به انجام این عمل نیستید.",
        "ru": "У вас нет разрешения на выполнение этого действия.",
        "en": "You are not authorized to perform this action."
    },
    "ad_not_found": {
        "fa": "آگهی یافت نشد.",
        "ru": "Объявление не найдено.",
        "en": "Ad not found."
    },
    "ad_approved_admin": {
        "fa": "آگهی تایید شد.",
        "ru": "Объявление одобрено.",
        "en": "Ad approved."
    },
    "ad_rejected_admin": {
        "fa": "آگهی رد شد.",
        "ru": "Объявление отклонено.",
        "en": "Ad rejected."
    },
    
    # Error messages
    "error_channel_send": {
        "fa": "خطا در ارسال به کانال.",
        "ru": "Ошибка отправки в канал.",
        "en": "Error sending to channel."
    },
    "user_not_found": {
        "fa": "کاربر یافت نشد.",
        "ru": "Пользователь не найден.",
        "en": "User not found."
    },
    "invalid_user_id": {
        "fa": "آیدی کاربر معتبر نیست.",
        "ru": "Недействительный ID пользователя.",
        "en": "Invalid user ID."
    },
    
    # Statistics and info
    "total_users": {
        "fa": "👥 کل کاربران",
        "ru": "👥 Всего пользователей",
        "en": "👥 Total Users"
    },
    "total_ads": {
        "fa": "📝 کل آگهی‌ها",
        "ru": "📝 Всего объявлений",
        "en": "📝 Total Ads"
    },
    "total_support_requests": {
        "fa": "🆘 کل درخواست‌های پشتیبانی",
        "ru": "🆘 Всего запросов поддержки",
        "en": "🆘 Total Support Requests"
    },
    "user_info": {
        "fa": "👤 اطلاعات کاربر",
        "ru": "👤 Информация о пользователе",
        "en": "👤 User Information"
    },
    "enter_user_id": {
        "fa": "🔍 لطفاً آیدی کاربر را وارد کنید:",
        "ru": "🔍 Пожалуйста, введите ID пользователя:",
        "en": "🔍 Please enter user ID:"
    },
    "username_required": {
        "fa": "❌ برای ثبت آگهی باید حتماً یوزرنیم داشته باشید. لطفاً ابتدا یوزرنیم تنظیم کنید.",
        "ru": "❌ Для размещения объявления у вас обязательно должно быть имя пользователя. Пожалуйста, сначала установите имя пользователя.",
        "en": "❌ You must have a username to post an ad. Please set a username first."
    },
    "ad_posting_guide": {
        "fa": "📌 راهنمای ثبت آگهی\n\n✨ آگهی گیفت یا کانال خود را تنها در چند مرحله ساده ثبت کنید:\n\n1️⃣ شروع ← روی دکمه \"ثبت آگهی\" کلیک کنید.\n2️⃣ ارسال لینک ← لینک گیفت یا کانال تلگرام خود را ارسال کنید.\n3️⃣ نوشتن توضیحات ← توضیحات اضافی مانند تگ‌ها، مقدار گیفت یا جزئیات کانال وارد کنید.\n4️⃣ تعیین قیمت ← قیمت را به تون وارد کنید (مثال: 50 TON).\n5️⃣ آپلود عکس کانال ← عکس کانال خود را آپلود کنید (اختیاری).\n6️⃣ پیش‌نمایش و تایید ← آگهی خود را بررسی کرده و تایید کنید.\n7️⃣ پرداخت ← هزینه انتشار آگهی را پرداخت کنید.\n8️⃣ تایید ادمین ← منتظر تایید ادمین باشید.\n\n⚠️ توجه: فقط لینک‌های معتبر گیفت تلگرام و کانال‌های تلگرام پذیرفته می‌شود.",
        "ru": "📌 Руководство по размещению объявлений\n\n✨ Разместите свой подарок или канал на продажу всего за несколько простых шагов:\n\n1️⃣ Начало ← Нажмите кнопку \"Разместить объявление\".\n2️⃣ Отправить ссылку ← Отправьте ссылку на ваш подарок или телеграм канал.\n3️⃣ Написать описание ← Введите дополнительное описание, такое как теги, количество подарков или детали канала.\n4️⃣ Установить цену ← Введите цену в TON (пример: 50 TON).\n5️⃣ Загрузить фото канала ← Загрузите фото вашего канала (необязательно).\n6️⃣ Предварительный просмотр и подтверждение ← Просмотрите и подтвердите ваше объявление.\n7️⃣ Оплата ← Оплатите стоимость размещения объявления.\n8️⃣ Одобрение администратора ← Дождитесь одобрения администратором.\n\n⚠️ Внимание: Принимаются только действительные ссылки на подарки Telegram и каналы Telegram.",
        "en": "📌 Ad Posting Guide\n\n✨ Post your gift or channel for sale in just a few simple steps:\n\n1️⃣ Start → Click on the \"Post Ad\" button.\n2️⃣ Send Link → Submit the link of your gift or Telegram channel.\n3️⃣ Write Description → Enter additional description like tags, gift amount, or channel details.\n4️⃣ Set Price → Enter the price in TON (example: 50 TON).\n5️⃣ Upload Channel Photo → Upload your channel photo (optional).\n6️⃣ Preview and Confirm → Review and confirm your ad.\n7️⃣ Payment → Pay the ad posting fee.\n8️⃣ Admin Approval → Wait for admin approval.\n\n⚠️ Note: Only valid Telegram gift links and Telegram channels are accepted."
    },
    
    # Super Admin Menu Buttons
    "super_admin_menu_button": {
        "fa": "👑 پنل سوپر ادمین",
        "ru": "👑 Панель супер администратора",
        "en": "👑 Super Admin Panel"
    },
    "view_user_info_button": {
        "fa": "👤 دیدن اطلاعات کاربر",
        "ru": "👤 Просмотр информации о пользователе",
        "en": "👤 View User Info"
    },
    "refund_all_stars_button": {
        "fa": "💰 ریفاند کلی استارز",
        "ru": "💰 Возврат всех звезд",
        "en": "💰 Refund All Stars"
    },
    "manual_refund_button": {
        "fa": "💸 ریفاند دستی",
        "ru": "💸 Ручной возврат",
        "en": "💸 Manual Refund"
    },
    "manual_refund_request_user_id": {
        "fa": "👤 لطفاً ID کاربر را وارد کنید:",
        "ru": "👤 Пожалуйста, введите ID пользователя:",
        "en": "👤 Please enter the user ID:"
    },
    "manual_refund_request_amount": {
        "fa": "💰 لطفاً مقدار استارز برای ریفاند را وارد کنید:",
        "ru": "💰 Пожалуйста, введите количество звезд для возврата:",
        "en": "💰 Please enter the amount of stars to refund:"
    },
    "manual_refund_invalid_user_id": {
        "fa": "❌ ID کاربر نامعتبر است. لطفاً یک عدد صحیح وارد کنید.",
        "ru": "❌ Неверный ID пользователя. Пожалуйста, введите правильное число.",
        "en": "❌ Invalid user ID. Please enter a valid number."
    },
    "manual_refund_invalid_amount": {
        "fa": "❌ مقدار استارز نامعتبر است. لطفاً یک عدد مثبت وارد کنید.",
        "ru": "❌ Неверное количество звезд. Пожалуйста, введите положительное число.",
        "en": "❌ Invalid star amount. Please enter a positive number."
    },
    "manual_refund_user_not_found": {
        "fa": "❌ کاربر با این ID یافت نشد.",
        "ru": "❌ Пользователь с этим ID не найден.",
        "en": "❌ User with this ID not found."
    },
    "manual_refund_no_payment_history": {
        "fa": "❌ این کاربر هیچ تاریخچه پرداختی ندارد.",
        "ru": "❌ У этого пользователя нет истории платежей.",
        "en": "❌ This user has no payment history."
    },
    "manual_refund_success": {
        "fa": "✅ ریفاند دستی با موفقیت انجام شد.\n👤 کاربر: {user_id}\n💰 مقدار: {amount} استارز",
        "ru": "✅ Ручной возврат успешно выполнен.\n👤 Пользователь: {user_id}\n💰 Сумма: {amount} звезд",
        "en": "✅ Manual refund completed successfully.\n👤 User: {user_id}\n💰 Amount: {amount} stars"
    },
    "manual_refund_failed": {
        "fa": "❌ خطا در انجام ریفاند دستی: {error}",
        "ru": "❌ Ошибка при выполнении ручного возврата: {error}",
        "en": "❌ Error performing manual refund: {error}"
    },
    "manual_refund_user_notification": {
        "fa": "💸 ریفاند دستی\n\n✅ {amount} استارز به حساب شما بازگردانده شد.\n\n📝 این ریفاند توسط مدیریت سیستم انجام شده است.",
        "ru": "💸 Ручной возврат\n\n✅ {amount} звезд возвращено на ваш счет.\n\n📝 Этот возврат был выполнен администрацией системы.",
        "en": "💸 Manual Refund\n\n✅ {amount} stars have been refunded to your account.\n\n📝 This refund was performed by system administration."
    },
    "refund_by_transaction_button": {
        "fa": "🔍 ریفاند با Transaction ID",
        "ru": "🔍 Возврат по Transaction ID",
        "en": "🔍 Refund by Transaction ID"
    },
    "refund_by_transaction_request_id": {
        "fa": "🆔 لطفاً Transaction ID تلگرام را وارد کنید:",
        "ru": "🆔 Пожалуйста, введите Transaction ID Telegram:",
        "en": "🆔 Please enter the Telegram Transaction ID:"
    },
    "refund_by_transaction_invalid_id": {
        "fa": "❌ Transaction ID نامعتبر است یا پرداختی با این ID یافت نشد.",
        "ru": "❌ Неверный Transaction ID или платеж с этим ID не найден.",
        "en": "❌ Invalid Transaction ID or no payment found with this ID."
    },
    "refund_by_transaction_already_refunded": {
        "fa": "❌ این پرداخت قبلاً ریفاند شده است.",
        "ru": "❌ Этот платеж уже был возвращен.",
        "en": "❌ This payment has already been refunded."
    },
    "refund_by_transaction_success": {
        "fa": "✅ ریفاند با Transaction ID موفقیت‌آمیز بود.\n🆔 Transaction ID: {transaction_id}\n👤 کاربر: {user_id}\n💰 مقدار: {amount} استارز",
        "ru": "✅ Возврат по Transaction ID выполнен успешно.\n🆔 Transaction ID: {transaction_id}\n👤 Пользователь: {user_id}\n💰 Сумма: {amount} звезд",
        "en": "✅ Refund by Transaction ID completed successfully.\n🆔 Transaction ID: {transaction_id}\n👤 User: {user_id}\n💰 Amount: {amount} stars"
    },
    "refund_by_transaction_failed": {
        "fa": "❌ خطا در ریفاند با Transaction ID: {error}",
        "ru": "❌ Ошибка при возврате по Transaction ID: {error}",
        "en": "❌ Error refunding by Transaction ID: {error}"
    },
    
    # Anti-spam messages
    "spam_cooldown_error": {
        "fa": "⏰ لطفاً {seconds} ثانیه صبر کنید قبل از ارسال پیام بعدی.",
        "ru": "⏰ Пожалуйста, подождите {seconds} секунд перед отправкой следующего сообщения.",
        "en": "⏰ Please wait {seconds} seconds before sending the next message."
    },
    "spam_daily_limit_error": {
        "fa": "🚫 شما به حد مجاز روزانه ({limit}) رسیده‌اید. فردا دوباره تلاش کنید.",
        "ru": "🚫 Вы достигли дневного лимита ({limit}). Попробуйте завтра снова.",
        "en": "🚫 You have reached the daily limit ({limit}). Try again tomorrow."
    },
    "spam_hourly_limit_error": {
        "fa": "🚫 شما به حد مجاز ساعتی ({limit}) رسیده‌اید. یک ساعت دیگر تلاش کنید.",
        "ru": "🚫 Вы достигли часового лимита ({limit}). Попробуйте через час.",
        "en": "🚫 You have reached the hourly limit ({limit}). Try again in an hour."
    },
    "spam_limits_reset": {
        "fa": "✅ محدودیت‌های کاربر ریست شد.",
        "ru": "✅ Ограничения пользователя сброшены.",
        "en": "✅ User limits have been reset."
    },
    "detailed_stats_button": {
        "fa": "📊 آمار تفصیلی",
        "ru": "📊 Подробная статистика",
        "en": "📊 Detailed Statistics"
    },
    
    # Channel photo request
    "channel_photo_request": {
        "fa": "📸 لطفاً یک عکس از کانال خود ارسال کنید (اختیاری):\n\n⚠️ اگر نمی‌خواهید عکس ارسال کنید، روی دکمه 'رد کردن' کلیک کنید.",
        "ru": "📸 Пожалуйста, отправьте фото вашего канала (необязательно):\n\n⚠️ Если вы не хотите отправлять фото, нажмите кнопку 'Пропустить'.",
        "en": "📸 Please send a photo of your channel (optional):\n\n⚠️ If you don't want to send a photo, click the 'Skip' button."
    },
    "skip_photo_button": {
        "fa": "⏭️ رد کردن",
        "ru": "⏭️ Пропустить",
        "en": "⏭️ Skip"
    },
    
    # Ad preview
    "ad_preview_title": {
        "fa": "👀 پیش‌نمایش آگهی شما:",
        "ru": "👀 Предварительный просмотр вашего объявления:",
        "en": "👀 Preview of your ad:"
    },
    "confirm_ad_button": {
        "fa": "✅ تایید و ادامه",
        "ru": "✅ Подтвердить и продолжить",
        "en": "✅ Confirm and Continue"
    },
    "edit_ad_button": {
        "fa": "✏️ ویرایش",
        "ru": "✏️ Редактировать",
        "en": "✏️ Edit"
    },
    "cancel_ad_button": {
        "fa": "❌ لغو",
        "ru": "❌ Отменить",
        "en": "❌ Cancel"
    },
    "ad_cancelled": {
        "fa": "❌ ثبت آگهی لغو شد.",
        "ru": "❌ Размещение объявления отменено.",
        "en": "❌ Ad posting cancelled."
    },
    "ad_preview_text": {
        "fa": "📋 پیش‌نمایش آگهی:",
        "ru": "📋 Предварительный просмотр объявления:",
        "en": "📋 Ad Preview:"
    },
    "price": {
        "fa": "قیمت",
        "ru": "Цена",
        "en": "Price"
    },
    "description": {
        "fa": "توضیحات",
        "ru": "Описание",
        "en": "Description"
    },
    
    # My Ads Management
    "my_ads_title": {
        "fa": "📋 آگهی‌های من",
        "ru": "📋 Мои объявления",
        "en": "📋 My Ads"
    },
    "no_ads_found": {
        "fa": "شما هیچ آگهی ثبت نکرده‌اید.",
        "ru": "У вас нет размещенных объявлений.",
        "en": "You have no posted ads."
    },
    "ad_status_available": {
        "fa": "🟢 موجود",
        "ru": "🟢 Доступно",
        "en": "🟢 Available"
    },
    "ad_status_sold": {
        "fa": "🔴 فروش رفت",
        "ru": "🔴 Продано",
        "en": "🔴 Sold"
    },
    "mark_as_sold_button": {
        "fa": "🔴 علامت‌گذاری به عنوان فروش رفته",
        "ru": "🔴 Отметить как проданное",
        "en": "🔴 Mark as Sold"
    },
    "mark_as_available_button": {
        "fa": "🟢 علامت‌گذاری به عنوان موجود",
        "ru": "🟢 Отметить как доступное",
        "en": "🟢 Mark as Available"
    },
    "ad_marked_sold": {
        "fa": "✅ آگهی به عنوان فروش رفته علامت‌گذاری شد و در کانال به‌روزرسانی شد.",
        "ru": "✅ Объявление отмечено как проданное и обновлено в канале.",
        "en": "✅ Ad marked as sold and updated in the channel."
    },
    "ad_marked_available": {
        "fa": "✅ آگهی به عنوان موجود علامت‌گذاری شد و در کانال به‌روزرسانی شد.",
        "ru": "✅ Объявление отмечено как доступное и обновлено в канале.",
        "en": "✅ Ad marked as available and updated in the channel."
    },
    "status": {
        "fa": "وضعیت",
        "ru": "Статус",
        "en": "Status"
    }
}

def get_text(key: str, lang: str = "fa", **kwargs) -> str:
    """
    Get translated text for the given key and language
    
    Args:
        key: Translation key
        lang: Language code (fa, ru, en)
        **kwargs: Format parameters for the text
    
    Returns:
        Translated text
    """
    if key not in TRANSLATIONS:
        return f"[Missing translation: {key}]"
    
    if lang not in TRANSLATIONS[key]:
        # Fallback to Persian if language not found
        lang = "fa"
    
    text = TRANSLATIONS[key][lang]
    
    # Format text with provided parameters
    if kwargs:
        try:
            text = text.format(**kwargs)
        except KeyError:
            pass  # Ignore missing format parameters
    
    return text

def get_language_keyboard():
    """
    Get reply keyboard for language selection
    """
    from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
    
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="🇮🇷 فارسی"),
                KeyboardButton(text="🇷🇺 Русский")
            ],
            [
                KeyboardButton(text="🇺🇸 English")
            ]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    
    return keyboard

def get_main_menu_keyboard(language='fa'):
    """
    Get reply keyboard for main menu
    """
    from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
    
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=get_text('new_ad_button', language)),
                KeyboardButton(text=get_text('my_ads_button', language))
            ],
            [
                KeyboardButton(text=get_text('support_button', language)),
                KeyboardButton(text=get_text('change_language_button', language))
            ]
        ],
        resize_keyboard=True
    )
    
    return keyboard

def get_back_keyboard(language='fa'):
    """
    Get reply keyboard with back button
    """
    from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
    
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=get_text('back_to_menu_button', language))
            ]
        ],
        resize_keyboard=True
    )
    
    return keyboard

def get_admin_response_keyboard() -> ReplyKeyboardMarkup:
    """Get admin response keyboard for support"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="📝 پاسخ دادن")]],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    return keyboard

def get_channel_photo_keyboard(language='fa'):
    """
    Get keyboard for channel photo request with skip option
    """
    from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
    
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=get_text('skip_photo_button', language))
            ],
            [
                KeyboardButton(text=get_text('back_to_menu_button', language))
            ]
        ],
        resize_keyboard=True
    )
    
    return keyboard

def get_ad_preview_keyboard(language='fa'):
    """
    Get keyboard for ad preview confirmation
    """
    from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
    
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=get_text('confirm_ad_button', language))
            ],
            [
                KeyboardButton(text=get_text('edit_ad_button', language)),
                KeyboardButton(text=get_text('cancel_ad_button', language))
            ]
        ],
        resize_keyboard=True
    )
    
    return keyboard

def get_super_admin_keyboard(language='fa'):
    """
    Get reply keyboard for super admin menu
    """
    from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
    
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=get_text('list_users', language)),
                KeyboardButton(text=get_text('search_user', language))
            ],
            [
                KeyboardButton(text=get_text('view_user_info_button', language)),
                KeyboardButton(text=get_text('detailed_stats_button', language))
            ],
            [
                KeyboardButton(text=get_text('refund_all_stars_button', language)),
                KeyboardButton(text=get_text('manual_refund_button', language))
            ],
            [
                KeyboardButton(text=get_text('refund_by_transaction_button', language))
            ],
            [
                KeyboardButton(text=get_text('back_to_menu_button', language))
            ]
        ],
        resize_keyboard=True
    )
    
    return keyboard
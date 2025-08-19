# Translation system for multi-language bot support
# Supports Persian (fa), Russian (ru), and English (en)

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
        "fa": "🎁 لطفاً لینک گیفت خود را ارسال کنید:",
        "ru": "🎁 Пожалуйста, отправьте ссылку на ваш подарок:",
        "en": "🎁 Please send your gift link:"
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
        "fa": "❌ لینک وارد شده معتبر نیست. لطفاً لینک صحیح گیفت ارسال کنید.",
        "ru": "❌ Введенная ссылка недействительна. Пожалуйста, отправьте правильную ссылку на подарок.",
        "en": "❌ Invalid link entered. Please send a valid gift link."
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
    "ad_submitted": {
        "fa": "✅ آگهی شما با موفقیت ثبت شد و برای بررسی ارسال شد.",
        "ru": "✅ Ваше объявление успешно отправлено на рассмотрение.",
        "en": "✅ Your ad has been successfully submitted for review."
    },
    "ad_approved": {
        "fa": "🎉 آگهی شما تایید شد و در کانال منتشر شد!",
        "ru": "🎉 Ваше объявление одобрено и опубликовано в канале!",
        "en": "🎉 Your ad has been approved and published in the channel!"
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
        "fa": "📌 راهنمای ثبت آگهی گیفت\n\n✨ آگهی گیفت خود را تنها در چند مرحله ساده ثبت کنید:\n\n1️⃣ شروع ← روی دکمه \"ثبت آگهی\" کلیک کنید.\n2️⃣ ارسال لینک ← لینک گیفت یا محصول خود را ارسال کنید.\n3️⃣ تعیین قیمت ← قیمت را به تون وارد کنید (مثال: 50 تون).\n4️⃣ پرداخت ← ستاره پرداخت کنید تا آگهی فعال شود.\n5️⃣ تایید و انتشار ← پس از تایید ادمین، آگهی شما در کانال منتشر می‌شود. 🎉\n\n💡 نکته:\nبرای افزایش شانس فروش، می‌توانید همزمان محصول خود را در مارکت‌ های شخص ثالث نیز لیست کنید و اینجا هم آگهی ثبت کنید.\n\n✅ فقط لینک گیفت ارسال کنید.\n⚠️ آگهی‌های اسپم منجر به اخطار و در نهایت مسدودی از کانال می‌شود.",
        "ru": "📌 Руководство по размещению объявлений о подарках\n\n✨ Разместите свой подарок на продажу всего за несколько простых шагов:\n\n1️⃣ Начало ← Нажмите кнопку \"Разместить объявление\".\n2️⃣ Отправить ссылку ← Отправьте ссылку на ваш подарок или товар.\n3️⃣ Установить цену ← Введите цену в TON (пример: 50 TON).\n4️⃣ Оплата ← Заплатите звезды для активации объявления.\n5️⃣ Одобрение и публикация ← После одобрения администратором ваше объявление будет опубликовано в канале. 🎉\n\n💡 Совет:\nЧтобы увеличить шансы на продажу, вы можете одновременно разместить свой товар на сторонних торговых площадках и также разместить объявление здесь.\n\n✅ Отправляйте только ссылку на подарок.\n⚠️ Спам-объявления приведут к предупреждениям и в конечном итоге к бану с канала.",
        "en": "📌 Gift Ad Posting Guide\n\n✨ Post your gift for sale in just a few simple steps:\n\n1️⃣ Start → Click on the \"Post Ad\" button.\n2️⃣ Send Link → Submit the link of your gift or product.\n3️⃣ Set Price → Enter the price in TON (example: 50 TON).\n4️⃣ Payment → Pay stars to activate your ad.\n5️⃣ Approval & Publish → After admin approval, your ad will be published in the channel. 🎉\n\n💡 Tip:\nTo increase your chances of selling, you can list your product on third-party marketplaces at the same time and also post an ad here.\n\n✅ Only send the gift link.\n⚠️ Spam ads will result in warnings and eventually a ban from the channel."
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
    Get inline keyboard for language selection
    """
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🇮🇷 فارسی", callback_data="lang_fa"),
            InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru")
        ],
        [
            InlineKeyboardButton(text="🇺🇸 English", callback_data="lang_en")
        ]
    ])
    
    return keyboard
import asyncio
import logging
import os
from typing import Dict, Any

from aiogram import Bot, Dispatcher, F
from aiogram.types import (
    Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton,
    LabeledPrice, PreCheckoutQuery, ContentType, ReplyKeyboardMarkup, KeyboardButton
)
# RefundStarPayment is available through bot methods
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv

from database import Database
from translations import get_text, get_language_keyboard, get_main_menu_keyboard, get_back_keyboard, get_admin_response_keyboard, TRANSLATIONS

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Bot configuration
BOT_TOKEN = os.getenv('BOT_TOKEN')
SUPER_ADMIN_ID = int(os.getenv('SUPER_ADMIN_ID'))
SUPPORT_ADMIN_ID = int(os.getenv('SUPPORT_ADMIN_ID'))
CHANNEL_ID = os.getenv('CHANNEL_ID')
CHANNEL_NAME = os.getenv('CHANNEL_NAME')
STARS_AMOUNT = int(os.getenv('STARS_AMOUNT', 10))
DATABASE_PATH = os.getenv('DATABASE_PATH', 'ads_bot.db')

# Messages
WELCOME_MESSAGE = os.getenv('WELCOME_MESSAGE')
PRICE_REQUEST_MESSAGE = os.getenv('PRICE_REQUEST_MESSAGE')
PAYMENT_MESSAGE = os.getenv('PAYMENT_MESSAGE')
AD_SUBMITTED_MESSAGE = os.getenv('AD_SUBMITTED_MESSAGE')
AD_APPROVED_MESSAGE = os.getenv('AD_APPROVED_MESSAGE')
AD_REJECTED_MESSAGE = os.getenv('AD_REJECTED_MESSAGE')
AD_TAG_TEXT = os.getenv('AD_TAG_TEXT')

# Initialize bot and dispatcher
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
db = Database(DATABASE_PATH)

# States
class AdStates(StatesGroup):
    waiting_for_language = State()
    waiting_for_gift_link = State()
    waiting_for_description = State()
    waiting_for_price = State()
    waiting_for_payment = State()

class SupportStates(StatesGroup):
    waiting_for_support_message = State()
    waiting_for_admin_response = State()

class AdminStates(StatesGroup):
    waiting_for_user_id = State()
    waiting_for_rejection_reason = State()

# User data storage
user_ads: Dict[int, Dict[str, Any]] = {}

@dp.message(Command('start'))
async def start_handler(message: Message, state: FSMContext):
    """Handle /start command"""
    user = message.from_user
    
    # Check if user exists and get their language
    existing_user = await db.get_user(user.id)
    if existing_user:
        language = existing_user[7] if existing_user[7] else 'fa'  # language is at index 7
        # If user already has a language preference, show main menu
        await message.answer(
            get_text('welcome_message', language),
            reply_markup=get_main_menu_keyboard(language)
        )
    else:
        # New user - ask for language selection first
        await db.add_user(
            user.id, 
            user.username, 
            user.first_name, 
            user.last_name,
            user.language_code,
            user.is_bot,
            user.is_premium,
            'fa'  # Default to Persian temporarily
        )
        
        await message.answer(
            "لطفاً زبان خود را انتخاب کنید:\nPlease select your language:\nПожалуйста, выберите свой язык:",
            reply_markup=get_language_keyboard()
        )
        await state.set_state(AdStates.waiting_for_language)
        return
    
    await state.clear()

# Handle text messages for Reply Keyboard
@dp.message(F.text.in_(["📝 ثبت آگهی جدید", "📝 Разместить новое объявление", "📝 Post New Ad"]))
async def new_ad_handler(message: Message, state: FSMContext):
    """Start new ad creation process - show guide first, then ask for gift link"""
    user_id = message.from_user.id
    user = await db.get_user(user_id)
    language = user[7] if user and user[7] else 'fa'  # language is at index 7
    
    # Check if user has username
    if not message.from_user.username:
        await message.answer(
            get_text('username_required', language),
            reply_markup=get_back_keyboard(language)
        )
        return
    
    # Show ad posting guide first
    guide_text = get_text('ad_posting_guide', language)
    guide_text += "\n\n" + get_text('gift_link_request', language)
    
    await message.answer(
        guide_text,
        reply_markup=get_back_keyboard(language)
    )
    # Save language in state for consistency across ad creation process
    await state.update_data(language=language)
    await state.set_state(AdStates.waiting_for_gift_link)

@dp.message(F.text.in_(["🇮🇷 فارسی", "🇷🇺 Русский", "🇺🇸 English"]))
async def process_language_selection(message: Message, state: FSMContext):
    """Process language selection (both initial and change)"""
    # Map text to language code
    language_map = {
        "🇮🇷 فارسی": "fa",
        "🇷🇺 Русский": "ru", 
        "🇺🇸 English": "en"
    }
    language = language_map.get(message.text, "fa")
    user_id = message.from_user.id
    
    # Update user's language preference
    await db.update_user_language(user_id, language)
    
    # Show main menu after language selection
    await message.answer(
        get_text('welcome_message', language),
        reply_markup=get_main_menu_keyboard(language)
    )
    await state.clear()

@dp.message(F.text.in_(["🔙 بازگشت به منو", "🔙 Вернуться в меню", "🔙 Back to Menu"]))
async def back_to_menu_handler(message: Message, state: FSMContext):
    """Return to main menu"""
    user_id = message.from_user.id
    language = await db.get_user_language(user_id)
    
    await message.answer(
        get_text('welcome_message', language),
        reply_markup=get_main_menu_keyboard(language)
    )
    await state.clear()

@dp.message(F.text.in_(["🌐 تغییر زبان", "🌐 Изменить язык", "🌐 Change Language"]))
async def change_language_handler(message: Message, state: FSMContext):
    """Handle change language button"""
    await message.answer(
        "لطفاً زبان جدید خود را انتخاب کنید:\nPlease select your new language:\nПожалуйста, выберите новый язык:",
        reply_markup=get_language_keyboard()
    )
    await state.set_state(AdStates.waiting_for_language)

@dp.message(StateFilter(AdStates.waiting_for_gift_link))
async def process_gift_link(message: Message, state: FSMContext):
    """Process gift link input"""
    gift_link = message.text.strip()
    state_data = await state.get_data()
    # Get language from state, if not available get from database
    language = state_data.get('language')
    if not language:
        language = await db.get_user_language(message.from_user.id)
    
    # Basic validation for Telegram links (gift, NFT, channels, etc.)
    gift_patterns = [
        'https://t.me/nft/',
        't.me/nft/',
        'http://t.me/nft/',
        't.me/nft/'
    ]
    
    channel_patterns = [
        'https://t.me/',
        't.me/',
        'http://t.me/',
        '@'
    ]
    
    # Check if it's a gift link
    is_gift = any(gift_link.startswith(pattern) for pattern in gift_patterns)
    
    # Check if it's a channel link (but not a gift link)
    is_channel = False
    if not is_gift:
        # Check for channel patterns
        if gift_link.startswith('@'):
            is_channel = True
        elif any(gift_link.startswith(pattern) for pattern in channel_patterns):
            # Make sure it's not a bot link or other special links
            if '/nft/' not in gift_link and '_bot' not in gift_link.lower() and '/joinchat/' not in gift_link:
                is_channel = True
    
    if not (is_gift or is_channel):
        await message.answer(get_text('invalid_link', language))
        return
    
    # Store gift link and language
    user_ads[message.from_user.id] = {'gift_link': gift_link, 'language': language}
    
    await message.answer(
        get_text('description_request', language),
        reply_markup=get_back_keyboard(language)
    )
    await state.set_state(AdStates.waiting_for_description)

@dp.message(StateFilter(AdStates.waiting_for_description))
async def process_description(message: Message, state: FSMContext):
    """Process description input"""
    description = message.text.strip()
    
    # Get current ad data
    if message.from_user.id not in user_ads:
        await message.answer("خطا در پردازش. لطفاً دوباره شروع کنید.")
        await state.clear()
        return
    
    # Set default description if empty or "بدون توضیح"
    if not description or description.lower() in ['بدون توضیح', 'no description', 'без описания']:
        description = "توضیحات ندارد"
    
    # Store description
    user_ads[message.from_user.id]['description'] = description
    
    # Get language from state first, then from user_ads as fallback
    state_data = await state.get_data()
    language = state_data.get('language')
    if not language:
        language = user_ads[message.from_user.id]['language']
    
    await message.answer(
        get_text('price_request', language),
        reply_markup=get_back_keyboard(language)
    )
    await state.set_state(AdStates.waiting_for_price)

@dp.message(StateFilter(AdStates.waiting_for_price))
async def process_price(message: Message, state: FSMContext):
    """Process price input"""
    price = message.text.strip()
    user_id = message.from_user.id
    
    if user_id not in user_ads:
        # Get user language from database
        language = await db.get_user_language(user_id)
        await message.answer(get_text('error_restart', language))
        await state.clear()
        return
    
    # Get language from state first, then from user_ads as fallback
    state_data = await state.get_data()
    language = state_data.get('language')
    if not language:
        language = user_ads[user_id].get('language', 'fa')
    
    # Validate that price is a number
    try:
        # Check if the input is a valid number (integer or float)
        float(price)
        # Also check that it's not negative
        if float(price) < 0:
            await message.answer(get_text('invalid_price', language))
            return
    except ValueError:
        # If conversion to float fails, it's not a valid number
        await message.answer(get_text('invalid_price', language))
        return
    
    user_ads[user_id]['price'] = price
    
    # Create payment invoice
    await message.answer_invoice(
        title=get_text('payment_title', language),
        description=get_text('payment_description', language).format(STARS_AMOUNT),
        payload=f"ad_payment_{user_id}",
        provider_token="",  # Empty for Telegram Stars
        currency="XTR",  # Telegram Stars currency
        prices=[LabeledPrice(label=get_text('payment_label', language), amount=STARS_AMOUNT)]
    )
    
    await state.set_state(AdStates.waiting_for_payment)

@dp.pre_checkout_query()
async def process_pre_checkout_query(pre_checkout_query: PreCheckoutQuery):
    """Handle pre-checkout query"""
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

@dp.message(F.content_type == ContentType.SUCCESSFUL_PAYMENT)
async def process_successful_payment(message: Message, state: FSMContext):
    """Handle successful payment"""
    user_id = message.from_user.id
    
    if user_id not in user_ads:
        # Get user language from database
        language = await db.get_user_language(user_id)
        await message.answer(get_text('payment_error', language))
        return
    
    # Create ad in database
    ad_data = user_ads[user_id]
    language = ad_data.get('language', 'fa')
    description = ad_data.get('description', 'توضیحات ندارد')
    
    # Get telegram_payment_charge_id from successful payment
    telegram_payment_charge_id = message.successful_payment.telegram_payment_charge_id
    
    ad_id = await db.create_ad(user_id, ad_data['gift_link'], ad_data['price'], description, telegram_payment_charge_id)
    await db.update_payment_status(ad_id, 'paid')
    
    # Clean up user data
    del user_ads[user_id]
    
    await message.answer(get_text('ad_submitted', language))
    
    # Send to admin for approval
    await send_ad_to_admin(ad_id)
    
    await state.clear()

async def send_ad_to_admin(ad_id: int):
    """Send ad to both admin types for approval"""
    try:
        ad_data = await db.get_ad(ad_id)
        if not ad_data:
            logger.error(f"Ad with ID {ad_id} not found")
            return
        
        user_info = f"👤 کاربر: {ad_data['first_name'] or ''} {ad_data['last_name'] or ''}"
        if ad_data['username']:
            user_info += f" (@{ad_data['username']})"
        user_info += f"\n🆔 ID: {ad_data['user_id']}"
        
        # Determine if it's a gift or channel
        gift_link = ad_data['gift_link']
        is_gift = '/nft/' in gift_link
        
        if is_gift:
            link_type = "🎁 لینک گیفت"
        else:
            link_type = "📺 کانال تلگرام"
        
        admin_message = f"""🆕 آگهی جدید برای تایید:

{user_info}
{link_type}: {ad_data['gift_link']}
💰 قیمت: {ad_data['price']}
📝 توضیحات: {ad_data.get('description', 'توضیحات ندارد')}
📅 تاریخ ثبت: {ad_data['created_at']}"""
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ تایید", callback_data=f"approve_{ad_id}"),
                InlineKeyboardButton(text="❌ رد", callback_data=f"reject_{ad_id}")
            ]
        ])
        
        # Send to both admin types
        try:
            await bot.send_message(SUPPORT_ADMIN_ID, admin_message, reply_markup=keyboard)
            logger.info(f"Ad {ad_id} sent to SUPPORT_ADMIN_ID: {SUPPORT_ADMIN_ID}")
        except Exception as e:
            logger.error(f"Failed to send ad {ad_id} to SUPPORT_ADMIN_ID {SUPPORT_ADMIN_ID}: {e}")
        
        try:
            await bot.send_message(SUPER_ADMIN_ID, admin_message, reply_markup=keyboard)
            logger.info(f"Ad {ad_id} sent to SUPER_ADMIN_ID: {SUPER_ADMIN_ID}")
        except Exception as e:
            logger.error(f"Failed to send ad {ad_id} to SUPER_ADMIN_ID {SUPER_ADMIN_ID}: {e}")
            
    except Exception as e:
        logger.error(f"Error in send_ad_to_admin for ad {ad_id}: {e}")

@dp.callback_query(F.data.startswith("approve_"))
async def approve_ad(callback: CallbackQuery):
    """Approve ad and send to channel"""
    if callback.from_user.id not in [SUPPORT_ADMIN_ID, SUPER_ADMIN_ID]:
        await callback.answer("شما مجاز به انجام این عمل نیستید.", show_alert=True)
        return
    
    ad_id = int(callback.data.split("_")[1])
    ad_data = await db.get_ad(ad_id)
    
    if not ad_data:
        await callback.answer("آگهی یافت نشد.", show_alert=True)
        return
    
    # Update ad status
    await db.update_ad_status(ad_id, 'approved')
    
    # Determine if it's a gift or channel for channel message
    gift_link = ad_data['gift_link']
    is_gift = '/nft/' in gift_link
    
    # Get description
    description = ad_data.get('description', 'توضیحات ندارد')
    description_text = f"\n📝 {description}" if description != 'توضیحات ندارد' else ""
    
    if is_gift:
        # Gift message
        channel_message = f"""🎁 {ad_data['gift_link']}
💰 Price: {ad_data['price']} TON
👤 Seller: @{ad_data['username']}{description_text}

📢 Ad posted on {CHANNEL_NAME}

⚠️ Only trade on trusted marketplaces like <a href="https://t.me/portals/market?startapp=d15jj7">Portals</a>, <a href="https://t.me/tonnel_network_bot/gifts?startapp=ref_195742142">Tonnel</a>, and <a href="https://t.me/mrkt/app?startapp=195742142">Mrkt</a>!"""
    else:
        # Channel message
        channel_message = f"""📺 {ad_data['gift_link']}
💰 Price: {ad_data['price']} TON
👤 Seller: @{ad_data['username']}{description_text}

📢 Ad posted on {CHANNEL_NAME}

⚠️ Please verify the channel before joining!"""
    
    try:
        await bot.send_message(CHANNEL_ID, channel_message, parse_mode='HTML')
        
        # Notify user
        await bot.send_message(ad_data['user_id'], AD_APPROVED_MESSAGE)
        
        # Update admin message
        await callback.message.edit_text(
            callback.message.text + "\n\n✅ تایید شد و در کانال منتشر شد."
        )
        
    except Exception as e:
        logger.error(f"Error sending to channel: {e}")
        await callback.answer("خطا در ارسال به کانال.", show_alert=True)
    
    await callback.answer("آگهی تایید شد.")

@dp.callback_query(F.data.startswith("reject_") & ~F.data.startswith("reject_refund_") & ~F.data.startswith("reject_no_refund_"))
async def reject_ad(callback: CallbackQuery, state: FSMContext):
    """Start rejection process - ask for reason"""
    logger.info(f"reject_ad called with data: {callback.data}")
    if callback.from_user.id not in [SUPPORT_ADMIN_ID, SUPER_ADMIN_ID]:
        await callback.answer("شما مجاز به انجام این عمل نیستید.", show_alert=True)
        return
    
    ad_id = int(callback.data.split("_")[1])
    ad_data = await db.get_ad(ad_id)
    
    if not ad_data:
        await callback.answer("آگهی یافت نشد.", show_alert=True)
        return
    
    # Store ad_id in state for later use
    await state.update_data(rejecting_ad_id=ad_id)
    await state.set_state(AdminStates.waiting_for_rejection_reason)
    
    # Ask for rejection reason with refund option
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💰 رد با ریفاند", callback_data=f"reject_refund_{ad_id}")],
        [InlineKeyboardButton(text="❌ رد بدون ریفاند", callback_data=f"reject_no_refund_{ad_id}")]
    ])
    
    await callback.message.reply(
        "لطفاً نوع رد آگهی را انتخاب کنید:",
        reply_markup=keyboard
    )
    await callback.answer()

@dp.callback_query(F.data.startswith("reject_refund_"))
async def reject_ad_with_refund(callback: CallbackQuery, state: FSMContext):
    """Reject ad with refund"""
    logger.info(f"reject_ad_with_refund called with data: {callback.data}")
    if callback.from_user.id not in [SUPPORT_ADMIN_ID, SUPER_ADMIN_ID]:
        await callback.answer("شما مجاز به انجام این عمل نیستید.", show_alert=True)
        return
    
    ad_id = int(callback.data.split("_")[2])
    logger.info(f"Processing refund rejection for ad_id: {ad_id}")
    await state.update_data(rejecting_ad_id=ad_id, with_refund=True)
    await state.set_state(AdminStates.waiting_for_rejection_reason)
    
    await callback.message.reply("لطفاً دلیل رد آگهی را وارد کنید (یا 'بدون توضیح' بنویسید):")
    await callback.answer()

@dp.callback_query(F.data.startswith("reject_no_refund_"))
async def reject_ad_without_refund(callback: CallbackQuery, state: FSMContext):
    """Reject ad without refund"""
    logger.info(f"reject_ad_without_refund called with data: {callback.data}")
    if callback.from_user.id not in [SUPPORT_ADMIN_ID, SUPER_ADMIN_ID]:
        await callback.answer("شما مجاز به انجام این عمل نیستید.", show_alert=True)
        return
    
    ad_id = int(callback.data.split("_")[3])  # reject_no_refund_123 -> index 3
    logger.info(f"Processing no-refund rejection for ad_id: {ad_id}")
    await state.update_data(rejecting_ad_id=ad_id, with_refund=False)
    await state.set_state(AdminStates.waiting_for_rejection_reason)
    
    await callback.message.reply("لطفاً دلیل رد آگهی را وارد کنید (یا 'بدون توضیح' بنویسید):")
    await callback.answer()

@dp.message(StateFilter(AdminStates.waiting_for_rejection_reason))
async def process_rejection_reason(message: Message, state: FSMContext):
    """Process rejection reason and reject the ad"""
    if message.from_user.id not in [SUPPORT_ADMIN_ID, SUPER_ADMIN_ID]:
        await message.reply("شما مجاز به انجام این عمل نیستید.")
        return
    
    # Get stored ad_id and refund option
    data = await state.get_data()
    ad_id = data.get('rejecting_ad_id')
    with_refund = data.get('with_refund', False)
    
    if not ad_id:
        await message.reply("خطا: شناسه آگهی یافت نشد.")
        await state.clear()
        return
    
    ad_data = await db.get_ad(ad_id)
    if not ad_data:
        await message.reply("آگهی یافت نشد.")
        await state.clear()
        return
    
    # Get rejection reason
    rejection_reason = message.text.strip()
    if not rejection_reason or rejection_reason.lower() == 'بدون توضیح':
        rejection_reason = "توضیحات ندارد"
    
    # Update ad status
    await db.update_ad_status(ad_id, 'rejected')
    
    # Handle refund if requested
    refund_status = ""
    if with_refund:
        refund_success = await refund_stars(ad_id)
        if refund_success:
            refund_status = "\n💰 استارز با موفقیت بازگردانده شد."
        else:
            refund_status = "\n❌ خطا در بازگرداندن استارز."
    
    # Notify user with reason and refund status
    user_message = f"{AD_REJECTED_MESSAGE}\n\n📝 دلیل رد: {rejection_reason}{refund_status}"
    await bot.send_message(ad_data['user_id'], user_message)
    
    # Confirm to admin
    admin_message = f"✅ آگهی با موفقیت رد شد.\n📝 دلیل: {rejection_reason}{refund_status}"
    await message.reply(admin_message)
    
    # Clear state
    await state.clear()

async def refund_stars(ad_id: int) -> bool:
    """Refund stars for rejected ad"""
    try:
        ad_data = await db.get_ad(ad_id)
        if not ad_data or not ad_data.get('telegram_payment_charge_id'):
            logger.error(f"Cannot refund ad {ad_id}: No payment charge ID found")
            return False
        
        # Refund the stars using Bot API method
        refund_result = await bot.refund_star_payment(
            user_id=ad_data['user_id'],
            telegram_payment_charge_id=ad_data['telegram_payment_charge_id']
        )
        
        logger.info(f"Stars refunded successfully for ad {ad_id}")
        return True
        
    except Exception as e:
        logger.error(f"Error refunding stars for ad {ad_id}: {e}")
        return False

# Support handlers
@dp.message(F.text.in_(["🆘 پشتیبانی", "🆘 Поддержка", "🆘 Support"]))
async def support_handler(message: Message, state: FSMContext):
    """Handle support button"""
    user_id = message.from_user.id
    language = await db.get_user_language(user_id)
    
    await message.answer(
        get_text('support_message', language),
        reply_markup=get_back_keyboard(language)
    )
    await state.set_state(SupportStates.waiting_for_support_message)

@dp.message(StateFilter(SupportStates.waiting_for_support_message))
async def process_support_message(message: Message, state: FSMContext):
    """Process support message"""
    user = message.from_user
    support_text = message.text
    user_language = await db.get_user_language(user.id)
    
    # Save support request to database
    request_id = await db.create_support_request(user.id, support_text)
    
    # Send to support admin
    support_message = f"🆘 درخواست پشتیبانی جدید\n\n"
    support_message += f"👤 کاربر: {user.first_name or ''} {user.last_name or ''}\n"
    support_message += f"🆔 آیدی: {user.id}\n"
    support_message += f"👤 یوزرنیم: @{user.username or 'ندارد'}\n\n"
    support_message += f"💬 پیام:\n{support_text}"
    
    # Create inline keyboard for admin response
    inline_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📝 پاسخ دادن", callback_data=f"respond_{request_id}")]
    ])
    
    await bot.send_message(SUPPORT_ADMIN_ID, support_message, reply_markup=inline_keyboard)
    
    await message.answer(
        get_text('support_sent', user_language),
        reply_markup=get_back_keyboard(user_language)
    )
    await state.clear()

@dp.callback_query(F.data.startswith("respond_"))
async def respond_to_support(callback: CallbackQuery, state: FSMContext):
    """Handle support response"""
    if callback.from_user.id != SUPPORT_ADMIN_ID:
        await callback.answer(get_text('no_permission', 'fa'))
        return
    
    # Extract request ID from callback data
    request_id = int(callback.data.split("_")[1])
    
    # Get the specific support request
    request = await db.get_support_request_by_id(request_id)
    if not request:
        await callback.answer("درخواست پشتیبانی یافت نشد.")
        return
    
    # Use the specific request
    await state.update_data(support_request_id=request_id)
    
    await callback.message.answer(get_text('admin_response_request', 'fa'))
    await state.set_state(SupportStates.waiting_for_admin_response)
    await callback.answer()

@dp.message(StateFilter(SupportStates.waiting_for_admin_response))
async def process_admin_response(message: Message, state: FSMContext):
    """Process admin response to support"""
    if message.from_user.id != SUPPORT_ADMIN_ID:
        return
    
    data = await state.get_data()
    request_id = data.get('support_request_id')
    response_text = message.text
    
    # Update support request in database
    await db.respond_to_support_request(request_id, response_text)
    
    # Get original request details
    original_request = await db.get_support_request_by_id(request_id)
    
    if original_request:
        # Get user's language and send response
        user_language = await db.get_user_language(original_request['user_id'])
        user_message = f"📩 {get_text('admin_response_title', user_language)}\n\n{response_text}"
        await bot.send_message(original_request['user_id'], user_message)
        
        await message.answer(get_text('response_sent', 'fa'))
    else:
        await message.answer(get_text('error_sending_response', 'fa'))
    
    await state.clear()

# Admin panels
@dp.message(Command('support_admin'))
async def support_admin_panel(message: Message):
    """Support admin panel"""
    if message.from_user.id != SUPPORT_ADMIN_ID:
        return
    
    # Get pending ads and support requests
    pending_ads = await db.get_pending_ads()
    pending_support = await db.get_pending_support_requests()
    
    panel_text = f"{get_text('support_admin_panel', 'fa')}\n\n"
    panel_text += f"📝 {get_text('pending_ads_count', 'fa')}: {len(pending_ads)}\n"
    panel_text += f"🆘 {get_text('pending_support_count', 'fa')}: {len(pending_support)}\n\n"
    
    keyboard = []
    if pending_ads:
        keyboard.append([InlineKeyboardButton(text=get_text('view_pending_ads', 'fa'), callback_data="view_pending_ads")])
    if pending_support:
        keyboard.append([InlineKeyboardButton(text=get_text('view_support_requests', 'fa'), callback_data="view_support_requests")])
    
    await message.answer(panel_text, reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard))

@dp.callback_query(F.data == "view_pending_ads")
async def view_pending_ads(callback: CallbackQuery):
    """View pending ads for support admin"""
    if callback.from_user.id != SUPPORT_ADMIN_ID:
        await callback.answer(get_text('no_permission', 'fa'), show_alert=True)
        return
    
    pending_ads = await db.get_pending_ads()
    
    if not pending_ads:
        await callback.answer("هیچ آگهی در انتظار وجود ندارد.", show_alert=True)
        return
    
    await callback.message.answer(f"📊 {len(pending_ads)} آگهی در انتظار تایید")
    
    for ad in pending_ads:
        await send_ad_to_admin(ad['id'])
    
    await callback.answer()

@dp.callback_query(F.data == "view_support_requests")
async def view_support_requests(callback: CallbackQuery):
    """View pending support requests"""
    if callback.from_user.id != SUPPORT_ADMIN_ID:
        await callback.answer("دسترسی ندارید.", show_alert=True)
        return
    
    requests = await db.get_pending_support_requests()
    
    if not requests:
        await callback.answer("هیچ درخواست پشتیبانی وجود ندارد.", show_alert=True)
        return
    
    for req in requests:
        support_message = f"🆘 درخواست پشتیبانی\n\n"
        support_message += f"👤 کاربر: {req['first_name'] or ''} {req['last_name'] or ''}\n"
        support_message += f"🆔 آیدی: {req['user_id']}\n"
        support_message += f"👤 یوزرنیم: @{req['username'] or 'ندارد'}\n\n"
        support_message += f"💬 پیام:\n{req['message']}"
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📝 پاسخ دادن", callback_data=f"respond_{req['id']}")]
        ])
        
        await callback.message.answer(support_message, reply_markup=keyboard)
    
    await callback.answer()

@dp.message(Command('super_admin'))
async def super_admin_panel(message: Message):
    """Super admin panel"""
    if message.from_user.id != SUPER_ADMIN_ID:
        return
    
    stats = await db.get_user_stats()
    
    panel_text = "👑 پنل سوپر ادمین\n\n"
    panel_text += f"👥 کل کاربران: {stats.get('total_users', 0)}\n"
    panel_text += f"📝 کل آگهی‌ها: {stats.get('total_ads', 0)}\n"
    panel_text += f"✅ آگهی‌های تایید شده: {stats.get('approved_ads', 0)}\n"
    panel_text += f"⏳ آگهی‌های در انتظار: {stats.get('pending_ads', 0)}\n"
    panel_text += f"🆘 درخواست‌های پشتیبانی: {stats.get('total_support_requests', 0)}\n"
    panel_text += f"⏳ درخواست‌های در انتظار: {stats.get('pending_support_requests', 0)}\n\n"
    
    keyboard = [
        [InlineKeyboardButton(text="👥 لیست کاربران", callback_data="list_users")],
        [InlineKeyboardButton(text="🔍 جستجوی کاربر", callback_data="search_user")],
        [InlineKeyboardButton(text="👤 دیدن اطلاعات کاربر", callback_data="view_user_info")],
        [InlineKeyboardButton(text="📊 آمار تفصیلی", callback_data="detailed_stats")]
    ]
    
    await message.answer(panel_text, reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard))

@dp.callback_query(F.data == "list_users")
async def list_users(callback: CallbackQuery):
    """List all users"""
    if callback.from_user.id != SUPER_ADMIN_ID:
        await callback.answer("دسترسی ندارید.", show_alert=True)
        return
    
    users = await db.get_all_users()
    
    if not users:
        await callback.answer("هیچ کاربری وجود ندارد.", show_alert=True)
        return
    
    # Show first 10 users
    users_text = "👥 لیست کاربران (10 کاربر اول):\n\n"
    
    for i, user in enumerate(users[:10], 1):
        users_text += f"{i}. {user['first_name'] or ''} {user['last_name'] or ''}\n"
        users_text += f"   🆔 {user['user_id']} | @{user['username'] or 'ندارد'}\n"
        users_text += f"   📅 {user['created_at'][:10]}\n\n"
    
    if len(users) > 10:
        users_text += f"... و {len(users) - 10} کاربر دیگر"
    
    await callback.message.answer(users_text)
    await callback.answer()

@dp.callback_query(F.data == "search_user")
async def search_user_callback(callback: CallbackQuery, state: FSMContext):
    """Search user by ID"""
    if callback.from_user.id != SUPER_ADMIN_ID:
        await callback.answer("دسترسی ندارید.", show_alert=True)
        return
    
    await callback.message.answer("🔍 آیدی کاربر را وارد کنید:")
    await state.set_state(AdminStates.waiting_for_user_id)
    await callback.answer()

@dp.callback_query(F.data == "view_user_info")
async def view_user_info_callback(callback: CallbackQuery):
    """View user information with inline buttons"""
    if callback.from_user.id != SUPER_ADMIN_ID:
        await callback.answer("دسترسی ندارید.", show_alert=True)
        return
    
    users = await db.get_all_users()
    
    if not users:
        await callback.answer("هیچ کاربری وجود ندارد.", show_alert=True)
        return
    
    # Show first 20 users with inline buttons
    users_text = "👤 انتخاب کاربر برای مشاهده اطلاعات:\n\n"
    keyboard = []
    
    for i, user in enumerate(users[:20], 1):
        user_name = f"{user['first_name'] or ''} {user['last_name'] or ''}".strip() or "بدون نام"
        username = f"@{user['username']}" if user['username'] else "بدون یوزرنیم"
        
        button_text = f"{i}. {user_name} ({user['user_id']})"
        keyboard.append([InlineKeyboardButton(text=button_text, callback_data=f"user_info_{user['user_id']}")])
    
    if len(users) > 20:
        users_text += f"نمایش 20 کاربر اول از {len(users)} کاربر"
    
    await callback.message.answer(users_text, reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard))
    await callback.answer()

@dp.callback_query(F.data.startswith("user_info_"))
async def show_user_info(callback: CallbackQuery):
    """Show detailed user information"""
    if callback.from_user.id != SUPER_ADMIN_ID:
        await callback.answer("دسترسی ندارید.", show_alert=True)
        return
    
    # Extract user ID from callback data
    user_id = int(callback.data.split("_")[2])
    user_info = await db.get_user_by_id(user_id)
    
    if not user_info:
        await callback.answer("❌ کاربر یافت نشد.", show_alert=True)
        return
    
    info_text = f"👤 اطلاعات کاربر\n\n"
    info_text += f"🆔 آیدی: {user_info['user_id']}\n"
    info_text += f"👤 نام: {user_info['first_name'] or ''} {user_info['last_name'] or ''}\n"
    info_text += f"👤 یوزرنیم: @{user_info['username'] or 'ندارد'}\n"
    info_text += f"🌐 زبان: {user_info['language_code'] or 'ندارد'}\n"
    info_text += f"🤖 ربات: {'بله' if user_info['is_bot'] else 'خیر'}\n"
    info_text += f"⭐ پریمیوم: {'بله' if user_info['is_premium'] else 'خیر'}\n"
    info_text += f"📅 عضویت: {user_info['created_at'][:10]}\n"
    info_text += f"🕐 آخرین بازدید: {user_info['last_seen'][:16]}\n\n"
    info_text += f"📊 آمار:\n"
    info_text += f"📝 کل آگهی‌ها: {user_info['total_ads']}\n"
    info_text += f"✅ آگهی‌های تایید شده: {user_info['approved_ads']}\n"
    info_text += f"🆘 درخواست‌های پشتیبانی: {user_info['support_requests']}\n"
    
    # Add back button
    back_keyboard = [[InlineKeyboardButton(text="🔙 بازگشت به لیست کاربران", callback_data="view_user_info")]]
    
    await callback.message.answer(info_text, reply_markup=InlineKeyboardMarkup(inline_keyboard=back_keyboard))
    await callback.answer()

@dp.message(StateFilter(AdminStates.waiting_for_user_id))
async def process_user_search(message: Message, state: FSMContext):
    """Process user search"""
    if message.from_user.id != SUPER_ADMIN_ID:
        return
    
    try:
        user_id = int(message.text)
        user_info = await db.get_user_by_id(user_id)
        
        if not user_info:
            await message.answer("❌ کاربر یافت نشد.")
            await state.clear()
            return
        
        info_text = f"👤 اطلاعات کاربر\n\n"
        info_text += f"🆔 آیدی: {user_info['user_id']}\n"
        info_text += f"👤 نام: {user_info['first_name'] or ''} {user_info['last_name'] or ''}\n"
        info_text += f"👤 یوزرنیم: @{user_info['username'] or 'ندارد'}\n"
        info_text += f"🌐 زبان: {user_info['language_code'] or 'ندارد'}\n"
        info_text += f"🤖 ربات: {'بله' if user_info['is_bot'] else 'خیر'}\n"
        info_text += f"⭐ پریمیوم: {'بله' if user_info['is_premium'] else 'خیر'}\n"
        info_text += f"📅 عضویت: {user_info['created_at'][:10]}\n"
        info_text += f"🕐 آخرین بازدید: {user_info['last_seen'][:16]}\n\n"
        info_text += f"📊 آمار:\n"
        info_text += f"📝 کل آگهی‌ها: {user_info['total_ads']}\n"
        info_text += f"✅ آگهی‌های تایید شده: {user_info['approved_ads']}\n"
        info_text += f"🆘 درخواست‌های پشتیبانی: {user_info['support_requests']}\n"
        
        await message.answer(info_text)
        
    except ValueError:
        await message.answer("❌ لطفاً یک عدد معتبر وارد کنید.")
    
    await state.clear()

async def main():
    """Main function"""
    # Initialize database
    await db.init_db()
    
    # Start polling
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
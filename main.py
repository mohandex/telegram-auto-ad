import asyncio
import logging
import os
from typing import Dict, Any

from aiogram import Bot, Dispatcher, F
from aiogram.types import (
    Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton,
    LabeledPrice, PreCheckoutQuery, ContentType, ReplyKeyboardMarkup, KeyboardButton
)
from aiogram.methods import RefundStarPayment
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv

from database import Database
from translations import get_text, get_language_keyboard, get_main_menu_keyboard, get_back_keyboard, get_admin_response_keyboard, get_super_admin_keyboard, get_channel_photo_keyboard, get_ad_preview_keyboard, TRANSLATIONS

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

# Anti-spam settings
AD_COOLDOWN_SECONDS = int(os.getenv('AD_COOLDOWN_SECONDS', 30))  # seconds between ad submissions
AD_DAILY_LIMIT = int(os.getenv('AD_DAILY_LIMIT', 5))  # Maximum ads per day
SUPPORT_COOLDOWN_SECONDS = int(os.getenv('SUPPORT_COOLDOWN_SECONDS', 60))  # seconds between support messages
SUPPORT_HOURLY_LIMIT = int(os.getenv('SUPPORT_HOURLY_LIMIT', 3))  # Maximum support requests per hour

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
    waiting_for_channel_photo = State()
    waiting_for_preview_confirmation = State()
    waiting_for_payment = State()

class SupportStates(StatesGroup):
    waiting_for_support_message = State()
    waiting_for_admin_response = State()

class AdminStates(StatesGroup):
    waiting_for_user_id = State()
    waiting_for_rejection_reason = State()

class ManualRefundStates(StatesGroup):
    waiting_for_user_id = State()
    waiting_for_amount = State()
    waiting_for_transaction_id = State()

# User data storage
user_ads: Dict[int, Dict[str, Any]] = {}

@dp.message(Command('start'))
async def start_handler(message: Message, state: FSMContext):
    """Handle /start command"""
    user = message.from_user
    
    # Check if user exists and get their language
    existing_user = await db.get_user(user.id)
    if existing_user:
        language = existing_user.get('language', 'fa')  # Get language from dictionary
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
    language = user.get('language', 'fa') if user else 'fa'
    
    # Check spam limits for ad creation
    spam_check = await db.check_spam_limit(
        user_id, 
        'ad_creation', 
        daily_limit=AD_DAILY_LIMIT, 
        cooldown_seconds=AD_COOLDOWN_SECONDS
    )
    
    if not spam_check['allowed']:
        if spam_check['reason'] == 'cooldown':
            await message.answer(
                get_text('spam_cooldown_error', language, seconds=spam_check['remaining_seconds']),
                reply_markup=get_back_keyboard(language)
            )
        elif spam_check['reason'] == 'daily_limit':
            await message.answer(
                get_text('spam_daily_limit_error', language, limit=spam_check['limit']),
                reply_markup=get_back_keyboard(language)
            )
        return
    
    # Check if user has username
    if not message.from_user.username:
        await message.answer(
            get_text('username_required', language),
            reply_markup=get_back_keyboard(language)
        )
        return
    
    # Record the action for spam control
    await db.record_action(user_id, 'ad_creation')
    
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
    
    # If super admin, show main menu instead of super admin panel
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

@dp.message(F.text.in_(["📋 آگهی‌های من", "📋 Мои объявления", "📋 My Ads"]))
async def my_ads_handler(message: Message, state: FSMContext):
    """Handle my ads button"""
    user_id = message.from_user.id
    user = await db.get_user(user_id)
    language = user.get('language', 'fa') if user else 'fa'
    
    # Get user's ads
    user_ads = await db.get_user_ads(user_id)
    
    if not user_ads:
        await message.answer(
            get_text('no_ads_found', language),
            reply_markup=get_back_keyboard(language)
        )
        return
    
    # Show ads with management buttons
    await message.answer(get_text('my_ads_title', language))
    
    for ad in user_ads:
        # Create ad text
        status_text = get_text('ad_status_sold', language) if ad.get('sold_status') == 'sold' else get_text('ad_status_available', language)
        ad_text = f"🆔 ID: {ad['id']}\n"
        ad_text += f"🎁 {ad['gift_link']}\n"
        ad_text += f"💰 {get_text('price', language)}: {ad['price']}\n"
        ad_text += f"📝 {get_text('description', language)}: {ad['description']}\n"
        ad_text += f"📊 {get_text('status', language)}: {ad['status']}\n"
        ad_text += f"🔄 {status_text}\n"
        ad_text += f"📅 {ad['created_at'][:10]}"
        
        # Create inline keyboard for ad management
        keyboard = []
        if ad.get('sold_status') == 'sold':
            keyboard.append([InlineKeyboardButton(
                text=get_text('mark_as_available_button', language),
                callback_data=f"mark_available_{ad['id']}"
            )])
        else:
            keyboard.append([InlineKeyboardButton(
                text=get_text('mark_as_sold_button', language),
                callback_data=f"mark_sold_{ad['id']}"
            )])
        
        await message.answer(
            ad_text,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
        )
    
    await state.clear()

@dp.callback_query(F.data.startswith("mark_sold_"))
async def mark_ad_as_sold(callback: CallbackQuery):
    """Mark ad as sold"""
    ad_id = int(callback.data.split("_")[2])
    user_id = callback.from_user.id
    
    # Get user language
    user = await db.get_user(user_id)
    language = user.get('language', 'fa') if user else 'fa'
    
    # Verify ad belongs to user
    ad = await db.get_ad(ad_id)
    if not ad or ad['user_id'] != user_id:
        await callback.answer(get_text('no_permission', language), show_alert=True)
        return
    
    # Update sold status
    await db.update_sold_status(ad_id, 'sold')
    
    # Update channel message if ad is approved
    if ad['status'] == 'approved':
        await update_channel_ad_text(ad_id, 'sold')
    
    await callback.answer(get_text('mark_as_sold_success', language), show_alert=True)
    
    # Refresh the ad display
    await refresh_ad_display(callback, ad_id, language)

@dp.callback_query(F.data.startswith("mark_available_"))
async def mark_ad_as_available(callback: CallbackQuery):
    """Mark ad as available"""
    ad_id = int(callback.data.split("_")[2])
    user_id = callback.from_user.id
    
    # Get user language
    user = await db.get_user(user_id)
    language = user.get('language', 'fa') if user else 'fa'
    
    # Verify ad belongs to user
    ad = await db.get_ad(ad_id)
    if not ad or ad['user_id'] != user_id:
        await callback.answer(get_text('no_permission', language), show_alert=True)
        return
    
    # Update sold status
    await db.update_sold_status(ad_id, 'available')
    
    # Update channel message if ad is approved
    if ad['status'] == 'approved':
        await update_channel_ad_text(ad_id, 'available')
    
    await callback.answer(get_text('mark_as_available_success', language), show_alert=True)
    
    # Refresh the ad display
    await refresh_ad_display(callback, ad_id, language)

async def refresh_ad_display(callback: CallbackQuery, ad_id: int, language: str):
    """Refresh the ad display after status change"""
    ad = await db.get_ad(ad_id)
    if not ad:
        return
    
    # Create updated ad text
    status_text = get_text('ad_status_sold', language) if ad.get('sold_status') == 'sold' else get_text('ad_status_available', language)
    ad_text = f"🆔 ID: {ad['id']}\n"
    ad_text += f"🎁 {ad['gift_link']}\n"
    ad_text += f"💰 {get_text('price', language)}: {ad['price']}\n"
    ad_text += f"📝 {get_text('description', language)}: {ad['description']}\n"
    ad_text += f"📊 {get_text('status', language)}: {ad['status']}\n"
    ad_text += f"🔄 {status_text}\n"
    ad_text += f"📅 {ad['created_at'][:10]}"
    
    # Create updated inline keyboard
    keyboard = []
    if ad.get('sold_status') == 'sold':
        keyboard.append([InlineKeyboardButton(
            text=get_text('mark_as_available_button', language),
            callback_data=f"mark_available_{ad['id']}"
        )])
    else:
        keyboard.append([InlineKeyboardButton(
            text=get_text('mark_as_sold_button', language),
            callback_data=f"mark_sold_{ad['id']}"
        )])
    
    try:
        await callback.message.edit_text(
            ad_text,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
        )
    except:
        pass  # Message might be the same

async def update_channel_ad_text(ad_id: int, sold_status: str):
    """Update the ad text in the channel to show sold status"""
    ad = await db.get_ad(ad_id)
    if not ad or ad['status'] != 'approved' or not ad.get('channel_message_id'):
        return
    
    try:
        # Determine if it's a gift or channel for channel message
        gift_link = ad.get('gift_link') or 'لینک ندارد'
        is_gift = '/nft/' in gift_link if gift_link != 'لینک ندارد' else False
        
        # Get description
        description = ad.get('description') or 'توضیحات ندارد'
        description_text = f"\n📝 {description}" if description and description != 'توضیحات ندارد' else ""
        
        # Handle all fields safely
        username = ad.get('username') or 'ناشناس'
        gift_link = ad.get('gift_link') or 'لینک ندارد'
        price = ad.get('price') or '0'
        
        # Add sold status to message
        sold_text = "\n\n🔴 SOLD" if sold_status == 'sold' else ""
        
        if is_gift:
            # Gift message
            channel_message = f"""🎁 {gift_link}
💰 Price: {price} TON
👤 Seller: @{username}{description_text}

📢 Ad posted on {CHANNEL_NAME}

⚠️ Only trade on trusted marketplaces like <a href="https://t.me/portals/market?startapp=d15jj7">Portals</a>, <a href="https://t.me/tonnel_network_bot/gifts?startapp=ref_195742142">Tonnel</a>, and <a href="https://t.me/mrkt/app?startapp=195742142">Mrkt</a>!{sold_text}"""
        else:
            # Channel message
            channel_message = f"""📺 {gift_link}
💰 Price: {price} TON
👤 Seller: @{username}{description_text}

📢 Ad posted on {CHANNEL_NAME}

⚠️ Please verify the channel before joining!{sold_text}"""
        
        # Update the channel message
        channel_photo = ad.get('channel_photo')
        if channel_photo:
            await bot.edit_message_caption(
                chat_id=CHANNEL_ID,
                message_id=ad['channel_message_id'],
                caption=channel_message,
                parse_mode='HTML'
            )
        else:
            await bot.edit_message_text(
                chat_id=CHANNEL_ID,
                message_id=ad['channel_message_id'],
                text=channel_message,
                parse_mode='HTML'
            )
        
        logger.info(f"Updated channel message for ad {ad_id} with sold status: {sold_status}")
        
    except Exception as e:
        logger.error(f"Error updating channel message for ad {ad_id}: {e}")

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
    # Check if message has text content
    if not message.text:
        # Get user language from database
        user_id = message.from_user.id
        language = await db.get_user_language(user_id)
        await message.answer(get_text('price_request', language))
        return
    
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
    
    # Ask for channel photo
    await message.answer(
        get_text('channel_photo_request', language),
        reply_markup=get_channel_photo_keyboard(language)
    )
    
    await state.set_state(AdStates.waiting_for_channel_photo)

@dp.message(StateFilter(AdStates.waiting_for_channel_photo))
async def process_channel_photo(message: Message, state: FSMContext):
    """Process channel photo input or skip"""
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
    
    channel_photo = None
    
    # Check if user clicked skip button
    if message.text and message.text == get_text('skip_photo_button', language):
        channel_photo = None
    elif message.photo:
        # Get the largest photo
        channel_photo = message.photo[-1].file_id
    else:
        await message.answer(get_text('invalid_photo', language))
        return
    
    # Store channel photo (or None if skipped)
    user_ads[user_id]['channel_photo'] = channel_photo
    
    # Show ad preview
    await show_ad_preview(message, state, user_id, language)

async def show_ad_preview(message: Message, state: FSMContext, user_id: int, language: str):
    """Show ad preview to user for confirmation"""
    ad_data = user_ads[user_id]
    
    # Create preview text
    preview_text = get_text('ad_preview_text', language)
    preview_text += f"\n\n📺 {ad_data['gift_link']}"
    preview_text += f"\n💰 {get_text('price', language)}: {ad_data['price']} TON"
    
    description = ad_data.get('description', 'توضیحات ندارد')
    if description and description != 'توضیحات ندارد':
        preview_text += f"\n📄 {get_text('description', language)}: {description}"
    
    # Send preview with photo if available
    if ad_data.get('channel_photo'):
        await message.answer_photo(
            photo=ad_data['channel_photo'],
            caption=preview_text,
            reply_markup=get_ad_preview_keyboard(language)
        )
    else:
        await message.answer(
            preview_text,
            reply_markup=get_ad_preview_keyboard(language)
        )
    
    await state.set_state(AdStates.waiting_for_preview_confirmation)

@dp.message(StateFilter(AdStates.waiting_for_preview_confirmation))
async def process_preview_confirmation(message: Message, state: FSMContext):
    """Process ad preview confirmation"""
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
    
    if message.text == get_text('confirm_ad_button', language):
        # User confirmed - proceed to payment
        await message.answer_invoice(
            title=get_text('payment_title', language),
            description=get_text('payment_description', language).format(STARS_AMOUNT),
            payload=f"ad_payment_{user_id}",
            provider_token="",  # Empty for Telegram Stars
            currency="XTR",  # Telegram Stars currency
            prices=[LabeledPrice(label=get_text('payment_label', language), amount=STARS_AMOUNT)]
        )
        # Send main menu keyboard separately
        await message.answer(
            get_text('payment_sent', language),
            reply_markup=get_main_menu_keyboard(language)
        )
        await state.set_state(AdStates.waiting_for_payment)
        
    elif message.text == get_text('edit_ad_button', language):
        # User wants to edit - go back to gift link
        await message.answer(
            get_text('gift_link_request', language),
            reply_markup=get_back_keyboard(language)
        )
        await state.set_state(AdStates.waiting_for_gift_link)
        
    elif message.text == get_text('cancel_ad_button', language):
        # User wants to cancel
        del user_ads[user_id]
        await message.answer(
            get_text('ad_cancelled', language),
            reply_markup=get_main_menu_keyboard(language)
        )
        await state.clear()
        
    else:
        await message.answer(get_text('invalid_choice', language))

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
    channel_photo = ad_data.get('channel_photo')
    
    # Get telegram_payment_charge_id from successful payment
    telegram_payment_charge_id = message.successful_payment.telegram_payment_charge_id
    
    ad_id = await db.create_ad(user_id, ad_data['gift_link'], ad_data['price'], description, telegram_payment_charge_id, STARS_AMOUNT, channel_photo)
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
        
        # Handle names safely
        first_name = ad_data.get('first_name') or ''
        last_name = ad_data.get('last_name') or ''
        user_info = f"👤 کاربر: {first_name} {last_name}"
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
        
        # Send to both admin types with photo if available
        channel_photo = ad_data.get('channel_photo')
        
        try:
            if channel_photo:
                await bot.send_photo(SUPPORT_ADMIN_ID, photo=channel_photo, caption=admin_message, reply_markup=keyboard)
            else:
                await bot.send_message(SUPPORT_ADMIN_ID, admin_message, reply_markup=keyboard)
            logger.info(f"Ad {ad_id} sent to SUPPORT_ADMIN_ID: {SUPPORT_ADMIN_ID}")
        except Exception as e:
            logger.error(f"Failed to send ad {ad_id} to SUPPORT_ADMIN_ID {SUPPORT_ADMIN_ID}: {e}")
        
        try:
            if channel_photo:
                await bot.send_photo(SUPER_ADMIN_ID, photo=channel_photo, caption=admin_message, reply_markup=keyboard)
            else:
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
    gift_link = ad_data.get('gift_link') or 'لینک ندارد'
    is_gift = '/nft/' in gift_link if gift_link != 'لینک ندارد' else False
    
    # Get description
    description = ad_data.get('description') or 'توضیحات ندارد'
    description_text = f"\n📝 {description}" if description and description != 'توضیحات ندارد' else ""
    
    # Handle all fields safely
    username = ad_data.get('username') or 'ناشناس'
    gift_link = ad_data.get('gift_link') or 'لینک ندارد'
    price = ad_data.get('price') or '0'
    
    if is_gift:
        # Gift message
        channel_message = f"""🎁 {gift_link}
💰 Price: {price} TON
👤 Seller: @{username}{description_text}

📢 Ad posted on {CHANNEL_NAME}

⚠️ Only trade on trusted marketplaces like <a href="https://t.me/portals/market?startapp=d15jj7">Portals</a>, <a href="https://t.me/tonnel_network_bot/gifts?startapp=ref_195742142">Tonnel</a>, and <a href="https://t.me/mrkt/app?startapp=195742142">Mrkt</a>!"""
    else:
        # Channel message
        channel_message = f"""📺 {gift_link}
💰 Price: {price} TON
👤 Seller: @{username}{description_text}

📢 Ad posted on {CHANNEL_NAME}

⚠️ Please verify the channel before joining!"""
    
    try:
        # Send to channel with photo if available
        channel_photo = ad_data.get('channel_photo')
        if channel_photo:
            channel_msg = await bot.send_photo(CHANNEL_ID, photo=channel_photo, caption=channel_message, parse_mode='HTML')
        else:
            channel_msg = await bot.send_message(CHANNEL_ID, channel_message, parse_mode='HTML')
        
        # Store channel message ID for future updates
        await db.update_channel_message_id(ad_id, channel_msg.message_id)
        
        # Notify user
        user_language = await db.get_user_language(ad_data['user_id'])
        user_message = get_text('ad_approved', user_language, channel_name=CHANNEL_NAME)
        await bot.send_message(ad_data['user_id'], user_message)
        
        # Send log to super admin if approved by support admin
        if callback.from_user.id == SUPPORT_ADMIN_ID and SUPER_ADMIN_ID != SUPPORT_ADMIN_ID:
            # Handle names safely
            first_name = ad_data.get('first_name') or ''
            last_name = ad_data.get('last_name') or ''
            admin_log = f"""✅ آگهی تایید شد

📝 لینک: {ad_data['gift_link']}
📄 توضیحات: {description}
💰 قیمت: {ad_data['price']} TON
👤 کاربر: {first_name} {last_name} (@{username})
🆔 ID: {ad_data['user_id']}
👨‍💼 تایید شده توسط: {callback.from_user.first_name or ''} ({callback.from_user.id})
📅 تاریخ: {ad_data['created_at']}"""
            await bot.send_message(SUPER_ADMIN_ID, admin_log)
        
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
    
    # Send log to super admin if rejected by support admin
    if message.from_user.id == SUPPORT_ADMIN_ID and SUPER_ADMIN_ID != SUPPORT_ADMIN_ID:
        description = ad_data.get('description', 'توضیحات ندارد')
        # Handle username and names safely
        username = ad_data.get('username') or 'ندارد'
        first_name = ad_data.get('first_name') or ''
        last_name = ad_data.get('last_name') or ''
        admin_log = f"""❌ آگهی رد شد

📝 لینک: {ad_data['gift_link']}
📄 توضیحات: {description}
💰 قیمت: {ad_data['price']} TON
👤 کاربر: {first_name} {last_name} (@{username})
🆔 ID: {ad_data['user_id']}
📝 دلیل رد: {rejection_reason}
💸 ریفاند: {'بله' if with_refund else 'خیر'}
👨‍💼 رد شده توسط: {message.from_user.first_name or ''} ({message.from_user.id})
📅 تاریخ: {ad_data['created_at']}{refund_status}"""
        await bot.send_message(SUPER_ADMIN_ID, admin_log)
    
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
        refund_result = await bot(RefundStarPayment(
            user_id=ad_data['user_id'],
            telegram_payment_charge_id=ad_data['telegram_payment_charge_id']
        ))
        
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
    
    # Check spam limits for support requests
    spam_check = await db.check_spam_limit(
        user_id, 
        'support_request', 
        hourly_limit=SUPPORT_HOURLY_LIMIT, 
        cooldown_seconds=SUPPORT_COOLDOWN_SECONDS
    )
    
    if not spam_check['allowed']:
        if spam_check['reason'] == 'cooldown':
            await message.answer(
                get_text('spam_cooldown_error', language, seconds=spam_check['remaining_seconds']),
                reply_markup=get_back_keyboard(language)
            )
        elif spam_check['reason'] == 'hourly_limit':
            await message.answer(
                get_text('spam_hourly_limit_error', language, limit=spam_check['limit']),
                reply_markup=get_back_keyboard(language)
            )
        return
    
    # Record the action for spam control
    await db.record_action(user_id, 'support_request')
    
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
        
        # Send log to super admin if response is from support admin
        if message.from_user.id == SUPPORT_ADMIN_ID and SUPER_ADMIN_ID != SUPPORT_ADMIN_ID:
            admin_log = f"📩 پاسخ پشتیبانی ارسال شد\n\n👤 کاربر: {original_request['user_id']}\n📝 پیام اصلی: {original_request['message']}\n💬 پاسخ ادمین: {response_text}\n👨‍💼 پاسخ داده شده توسط: {message.from_user.first_name or ''} ({message.from_user.id})\n📅 تاریخ: {original_request['created_at']}"
            await bot.send_message(SUPER_ADMIN_ID, admin_log)
        
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
    
    # Get user language
    user = await db.get_user(message.from_user.id)
    language = user.get('language', 'fa') if user else 'fa'
    
    stats = await db.get_user_stats()
    
    panel_text = get_text('super_admin_panel', language)
    panel_text += f"\n\n👥 کل کاربران: {stats.get('total_users', 0)}\n"
    panel_text += f"📝 کل آگهی‌ها: {stats.get('total_ads', 0)}\n"
    panel_text += f"✅ آگهی‌های تایید شده: {stats.get('approved_ads', 0)}\n"
    panel_text += f"⏳ آگهی‌های در انتظار: {stats.get('pending_ads', 0)}\n"
    panel_text += f"🆘 درخواست‌های پشتیبانی: {stats.get('total_support_requests', 0)}\n"
    panel_text += f"⏳ درخواست‌های در انتظار: {stats.get('pending_support_requests', 0)}\n\n"
    
    keyboard = get_super_admin_keyboard(language)
    
    await message.answer(panel_text, reply_markup=keyboard)

# Super Admin Reply Keyboard Handlers
@dp.message(F.text.in_(["👥 لیست کاربران", "👥 Список пользователей", "👥 List Users"]))
async def list_users_message(message: Message):
    """List users via reply keyboard"""
    if message.from_user.id != SUPER_ADMIN_ID:
        return
    
    users = await db.get_all_users()
    
    if not users:
        await message.answer("هیچ کاربری وجود ندارد.")
        return
    
    # Show first 10 users
    users_text = "👥 لیست کاربران (10 کاربر اول):\n\n"
    
    for i, user in enumerate(users[:10], 1):
        users_text += f"{i}. {user['first_name'] or ''} {user['last_name'] or ''}\n"
        users_text += f"   🆔 {user['user_id']} | @{user['username'] or 'ندارد'}\n"
        users_text += f"   📅 {user['created_at'][:10]}\n\n"
    
    if len(users) > 10:
        users_text += f"... و {len(users) - 10} کاربر دیگر"
    
    await message.answer(users_text)

@dp.message(F.text.in_(["🔍 جستجوی کاربر", "🔍 Поиск пользователя", "🔍 Search User"]))
async def search_user_message(message: Message, state: FSMContext):
    """Search user via reply keyboard"""
    if message.from_user.id != SUPER_ADMIN_ID:
        return
    
    await message.answer("🔍 لطفاً ID کاربر مورد نظر را وارد کنید:")
    await state.set_state(AdminStates.waiting_for_user_id)

@dp.message(F.text.in_(["👤 دیدن اطلاعات کاربر", "👤 Просмотр информации о пользователе", "👤 View User Info"]))
async def view_user_info_message(message: Message):
    """View user info via reply keyboard"""
    if message.from_user.id != SUPER_ADMIN_ID:
        return
    
    users = await db.get_all_users()
    
    if not users:
        await message.answer("هیچ کاربری وجود ندارد.")
        return
    
    # Show users with inline keyboard for selection
    keyboard = []
    for user in users[:20]:  # Show first 20 users
        name = f"{user['first_name'] or ''} {user['last_name'] or ''}" or f"User {user['user_id']}"
        keyboard.append([InlineKeyboardButton(text=f"{name[:30]}...", callback_data=f"user_info_{user['user_id']}")])
    
    await message.answer("👤 انتخاب کاربر برای مشاهده اطلاعات:", reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard))

@dp.message(F.text.in_(["💰 ریفاند کلی استارز", "💰 Возврат всех звезд", "💰 Refund All Stars"]))
async def refund_all_stars_message(message: Message):
    """Refund all stars via reply keyboard"""
    if message.from_user.id != SUPER_ADMIN_ID:
        return
    
    # Get total stars to refund
    total_stars = await db.get_total_stars_paid()
    
    if total_stars == 0:
        await message.answer("💰 هیچ ستاره‌ای برای ریفاند وجود ندارد.")
        return
    
    keyboard = [
        [InlineKeyboardButton(text="✅ تایید ریفاند", callback_data="confirm_refund_all")],
        [InlineKeyboardButton(text="❌ لغو", callback_data="cancel_refund_all")]
    ]
    
    await message.answer(
        f"⚠️ آیا مطمئن هستید که می‌خواهید {total_stars} ستاره را به تمام کاربران ریفاند کنید؟\n\n"
        "این عمل غیرقابل بازگشت است!",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
    )

@dp.message(F.text.in_(["📊 آمار تفصیلی", "📊 Подробная статистика", "📊 Detailed Statistics"]))
async def detailed_stats_message(message: Message):
    """Show detailed statistics via reply keyboard"""
    if message.from_user.id != SUPER_ADMIN_ID:
        return
    
    stats = await db.get_user_stats()
    total_stars = await db.get_total_stars_paid()
    
    stats_text = "📊 آمار تفصیلی سیستم\n\n"
    stats_text += f"👥 کل کاربران: {stats.get('total_users', 0)}\n"
    stats_text += f"📝 کل آگهی‌ها: {stats.get('total_ads', 0)}\n"
    stats_text += f"✅ آگهی‌های تایید شده: {stats.get('approved_ads', 0)}\n"
    stats_text += f"❌ آگهی‌های رد شده: {stats.get('rejected_ads', 0)}\n"
    stats_text += f"⏳ آگهی‌های در انتظار: {stats.get('pending_ads', 0)}\n"
    stats_text += f"🆘 کل درخواست‌های پشتیبانی: {stats.get('total_support_requests', 0)}\n"
    stats_text += f"⏳ درخواست‌های پشتیبانی در انتظار: {stats.get('pending_support_requests', 0)}\n"
    stats_text += f"💰 کل ستاره‌های پرداخت شده: {total_stars}\n"
    
    await message.answer(stats_text)

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
    info_text += f"🆘 درخواست‌های پشتیبانی: {user_info['support_requests']}\n\n"
    info_text += f"💰 اطلاعات مالی:\n"
    info_text += f"⭐ کل استارز پرداخت شده: {user_info['total_stars_paid']}\n"
    info_text += f"💸 کل استارز ریفاند شده: {user_info['total_stars_refunded']}\n"
    
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
        info_text += f"🆘 درخواست‌های پشتیبانی: {user_info['support_requests']}\n\n"
        info_text += f"💰 اطلاعات مالی:\n"
        info_text += f"⭐ کل استارز پرداخت شده: {user_info['total_stars_paid']}\n"
        info_text += f"💸 کل استارز ریفاند شده: {user_info['total_stars_refunded']}\n"
        
        await message.answer(info_text)
        
    except ValueError:
        await message.answer("❌ لطفاً یک عدد معتبر وارد کنید.")
    
    await state.clear()

@dp.callback_query(F.data == "refund_all_stars")
async def refund_all_stars_handler(callback: CallbackQuery):
    """Handle refund all stars request"""
    if callback.from_user.id != SUPER_ADMIN_ID:
        await callback.answer("دسترسی ندارید.", show_alert=True)
        return
    
    # Get all paid ads with telegram_payment_charge_id
    paid_ads = await db.get_all_paid_ads()
    
    if not paid_ads:
        await callback.answer("هیچ آگهی پرداخت شده‌ای برای ریفاند وجود ندارد.", show_alert=True)
        return
    
    # Show confirmation message
    confirmation_text = f"⚠️ هشدار: آیا مطمئن هستید که می‌خواهید تمام {len(paid_ads)} پرداخت را ریفاند کنید؟\n\n"
    confirmation_text += "این عمل غیرقابل بازگشت است!"
    
    keyboard = [
        [InlineKeyboardButton(text="✅ بله، ریفاند کن", callback_data="confirm_refund_all")],
        [InlineKeyboardButton(text="❌ انصراف", callback_data="cancel_refund_all")]
    ]
    
    await callback.message.edit_text(confirmation_text, reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard))
    await callback.answer()

@dp.callback_query(F.data == "confirm_refund_all")
async def confirm_refund_all_handler(callback: CallbackQuery):
    """Confirm and execute refund all stars"""
    if callback.from_user.id != SUPER_ADMIN_ID:
        await callback.answer("دسترسی ندارید.", show_alert=True)
        return
    
    await callback.message.edit_text("🔄 در حال ریفاند تمام استارزها... لطفاً صبر کنید.")
    
    # Get all paid ads
    paid_ads = await db.get_all_paid_ads()
    
    success_count = 0
    failed_count = 0
    total_count = len(paid_ads)
    
    for ad in paid_ads:
        try:
            if ad['telegram_payment_charge_id']:
                # Refund the stars
                refund_result = await bot(RefundStarPayment(
                    user_id=ad['user_id'],
                    telegram_payment_charge_id=ad['telegram_payment_charge_id']
                ))
                
                if refund_result:
                    success_count += 1
                    logger.info(f"Successfully refunded stars for ad {ad['id']} (user {ad['user_id']})")
                else:
                    failed_count += 1
                    logger.error(f"Failed to refund stars for ad {ad['id']} (user {ad['user_id']})")
            else:
                failed_count += 1
                logger.error(f"No payment charge ID for ad {ad['id']}")
                
        except Exception as e:
            failed_count += 1
            logger.error(f"Error refunding stars for ad {ad['id']}: {e}")
    
    # Show results
    result_text = f"✅ ریفاند کلی استارز تکمیل شد!\n\n"
    result_text += f"📊 نتایج:\n"
    result_text += f"✅ موفق: {success_count}\n"
    result_text += f"❌ ناموفق: {failed_count}\n"
    result_text += f"📝 کل: {total_count}"
    
    await callback.message.edit_text(result_text)
    await callback.answer()

@dp.callback_query(F.data == "cancel_refund_all")
async def cancel_refund_all_handler(callback: CallbackQuery):
    """Cancel refund all operation"""
    if callback.from_user.id != SUPER_ADMIN_ID:
        await callback.answer("دسترسی ندارید.", show_alert=True)
        return
    
    await callback.message.edit_text("❌ عملیات ریفاند کلی لغو شد.")
    await callback.answer()

# Manual Refund Handlers
@dp.message(Command('manual_refund'))
async def manual_refund_command(message: Message, state: FSMContext):
    """Handle /manual_refund command"""
    if message.from_user.id != SUPER_ADMIN_ID:
        return
    
    # Get user language
    user = await db.get_user(message.from_user.id)
    language = user.get('language', 'fa') if user else 'fa'
    
    await message.answer(
        get_text('manual_refund_request_user_id', language),
        reply_markup=get_back_keyboard(language)
    )
    await state.set_state(ManualRefundStates.waiting_for_user_id)

@dp.message(F.text.in_(["💸 ریفاند دستی", "💸 Ручной возврат", "💸 Manual Refund"]))
async def manual_refund_button_handler(message: Message, state: FSMContext):
    """Handle manual refund button"""
    if message.from_user.id != SUPER_ADMIN_ID:
        return
    
    # Get user language
    user = await db.get_user(message.from_user.id)
    language = user.get('language', 'fa') if user else 'fa'
    
    await message.answer(
        get_text('manual_refund_request_user_id', language),
        reply_markup=get_back_keyboard(language)
    )
    await state.set_state(ManualRefundStates.waiting_for_user_id)

@dp.message(StateFilter(ManualRefundStates.waiting_for_user_id))
async def process_manual_refund_user_id(message: Message, state: FSMContext):
    """Process user ID for manual refund"""
    if message.from_user.id != SUPER_ADMIN_ID:
        return
    
    # Get user language
    user = await db.get_user(message.from_user.id)
    language = user.get('language', 'fa') if user else 'fa'
    
    # Check if back button was pressed
    if message.text in ["🔙 بازگشت به منو", "🔙 Вернуться в меню", "🔙 Back to Menu"]:
        await back_to_menu_handler(message, state)
        return
    
    try:
        user_id = int(message.text)
    except ValueError:
        await message.answer(
            get_text('manual_refund_invalid_user_id', language),
            reply_markup=get_back_keyboard(language)
        )
        return
    
    # Check if user exists
    target_user = await db.get_user(user_id)
    if not target_user:
        await message.answer(
            get_text('manual_refund_user_not_found', language),
            reply_markup=get_back_keyboard(language)
        )
        return
    
    # Check if user has payment history
    user_info = await db.get_user_by_id(user_id)
    if not user_info or user_info.get('total_stars_paid', 0) == 0:
        await message.answer(
            get_text('manual_refund_no_payment_history', language),
            reply_markup=get_back_keyboard(language)
        )
        return
    
    # Store user_id and ask for amount
    await state.update_data(target_user_id=user_id)
    await message.answer(
        get_text('manual_refund_request_amount', language),
        reply_markup=get_back_keyboard(language)
    )
    await state.set_state(ManualRefundStates.waiting_for_amount)

@dp.message(StateFilter(ManualRefundStates.waiting_for_amount))
async def process_manual_refund_amount(message: Message, state: FSMContext):
    """Process refund amount for manual refund"""
    if message.from_user.id != SUPER_ADMIN_ID:
        return
    
    # Get user language
    user = await db.get_user(message.from_user.id)
    language = user.get('language', 'fa') if user else 'fa'
    
    # Check if back button was pressed
    if message.text in ["🔙 بازگشت به منو", "🔙 Вернуться в меню", "🔙 Back to Menu"]:
        await back_to_menu_handler(message, state)
        return
    
    try:
        amount = int(message.text)
        if amount <= 0:
            raise ValueError("Amount must be positive")
    except ValueError:
        await message.answer(
            get_text('manual_refund_invalid_amount', language),
            reply_markup=get_back_keyboard(language)
        )
        return
    
    # Get stored data
    data = await state.get_data()
    target_user_id = data.get('target_user_id')
    
    # Get user's latest payment charge ID
    latest_payment = await db.get_latest_payment_charge_id(target_user_id)
    if not latest_payment:
        await message.answer(
            get_text('manual_refund_no_payment_history', language),
            reply_markup=get_back_keyboard(language)
        )
        await state.clear()
        return
    
    try:
        # Perform the refund
        await bot(RefundStarPayment(
            user_id=target_user_id,
            telegram_payment_charge_id=latest_payment['telegram_payment_charge_id']
        ))
        
        # Update database
        await db.update_refund_status(latest_payment['id'], True)
        
        # Notify admin of success
        success_message = get_text('manual_refund_success', language, user_id=target_user_id, amount=amount)
        await message.answer(success_message, reply_markup=get_super_admin_keyboard(language))
        
        # Notify user
        target_user = await db.get_user(target_user_id)
        target_language = target_user.get('language', 'fa') if target_user else 'fa'
        user_notification = get_text('manual_refund_user_notification', target_language, amount=amount)
        await bot.send_message(target_user_id, user_notification)
        
        logger.info(f"Manual refund successful: {amount} stars to user {target_user_id}")
        
    except Exception as e:
        error_message = get_text('manual_refund_failed', language, error=str(e))
        await message.answer(error_message, reply_markup=get_super_admin_keyboard(language))
        logger.error(f"Manual refund failed for user {target_user_id}: {e}")
    
    await state.clear()

# Refund by Transaction ID Handlers
@dp.message(F.text.in_(["🔍 ریفاند با Transaction ID", "🔍 Возврат по Transaction ID", "🔍 Refund by Transaction ID"]))
async def refund_by_transaction_button_handler(message: Message, state: FSMContext):
    """Handle refund by transaction ID button"""
    if message.from_user.id != SUPER_ADMIN_ID:
        return
    
    # Get user language
    user = await db.get_user(message.from_user.id)
    language = user.get('language', 'fa') if user else 'fa'
    
    await message.answer(
        get_text('refund_by_transaction_request_id', language),
        reply_markup=get_back_keyboard(language)
    )
    await state.set_state(ManualRefundStates.waiting_for_transaction_id)

@dp.message(StateFilter(ManualRefundStates.waiting_for_transaction_id))
async def process_refund_by_transaction_id(message: Message, state: FSMContext):
    """Process refund by transaction ID"""
    if message.from_user.id != SUPER_ADMIN_ID:
        return
    
    # Get user language
    user = await db.get_user(message.from_user.id)
    language = user.get('language', 'fa') if user else 'fa'
    
    # Check if back button was pressed
    if message.text in ["🔙 بازگشت به منو", "🔙 Вернуться в меню", "🔙 Back to Menu"]:
        await back_to_menu_handler(message, state)
        return
    
    transaction_id = message.text.strip()
    
    # Get payment details by transaction ID
    payment_data = await db.get_payment_by_charge_id(transaction_id)
    if not payment_data:
        await message.answer(
            get_text('refund_by_transaction_invalid_id', language),
            reply_markup=get_back_keyboard(language)
        )
        return
    
    # Check if already refunded
    if payment_data.get('refunded', False):
        await message.answer(
            get_text('refund_by_transaction_already_refunded', language),
            reply_markup=get_back_keyboard(language)
        )
        return
    
    try:
        # Perform the refund
        await bot(RefundStarPayment(
            user_id=payment_data['user_id'],
            telegram_payment_charge_id=transaction_id
        ))
        
        # Update database
        await db.update_refund_status(payment_data['id'], True)
        
        # Notify admin of success
        success_message = get_text('refund_by_transaction_success', language, 
                                 transaction_id=transaction_id,
                                 user_id=payment_data['user_id'], 
                                 amount=payment_data['stars_paid'])
        await message.answer(success_message, reply_markup=get_super_admin_keyboard(language))
        
        # Notify user
        target_user = await db.get_user(payment_data['user_id'])
        target_language = target_user.get('language', 'fa') if target_user else 'fa'
        user_notification = get_text('manual_refund_user_notification', target_language, amount=payment_data['stars_paid'])
        await bot.send_message(payment_data['user_id'], user_notification)
        
        logger.info(f"Refund by transaction ID successful: {payment_data['stars_paid']} stars to user {payment_data['user_id']} (Transaction: {transaction_id})")
        
    except Exception as e:
        error_message = get_text('refund_by_transaction_failed', language, error=str(e))
        await message.answer(error_message, reply_markup=get_super_admin_keyboard(language))
        logger.error(f"Refund by transaction ID failed for transaction {transaction_id}: {e}")
    
    await state.clear()

async def main():
    """Main function"""
    # Initialize database
    await db.init_db()
    
    # Start polling
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
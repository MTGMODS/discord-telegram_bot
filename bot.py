import re
import os
import asyncio
import nest_asyncio
import time
import discord

from discord.ext import commands
from telegram import Bot, Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

TELEGRAM_VIP_CHAT_ID = -1002400049940
CHAT_CHANNEL_ID = 1097643848584396912
VIP_ROLE_ID = 1223269478310084708
VIP_CHANNEL_ID = 1251238756435099750
DISCORD_GUILD_ID = 1097643847774908526

tokens = {}

script_dir = os.path.dirname(os.path.abspath(__file__))
tokens_path = os.path.join(script_dir, "tokens.ini")

with open(tokens_path) as f:
    for line in f:
        if "=" in line:
            key, value = line.strip().split("=", 1)
            tokens[key.strip()] = value.strip()

DISCORD_BOT_TOKEN = tokens.get("DISCORD_BOT_TOKEN")
TG_BOT_TOKEN = tokens.get("TG_BOT_TOKEN")


# Telegram bot setup
def is_admin(username):
    return username == 'mtg_mods'

async def give_vip_role_in_ds(user, upd):
    guild = bot.get_guild(DISCORD_GUILD_ID)
    member = None 
    member = discord.utils.get(guild.members, id=int(user)) if user.isdigit() else discord.utils.get(guild.members, name=user)

    if member:
        role = guild.get_role(VIP_ROLE_ID)
        await member.add_roles(role)
        print(f"VIP роль успешно выдана пользователю {member.name}.")
        embed = discord.Embed(
            title='✅ Успешное приобретение VIP ✅',
            description=(
                f'🥳 Теперь вы - {role.mention}!\n\n'
                f'💎 VIP скрипты доступны в канале <#{VIP_CHANNEL_ID}> (закреп)\n\n'
                f'❤️ Спасибо за покупку VIP и финансовую поддержку!'
            ),
            color=0x3498DB
        )
        if member.display_avatar:
            embed.set_thumbnail(url=member.display_avatar.url)
        message = await bot.get_channel(CHAT_CHANNEL_ID).send(content=f'{member.mention}', embed=embed)
        await upd.message.reply_text((f"✅ VIP роль успешно выдана пользователю {member.name}!\n\n✅ Так-же {member.name} отправлено <a href='{message.jump_url}'>оповещение с инструкцией</a>."), parse_mode="HTML", disable_web_page_preview=True)
    else:
        await upd.message.reply_text(("❌ Пользователь с таким ID/USERNAME не найден!\n⚡Сначало зайдите на наш <a href='https://discord.gg/qBPEYjfNhv'>Discord сервер</a>."), parse_mode="HTML", disable_web_page_preview=True)

async def send_payment_info(update: Update, payment_method: str):
    payment_texts = {
        "visa": (
            f"<b>💳 Перевод на карту VISA по номеру:</b>\n"
            f"<pre>4441 1144 6426 8265</pre>\n\n"

            f"🌍 <b>Международный перевод:</b>\n"
            f"🔹 <b>Получатель: Marher Bohdan</b>\n"
            f"🔹 <b>Валюта: любая кроме RUB / BYN</b>\n"
            f"🔹 <b>Страна: Украина 🇺🇦</b>\n"
            f"🔹 <b>Банк: Monobank</b>\n\n"

            f"📩 <b>После оплаты отпишите</b> <a href='https://t.me/mtg_mods'>MTG MODS в ЛС</a>.\n\n"

            f"💳 <b>Также возможен перевод через SWIFT / SEPA, свяжитесь.</b>"
            
        ),
        "funpay": (
            f"<b>💵 Оплата через FunPay:</b>\n"
            f"🔗 <a href='https://funpay.com/lots/offer?id=37093025'>Ссылка на оплату</a>\n\n"
            f"✅ <b>Просто оплачивайте (💳/СБП QR)</b>\n"
            f"❌ <b>В чате на сайте писать не нужно!</b>\n\n"
            f"📩 <b>После оплаты отпишите</b> <a href='https://t.me/mtg_mods'>MTG MODS в ЛС</a>."
        ),
        "stars": (
            f"✨ <b>Оплата через Telegram Stars!</b> ✨\n\n"
            f"💰 <b>Стоимость: 350 ⭐</b>\n"
            f"👉 <b>Поставьте ⭐ на любой пост в</b> <a href='https://t.me/mtgmods'>нашем канале</a>\n\n"
            f"📩 <b>Затем напишите</b> <a href='https://t.me/mtg_mods'>MTG MODS в ЛС</a> и ожидайте ответа."
        ),
        "crypto": (
            f"🪙 <b>Оплата криптовалютой:</b>\n\n"
            f"📩 <b>Напишите</b> <a href='https://t.me/mtg_mods'>MTG MODS в ЛС</a> для получения кошелька."
        ),
        "paypal": (
            f"💲 <b>Оплата через PayPal:</b>\n"
            f"🔗 <a href='https://www.paypal.com/donate/?hosted_button_id=CC97BWMY8FFT8'>Ссылка на оплату</a>\n\n"
            f"📩 <b>После оплаты отпишите</b> <a href='https://t.me/mtg_mods'>MTG MODS в ЛС</a>."
        )
    }

    text = payment_texts.get(payment_method, "🤔")
    await update.message.reply_text(text, parse_mode="HTML", disable_web_page_preview=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        ['💎 Преимущества и цена VIP 💎'],
        ['💵 Приобрести VIP 💵'],
        ['ℹ️ Статистика покупок VIP ℹ️']
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(
        f"👋 Привет, {update.effective_user.name}!\n\n"
        f"🤖 Я бот-помощник скриптера MTG MODS.\n\n"
        f"ℹ️ Здесь ты можешь узнать про VIP и приобрести её!",
        reply_markup=reply_markup
    )

    user_command = context.args
    if user_command:
        await send_payment_info(update, user_command[0])

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == '💎 Преимущества и цена VIP 💎':
        await update.message.reply_text(
            (
                f"🔥 <b>VIP НАВСЕГДА – никаких подписок и доплат!</b>\n\n"

                f"🚀 <u><b>Что вы получаете после покупки:</b></u>\n"
                f"✅ <b>Вечный доступ ко всем моим платным скриптам.</b>\n"
                f"✅ <b>Вход в закрытый VIP-чат (Telegram/Discord).</b>\n"
                f"✅ <b>Ранний доступ к обновлениям бесплатных скриптов.</b>\n"
                f"✅ <b>Отключение рекламы в лаунчере MonetLoader.</b>\n"
                f"✅ <b>Выделение среди других благодаря VIP-роли в Discord.</b>\n\n"

                f"💰<u><b>Цена всего $5 (в любой валюте) – как одна пицца! 🍕</b></u>\n"
                f"🔥Дешевле подписки TG Prem / DS Nitro, но НАВСЕГДА 🔥\n"
                f"● 20 BYN / 200 UAH / 500 RUB / 2500 KZT / 65K UZS и т.д."
            ),
            parse_mode="HTML"
        )
    elif text == 'ℹ️ Статистика покупок VIP ℹ️':
        guild = bot.get_guild(DISCORD_GUILD_ID) 
        role = guild.get_role(VIP_ROLE_ID)
        all_members = guild.members
        total_members = len(all_members)
        vip_members = [m for m in all_members if role in m.roles]
        vip_count_discord = len(vip_members)
        tg_vipchat_members_count = await get_tg_vipchat_members_count(context.bot, TELEGRAM_VIP_CHAT_ID) - 2
        total_vip_members = vip_count_discord + tg_vipchat_members_count
        await update.message.reply_text(
            (
                f"✨ <b>Наш VIP-чат доступен как в Telegram, так и в Discord!</b> ✨\n"
                f"🔹 <i>Вы можете находиться в обоих или выбрать тот, который удобнее.</i>\n\n"
                
                f"👥 <b>Актуальная статистика VIP-участников:</b>\n"
                f"1️⃣ <b><a href='https://discord.gg/qBPEYjfNhv'>Discord сервер</a></b>: {vip_count_discord} из {total_members} участников имеют VIP-роль.\n"
                f"2️⃣ <b>VIP-чат в Telegram</b>: {tg_vipchat_members_count} участников.\n\n"
                
                f"🏆 <i>Присоединяйтесь к элитному сообществу прямо сейчас!</i>"
            ),
            parse_mode="HTML",
            disable_web_page_preview=True
        )
    elif text == '💵 Приобрести VIP 💵':
        await update.message.reply_text(
            f"<b>📌 Выберите удобный способ оплаты:</b>",
            parse_mode="HTML",
            reply_markup=ReplyKeyboardMarkup(
                [
                    ['💳 Перевод на карту VISA'],
                    ['💵 FunPay (RUB/BYN)', '💲 PayPal (USD/EUR)'],
                    ['⭐ Telegram Stars', '🪙 Криптовалюта'],
                    ['🔙 Назад']
                ],
                resize_keyboard=True
            )
        )
    elif text == '💳 Перевод на карту VISA':
        await send_payment_info(update, "visa")
    elif text == '💵 FunPay (RUB/BYN)':
        await send_payment_info(update, "funpay")
    elif text == '💲 PayPal (USD/EUR)':
        await send_payment_info(update, "paypal")
    elif text == '⭐ Telegram Stars':
        await send_payment_info(update, "stars")
    elif text == '🪙 Криптовалюта':
        await send_payment_info(update, "crypto")
    elif text == '🔙 Назад':
        await start(update, context)
    elif text == 'fp':
        await update.message.reply_text(
            f"<b>ℹ️ Поскольку вы покупали VIP через FunPay, ОБЯЗАТЕЛЬНО:</b>\n\n"
            f"<b>⚡Зайдите на <a href='https://funpay.com/orders/'>страницу покупок</a>.</b>\n"
            f"<b>⚡Выберите покупку и нажмите \"Подтвердить выполнение\".</b>\n\n"
            f"<b>✅ Это нужно чтобы я получил ваши деньги за покупку VIP!</b>",
            parse_mode="HTML", disable_web_page_preview=True
        )
    elif is_admin(update.message.from_user.username) and not re.search(r'@', text) and not re.search(r'[а-яА-ЯёЁ]', text):
        await give_vip_role_in_ds(text, update)
    elif is_admin(update.message.from_user.username) and not re.search(r'[а-яА-ЯёЁ]', text):
        invite_link = await generate_single_user_invite_link(context.bot, TELEGRAM_VIP_CHAT_ID)
        if invite_link:
            await update.message.reply_text(
                f'✅ <b>Успешное приобретение VIP</b> ✅\n\n'
                f'🥳 <b>{text}</b>, теперь вы - <b>VIP участник!</b>\n\n'
                f'💎 <b>VIP скрипты доступны в <a href="{invite_link}">этом канале</a> (закреп)</b>\n\n'
                f'❤️ <b>Спасибо за покупку VIP и финансовую поддержку!</b>',
                parse_mode="HTML"
            )
        else:
            await update.message.reply_text("❗Не удалось создать приглашение в TG VIP чат!\n\n👉 Свяжитесь с @mtg_mods.")

async def get_tg_vipchat_members_count(bot, chat_id: int):
    return await bot.get_chat_member_count(chat_id)

async def generate_single_user_invite_link(bot: Bot, chat_id: int):
    try:
        expire_time = int(time.time()) + 3600
        invite_link = await bot.create_chat_invite_link(
            chat_id=chat_id,
            member_limit=1,
            expire_date=expire_time
        )
        print(f"Ссылка на TG VIP чат создана: {invite_link.invite_link}")
        return invite_link.invite_link
    except Exception as e:
        print(f"Ошибка создания ссылки на тг вип чат: {e}")
        return None

async def run_telegram_bot():
    app = ApplicationBuilder().token(TG_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    await app.run_polling()

# Discord bot setup
bot = commands.Bot(command_prefix="/", intents=intents)
@bot.event
async def on_ready():
    print(f'Discord bot запущен как {bot.user}')
    try:
        await bot.tree.sync() 
        print("Команды успешно синхронизованы.")
    except Exception as e:
        print(f"Ошибка синхронизации команд: {e}")

@bot.tree.command(name="vip", description="Выдать VIP роль")
async def vip(interaction: discord.Interaction, member: discord.Member):
    role = interaction.guild.get_role(VIP_ROLE_ID)
    await member.add_roles(role)
    print(f"VIP роль успешно выдана пользователю {member.name}")
    embed = discord.Embed(
        title='✅ Успешное приобретение VIP роли ✅',
        description=(
            f'🥳 Теперь вы - {role.mention}!\n\n'
            f'💎 VIP скрипты доступны в канале <#{VIP_CHANNEL_ID}> (закреп)\n\n'
            f'❤️ Спасибо за покупку VIP и финансовую поддержку!'
        ),
        color=0x3498DB
    )
    if member.avatar:
        embed.set_thumbnail(url=member.avatar.url)
    await interaction.response.send_message(content=f'{member.mention}', embed=embed)

@bot.tree.command(name="vips", description="Посмотреть статистику покупок VIP")
async def vips(interaction: discord.Interaction):
    role = interaction.guild.get_role(VIP_ROLE_ID)
    all_members = interaction.guild.members
    total_members = len(all_members)
    vip_members = [m for m in all_members if role in m.roles]
    vip_count = len(vip_members)
    embed = discord.Embed(
        description=(
            f'**:sunglasses: {vip_count} из {total_members} участников данного сервера - <@&{VIP_ROLE_ID}>**'
        ),
        color=0x3498DB
    )
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="tgvip", description="Вступить в VIP чат в Telegram")
async def tgvip(interaction: discord.Interaction):
    member = interaction.user
    role = discord.utils.get(member.roles, id=VIP_ROLE_ID)
    if not role:
        embed = discord.Embed(
            description=(f"Данная команда доступна только для <@&{VIP_ROLE_ID}>!"),
            color=0x3498DB
        )
        await interaction.response.send_message(embed=embed)
        return
    elif interaction.channel.id != VIP_CHANNEL_ID:
        embed = discord.Embed(
            description=(f"Данную команду можно использовать только в <#{VIP_CHANNEL_ID}>"),
            color=0x3498DB
        )
        await interaction.response.send_message(embed=embed)
        return
    elif role and interaction.channel.id == VIP_CHANNEL_ID:
        app = ApplicationBuilder().token(TG_BOT_TOKEN).build()
        print('Запрос TG ссылки от пользователя ' + member.mention)
        invite_link = await generate_single_user_invite_link(app.bot, TELEGRAM_VIP_CHAT_ID)
        if invite_link:
            embed = discord.Embed(
            description=(
                f"**{member.mention}, наш Telegram VIP чат по cсылке:\n{invite_link}** *(действует 60 минут)*"
            ),
            color=0x3498DB
        )
        else:
            embed = discord.Embed(
            description=(
                f"Ошибка, не удалось сгенерировать приглашение в Telegram VIP чат!"
            ),
            color=0x3498DB
        )
        await interaction.response.send_message(embed=embed)

async def run_discord_bot():
    await bot.start(DISCORD_BOT_TOKEN)

# Start bots
if __name__ == '__main__':
    nest_asyncio.apply()
    asyncio.run(asyncio.gather(run_discord_bot(), run_telegram_bot()))
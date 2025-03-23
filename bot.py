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

async def give_vip_role_in_ds(user, upd, checker):
    guild = bot.get_guild(DISCORD_GUILD_ID)
    member = None 
    member = discord.utils.get(guild.members, id=int(user)) if user.isdigit() else discord.utils.get(guild.members, name=user)

    if member:
        role = guild.get_role(VIP_ROLE_ID)
        await member.add_roles(role)
        print(f"VIP роль успешно выдана пользователю {member.name} через автопокупку в боте." if checker else f"VIP роль успешно выдана пользователю {member.name}.")
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

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        ['💎 Преимущества и цена VIP 💎'],
        # ['💵 Приобрести VIP 💵'],
        ['ℹ️ Статисика покупок VIP ℹ️']
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(f"👋 Привет {update.effective_user.name}!\n🤖 Я бот-помощник скриптера MTG MODS\nℹ️ Здесь ты можешь узнать про VIP и приобрести её!", reply_markup=reply_markup)
    
    user_command = context.args 
    if user_command and user_command[0] == 'visa':
        await update.message.reply_text(
            (
                f"<b>💳 Перевод на карту VISA по номеру:</b>\n"
                f"<pre>4441 1144 6426 8265</pre>\n\n"
                
                f"<b>💰 Сумма перевода: 5$ (или больше 😍) по вашему курсу</b>\n\n"
                f"<b>❗️ Валюта перевода: любая кроме RUB / BYN ❗️</b>\n\n"
                
                f"<b>🌍 Международный перевод (если вы не из Украины):</b>\n"
                f"<b>🔹 Получатель: Marher Bohdan</b>\n"
                f"<b>🔹 Банк получателя: Monobank</b>\n"
                f"<b>🔹 Страна получателя: Украина 🇺🇦</b>\n\n"
                
                f"<b>💳 Также возможен перевод и по SWIFT / SEPA, <a href='https://t.me/mtg_mods'>свяжитесь</a>.</b>"
            ),
            parse_mode="HTML",
            disable_web_page_preview=True
        )

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

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == '💎 Преимущества и цена VIP 💎':
        await context.bot.forward_message(
            chat_id=update.message.chat_id,
            from_chat_id="@mtgmods",
            message_id=60
        )
    elif text == 'ℹ️ Статисика покупок VIP ℹ️':
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
                # f"ℹ️ Количество пользователей которые приобрели VIP:\n\n"
                f"1️⃣ Наш <a href='https://discord.gg/qBPEYjfNhv'>Discord сервер</a>: {vip_count_discord} из {total_members} участников - VIP.\n"
                f"2️⃣ Наш Telegram VIP чат: {tg_vipchat_members_count} участников.\n\n"
                ##f"😎 Всего VIP пользователей: {total_vip_members}.\n\n"
            ),
            parse_mode="HTML",
            disable_web_page_preview=True
        )
    elif text == '💳':
        await update.message.reply_text(
            (
                f"<b>💳 Перевод на карту VISA по номеру:</b>\n"
                f"<pre>4441 1144 6426 8265</pre>\n\n"
                
                f"<b>💰 Сумма перевода: 5$ (или больше 😍) по вашему курсу</b>\n\n"
                f"<b>❗️ Валюта перевода: любая кроме RUB / BYN ❗️</b>\n\n"
                
                f"<b>🌍 Международный перевод (если вы не из Украины):</b>\n"
                f"<b>🔹 Получатель: Marher Bohdan</b>\n"
                f"<b>🔹 Банк получателя: Monobank</b>\n"
                f"<b>🔹 Страна получателя: Украина 🇺🇦</b>\n\n"
                
                f"<b>💳 Также возможен перевод и по SWIFT / SEPA, <a href='https://t.me/mtg_mods'>свяжитесь</a>.</b>"
            ),
            parse_mode="HTML",
            disable_web_page_preview=True
        )
    elif is_admin(update.message.from_user.username) and not re.search(r'@', text) and not re.search(r'[а-яА-ЯёЁ]', text):
        await give_vip_role_in_ds(text, update, False)
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
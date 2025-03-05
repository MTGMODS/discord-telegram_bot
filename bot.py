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
            key, value = line.strip().split("=", 1)  # Видаляємо пробіли та розділяємо по "="
            tokens[key.strip()] = value.strip()  # Видаляємо зайві пробіли з обох сторін

DISCORD_BOT_TOKEN = tokens.get("DISCORD_BOT_TOKEN")
TG_BOT_TOKEN = tokens.get("TG_BOT_TOKEN")

ADMIN_USERNAME = 'mtg_mods'

# Telegram bot setup
def is_admin(username):
    return username == ADMIN_USERNAME

async def give_vip_role(user, upd, checker):

    guild = bot.get_guild(DISCORD_GUILD_ID)
    member = None 
    member = discord.utils.get(guild.members, id=int(user)) if user.isdigit() else discord.utils.get(guild.members, name=user)

    if member:
        role = guild.get_role(VIP_ROLE_ID)
        await member.add_roles(role)
        print(f"VIP роль успешно выдана пользователю {member.name} через автопокупку в боте." if checker else f"VIP роль успешно выдана пользователю {member.name}.")
        embed = discord.Embed(
            title='✅ Успешное приобретение VIP роли ✅',
            description=(
                f'🥳 Теперь вы - {role.mention}!\n\n'
                f'💎 VIP скрипты доступны в канале <#{VIP_CHANNEL_ID}> (закреп)\n\n'
                f'❤️ Спасибо за покупку VIP и финансовую поддержку!'
            ),
            color=0x3498DB
        )
        # if member.avatar:
        #     embed.set_thumbnail(url=member.avatar.url)
        if member.display_avatar:
            embed.set_thumbnail(url=member.display_avatar.url)
        message = await bot.get_channel(CHAT_CHANNEL_ID).send(content=f'{member.mention}', embed=embed)
        await upd.message.reply_text((f"✅ VIP роль успешно выдана пользователю {member.name}!\n\n✅ Так-же {member.name} отправлено <a href='{message.jump_url}'>оповещение с инструкцией</a>."), parse_mode="HTML", disable_web_page_preview=True)
    else:
        await upd.message.reply_text(("❌ Пользователь с таким ID/USERNAME не найден!\n⚡Сначало зайдите на наш <a href='https://discord.gg/qBPEYjfNhv'>Discord сервер</a>."), parse_mode="HTML", disable_web_page_preview=True)

async def tg_vip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = context.args[0] if context.args else None
    if username:
        member = None
        if username.isdigit(): 
            member = discord.utils.get(bot.get_guild(DISCORD_GUILD_ID).members, id=int(username))
        else:
            member = discord.utils.get(bot.get_guild(DISCORD_GUILD_ID).members, name=username)

        if member:
            await give_vip_role(member.name)
            await update.message.reply_text(f'✅ VIP роль в Discord успешно выдана юзеру {member.name}!')
        else:
            await update.message.reply_text(("❌ Пользователь с таким ID/USERNAME не найден на нашем <a href='https://discord.gg/qBPEYjfNhv'>Discord сервере</a>!"), parse_mode="HTML", disable_web_page_preview=True)
    else:
        await update.message.reply_text('📝 Укажите свой Discord ID/USERNAME пользователя.')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        ['💎 Преимущества и цена VIP 💎'],
        # ['💵 Приобрести VIP 💵'],
        ['ℹ️ Статисика покупок VIP ℹ️']
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(f"👋 Привет {update.effective_user.name}!\n🤖 Я бот-помощник скриптера MTG MODS\nℹ️ Здесь ты можешь узнать про VIP и приобрести её!", reply_markup=reply_markup)

async def get_tg_vipchat_members_count(bot, chat_id: int):
    # Отримання кількості учасників у Telegram VIP чаті
    return await bot.get_chat_member_count(chat_id)

async def generate_single_user_invite_link(bot: Bot, chat_id: int):
    try:
        expire_time = int(time.time()) + 3600
        invite_link = await bot.create_chat_invite_link(
            chat_id=chat_id,
            member_limit=1,
            expire_date=expire_time
        )
        print(f"Індивідуальне запрошення створено: {invite_link.invite_link}")
        return invite_link.invite_link
    except Exception as e:
        print(f"Помилка створення посилання: {e}")
        return None

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == '💎 Преимущества и цена VIP 💎':
        # await update.message.reply_text((
        #     # "ℹ️ Преимущества которые вы получите после покупки VIP роли на нашем <a href='https://discord.gg/qBPEYjfNhv'>Discord сервере</a>\n\n"
        #     "ℹ️ Преимущества которые вы получите после приобретения VIP:\n\n"
        #     "1️⃣ VIP выдаётся вам НАВСЕГДА — один раз приобрели, и она остаётся с вами.\n"
        #     "2️⃣ Вы сразу же будете добавлены в VIP чат (<a href='https://discord.gg/qBPEYjfNhv'>Discord</a>/Telegram на ваш выбор).\n"
        #     "3️⃣ Вы получите доступ ко всем моим платным скриптам (они находятся в VIP чате).\n"
        #     "4️⃣ Платные скрипты всегда актуальны и регулярно обновляются..\n"
        #     "5️⃣ Ранний доступ к обновлениям бесплатных скриптов (исключение – срочный фикс).\n"
        #     "6️⃣ Отключение рекламы в <a href='https://t.me/mtgmods/1359'>лаунчере MonetLoader</a>.\n"
        #     "7️⃣ Выделение среди других участников благодаря VIP роли (только в <a href='https://discord.gg/qBPEYjfNhv'>Discord</a>).\n"
        # ), parse_mode="HTML", disable_web_page_preview=True)
        await context.bot.forward_message(
            chat_id=update.message.chat_id,  # Переслати в той же чат
            from_chat_id="@mtgmods",
            message_id=60
        )
    # elif text == '💵 Приобрести VIP 💵':
    #     await update.message.reply_text((
    #         "ℹ️ Цена приобретения VIP и способы + реквизиты для оплаты:\n\n"
    #         "● 🪙 Криптовалюта: адрес дам <a href='https://t.me/mtg_mods'>в ЛС</a>\n"
    #         "● Оплата: 4 USDT / $4 в любых монетах\n\n"
    #         "● 💳 Банковская карта: номер карты дам <a href='https://t.me/mtg_mods'>в ЛС</a>\n"
    #         "● Оплата: $4 / €4 / 150 UAH / 2000 KZT / 13 BYN / 50000 UZS\n\n"
    #         "● 💵 FunPay: https://funpay.com/lots/offer?id=36199657\n"
    #         "● Оплата: ± 400 RUB / $4\n\n"
    #         "● ⭐ Telegram Stars: Пишите <a href='https://t.me/mtg_mods'>мне в ЛС</a>\n"
    #         "● Оплата: 300 ⭐\n\n"
    #         "● 💵 PayPal: bogdan.mtg@gmail.com\n"
    #         "● Оплата: $4\n\n"
    #         "● 💸 Пополнение Steam по логину: bogdan_grile15\n"
    #         "● Оплата: $5 в вашей валюте\n\n"
    #         "ℹ️ Если есть желание то вы можете отправить даже больше чем нужно чтобы поддержать меня!\n"
    #     ),parse_mode="HTML",disable_web_page_preview=True)
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
                f"ℹ️ Количество пользователей которые приобрели VIP:\n\n"
                f"1️⃣ Наш <a href='https://discord.gg/qBPEYjfNhv'>Discord сервер</a>: {vip_count_discord} из {total_members} участников - VIP.\n"
                f"2️⃣ Наш Telegram VIP чат: {tg_vipchat_members_count} участников.\n\n"
                ##f"😎 Всего VIP пользователей: {total_vip_members}.\n\n"
            ),
            parse_mode="HTML",
            disable_web_page_preview=True
        )
    elif is_admin(update.message.from_user.username) and not re.search(r'@', text) and not re.search(r'[а-яА-ЯёЁ]', text):
        await give_vip_role(text, update, False)
    elif is_admin(update.message.from_user.username) and not re.search(r'[а-яА-ЯёЁ]', text):
        invite_link = await generate_single_user_invite_link(context.bot, TELEGRAM_VIP_CHAT_ID)
        if invite_link:
            await update.message.reply_text(f"{text}, заходите в наш Telegram VIP чат по cсылке:\n\n{invite_link}\n\nДанная ссылка действует 60 минут и только для вас!")
        else:
            await update.message.reply_text("Не удалось создать приглашение в TG VIP чат! Свяжитесь с @mtg_mods.")

async def run_telegram_bot():
    app = ApplicationBuilder().token(TG_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    await app.run_polling()

# Discord bot setup
bot = commands.Bot(command_prefix="/", intents=intents)
@bot.event
async def on_ready():
    print(f'Бот запущен как {bot.user}')
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
                f"Заходите в наш Telegram VIP чат по cсылке:\n\n{invite_link}\n\nДанная ссылка действует 60 минут и только для вас!"
                #f'**:sunglasses: {vip_count} из {total_members} участников данного сервера - <@&{VIP_ROLE_ID}>**'
            ),
            color=0x3498DB
        )
        else:
            embed = discord.Embed(
            description=(
                f"Ошибка не удалось сгенерировать приглашение в Telegram VIP чат!"

            ),
            color=0x3498DB
        )
        await interaction.response.send_message(embed=embed)

async def run_discord_bot():
    await bot.start(DISCORD_BOT_TOKEN)


# Start my bots
if __name__ == '__main__':
    nest_asyncio.apply()
    asyncio.run(asyncio.gather(run_discord_bot(), run_telegram_bot()))
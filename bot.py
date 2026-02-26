import discord
from discord.ext import commands
from discord import app_commands
import datetime
from flask import Flask
from threading import Thread

# --- БЛОК ДЛЯ РАБОТЫ 24/7 (Flask) ---
app = Flask('')

@app.route('/')
def home():
    return "Бот запущен и работает!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- НАСТРОЙКИ БОТА ---
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='/', intents=intents)

@bot.event
async def on_ready():
    try:
        synced = await bot.tree.sync()
        print(f"Синхронизировано {len(synced)} команд")
    except Exception as e:
        print(f"Ошибка синхронизации: {e}")
    print(f'Бот {bot.user} готов к работе!')

# --- ПРОВЕРКА НА АДМИНА ---
def is_admin(interaction: discord.Interaction) -> bool:
    return interaction.user.guild_permissions.administrator

# --- КОМАНДЫ МОДЕРАЦИИ (Только для Админов) ---

@bot.tree.command(name="clear", description="Удалить сообщения (админ)")
@app_commands.check(is_admin)
async def clear(interaction: discord.Interaction, amount: int):
    await interaction.response.defer(ephemeral=True)
    deleted = await interaction.channel.purge(limit=amount)
    await interaction.followup.send(f"✅ Удалено {len(deleted)} сообщений.")

@bot.tree.command(name="kick", description="Выгнать участника (админ)")
@app_commands.check(is_admin)
async def kick(interaction: discord.Interaction, member: discord.Member, reason: str = "Не указана"):
    await member.kick(reason=reason)
    await interaction.response.send_message(f"👞 {member.display_name} был выгнан. Причина: {reason}")

@bot.tree.command(name="ban", description="Забанить участника (админ)")
@app_commands.check(is_admin)
async def ban(interaction: discord.Interaction, member: discord.Member, reason: str = "Не указана"):
    await member.ban(reason=reason)
    await interaction.response.send_message(f"🚫 {member.display_name} забанен. Причина: {reason}")

@bot.tree.command(name="mute", description="Замутить (тайм-аут) (админ)")
@app_commands.check(is_admin)
async def mute(interaction: discord.Interaction, member: discord.Member, minutes: int, reason: str = "Не указана"):
    duration = datetime.timedelta(minutes=minutes)
    await member.timeout(duration, reason=reason)
    await interaction.response.send_message(f"🔇 {member.display_name} в муте на {minutes} мин. Причина: {reason}")

@bot.tree.command(name="unmute", description="Снять тайм-аут (админ)")
@app_commands.check(is_admin)
async def unmute(interaction: discord.Interaction, member: discord.Member):
    await member.timeout(None)
    await interaction.response.send_message(f"🔊 С {member.display_name} сняты ограничения.")

@bot.tree.command(name="slowmode", description="Медленный режим (админ)")
@app_commands.check(is_admin)
async def slowmode(interaction: discord.Interaction, seconds: int):
    await interaction.channel.edit(slowmode_delay=seconds)
    await interaction.response.send_message(f"⏳ Медленный режим: {seconds} сек.")

@bot.tree.command(name="lock", description="Заблокировать канал (админ)")
@app_commands.check(is_admin)
async def lock(interaction: discord.Interaction):
    await interaction.channel.set_permissions(interaction.guild.default_role, send_messages=False)
    await interaction.response.send_message("🔒 Канал заблокирован.")

@bot.tree.command(name="unlock", description="Разблокировать канал (админ)")
@app_commands.check(is_admin)
async def unlock(interaction: discord.Interaction):
    await interaction.channel.set_permissions(interaction.guild.default_role, send_messages=True)
    await interaction.response.send_message("🔓 Канал разблокирован.")

@bot.tree.command(name="warn", description="Выдать предупреждение (админ)")
@app_commands.check(is_admin)
async def warn(interaction: discord.Interaction, member: discord.Member, reason: str):
    await interaction.response.send_message(f"⚠️ {member.mention}, вам выдано предупреждение! Причина: {reason}")

@bot.tree.command(name="rename", description="Сменить ник (админ)")
@app_commands.check(is_admin)
async def rename(interaction: discord.Interaction, member: discord.Member, new_name: str):
    await member.edit(nick=new_name)
    await interaction.response.send_message(f"📝 Ник {member.name} изменен на {new_name}")

# --- ОБЩИЕ КОМАНДЫ ---

@bot.tree.command(name="ping", description="Проверить пинг")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message(f"🏓 Понг! Задержка: {round(bot.latency * 1000)}мс")

@bot.tree.command(name="user", description="Инфо о пользователе")
async def user(interaction: discord.Interaction, member: discord.Member = None):
    member = member or interaction.user
    emb = discord.Embed(title=f"Информация о {member.name}", color=discord.Color.blue())
    emb.add_field(name="ID", value=member.id)
    emb.set_thumbnail(url=member.avatar.url if member.avatar else "")
    await interaction.response.send_message(embed=emb)

@bot.tree.command(name="avatar", description="Аватар пользователя")
async def avatar(interaction: discord.Interaction, member: discord.Member = None):
    member = member or interaction.user
    await interaction.response.send_message(member.avatar.url if member.avatar else "Нет аватара")

# --- ОБРАБОТКА ОШИБОК ---
@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.CheckFailure):
        await interaction.response.send_message("❌ Ошибка: У вас должны быть права Администратора!", ephemeral=True)

# --- ЗАПУСК ---
if __name__ == "__main__":
    keep_alive() # Запуск веб-сервера
    bot.run('MTQ3NjI4NTQ3OTM1OTA4NjYwMw.GBZfXm._3k-7PY6NodavJaf_D4Y9RZcPrUsnEfEmQwOZg')
  

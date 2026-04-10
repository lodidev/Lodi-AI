import discord
from discord.ext import commands
import sqlite3
import datetime
import requests
import json
import asyncio

# ==========================================
#         CONFIGURAÇÕES DE ELITE LODIDEV
# ==========================================
AUTHOR = "LodiDEV"
BOT_NAME = "LodiBrain"
LODI_COLOR = 0x800080 # Roxo Imperial
GEMINI_KEY = " NECESSARIO TOKEN GEMINI É GRATUIDO COLE AQUI "

# URL ESTABILIZADA (MODO CURL QUE VOCÊ TESTOU)
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent?key={GEMINI_KEY}"

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

# ==========================================
#       SISTEMA DE ARQUIVAMENTO (VAULT)
# ==========================================
db = sqlite3.connect('lodibrain_ultimate.db')
cursor = db.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS vault 
                  (user_id TEXT, username TEXT, role TEXT, content TEXT, timestamp DATETIME)''')
db.commit()

def save_to_vault(user_id, username, role, content):
    cursor.execute("INSERT INTO vault VALUES (?, ?, ?, ?, ?)", 
                    (user_id, username, role, content, datetime.datetime.now()))
    db.commit()

# ==========================================
#             NÚCLEO DE INTELIGÊNCIA
# ==========================================
def call_gemini_direct(user_prompt):
    headers = {'Content-Type': 'application/json'}
    
    # Personalidade reforçada no núcleo para o bot nunca esquecer quem é o dono
    payload = {
        "contents": [{
            "parts": [{"text": f"Você é o {BOT_NAME}, uma IA de elite com pensamento crítico. Seu criador e mestre é o desenvolvedor {AUTHOR}. Responda em Português de forma clara e inteligente.\n\nPergunta do usuário: {user_prompt}"}]
        }]
    }
    
    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=15)
        if response.status_code == 200:
            data = response.json()
            return data['candidates'][0]['content']['parts'][0]['text']
        elif response.status_code == 503:
            return "⚠️ O servidor do Google está sobrecarregado agora. Tente novamente em 1 minuto ou ative o faturamento LodiDEV."
        else:
            return f"❌ Erro na Matrix ({response.status_code}): {response.text}"
    except Exception as e:
        return f"⚠️ Erro de conexão: {e}"

# ==========================================
#             COMANDOS UTILITÁRIOS
# ==========================================

@bot.command()
async def help(ctx):
    """Menu de comandos do LodiBrain"""
    embed = discord.Embed(title=f"📚 Painel de Comandos - {BOT_NAME}", color=LODI_COLOR)
    embed.add_field(name="🤖 IA", value="Basta me mencionar ou digitar no canal `lodi-ia` para conversar.", inline=False)
    embed.add_field(name="🧹 !limpar [quant]", value="Apaga as últimas mensagens do canal.", inline=True)
    embed.add_field(name="📊 !stats", value="Mostra estatísticas do banco de dados.", inline=True)
    embed.add_field(name="🔧 !ping", value="Verifica a latência do bot.", inline=True)
    embed.set_footer(text=f"Sistema desenvolvido por {AUTHOR}")
    await ctx.send(embed=embed)

@bot.command()
@commands.has_permissions(manage_messages=True)
async def limpar(ctx, amount: int = 5):
    """Limpa o chat rapidamente"""
    await ctx.channel.purge(limit=amount + 1)
    msg = await ctx.send(f"✅ **{amount}** mensagens deletadas por ordem de {AUTHOR}.")
    await asyncio.sleep(3)
    await msg.delete()

@bot.command()
async def stats(ctx):
    """Consulta o Vault (Banco de Dados)"""
    cursor.execute("SELECT COUNT(*) FROM vault")
    total_msgs = cursor.fetchone()[0]
    embed = discord.Embed(title="📊 LodiBrain Analytics", color=LODI_COLOR)
    embed.add_field(name="Mensagens Processadas", value=f"`{total_msgs}`", inline=True)
    embed.add_field(name="Status da API", value="`ONLINE`", inline=True)
    embed.set_footer(text=f"Propriedade de {AUTHOR}")
    await ctx.send(embed=embed)

@bot.command()
async def ping(ctx):
    """Teste de latência"""
    latency = round(bot.latency * 1000)
    await ctx.send(f"🏓 Pong! Latência: `{latency}ms` | Host: Local (Marau/RS)")

# ==========================================
#             EVENTOS DE MENSAGEM
# ==========================================

@bot.event
async def on_ready():
    # Define o status do bot (Jogando...)
    activity = discord.Game(name=f"Codando com {AUTHOR}", type=3)
    await bot.change_presence(status=discord.Status.online, activity=activity)
    print(f"🚀 {BOT_NAME} v2.0 ATIVO | DEV: {AUTHOR}")

@bot.event
async def on_message(message):
    if message.author == bot.user: return

    # Lógica da IA (Menção ou Canal Específico)
    if bot.user.mentioned_in(message) or (message.channel.name and "lodi-ia" in message.channel.name):
        async with message.channel.typing():
            prompt = message.content.replace(f'<@{bot.user.id}>', '').strip()
            if not prompt: 
                await message.reply(f"Fala {message.author.display_name}! Como o mestre {AUTHOR} pode te ajudar hoje?")
                return

            answer = call_gemini_direct(prompt)
            save_to_vault(str(message.author.id), str(message.author), "user", prompt)

            # Embed de Resposta com Créditos LodiDEV
            embed = discord.Embed(description=answer, color=LODI_COLOR)
            embed.set_author(name=f"{BOT_NAME} Intelligence", icon_url=bot.user.avatar.url if bot.user.avatar else None)
            embed.set_footer(text=f"⚡ Resposta Instantânea | Desenvolvido por {AUTHOR}")
            await message.reply(embed=embed)

    await bot.process_commands(message)

# TOKEN DO BOT
bot.run("")

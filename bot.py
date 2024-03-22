import discord
from discord import Interaction
from discord.ext import commands
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import os
from dotenv import load_dotenv
load_dotenv()

TOKEN = 'MTIxODk1NzQ3NDU1MjQ4MzkzMw.GuaulA.BU4gIZVpKjR4-9ZmfKF8mJQcSbopJjaYYHMkuI'
#custom imports
import responses

async def send_message(message, user_message, is_private):
    try:
        
        response = responses.handle_response(user_message)
        await message.author.send(response) if is_private else await message.channel.send(response)
        
    except Exception as e:
        print(e)

def run_discord_bot():
    intents = discord.Intents.default() # or discord.Intents.all()
    intents.message_content = True
    client = commands.Bot(command_prefix='!', intents = intents)

    @client.event
    async def on_ready():
        await client.tree.sync()
        await client.change_presence(activity=discord.activity.Game(name="FORZA FERRARI"), status=discord.Status.do_not_disturb)
        print(f'{client.user.name} is now running!')
    
    @client.hybrid_command(name="ping", description="It will show my ping")
    async def ping(interacion : Interaction):
        bot_latency = round(client.latency*1000)
        await interacion.send(f"PING! {bot_latency} ms")
        await client.tree.sync()
    
    COOLDOWN_SECONDS = 300
    @client.hybrid_command(name="f1", description="Info about current race week")
    @commands.cooldown(1, COOLDOWN_SECONDS, commands.BucketType.default)
    async def f1(ctx):
        url = "https://f1calendar.com/pl"
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        races = soup.find_all("tbody")
        
        for race in races:
            
            race_status = race.find("span", string="Nadchodzący")
            
            if race_status:
                race_name = race.find("span", class_='').text
                dates = race.find_all('td', class_="text-right md:text-left", headers="date_header australian-grand-prix-header")
                date_times = race.find_all('td', class_="", headers="time_header australian-grand-prix-header")
                
                race_name = race.find("span", class_='').text
                sessions_name = ["FP1", "FP2", "FP3", "Kwalifikacje", "Wyścig"]

                dates = [date.text for date in dates]
                # dates = convert_date_to_weekday(dates)
                date_times = [time.text for time in date_times]
                date_times = convert_to_Warsaw_time(date_times)
                
                race_week_datetimes = list(zip(sessions_name, dates, date_times))
                
                embed = discord.Embed(title=f" :flag_au: {race_name} :flag_au: ", color=0xff0000)
                
                for session, date, time in race_week_datetimes:
                    print(f"{session}: {date} {time}")
                    # Zbuduj wiadomość
                    embed.add_field(name="", value=f":red_circle: **{session}**", inline=True)
                    embed.add_field(name="", value=f":calendar_spiral: {date}", inline=True)
                    embed.add_field(name="", value=f":alarm_clock: {time}", inline=True)

                await ctx.send(embed=embed)
                await client.tree.sync()
        else:
            # await ctx.send("Nie udało się pobrać informacji o najbliższym wyścigu.")   
            await client.tree.sync()
            
    @f1.error
    async def f1_error(ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f"Nie możesz jeszcze użyć tej komendy, poczekaj {round(error.retry_after)} sekund")
    
    @client.event
    async def on_message(message):
        if message.author==client.user.name:
            return
        
        username=str(message.author)
        user_message = str(message.content)
        channel = str(message.channel)

        print(f"{username} said: '{user_message}' ({channel})")
        
        if user_message and user_message[0] == '!':
            user_message = user_message[1:]
            await send_message(message, user_message, is_private=True)
        else:
            await send_message(message, user_message, is_private=False)
     
    client.run(TOKEN)
    
def convert_to_Warsaw_time(date_times):
    new_times = []
    for czas in date_times:
        h, m = map(int, czas.split(':'))
        h += 1
        if h == 24:  # Jeśli godzina wynosi 24, to zmieniamy na 00
            h = 0
        new_time = f"{h:02d}:{m:02d}"
        new_times.append(new_time)
    return new_times

def convert_date_to_weekday(date_string):
    polish_to_english_month = {
        'Sty': 'Jan', 'Lut': 'Feb', 'Mar': 'Mar', 'Kwi': 'Apr',
        'Maj': 'May', 'Cze': 'Jun', 'Lip': 'Jul', 'Sie': 'Aug',
        'Wrz': 'Sep', 'Paź': 'Oct', 'Lis': 'Nov', 'Gru': 'Dec'
    }
    
    # Zamiana polskich nazw miesięcy na angielskie
    for polish_month, english_month in polish_to_english_month.items():
        if polish_month in date_string:
            date_string = date_string.replace(polish_month, english_month)
            break
    
    date_object = datetime.strptime(date_string, '%d %b')
    weekday_num = date_object.weekday()
    weekday_num = (weekday_num + 1) % 7
    weekdays = ['Pn', 'Wt', 'Śr', 'Cz', 'Pt', 'Sb', 'Nd']
    weekday_name = weekdays[weekday_num]
    
    return weekday_name
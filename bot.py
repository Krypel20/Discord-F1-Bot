import discord, requests, asyncio, os
from discord import Interaction
from discord.ext import commands, tasks
from discord.ui import Button, View
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from dotenv import load_dotenv
load_dotenv()

#custom imports
TOKEN = os.getenv('TOKEN')
announcements_channel_id = 1224669338255233044
from async_commands import send_message
current_datetime = datetime.now()

polish_to_english_month = {
    'Sty': 'Jan', 'Lut': 'Feb', 'Mar': 'Mar', 'Kwi': 'Apr',
    'Maj': 'May', 'Cze': 'Jun', 'Lip': 'Jul', 'Sie': 'Aug',
    'Wrz': 'Sep', 'Paź': 'Oct', 'Lis': 'Nov', 'Gru': 'Dec'
}
    
flags_emojis = {
    "bahrain-grand-prix": ":flag_bh:",
    "saudi-arabia-grand-prix": ":flag_sa:",
    "australian-grand-prix": ":flag_au:",
    "japanese-grand-prix": ":flag_jp:",
    "chinese-grand-prix": ":flag_cn:",
    "miami-grand-prix": ":flag_us:",
    "emilia-romagna-grand-prix": ":flag_it:",
    "monaco-grand-prix": ":flag_mc:",
    "canadian-grand-prix": ":flag_ca:",
    "spanish-grand-prix": ":flag_es:",
    "austrian-grand-prix": ":flag_at:",
    "british-grand-prix": ":flag_gb:",
    "hungarian-grand-prix": ":flag_hu:",
    "belgian-grand-prix": ":flag_be:",
    "dutch-grand-prix": ":flag_nl:",
    "italian-grand-prix": ":flag_it:",
    "azerbaijan-grand-prix": ":flag_az:",
    "singapore-grand-prix": ":flag_sg:",
    "us-grand-prix": ":flag_us:",
    "mexican-grand-prix": ":flag_mx:",
    "brazilian-grand-prix": ":flag_br:",
    "las-vegas-grand-prix": ":flag_us:",
    "qatar-grand-prix": ":flag_qa:",
    "abu-dhabi-grand-prix": ":flag_ae:"
}

race_place_html_adress = {
    "bahrain-grand-prix": "1229/bahrain",
    "saudi-arabia-grand-prix": "1230/saudi-arabia",
    "australian-grand-prix": "1231/australia",
    "japanese-grand-prix": "1232/japan",
    "chinese-grand-prix": "1233/china",
    "miami-grand-prix": "1234/miami",
    "emilia-romagna-grand-prix": "1235/italy",
    "monaco-grand-prix": "1236/monaco",
    "canadian-grand-prix": "1237/canada",
    "spanish-grand-prix": "1238/spain",
    "austrian-grand-prix": "1239/austria",
    "british-grand-prix": "1240/great-britain",
    "hungarian-grand-prix": "1241/hungary",
    "belgian-grand-prix": "1242/belgium",
    "dutch-grand-prix": "1243/netherlands",
    "italian-grand-prix": "1244/italy",
    "azerbaijan-grand-prix": "1245/azerbaijan",
    "singapore-grand-prix": "1246/singapore",
    "us-grand-prix": "1247/united-states",
    "mexican-grand-prix": "1248/mexico",
    "brazilian-grand-prix": "1249/brazil",
    "las-vegas-grand-prix": "1250/las-vegas",
    "qatar-grand-prix": "1251/qatar",
    "abu-dhabi-grand-prix": "1252/abu-dhabi"
}

def current_race_html():
    calendar_url = "https://f1calendar.com/pl"
    response = requests.get(calendar_url)
    soup = BeautifulSoup(response.content, 'html.parser')
    races = soup.find_all("tbody")
    
    for race in races:
        race_status = race.find("span", string="Nadchodzący")
    
        if race_status:   
            return race

def race_results_url_id(race):
    race_id = race.get('id')
    get_current_race_url = lambda race_id: race_place_html_adress.get(race_id, ":question:")
    return get_current_race_url(race_id)

def convert_to_Warsaw_time(date_times):
    new_times = []
    for czas in date_times:
        h, m = map(int, czas.split(':'))
        h += 1
        if h == 24:
            h = 0
        new_time = f"{h:02d}:{m:02d}"
        new_times.append(new_time)
    return new_times

def convert_dates_to_weekdays(date_strings):
    converted_dates = []
    
    for date_string in date_strings:
        for polish_month, english_month in polish_to_english_month.items():
            if polish_month in date_string:
                date_string = date_string.replace(polish_month, english_month)
                break
        
        date_object = datetime.strptime(date_string, '%d %b')
        weekday_num = (date_object.weekday() + 1) % 7
        weekdays = ['Pn', 'Wt', 'Śr', 'Cz', 'Pt', 'Sb', 'Nd']
        weekday_name = weekdays[weekday_num]
        converted_dates.append(weekday_name)
    
    return converted_dates

def convert_date_to_weekday(date_string):
    for polish_month, english_month in polish_to_english_month.items():
        if polish_month is date_string:
            date_string = date_string.replace(polish_month, english_month)
            break
    
    date_object = datetime.strptime(date_string, '%d %b')
    weekday_num = (date_object.weekday() + 1) % 7
    weekdays = ['Pn', 'Wt', 'Śr', 'Cz', 'Pt', 'Sb', 'Nd']
    weekday_name = weekdays[weekday_num]
    return weekday_name

def convert_date_to_polish_months(date_strings):
    polish_dates = []
    for date_string in date_strings:
        for polish_month, english_month in polish_to_english_month.items():
            if english_month in date_string:
                day = date_string.split()[0]
                polish_dates.append(f"{day} {polish_month}")
                break
    return polish_dates
            
class RaceWeek:

    def __init__(self, race_html):
        self.id = race_html.get('id')
        self.flag_emoji = flags_emojis.get(self.id, ":question:")
        self.name = race_html.find("span", class_='').text
        dates = race_html.find_all('td', class_="text-right md:text-left")
        date_times = race_html.find_all('div', class_="text-right md:text-left pr-2 md:pr-0", string=True)
        sessions_name = ["FP1", "FP2", "FP3", "Kwalifikacje", "Wyścig"]
        dates = [date.text for date in dates]
        datesPL = convert_date_to_polish_months(dates)
        self.week_start = datesPL[0]
        self.week_end = datesPL[-1]
        date_times = [time.text for time in date_times]
        date_times = convert_to_Warsaw_time(date_times)
        self.race_week_datetimes = list(zip(sessions_name, dates, date_times))
        self.session = {}
        self.sessions = []
        
        # List of sessions as Session objects and single session model to inicialize each session (done below)
        for session_name, date, date_time in self.race_week_datetimes:
            session_obj = self.Session(session_name, date, date_time)
            self.sessions.append(session_obj)
            self.session[session_name] = session_obj

        # Session object inicialization for each session (FP1, FP2, FP3, Quali, Race)
        for session_name, date, date_time in self.race_week_datetimes:
            if session_name == "FP1":
                self.FP1 = self.session[session_name]
            elif session_name == "FP2":
                self.FP2 = self.session[session_name]
            elif session_name == "FP3":
                self.FP3 = self.session[session_name]
            elif session_name == "Kwalifikacje":
                self.Quali = self.session[session_name]
            elif session_name == "Wyścig":
                self.Race = self.session[session_name]
    
    def next_session(self, current_datetime=datetime.now()):
        
        for session in self.sessions:
            time_difference = session.datetime - current_datetime
            
            if 0 < time_difference.total_seconds():
                return session
    
    def current_session(self, current_datetime=datetime.now()):
        
        for session in self.sessions:
            time_difference = session.datetime - current_datetime
            if -4500 < time_difference.total_seconds() <= 0:
                return session
        return None
        
    class Session:
        def __init__(self, session_name, date, time):
            self.weekday = convert_date_to_weekday(date)
            self.session_name = session_name
            self.date = date
            self.time = time
            self.datetime = datetime.strptime(f"{self.date} {self.time} {current_datetime.year}", "%d %b %H:%M %Y")
        
        def check_session_status(self, current_datetime=datetime.now()):
            if self.session_name in ["FP1", "FP2", "FP3"]: 
                session_duration = timedelta(hours=1, minutes=5)
            elif self.session_name == 'Kwalifikacje':
                session_duration = timedelta(hours=0, minutes=55)
            elif self.session_name == 'Wyścig':
                session_duration = timedelta(hours=1, minutes=45)
            
            if self.datetime < current_datetime:
                if current_datetime - self.datetime >= session_duration:
                    return "⚫"
                else:
                    return "🟢"
            elif self.datetime > current_datetime:
                return "🔴"
            else:
                return "🟢"
            
        def session_starts_in(self, current_datetime=datetime.now()):
            
            if self.check_session_status(current_datetime) == "🔴":
                time_left = self.datetime - current_datetime
                days = time_left.days
                hours, remainder = divmod(time_left.seconds, 3600)
                minutes, _ = divmod(remainder, 60)
                if days > 0:
                    time_left = f":clock1: Pozostało **{days}d {hours}h {minutes}m**"
                elif hours > 0:
                    time_left = f":clock1: Pozostało **{hours}h {minutes}m**"
                else:
                    time_left = f":clock1: Pozostało **{minutes} minut**"
            elif self.check_session_status(current_datetime) == "🟢":
                time_left = '**🟢AKTUALNIE TRWA🟢**'
            else: 
                time_left = "**⚫ZAKOŃCZONE⚫**" 
                
            return time_left
        
        def time_left(self, current_datetime=datetime.now()):
            time_difference = self.datetime - current_datetime
            return time_difference.total_seconds()
        
        def get_session_embed(self, race_week):
            try:
                embed = discord.Embed(title=f"{self.check_session_status()} {race_week.name} - {self.session_name} {race_week.flag_emoji}", color=0xEF1A2D)
                thumbnail = "https://cdn.betterttv.net/emote/611fc2b976ea4e2b9f78518f/3x.gif"
                embed.set_thumbnail(url=thumbnail)
                time_left = self.session_starts_in(current_datetime)
                            
                embed.add_field(name="", value=f":calendar_spiral: {self.weekday}", inline=True)
                embed.add_field(name="", value=f":alarm_clock: **{self.time}**", inline=True)
                embed.add_field(name="", value=f"{time_left}", inline=False)
                return embed
            
            except Exception as e:
                print("Wystąpił wyjątek:", e)
                return None

race_html = current_race_html() #get current race week data from calendar
race_week = RaceWeek(race_html) 

def run_discord_bot():
    intents = discord.Intents.default() # or discord.Intents.all()
    intents.message_content = True
    client = commands.Bot(command_prefix='!', intents = intents)
    
    async def background_task():
        channel = client.get_channel(announcements_channel_id)
        cooldown = 15
        print(f"rozpoczęcie background task")
        
        while True: 
            print(f'__________Backgound Task Start__________')
            global race_html, race_week
            
            race_html = current_race_html() # update race week data from calendar
            race_week = RaceWeek(race_html) # create RaceWeek object from newly gathered data
            
            next_session = race_week.next_session()
            remaining_time = int(next_session.time_left()/60) # in minutes
            session_name = next_session.session_name
            
            print(f'Next session: {next_session.session_name} starts in {int(remaining_time)} minutes')
            
            if session_name in ["FP1", "FP2", "FP3"]:
                if 0 < remaining_time <= 15:
                    await channel.send(f"<@&1224668671499178005> :checkered_flag: **{session_name}** zacznie się w ciągu **{remaining_time} minut**:checkered_flag:")
                    print(f"{session_name} ZACZNIE SIĘ W CIAGU {remaining_time} MINUT")
                    cooldown = 900
                    await asyncio.sleep(cooldown)
                    await channel.send(f"<@&1224668671499178005> :checkered_flag: **{session_name}** SIĘ ROZPOCZEŁO :checkered_flag:")
                    embed = next_session.get_session_embed(race_week)
                    await channel.send(embed=embed)
                    cooldown = 10800
                else:
                    cooldown = 15
                    
            if session_name in ["Kwalifikacje", "Wyścig"]:
                if 5 < remaining_time <= 30: 
                    await channel.send(f"<@&1224668671499178005> :checkered_flag: **{session_name}** zacznie się w ciągu **{remaining_time} minut**:checkered_flag:")
                    print(f"{session_name} ZACZNIE SIĘ W CIAGU {remaining_time} MINUT")
                    cooldown = 1600
                elif 0 < remaining_time <= 5: 
                    await channel.send(f"<@&1224668671499178005> :checkered_flag: **{session_name}** ZARAZ SIĘ ZACZNIE pozostało **{remaining_time} minut**:checkered_flag:")
                    print(f"{session_name} ZACZNIE SIĘ W CIAGU {remaining_time} MINUT")
                    cooldown = 293
                    await asyncio.sleep(cooldown)
                    await channel.send(f"<@&1224668671499178005> :checkered_flag: **{session_name}** SIĘ ROZPOCZEŁO :checkered_flag:")
                    embed = next_session.get_session_embed()
                    await channel.send(embed=embed)
                    cooldown = 28800
                else:
                    cooldown = 15
            print(f'________Cooldown for {cooldown} seconds________')
            await asyncio.sleep(cooldown)
            
    @client.event
    async def on_ready():
        await client.tree.sync()
        await client.change_presence(activity=discord.activity.Game(name="FORZA FERRARI"), status=discord.Status.do_not_disturb)
        print(f'{client.user.name} is now running!')
        
        #starting asynchronous functions to run in the background
        asyncio.create_task(background_task())
        
    @client.hybrid_command(name="ping", description="It will show my ping")
    async def ping(interacion : Interaction):
        bot_latency = round(client.latency*1000)
        await interacion.send(f"PING! {bot_latency} ms")
        await client.tree.sync()
    
    COOLDOWN_SECONDS = 10
    @client.hybrid_command(name="f1", description="Info about current race week")
    @commands.cooldown(1, COOLDOWN_SECONDS, commands.BucketType.default)
    async def f1(ctx):
        global race_week, race_html
        
        embed = discord.Embed(title=f"{race_week.flag_emoji} {race_week.name} {race_week.flag_emoji} ‏ ‎ ‎ ‎ :calendar:{race_week.week_start} - {race_week.week_end} ", color=0xEF1A2D)
        thumbnail = "https://cdn.discordapp.com/emojis/734895858725683314.webp?size=96&quality=lossless"
        embed.add_field(name="", value="", inline=False)
        embed.set_thumbnail(url=thumbnail)
        current_datetime = datetime.now()
        next_session = race_week.next_session()
        current_session = race_week.current_session()
        
        for session in race_week.sessions:
            embed.add_field(name="", value=f"{session.check_session_status(current_datetime)} **{session.session_name}**", inline=True)
            embed.add_field(name="", value=f":calendar_spiral: {session.weekday}", inline=True)
            embed.add_field(name="", value=f":alarm_clock: **{session.time}**", inline=True)
            
            if session.session_name == next_session.session_name:
                time_left = session.session_starts_in(current_datetime)
                embed.add_field(name="", value=f"{time_left}", inline=False)
            elif current_session is not None and session.session_name == current_session.session_name:
                time_left = session.session_starts_in(current_datetime)
                embed.add_field(name="", value=f"{time_left}", inline=False)
            
            embed.add_field(name="", value=f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━", inline=False)
            
        await ctx.send(embed=embed)
        await client.tree.sync()
    
    @f1.error
    async def f1_error(ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f"Poczekaj {round(error.retry_after)} sekund")
    
    @client.hybrid_command(name="results", description="Last session results")
    async def results(ctx):
        embed = discord.Embed(title=f"Wyniki weekendu wyścigowego", color=0xEF1A2D)
        view = View()
        button = Button(label='Wyniki sesji', emoji='🏁', url=f'https://www.formula1.com/en/results.html/2024/races/{race_results_url_id(current_race_html())}/race-result.html')
        view.add_item(button)
        await ctx.send(embed=embed, view=view)
        await client.tree.sync()
    
    @client.hybrid_command(name="standings", description="Current driver/constructor standings")
    async def standings(ctx):
        button_teams = Button(label="Konstruktorzy", style=discord.ButtonStyle.red, emoji="⚙️")
        button_drivers = Button(label="Kierowcy", style=discord.ButtonStyle.red, emoji="🏎️")
        view = View()
         
        async def button_drivers_callback(interacion):
            driver_standings_url = "https://www.formula1.com/en/results.html/2024/drivers.html"
            embed = discord.Embed(title=f"Klasyfikacja generalna kierowców", color=0xFFF200)
            response = requests.get(driver_standings_url)
            soup = BeautifulSoup(response.content, 'html.parser')
            driver_standings_url = soup.find("tbody")
            drivers = driver_standings_url.find_all("tr")
        
            for driver in drivers:
                driver_pos = driver.find("td", class_="dark").text
                driver_name = driver.find('span', class_="hide-for-mobile").text
                driver_points = driver.find('td', class_="dark bold").text
                
                print(f"{driver_pos} | {driver_name} {driver_points} ")
                embed.add_field(name=f'', value=f"**{driver_pos}** 🔴 {driver_name} **{driver_points}**", inline=False)
            
            await interacion.response.edit_message(embed=embed, view=view)
        
        async def button_teams_callback(interacion):
            team_standings_url = "https://www.formula1.com/en/results.html/2024/team.html"
            embed = discord.Embed(title=f"Klasyfikacja generalna konstruktorów", color=0xFFF200)
            response = requests.get(team_standings_url)
            soup = BeautifulSoup(response.content, 'html.parser')
            team_standings_url = soup.find("tbody")
            teams = team_standings_url.find_all("tr")
            
            for team in teams:
                team_pos = team.find("td", class_="dark").text
                team_name = team.find('a').text
                team_points = team.find('td', class_="dark bold").text
                
                print(f"{team_pos} | {team_name} {team_points} ")
                embed.add_field(name=f'', value=f"**{team_pos}** 🔴 {team_name} **{team_points}**", inline=False)
            
            await interacion.response.edit_message(embed=embed, view=view)
        
        button_teams.callback = button_teams_callback
        button_drivers.callback = button_drivers_callback
        view.add_item(button_teams)
        view.add_item(button_drivers)
        
        await ctx.send(view=view)
        await client.tree.sync()
    
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
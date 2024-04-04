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

def current_race_results_url_id(race):
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
            
def check_session_status(current_datetime, session_datetime):

    session_duration = timedelta(hours=1, minutes=30)
    
    if session_datetime < current_datetime:
        if current_datetime - session_datetime >= session_duration:
            return "⚫"
        else:
            return "🟢"
    elif session_datetime > current_datetime:
        return "🔴"
    else:
        return "🟢"

def session_starts_in(current_datetime, session_datetime):
    
    if check_session_status(current_datetime, session_datetime) == "🔴":
        time_left = session_datetime - current_datetime
        days = time_left.days
        hours, remainder = divmod(time_left.seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        if days > 0:
            time_left = f"**{days}d {hours}h {minutes}m**"
        elif hours > 0:
            time_left = f"**{hours}h {minutes}m**"
        else:
            time_left = f"**{minutes} minut**"
        upcoming_session = True
    elif check_session_status(current_datetime, session_datetime) == "🟢":
        time_left = '**🟢AKTUALNIE TRWA🟢**'
        upcoming_session = True
    else: 
        time_left = "**⚫KONIEC⚫**" 
        upcoming_session = False
        
    return time_left, upcoming_session

def race_week_date_times(race):
    dates = race.find_all('td', class_="text-right md:text-left")
    date_times = race.find_all('div', class_="text-right md:text-left pr-2 md:pr-0", string=True)
    race_name = race.find("span", class_='').text.upper()
    sessions_name = ["FP1 " + race_name, "FP2 " + race_name, "FP3 " + race_name, "QUALI " + race_name, "WYŚCIG " + race_name]

    dates = [date.text for date in dates]
    date_times = [time.text for time in date_times]
    date_times = convert_to_Warsaw_time(date_times)
    
    return list(zip(sessions_name, dates, date_times))

def remaining_time_to_next_session(current_datetime, race):
    race_week_datetimes = race_week_date_times(race)
    
    for session, date, time in race_week_datetimes:
        session_datetime = datetime.strptime(f"{date} {time} {current_datetime.year}", "%d %b %H:%M %Y")
        time_difference = session_datetime - current_datetime
        
        print(f"{session} remaining time:", time_difference.total_seconds())
        
        if 0 < time_difference.total_seconds() <= 900: #check if remaining time to session is 15 minutes or less
            print(f'{session} odbedzie sie w ciągu {time_difference}')
            return time_difference.total_seconds() , session
    
    return 0, ''

def return_current_race_name(race):
    race_id = race.get('id')
    flag_emoji = lambda race_id: flags_emojis.get(race_id, ":question:")
    race_name = race.find("span", class_='').text
    
    return race_id, race_name, flag_emoji

class RaceWeek:

    def __init__(self, race_html):
        self.race_id = race_html.get('id')
        self.flag_emoji = flags_emojis.get(self.race_id, ":question:")
        self.race_name = race_html.find("span", class_='').text
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
        for session_name, date, date_time in self.race_week_datetimes:
            session_obj = self.Session(session_name, date, date_time)
            self.session[session_name] = session_obj

        # Session object inicialization (FP1, FP2, FP3, Quali, Race)
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

    def remaining_time_to_next_session(self, current_datetime):
        
        for session, date, time in self.race_week_datetimes:
            session_datetime = datetime.strptime(f"{date} {time} {current_datetime.year}", "%d %b %H:%M %Y")
            time_difference = session_datetime - current_datetime
            
            # print(f"{session} remaining time:", time_difference.total_seconds())
            
            if 0 < time_difference.total_seconds(): #check if remaining time to session is 15 minutes or less
                return time_difference.total_seconds()
        
        
    class Session:
        def __init__(self, session_name, date, date_time):
            self.weekday = convert_date_to_weekday(date)
            self.session_name = session_name
            self.date = date
            self.date_time = date_time
        
        def check_session_status(current_datetime, session_datetime):
            session_duration = timedelta(hours=1, minutes=30)
            
            if session_datetime < current_datetime:
                if current_datetime - session_datetime >= session_duration:
                    return "⚫"
                else:
                    return "🟢"
            elif session_datetime > current_datetime:
                return "🔴"
            else:
                return "🟢"
            
        def session_starts_in(self, current_datetime):
    
            if check_session_status(current_datetime, self.date_time) == "🔴":
                time_left = self.date_time - current_datetime
                days = time_left.days
                hours, remainder = divmod(time_left.seconds, 3600)
                minutes, _ = divmod(remainder, 60)
                if days > 0:
                    time_left = f"**{days}d {hours}h {minutes}m**"
                elif hours > 0:
                    time_left = f"**{hours}h {minutes}m**"
                else:
                    time_left = f"**{minutes} minut**"
                upcoming_session = True
            elif check_session_status(current_datetime, self.date_time) == "🟢":
                time_left = '**🟢AKTUALNIE TRWA🟢**'
                upcoming_session = True
            else: 
                time_left = "**⚫KONIEC⚫**" 
                upcoming_session = False
                
            return time_left, upcoming_session

race_html = current_race_html()

# Tworzymy obiekt klasy RaceWeek
race_week = RaceWeek(race_html)
current_datetime = datetime.now()

# Wywołanie atrybutów klasy RaceWeek
print("Race ID:", race_week.race_id)
print("Flag Emoji:", race_week.flag_emoji)  # Przykład, przekazujemy identyfikator wyścigu
print("Race Name:", race_week.race_name)
print("Week Start:", race_week.week_start)
print("Week End:", race_week.week_end)
print("Sessions Info:", race_week.race_week_datetimes)
print("Remaining time to next session:", race_week.remaining_time_to_next_session(current_datetime))

# Wywołanie atrybutów klasy Session dla konkretnego obiektu Session w RaceWeek
# Zakładając, że chcemy uzyskać atrybuty sesji FP1
print("\nSession Name:", race_week.FP1.session_name)
print("Date:", race_week.FP1.date)
print("Date Time:", race_week.FP1.date_time)
print("Weekday:", race_week.FP1.weekday)
print("\nSession Name:", race_week.Quali.session_name)
print("Date:", race_week.Quali.date)
print("Date Time:", race_week.Quali.date_time)
print("Weekday:", race_week.Quali.weekday)

def run_discord_bot():
    intents = discord.Intents.default() # or discord.Intents.all()
    intents.message_content = True
    client = commands.Bot(command_prefix='!', intents = intents)
    
    async def background_task():
        channel = client.get_channel(announcements_channel_id)
        last_session_name = ''
        cooldown = 15
        print(f"rozpoczęcie background task")
        
        while True:
            current_datetime = datetime.now()
            print(f"rozpoczęcie pętli, cooldown: {cooldown}")
            race = current_race_html()
            remaining_time, session_name = remaining_time_to_next_session(current_datetime, race)
            
            if 0 < remaining_time and last_session_name != session_name:
                await channel.send(f"<@&1224668671499178005> :checkered_flag: **{session_name}** zacznie się w ciągu **{int(remaining_time/60)} minut**:checkered_flag:")
                print(f"{session_name} ZACZNIE SIĘ W CIAGU {remaining_time}")
                last_session_name = session_name
                cooldown = 10800
                await asyncio.sleep(cooldown)
            else:
                cooldown = 15
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
        race = current_race_html()
        race_id = race.get('id')
        get_flag_emoji = lambda race_id: flags_emojis.get(race_id, ":question:")
        race_name = race.find("span", class_='').text
        
        dates = race.find_all('td', class_="text-right md:text-left")
        date_times = race.find_all('div', class_="text-right md:text-left pr-2 md:pr-0", string=True)
        
        sessions_name = ["FP1", "FP2", "FP3", "Kwalifikacje", "Wyścig"]

        dates = [date.text for date in dates]
        
        datesPL = convert_date_to_polish_months(dates)
        week_start = datesPL[0]
        week_end = datesPL[-1]
        
        weekdays = convert_dates_to_weekdays(dates)
        date_times = [time.text for time in date_times]
        date_times = convert_to_Warsaw_time(date_times)
        
        race_week_datetimes = list(zip(sessions_name, dates, weekdays, date_times))
        
        embed = discord.Embed(title=f"{get_flag_emoji(race_id)} {race_name} {get_flag_emoji(race_id)} ‏ ‎ ‎ ‎ :calendar:{week_start} - {week_end} ", color=0xEF1A2D)
        thumbnail = "https://cdn.discordapp.com/emojis/734895858725683314.webp?size=96&quality=lossless"
        embed.add_field(name="", value="", inline=False)
        embed.set_thumbnail(url=thumbnail)
        
        current_datetime = datetime.now()
        upcoming_session = False
        print(race_week_datetimes)
        
        for session, date, weekday, time in race_week_datetimes:
            session_datetime = datetime.strptime(f"{date} {time} {current_datetime.year}", "%d %b %H:%M %Y")
            print(f"{session}: {date} {time}")
            embed.add_field(name="", value=f"{check_session_status(current_datetime, session_datetime)} **{session}**", inline=True)
            embed.add_field(name="", value=f":calendar_spiral: {weekday}", inline=True)
            embed.add_field(name="", value=f":alarm_clock: **{time}**", inline=True)
            
            if not upcoming_session:
                time_left, upcoming_session = session_starts_in(current_datetime, session_datetime)
                embed.add_field(name="", value=f":clock1: Pozostało {time_left}", inline=False)
                    
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
        button = Button(label='Wyniki sesji', emoji='🏁', url=f'https://www.formula1.com/en/results.html/2024/races/{current_race_results_url_id(current_race_html())}/race-result.html')
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
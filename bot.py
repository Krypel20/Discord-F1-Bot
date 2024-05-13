import discord, asyncio, os
from discord import Interaction
from discord.ext import commands
from discord.ui import Button, View
from raceWeek import RaceWeek, drivers_standings, teams_standings
from datetime import datetime
from table2ascii import table2ascii as t2a, PresetStyle
from dotenv import load_dotenv
load_dotenv()

#custom imports
from async_commands import send_message

TOKEN = os.getenv('TOKEN')
# announcements_channel_id = 1224669338255233044
announcements_channel_id = 1224669338255233044

race_week = RaceWeek() 

def run_discord_bot():
    intents = discord.Intents.default() # or discord.Intents.all()
    intents.message_content = True
    client = commands.Bot(command_prefix='!', intents = intents)
    
    async def background_task():
        global race_week
        channel = client.get_channel(announcements_channel_id)
        current_datetime = datetime.now()
        next_session = race_week.next_session(current_datetime)
        remaining_time = next_session.time_left(current_datetime) # in seconds
        cooldown = remaining_time % 60
        print(f'__________Backgound Task Start__________')
        print(f'First cooldown for {cooldown} seconds')
        await asyncio.sleep(cooldown)

        while True: 
            print(f'__________Backgound Task Reactivation__________')

            race_week = RaceWeek() # replace RaceWeek object from newly gathered data
            current_datetime = datetime.now()

            next_session = race_week.next_session(current_datetime)
            remaining_time = round(next_session.time_left(current_datetime)) # in seconds
            session_name = next_session.session_name
            
            try:
                print(f'Checking next session: {next_session.session_name} starts in {remaining_time} seconds')
            
                if session_name in ["Pierwszy trening", "Drugi trening", "Trzeci trening", "FP1", "FP2", "FP3"]:
                    if 0 < remaining_time <= 15*60:
                        await channel.send(f"<@&1224668671499178005> :checkered_flag: **{session_name}** zacznie się w ciągu **{round(remaining_time/60)} minut**:checkered_flag:")
                        print(f"{session_name} STARTS IN {round(remaining_time/60)} MINUTES")
                        asyncio.create_task(annouce_session_start(next_session,channel))
                        cooldown = round(remaining_time)+4500
                    else:
                        if remaining_time % 60 > 0:
                            cooldown = remaining_time % 60
                        else: cooldown = 60
                        
                if session_name in ["Kwalifikacje", "Wyścig", "Sprint", "Sprint Qualifying"]:
                    if 0 < remaining_time <= 30*60: 
                        await channel.send(f"<@&1224668671499178005> :checkered_flag: **{session_name}** zacznie się w ciągu **{round(remaining_time/60)} minut**:checkered_flag:")
                        print(f"{session_name} STARTS IN {round(remaining_time/60)} MINUTES")
                        asyncio.create_task(annouce_session_start(next_session,channel))
                        cooldown = int(remaining_time)+5400
                    else:
                        if remaining_time % 60 > 0:
                            cooldown = remaining_time % 60
                        else: cooldown = 60

            except Exception as e:
                print(f'**BS4 retrived old race data** - ', e)
                
            print(f'________Cooldown for {cooldown} seconds________')
            await asyncio.sleep(cooldown)
    
    async def annouce_session_start(session, channel):
        while True:
            current_datetime = datetime.now()
            remaining_time = round(session.time_left(current_datetime)) # in seconds

            if remaining_time <=0:
                print(f"ANNOUCE SESSION START FUNCTION: \t-----{session.session_name} has begun-----")
                embed = session.get_session_embed()
                await channel.send(embed=embed)
                await channel.send(f"<@&1224668671499178005> :checkered_flag: **{session.session_name}** SIĘ ROZPOCZĄŁ :checkered_flag:")
                print(f"\t-----------------------------------------------")
                return
            else:
                print(f'Waiting {remaining_time+1} seconds to annouce session')
                await asyncio.sleep(remaining_time)

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
        
        try: 
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

        except Exception as e:
            print('Exepction', e)
            await ctx.send('Musisz poczekać, pobieram przestarzałe dane ze strony :(')
            await client.tree.sync()

    @f1.error
    async def f1_error(ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f"Poczekaj {round(error.retry_after)} sekund")
    
    @client.hybrid_command(name="results", description="Last session results")
    async def results(ctx):
        global iteration
        iteration = 0
        results_urls = race_week.results_urls + race_week.previous_results_urls
        button_results = Button(label=f'Oficialna strona wyników',
                        emoji='🏁',
                        url=f'https://www.formula1.com/en/results.html/2024/races/{race_week.results_url_path}/race-result.html')
        button_previous = Button(label="Poprzednia sesja", style=discord.ButtonStyle.green, emoji="⏮")
        button_next = Button(label="Następna sesja", style=discord.ButtonStyle.green, emoji="⏭", disabled=True)
        view = View()
        
        async def button_previous_callback(interaction):
            global iteration
            iteration = iteration + 1
            button_next.disabled = False
            if iteration + 1 > len(results_urls) - 1:
                button_previous.disabled = True
            else: button_previous.disabled = False
                
            url = results_urls[iteration][1]
            session_name = results_urls[iteration][0]
            table_headers, table_rows = race_week.get_results_table_from_url(url)  # prase results table from given url
            table = t2a(
                header=table_headers,
                body=table_rows,
                style=PresetStyle.thin_compact
            )
            button_results.url = url
            print(f"\t{session_name}\n{table}\n")
            await interaction.response.edit_message(content=f"## {session_name}\n```\n{table}\n```{iteration+1} z {len(results_urls)}", view=view)
        
        async def button_next_callback(interaction):
            global iteration
            iteration = iteration - 1
            button_previous.disabled = False
            if iteration - 1 < 0:
                button_next.disabled = True
            else: button_next.disabled = False
               
            url = results_urls[iteration][1]
            session_name = results_urls[iteration][0]
            table_headers, table_rows = race_week.get_results_table_from_url(url)  # prase results table from given url
            table = t2a(
                header=table_headers,
                body=table_rows,
                style=PresetStyle.thin_compact
            )
            button_results.url = url
            print(f"\t{session_name}\n{table}\n")
            await interaction.response.edit_message(content=f"## {session_name}\n```\n{table}\n```{iteration+1} z {len(results_urls)}", view=view)

        if results_urls:
            # prase latest session results from url list
            url = results_urls[iteration][1]
            session_name = results_urls[iteration][0]
            table_headers, table_rows = race_week.get_results_table_from_url(url)  # prase results table from given url
            table = t2a(
                header=table_headers,
                body=table_rows,
                style=PresetStyle.thin_compact
            )
            print(f"\t{session_name}\n{table}\n")
            button_results.url = button_results.url = url
            button_previous.callback = button_previous_callback
            button_next.callback = button_next_callback
            view.add_item(button_previous)
            view.add_item(button_results)
            view.add_item(button_next)
            await ctx.send(content=f"## {session_name}\n```\n{table}\n```{iteration+1} z {len(results_urls)}", view=view)
            
        else:
            embed = discord.Embed(title=f"Aktualnie brak wyników {race_week.name}", color=0xEF1A2D)
            button_results.url = f'https://www.formula1.com/en/results.html/2024/races/{race_week.results_url_path}/race-result.html'
            button_previous.callback = button_previous_callback
            view.add_item(button_previous)
            view.add_item(button_results)
            view.add_item(button_next)

            await ctx.send(embed=embed, view=view)

        await client.tree.sync()
    
    @client.hybrid_command(name="standings", description="Current driver/constructor standings")
    async def standings(ctx):
        button_teams = Button(label="Konstruktorzy", style=discord.ButtonStyle.red, emoji="⚙️")
        button_drivers = Button(label="Kierowcy", style=discord.ButtonStyle.red, emoji="🏎️")
        view = View()
         
        async def button_drivers_callback(interaction):
            embed = discord.Embed(title=f"Klasyfikacja generalna kierowców", color=0xFFF200)
            drivers = drivers_standings()
            
            for driver_pos, driver_name, driver_points in drivers:
                print(f"{driver_pos} | {driver_name} {driver_points} ")
                embed.add_field(name=f'', value=f"**{driver_pos}** 🔴 {driver_name} **{driver_points}**", inline=False)
            
            await interaction.response.edit_message(embed=embed, view=view)
        
        async def button_teams_callback(interaction):
            embed = discord.Embed(title=f"Klasyfikacja generalna konstruktorów", color=0xFFF200)
            teams = teams_standings()
            
            for team_pos, team_name, team_points in teams:
                print(f"{team_pos} | {team_name} {team_points} ")
                embed.add_field(name=f'', value=f"**{team_pos}** 🔴 {team_name} **{team_points}**", inline=False)
            
            await interaction.response.edit_message(embed=embed, view=view)
        
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
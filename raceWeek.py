import requests, discord
from utils import remove_duplicates, convert_to_Warsaw_time, convert_date_to_polish_months, convert_date_to_weekday
from constants import flags_emojis, race_place_html_adress
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from table2ascii import table2ascii as t2a, PresetStyle

def current_race_week_html_data(calendar_url = "https://f1calendar.com/pl"):
    response = requests.get(calendar_url)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        races = soup.find_all("tbody")
        today = datetime.now().date()
        
        for race in races:
            th = race.find('th', class_='flex p-4')
            if th:
                dates = [date.text for date in race.find_all("td", class_="text-right md:text-left")]
                race_date = datetime.strptime(f"{dates[-1].strip()} {today.year}", "%d %b %Y").date()

                if race_date>=today:
                    return race
    else:
        print("***could not read website HTML file***")

def race_week_results_urls(race_id): #get urls of race week sessions results from formula1.com page
    results_page = f"https://www.formula1.com/en/results.html/2024/races/{race_id}/race-result.html"
    response = requests.get(results_page)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        page = soup.find("div", class_="resultsarchive-content group")
        track_name = soup.find("span", class_="circuit-info").string
        p_elements = page.find_all("p")
        
        if any(p.string == "No results are currently available" for p in p_elements):
            return []
        else:
            session_list = page.find("ul", class_="resultsarchive-side-nav").find_all('li')
            sessions_results_urls = []

            for session in session_list:
                a_tag = session.find('a')

                if a_tag and a_tag.text.strip() not in ["Pit stop summary"]:
                    url = "https://www.formula1.com" + a_tag['href']
                    text = a_tag.text.strip()
                    session_name = track_name+" - "+ text
                    sessions_results_urls.append((session_name, url))
                    
            return sessions_results_urls

def race_results_adress(race_id):
    get_current_race_url = lambda race_id: race_place_html_adress.get(race_id, ":question:")
    return get_current_race_url(race_id)

def get_previous_race_results_adress(race_adress):
    for race, html_adress in race_place_html_adress.items():
        if race_adress == html_adress:
            previous_index = list(race_place_html_adress.items()).index((race, html_adress)) - 1
            if previous_index >= 0:
                return list(race_place_html_adress.values())[previous_index]
            else:
                return race_adress
       
def drivers_standings():
    driver_standings_url = "https://www.formula1.com/en/results.html/2024/drivers.html"
    response = requests.get(driver_standings_url)
    soup = BeautifulSoup(response.content, 'html.parser')
    driver_standings_url = soup.find("tbody")
    drivers = driver_standings_url.find_all("tr")
    standings = []
    
    for driver in drivers:
        driver_pos = driver.find("td", class_="dark").text
        driver_name = driver.find('span', class_="hide-for-mobile").text
        driver_points = driver.find('td', class_="dark bold").text
        standings.append((driver_pos, driver_name, driver_points))
    
    return standings

def teams_standings():
    team_standings_url = "https://www.formula1.com/en/results.html/2024/team.html"
    response = requests.get(team_standings_url)
    soup = BeautifulSoup(response.content, 'html.parser')
    team_standings_url = soup.find("tbody")
    teams = team_standings_url.find_all("tr")
    standings = []
    
    for team in teams:
        team_pos = team.find("td", class_="dark").text
        team_name = team.find('a').text
        team_points = team.find('td', class_="dark bold").text
        standings.append((team_pos, team_name, team_points))
    
    return standings

def get_session_names(race_html):
    session_names = [] 
    sessions = race_html.find_all("td", class_='p-4')
    
    for session_name in sessions:
        name = session_name.contents[-1].strip()
        session_names.append(name)
    return session_names

def add_missing_values(thead_cols, session_results): # filling in the blanks of the table
    
    for session_result in session_results:
        if len(session_result) < len(thead_cols):
            # add "-" at the end of the list for empty cell
            for i in range(len(thead_cols)-len(session_result)):
                session_result.append('-')

    return session_results

class RaceWeek:
    def __init__(self, race_html = current_race_week_html_data(), f3 = False):
        self.id = race_html.get('id')
        if f3 is True:
            race_html = current_race_week_html_data("https://f3calendar.com/pl")
        if f3 is False:
            self.results_url_path = race_results_adress(self.id)
            self.previous_results_url_path = get_previous_race_results_adress(self.results_url_path)
            self.results_urls = race_week_results_urls(self.results_url_path)
            self.previous_results_urls = race_week_results_urls(self.previous_results_url_path)
        self.flag_emoji = flags_emojis.get(self.id, ":question:")
        self.name = race_html.find("span", class_='').text
        session_names = get_session_names(race_html)
        dates = race_html.find_all('td', class_="text-right md:text-left")
        date_times = race_html.find_all('div', class_="text-right md:text-left pr-2 md:pr-0", string=True)
        dates = [date.text for date in dates]
        datesPL = convert_date_to_polish_months(dates)
        self.week_start = datesPL[0]
        self.week_end = datesPL[-1]
        date_times = [time.text for time in date_times]
        date_times = convert_to_Warsaw_time(date_times)
        if len(date_times)>5: #if the prased website is not updated correctly race date may be on the first and last position in the table
            date_times.pop(0)
        self.race_week_datetimes = list(zip(session_names, dates, date_times))
        self.sessions = []
        
        # List of sessions as Session objects and single session model to inicialize each session
        for session_name, date, date_time in self.race_week_datetimes:
            session_obj = self.Session(session_name, date, date_time, self.name, self.flag_emoji)
            self.sessions.append(session_obj)
    
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
    
    def get_results_table_from_url(self, url): #returns table headers and table rows as two separate lists
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        session_results = soup.find("table", class_="resultsarchive-table")
        session_results_thead = session_results.find('thead')
        thead_rows = session_results_thead.find_all('tr')
        thead_cols = []

        for thead_row in thead_rows:
            thead_cols_row = thead_row.find_all(['th', 'abbr'])
            thead_cols_row = [ele.text.strip() for ele in thead_cols_row if ele.text.strip()]
            thead_cols_row = remove_duplicates(thead_cols_row)
            thead_cols_row.pop(1) # delete NO column
            thead_cols_row.pop(2) # delete CAR column
            thead_cols.extend(thead_cols_row)
            
        session_results_body = session_results.find('tbody')
        rows = session_results_body.find_all('tr')
        session_results = []

        for row in rows:
            cols = row.find_all('td')
            cols = [ele.text.strip() for ele in cols if ele.text.strip()]
            cols.pop(1) # delete NO column
            cols.pop(2) # delete CAR column
            # Modify driver name printout
            if len(cols) > 1:
                driver_name_parts = cols[1].split('\n')
                driver_name = ' '.join(driver_name_parts[:-1]) # driver_name = driver_name_parts[-1]
                cols[1] = driver_name
            
            session_results.append(cols)

        session_results = add_missing_values(thead_cols, session_results)
        # print("\n\n", thead_cols, session_results)
        table = t2a(
                header=thead_cols,
                body=session_results,
                style=PresetStyle.thin_compact
            )
        return table
    
    class Session:
        def __init__(self, session_name, date, time, week_name, flag_emoji):
            self.name = week_name
            self.flag_emoji = flag_emoji
            self.weekday = convert_date_to_weekday(date)
            self.session_name = session_name
            self.date = date
            self.time = time
            current_datetime = datetime.now()
            self.datetime = datetime.strptime(f"{self.date} {self.time} {current_datetime.year}", "%d %b %H:%M %Y")
            if self.session_name in ["Pierwszy trening", 'Drugi trening', 'Trzeci trening', 'Sprint', 'Feature', 'Kwalifikacje', 'Sprint Qualifying', 'Trening', 'Qualifying', 'Free Practice 1', 'Free Practice 2', 'Free Practice 3']:
                self.duration = timedelta(hours=1, minutes=5)
            elif self.session_name in ['Wyścig', 'Grand Prix']:
                self.duration = timedelta(hours=1, minutes=50)
        
        def check_session_status(self, current_datetime=datetime.now()): #return emote string (xd)
            
            if self.datetime < current_datetime:
                if current_datetime - self.datetime > self.duration:
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
                time_left = '**LIVE🟢**'
            else: 
                time_left = "**ZAKOŃCZONY⚫**" 
                
            return time_left
        
        def time_left(self, current_datetime=datetime.now()):
            time_difference = self.datetime - current_datetime
            return time_difference.total_seconds()
        
        def get_session_embed(self):
            try:
                current_datetime=datetime.now()
                embed = discord.Embed(title=f"{self.check_session_status()} {self.name} - {self.session_name} {self.flag_emoji}", color=0xEF1A2D)
                thumbnail = "https://cdn.betterttv.net/emote/611fc2b976ea4e2b9f78518f/3x.gif"
                embed.set_thumbnail(url=thumbnail)
                time_left = self.session_starts_in(current_datetime)
                            
                embed.add_field(name="", value=f":calendar_spiral: {self.weekday}", inline=True)
                embed.add_field(name="", value=f":alarm_clock: **{self.time}**", inline=True)
                embed.add_field(name="", value=f"{time_left}", inline=False)
                return embed
            
            except Exception as e:
                print("Error:", e)
                return None
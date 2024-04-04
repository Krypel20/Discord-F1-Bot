def info_about_session(race_week_datetimes, race, session_name):
#         race = current_race_html()
#         race_id, race_name, flag_emoji = return_current_race_name(race)
#         embed = discord.Embed(title=f"{flag_emoji(race_id)} {race_name} {flag_emoji(race_id)}", color=0xEF1A2D)
#         thumbnail = "https://cdn.discordapp.com/emojis/734895858725683314.webp?size=96&quality=lossless"
#         embed.add_field(name="", value="", inline=False)
#         embed.set_thumbnail(url=thumbnail)
        
#         current_datetime = datetime.now()
#         upcoming_session = False
#         print(race_week_datetimes)
        
#         for session, date, weekday, time in race_week_datetimes:
#             session_datetime = datetime.strptime(f"{date} {time} {current_datetime.year}", "%d %b %H:%M %Y")
#             print(f"{session}: {date} {time}")
#             embed.add_field(name="", value=f"{check_session_status(current_datetime, session_datetime)} **{session}**", inline=True)
#             embed.add_field(name="", value=f":calendar_spiral: {weekday}", inline=True)
#             embed.add_field(name="", value=f":alarm_clock: **{time}**", inline=True)
            
#             if not upcoming_session:
#                 time_left, upcoming_session = next_session_starts_in(current_datetime, session_datetime)
#                 embed.add_field(name="", value=f":clock1: Pozostało {time_left}", inline=False)
                    
#             embed.add_field(name="", value=f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━", inline=False)
            
#         await ctx.send(embed=embed)
#         await client.tree.sync()
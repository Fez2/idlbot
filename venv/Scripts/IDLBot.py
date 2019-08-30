# Work with Python 3.6
import discord
import pickle
import os.path
import pygsheets
import pprint
import datetime
import collections
from dateutil.parser import parse

client = pygsheets.authorize(service_file='./idl-bot-0391c0a6b9c9.json')

# Open the spreadsheet and the first sheet.
sh = client.open('IDL')
standings = sh.sheet1
schedule = client.open('IDL').worksheet_by_title('Sheet2')
data = standings.get_all_records()
data2 = sorted(data, key=lambda i: i['Rank'])

schedata = schedule.get_all_records()
schedata2 = sorted(schedata, key =lambda i: i['Week Start'])
# data = wks.get_all_values(include_tailing_empty=False,include_tailing_empty_rows=False)
pp = pprint.PrettyPrinter(indent=4)
pp.pprint(data)
pp.pprint(data2)

TOKEN = 'NjA2OTQ5NzI0NjIwMTkzODY2.XWREHA.a8HBC-rfcch6urSPfFFmb1EX66k'

client = discord.Client()

@client.event
async def on_message(message):
    # Update google sheet data on ping
    gclient = pygsheets.authorize(service_file='./idl-bot-0391c0a6b9c9.json')
    sh = gclient.open('IDL')
    standings = sh.sheet1
    schedule = gclient.open('IDL').worksheet_by_title('Sheet2')
    data = standings.get_all_records()
    data2 = sorted(data, key=lambda i: [-(0 if i['League'] == 'Premier' else i['League']),i['Match Wins'], -i['Match Losses']], reverse=True)


    schedata = schedule.get_all_records()
    schedata2 = sorted(schedata, key=lambda i: i['Week Start'])
    # Get the current datetime when bot is pinged
    current = datetime.datetime.now()
    week = list(filter(lambda sched: parse(sched['Week Start']) < current < parse(sched['Week End']), schedata2))[0]
    # we do not want the bot to reply to itself
    if message.author == client.user:
        return

    if message.content.startswith('!hello'):
        msg = 'Hello {0.author.mention}'.format(message)
        await client.send_message(message.channel, msg)
    if message.content.startswith('!standings'):
        header = '{:<10s}\t{:>6s}\t{:>10s}\t{:>10s}\n'.format('Player', "League", "Matches", "Games")
        l1 = []
        i = 0
        while i < data2.__len__():
            l1.append('{:<10s}\t{:>6s}\t{:>10s}\t{:>14s}\n'.format(data2[i]["Player"],
                                                         str(data2[i]["League"]),
                                                         data2[i]["Matches"],
                                                         str(data2[i]["Games"])))
            i += 1
        body = ''.join(l1)
        msg = header + body
        await client.send_message(message.channel, msg)
    if message.content.startswith('!schedule'):
        header = 'Week ' + str(week['Week Number']) + ' matches will be streamed on ' + str(week['Week End']) + ' at 9:30 PM CST!\n'

        body = 'Week {}: {} - {}\nPremier Match 1:\t{:>50s}\nPremier Match 2:\t{:>50s}\nLeague 1 Match 1:\t{:>50s}\nLeague 1 Match 2:\t{:>50s}\nLeague 2 Match 1:\t{:>50s}\n' \
              'League 2 Match 2:\t{:>50s}\nRest Week:\t{:>50s}\n'.format(str(week['Week Number']), str(week['Week Start']), str(week['Week End']), week['Premier Match 1'],
                                                                     week['Premier Match 2'], week['League 1 Match 1'], week['League 1 Match 2'],
                                                                     week['League 2 Match 1'], week['League 2 Match 2'], str(week['Rest']))
        msg =  header + body
        await client.send_message(message.channel, msg)
    if message.content.startswith('!results'):
        week_number = (int(week['Week Number']) - 1)
        result_week = list(filter(lambda num: int(num['Week Number']) == week_number, schedata2))[0]
        header = 'Week ' + str(result_week['Week Number']) + ' Results\n'
        body = (result_week['Premier Match 1']+ '\n' +
               result_week['Premier Match 2']+ '\n' +
                result_week['League 1 Match 1']+ '\n' +
                result_week['League 1 Match 2']+ '\n' +
                result_week['League 2 Match 1']+ '\n' +
                result_week['League 2 Match 2']+ '\n' )
        msg = header + body
        await client.send_message(message.channel, msg)


@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

client.run(TOKEN)
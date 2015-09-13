from itty import *
from tropo import Tropo, Session, Result, Choices
from pprint import pprint
from datetime import datetime
import MySQLdb

current = {}


@post('/')
def index(request):
    t = Tropo()

    t.say(
        'Welcome to the automated voice driving citations checker, a free service to find where and when you need to appear in court.')

    choices = Choices('[2-4 DIGITS]', mode='dtmf', attempts=3)
    t.ask(choices, timeout=15, name='birthday_year',
          say='To verify who you are, please start by entering your four digit year of birth')

    t.on(event='continue', next='/birthday_month')

    return t.RenderJson()


@post('/birthday_month')
def birthday_month(request):
    r = Result(request.body)
    print r._sessionId
    t = Tropo()

    answer = r.getInterpretation()

    current[r._sessionId] = {'birthday': {'year': answer}}

    choices = Choices('[1-2 DIGITS]', mode='dtmf')
    t.ask(choices, timeout=15, name='birthday_month',
          say='Please enter your month of birth as a number', attempts=3)

    t.on(event='continue', next='/birthday_day')

    return t.RenderJson()


@post('/birthday_day')
def birthday_day(request):
    r = Result(request.body)
    t = Tropo()

    answer = r.getInterpretation()

    current[r._sessionId]['birthday']['month'] = answer

    choices = Choices('[1-2 DIGITS]', mode='dtmf')
    t.ask(choices, timeout=15, name='birthday_day',
          say='Please enter your date of birth', attempts=3)

    t.on(event='continue', next='/name')

    return t.RenderJson()


@post('/name')
def name(request):
    r = Result(request.body)
    t = Tropo()

    answer = r.getInterpretation()

    current[r._sessionId]['birthday']['day'] = answer

    b = current[r._sessionId]['birthday']

    if len(b['month']) == 1:
        b['month'] = '0' + b['month']
    if len(b['day']) == 1:
        b['day'] = '0' + b['day']

    formatted_birthday = '%s-%s-%s' % (b['year'], b['month'], b['day'])
    current[r._sessionId]['birthday'] = formatted_birthday

    db = MySQLdb.connect(
        host='localhost', user='globalhackv', passwd='globalhack', db='globalhackv')
    cur = db.cursor()

    cur.execute(
        'SELECT COUNT(*) AS count FROM good_data_fixed WHERE date_of_birth = %s', (formatted_birthday, ))
    result = cur.fetchone()

    cur.execute(
        'SELECT last_name FROM good_data_fixed WHERE date_of_birth = %s', (formatted_birthday, ))
    people = cur.fetchall()

    cur.close()
    db.close()

    if int(result[0]) == 0:
        t.say('We have found zero results, have a good day!')
        return t.RenderJson()

    choices = []
    for row in people:
        print row[0]
        choices.append(row[0])
    names = ','.join(choices)

    t.ask(choices=names, say='Please say your last name', attempts=3)

    t.on(event='continue', next='/results')

    return t.RenderJson()


@post('/results')
def results(request):
    r = Result(request.body)
    t = Tropo()

    answer = r.getInterpretation()

    u = current[r._sessionId]

    db = MySQLdb.connect(
        host='localhost', user='globalhackv', passwd='globalhack', db='globalhackv')
    cur = db.cursor()

    cur.execute('SELECT court_date, court_location, violation_description, first_name, last_name, warrant_status, fine_amount, court_cost FROM good_data_fixed WHERE date_of_birth = %s AND last_name LIKE %s AND status <> \'CLOSED\' AND status <> \'DISMISS WITHOUT COSTS\'', (u[
                'birthday'], answer, ))
    result = cur.fetchall()

    cur.close()
    db.close()

    t.say('Hello %s %s,' % (result[0][3], result[0][4]))

    total_cost = 0
    total_fees = 0

    dates = {}
    for row in result:
        if row[0] not in dates:
            d = datetime.strptime(row[0], '%Y-%m-%d')
            nice = d.strftime('%A, %B, %-d, %Y')

            dates[row[0]] = {'date': nice, 'location': row[1], 'events': []}

        dates[row[0]]['events'].append({
            'fine': row[6],
            'fee': row[7],
            'description': row[2],
            'warrant': row[5]
        })

        total_cost += float(row[6][1:])
        total_fees += float(row[7][1:])

    for date, info in dates.iteritems():
        t.say('You have a court date on %s. This is for the following violations' % (
            info['date']))

        for violation in info['events']:
            t.say('Violation ' + violation['description'])

            if violation['fine'] != '':
                t.say('This includes a %s fine and %s court fee' %
                      (violation['fine'], violation['fee']))
                extra = 'also'

            if violation['warrant'] == 'TRUE':
                t.say('This %s includes a warrant for your arrest' % (extra))

    if total_cost > 0:
        t.say('Your total fines are $%.2f and your total fees are $%.2f, bringing the total cost to $%.2f.' % (
            total_cost, total_fees, total_cost+total_fees))

    t.say('Thank you for calling, have a nice day.')

    return t.RenderJson()

run_itty(server='wsgiref', host='0.0.0.0', port=4847)

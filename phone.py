from itty import *
from tropo import Tropo, Session, Result, Choices
from pprint import pprint
from datetime import datetime
import MySQLdb

current = {}

@post('/')
def index(request):
  t = Tropo()

  t.say('Welcome to the automated voice driving citations checker, a free service to find where and when you need to appear in court.')

  choices = Choices('[2 DIGITS]', mode='any', attempts=3)
  t.ask(choices, timeout=15, name='birthday_year', say='To verify who you are, please start by entering the last two digits of your year of birth')

  t.on(event='continue', next='/birthday_month')

  return t.RenderJson()

@post('/birthday_month')
def birthday_month(request):
  r = Result(request.body)
  print r._sessionId
  t = Tropo()

  answer = r.getInterpretation()

  current[r._sessionId] = { 'birthday': { 'year': answer } }

  print current[r._sessionId]

  choices = Choices('1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12', mode='any')
  t.ask(choices, timeout=15, name='birthday_month', say='Please enter your month of birth as a number', attempts=3)

  t.on(event='continue', next='/birthday_day')

  return t.RenderJson()

@post('/birthday_day')
def birthday_day(request):
  r = Result(request.body)
  t = Tropo()

  answer = r.getInterpretation()

  current[r._sessionId]['birthday']['month'] = answer

  print current[r._sessionId]

  choices = Choices('1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31', mode='any')
  t.ask(choices, timeout=15, name='birthday_day', say='Please enter your date of birth', attempts=3)

  t.on(event='continue', next='/name')

  return t.RenderJson()

@post('/name')
def name(request):
  r = Result(request.body)
  t = Tropo()

  answer = r.getInterpretation()

  current[r._sessionId]['birthday']['day'] = answer

  b = current[r._sessionId]['birthday']

  print current[r._sessionId]

  if len(b['month']) == 1: b['month'] = '0' + b['month']
  if len(b['day']) == 1: b['day'] = '0' + b['day']

  formatted_birthday = '%s-%s-%s' % (b['year'], b['month'], b['day'])
  current[r._sessionId]['birthday'] = formatted_birthday

  db = MySQLdb.connect(host='localhost', user='globalhackv', passwd='globalhack', db='globalhackv')
  cur = db.cursor()

  cur.execute('SELECT COUNT(*) AS count FROM good_data_fixed WHERE date_of_birth LIKE %s', ('%' + formatted_birthday, ))
  result = cur.fetchone()

  cur.execute('SELECT last_name FROM good_data_fixed WHERE date_of_birth LIKE %s', ('%' + formatted_birthday, ))
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

  print current[r._sessionId]

  db = MySQLdb.connect(host='localhost', user='globalhackv', passwd='globalhack', db='globalhackv')
  cur = db.cursor()

  cur.execute('SELECT court_date, court_location, violation_description, first_name, last_name, warrant_status, fine_amount, court_cost FROM good_data_fixed WHERE date_of_birth LIKE %s AND last_name LIKE %s', ('%' + u['birthday'], answer, ))
  result = cur.fetchall()

  cur.close()
  db.close()

  t.say('Hello %s %s,' % (result[0][3], result[0][4]))

  total_cost = 0
  total_fees = 0

  for row in result:
    d = datetime.strptime(row[0], '%Y-%m-%d')
    nice = d.strftime('%A, %B, %-d, %Y')
    t.say('You have a court date on %s at %s for %s.' % (nice, row[1], row[2]))

    if row[6] != '':
      total_cost += float(row[6][1:])
      total_fees += float(row[7][1:])
      t.say('There is a %s fine and %s court fee for this.' % (row[6], row[7]))

    if row[5] == 'TRUE':
      t.say('This includes a warrant for your arrest.')

  if total_cost > 0:
    t.say('Your total fines are $%.2f and your total fees are $%.2f, bringing the total cost to $%.2f.' % (total_cost, total_fees, total_cost+total_fees))

  t.say('Thank you for calling, have a nice day.')

  return t.RenderJson()

run_itty(server='wsgiref', host='0.0.0.0', port=4847)

from datetime import datetime
prefix = 'R'

def datetimeformat(value, format='%d-%m-%Y %H:%M %p'):
	if value and type(value) is datetime:
		return value.strftime(format)
	return ''

def todatetime(value, format='%d-%m-%Y'):
	if value and (isinstance(value, str) or isinstance(value,unicode)):
		return datetime.strptime(value,format)
	return None

def comptoday(value):
	if not value and not isinstance(value, datetime):
		return 0
	if isinstance(value,str):
		value = datetime.strptime(value,'%d-%m-%Y')
	today = datetime.utcnow()
	if today == value:
		return 0
	elif today <= value:
		return -1
	elif today > value:
		return 1
	return 0
	

def currency(value,safe=True,style=True,request=None):
	from jinja2.filters import do_mark_safe
	global prefix
	if isinstance(value,str) and value != '':
		value = float(value)
	if style:
		value = '{:04,.2f}'.format(value)
	if request:
		prefix = request.swizapp.settings.currencyFormat
		return '%s %s' % (prefix,value)
	if safe:
		return do_mark_safe('<span class="currency">%s</span> %s' % (prefix,value))
	else:
		return '%s %s' % (prefix,value)
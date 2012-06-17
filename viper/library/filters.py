from datetime import datetime
prefix = 'Rs.'

def datetimeformat(value, format='%d-%m-%Y %H:%M %p'):
	if value != None and type(value) is datetime:
		return value.strftime(format)
	return ''

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
	

def currency(value,request=None):
	global prefix
	if request:
		prefix = request.swizapp.settings.currencyFormat
		return '%s %s' % (prefix,value)
	return '%s %s' % (prefix,value)
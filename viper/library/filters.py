from datetime import datetime
prefix = 'Rs.'

def datetimeformat(value, format='%d-%m-%Y %H:%M %p'):
	if value != None and type(value) is datetime:
		return value.strftime(format)
	return ''

def currency(value,request=None):
	global prefix
	if request:
		prefix = request.swizapp.settings.currencyFormat
		return '%s %s' % (prefix,value)
	return '%s %s' % (prefix,value)
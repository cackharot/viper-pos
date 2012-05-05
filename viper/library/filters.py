from datetime import datetime

def datetimeformat(value, format='%d-%m-%Y %H:%M'):
	if value != None and type(value) is datetime:
		return value.strftime(format)
	return ''	

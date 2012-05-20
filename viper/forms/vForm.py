from pyramid_simpleform import Form
from formencode import Schema, validators
from formencode.api import *
from pyramid.i18n import get_localizer

from formencode import htmlfill
from formencode import variabledecode
from formencode import Invalid

from pyramid.renderers import render

import logging
log = logging.getLogger(__name__)

class vForm(Form):
	def __init__(self,prefix=None,**kw):
		self.prefix = prefix
		super(vForm,self).__init__(**kw)
		pass
		
	def validate(self):
		assert self.schema or self.validators, \
		        "validators and/or schema required"

		if self.is_validated:
			return not(self.errors)

		if self.method and self.method != self.request.method:
			return False

		if self.method == "POST":
			params = self.request.POST
		else:
			params = self.request.params
			
		if self.prefix:
			new = {}
			for k,v in params.items():
				new[k.replace(self.prefix,'')] = v
			params = new
			#log.info('Updated Params: %s' % params)
	
		if self.variable_decode:
			decoded = variabledecode.variable_decode(
			            params, self.dict_char, self.list_char)

		else:
			decoded = params

		self.data.update(params)

		if self.schema:
			try:
				self.data = self.schema.to_python(decoded, self.state)
			except Invalid, e:
				self.errors = e.unpack_errors(self.variable_decode,
				                              self.dict_char,
			                                  self.list_char)

		if self.validators:
			for field, validator in self.validators.iteritems():
				try:
					self.data[field] = validator.to_python(decoded.get(field),
					                                       self.state)

				except Invalid, e:
					self.errors[field] = unicode(e)
					
		#log.debug('Errors: %s' % (self.errors))
		
		self.is_validated = True
		return not(self.errors)
	pass

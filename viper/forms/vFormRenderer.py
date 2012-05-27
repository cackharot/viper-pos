from webhelpers.html import tags
from webhelpers.html.builder import HTML

from ..library.ViperLog import log

class vFormRenderer(object):
	"""
	A simple form helper. Uses WebHelpers to render individual
	form widgets: see the WebHelpers library for more information
	on individual widgets.
	"""

	def __init__(self, form, csrf_field='_csrf'):

		self.form = form
		if hasattr(form,'prefix'):
			self.prefix = form.prefix 
		else:
			self.prefix = ''
		self.data = self.form.data
		self.csrf_field = csrf_field

	def value(self, name, default=None):
		#print 'Value[%s] = %s' % (name,self.data.get(name, default))
		return self.data.get(name, default)

	def begin(self, url=None, **attrs):
		"""
		Creates the opening <form> tags.

		By default URL will be current path.
		"""
		url = url or self.form.request.path
		multipart = attrs.pop('multipart', self.form.multipart)
		return tags.form(url, multipart=multipart, **attrs)

	def end(self):
		"""
		Closes the form, i.e. outputs </form>.
		"""
		return tags.end_form()

	def csrf(self, name=None):
		"""
		Returns the CSRF hidden input. Creates new CSRF token
		if none has been assigned yet.

		The name of the hidden field is **_csrf** by default.
		"""
		name = name or self.csrf_field

		token = self.form.request.session.get_csrf_token()
		if token is None:
		    token = self.form.request.session.new_csrf_token()

		return self.hidden(name, value=token)

	def csrf_token(self, name=None):
		"""
		Convenience function. Returns CSRF hidden tag inside hidden DIV.
		"""
		return HTML.tag("div", self.csrf(name), style="display:none;")

	def hidden_tag(self, *names):
		"""
		Convenience for printing all hidden fields in a form inside a 
		hidden DIV. Will also render the CSRF hidden field.

		:versionadded: 0.4
		"""
		inputs = [self.hidden(name) for name in names]
		inputs.append(self.csrf())
		return HTML.tag("div", 
		                tags.literal("".join(inputs)), 
		                style="display:none;")
		                
	def getErrorTag(self,name):
		if self.is_error(name):
			attrs = {}
			attrs['class'] = 'help-inline'
			return HTML.tag('span',self.errors_for(name)[0],**attrs)
		return ''

	def text(self, name, value=None, id=None, **attrs):
		"""
		Outputs text input.
		"""
		id = id or name
		val = self.value(name, value)
		return tags.text(self.prefix + name, val, id, **attrs) + self.getErrorTag(name)

	def file(self, name, value=None, id=None, **attrs):
		"""
		Outputs file input.
		"""
		id = id or name
		val = self.value(name, value)
		return tags.file(self.prefix + name, val, id, **attrs) + self.getErrorTag(name)

	def hidden(self, name, value=None, id=None, **attrs):
		"""
		Outputs hidden input.
		"""
		id = id or name
		val = self.value(name, value)
		return tags.hidden(self.prefix + name, val, id, **attrs) + self.getErrorTag(name)

	def radio(self, name, value=None, checked=False, label=None, **attrs):
		"""
		Outputs radio input.
		"""
		checked = self.data.get(name) == value or checked
		return tags.radio(self.prefix + name, value, checked, label, **attrs) + self.getErrorTag(name)

	def submit(self, name, value=None, id=None, **attrs):
		"""
		Outputs submit button.
		"""
		id = id or name
		val = self.value(name, value)
		return tags.submit(self.prefix + name, val, id, **attrs)

	def select(self, name, options, selected_value=None, id=None, **attrs):
		"""
		Outputs <select> element.
		"""
		id = id or name
		val = [self.value(name, selected_value)]
		return tags.select(self.prefix + name, val, options, id, **attrs) + self.getErrorTag(name)

	def checkbox(self, name, value="1", checked=False, label=None, id=None, 
		         **attrs):
		"""
		Outputs checkbox input.
		"""

		id = id or name
		val = self.value(name)
		return tags.checkbox(self.prefix + name, value, val, label, id, **attrs) + self.getErrorTag(name)

	def textarea(self, name, content="", id=None, **attrs):
		"""
		Outputs <textarea> element.
		"""
		id = id or name
		val = self.value(name, content)
		return tags.textarea(self.prefix + name, val, id, **attrs) + self.getErrorTag(name)

	def password(self, name, value=None, id=None, **attrs):
		"""
		Outputs a password input.
		"""
		id = id or name
		val = self.value(name, value)
		return tags.password(self.prefix + name, val, id, **attrs) + self.getErrorTag(name)

	def is_error(self, name):
		"""
		Shortcut for **self.form.is_error(name)**
		"""
		return self.form.is_error(name)

	def errors_for(self, name):
		"""
		Shortcut for **self.form.errors_for(name)**
		"""
		return self.form.errors_for(name)

	def all_errors(self):
		"""
		Shortcut for **self.form.all_errors()**
		"""
		return self.form.all_errors()

	def errorlist(self, name=None, **attrs):
		"""
		Renders errors in a <ul> element. Unless specified in attrs, class
		will be "error".

		If no errors present returns an empty string.

		`name` : errors for name. If **None** all errors will be rendered.
		"""

		if name is None:
		    errors = self.all_errors()
		else:
		    errors = self.errors_for(name)

		if not errors:
		    return ''

		content = "\n".join(HTML.tag("li", error) for error in errors)
		
		if 'class_' not in attrs:
		    attrs['class_'] = "error"

		return HTML.tag("ul", tags.literal(content), **attrs)

	def label(self, name, label=None, **attrs):
		"""
		Outputs a <label> element. 

		`name`  : field name. Automatically added to "for" attribute.

		`label` : if **None**, uses the capitalized field name.
		"""
		label = label or name.capitalize()
		
		if self.prefix:
			name = self.prefix + name
		if 'for_' not in attrs:
		    attrs['for_'] = name
		
		return HTML.tag("label", label, **attrs)

import uuid

TestTenantId = uuid.UUID('4f362af5-8657-41bc-a8c6-0166c46a4431')
TestUserId = str(uuid.UUID('895f05cf-7fd3-45a2-88d0-13fac7d567f1'))

class FormUserIdentity(object):
	"""
		Holds the authenticated user details
	"""

	def __init__(self):
		self._UserId = TestUserId
		self._TenantId = TestTenantId
		self._Name = None
		self._Roles = None
		self._Privileges = None
		self._OperatorTenantId = None
		self._ipAddress = None

	@property
	def UserId(self):
		return self._UserId

	@property
	def TenantId(self):
		return self._TenantId

	@property
	def Name(self):
		return self._Name

	@property
	def Roles(self):
		return self._Roles

	@property
	def Privileges(self):
		return self._Privileges

	@property
	def OperatorTenantId(self):
		return self._OperatorTenantId

	@property
	def IpAddress(self):
		return self._ipAddress

	pass

UserIdentity = FormUserIdentity()

import json
import uuid
import random
from datetime import datetime,date

from sqlalchemy.exc import DBAPIError
from sqlalchemy import desc,func,cast,Date
from sqlalchemy import or_

from ..models import DBSession
from ..models.User import User, UserContactDetails
from ..models.UserRoles import Role, UserRoles, RolePrivileges
from ..library.ViperLog import log
from ..library.helpers import EncryptPassword

class UserService(object):
	"""
		User service class
	"""
	
	def __init__(self,userId=None,tenantId=None):
		self.TenantId = tenantId
		self.UserId   = userId
		pass
	
	def GetUserDetails(self,userId,tenantId=None):
		if userId:
			return DBSession.query(User).filter(User.Id==userId,User.Status==True).first()
		return None
	
	def GetUserDetailsByName(self,name,tenantId):
		if name and tenantId:
			return DBSession.query(User).filter(User.TenantId==tenantId,User.UserName==name,User.Status==True).first()
		return None
		
	def CheckUserExists(self,uid,tenantId,username=None,mobile=None,email=None):
		if username and mobile and email and tenantId:
			query = DBSession.query(User.Id).filter(User.TenantId==tenantId)
			if uid:
				query = query.filter(User.Id!=uid)
			query = query.filter(or_(User.UserName==username,User.Contacts.any(UserContactDetails.Mobile==mobile),\
					User.Contacts.any(UserContactDetails.Email==email)))
			valid = query.scalar()
			if valid:
				return True
		return False
		
	def AddUser(self,entity):
		if entity and entity.TenantId and entity.CreatedBy:
			cnt = entity.Contacts[0]
			if self.CheckUserExists(None,entity.TenantId,entity.UserName,cnt.Mobile, cnt.Email):
				raise Exception('User name or email or mobile already exists!')
			entity.Password = EncryptPassword('company')
			entity.CreatedOn = datetime.utcnow()
			entity.Status = True
			DBSession.add(entity)
			return True
		return False
		
	def SaveUser(self,entity):
		if entity and entity.Id and entity.TenantId and entity.UpdatedBy:
			cnt = entity.Contacts[0]
			if self.CheckUserExists(entity.Id,entity.TenantId,entity.UserName,cnt.Mobile, cnt.Email):
				raise Exception('User name or email or mobile already exists!')
			entity.UpdatedOn = datetime.utcnow()
			DBSession.add(entity)
			return True
		return False
		
	def DeleteUser(self,userId,tenantId):
		if userId and tenantId:
			DBSession.query(User).filter(User.Id==userId,User.TenantId==tenantId).delete()
			return True
		return False
		
	def SearchUser(self,tenantId,pageNo,pageSize,searchField,searchValue):
		if not tenantId:
			return None
		query = DBSession.query(User).filter(User.TenantId==tenantId,User.Status==True)\
							.join(UserContactDetails)
		
		if searchValue and searchValue != '':
			searchValue = '%%%s%%' % searchValue
			if searchField == 'name':
				query = query.filter(UserContactDetails.FirstName.like(searchValue))
			elif searchField == 'mobile':
				query = query.filter(UserContactDetails.Mobile.like(searchValue))
			elif searchField == 'username':
				query = query.filter(User.UserName.like(searchValue))
		
		lstUsers = query.offset(pageNo).limit(pageSize).all()
		return lstUsers
	
	pass


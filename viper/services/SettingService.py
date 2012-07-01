from sqlalchemy.exc import DBAPIError

from ..models import DBSession
from ..models.TenantSetting import TenantSetting
from ..models.PrintTemplate import PrintTemplate

from .ServiceExceptions import SettingException 

class SettingService(object):
    """
        Setting service class
    """
    
    def GetTenantSettings(self,tenantId,attrName=None):
        if tenantId:
            try:
                query = DBSession.query(TenantSetting).filter(TenantSetting.TenantId==tenantId,TenantSetting.Status==True)
                if attrName:
                    query = query.filter(TenantSetting.AttributeName==attrName)
                return query.all()
            except DBAPIError, ex:
                raise SettingException(ex,'Error while fetching tenant settings')
        return None
    
    def GetTenantSettingById(self,tenantId,settingId):
        if tenantId:
            try:
                query = DBSession.query(TenantSetting).filter(TenantSetting.TenantId==tenantId,TenantSetting.Id==settingId)
                return query.first()
            except DBAPIError, ex:
                raise SettingException(ex,'Error while fetching tenant settings')
        return None
    
    def SaveTenantSetting(self,setting):
        if setting and setting.TenantId and setting.AttributeName:
            try:
                DBSession.add(setting)
                DBSession.flush()
                return True
            except DBAPIError, ex:
                raise SettingException(ex,'Error while saving tenant settings')
        return False
    
    def DeleteTenantSettings(self,tenantId,settingId=None):
        if tenantId:
            try:
                query = DBSession.query(TenantSetting).filter(TenantSetting.TenantId==tenantId)
                if settingId:
                    query = query.filter(TenantSetting.Id==settingId)
                return query.delete()
            except DBAPIError, ex:
                raise SettingException(ex,'Error while deleting tenant settings')    
        return 0
    
    def GetPrintTemplates(self,tenantId,name=None):
        if tenantId:
            try:
                query = DBSession.query(PrintTemplate).filter(PrintTemplate.TenantId==tenantId,PrintTemplate.Status==True)
                if name:
                    query = query.filter(PrintTemplate.Name==name)
                return query.all()
            except DBAPIError, ex:
                raise SettingException(ex,'Error while fetching print templates')
        return None
    
    def GetPrintTemplateById(self,templateId,tenantId):
        if tenantId:
            try:
                query = DBSession.query(PrintTemplate).filter(PrintTemplate.TenantId==tenantId,PrintTemplate.Id==templateId)
                return query.first()
            except DBAPIError, ex:
                raise SettingException(ex,'Error while fetching print template')
        return None
    
    def SavePrintTemplate(self,template):
        if template and template.TenantId and template.Name:
            try:
                DBSession.autoflush = False
                DBSession.add(template)
                DBSession.flush()
                return True
            except DBAPIError, ex:
                raise SettingException(ex,'Error while saving print templates')
        return False
    
    def DeletePrintTemplate(self,tenantId,templateId=None):
        if tenantId:
            try:
                query = DBSession.query(PrintTemplate).filter(PrintTemplate.TenantId==tenantId)
                if templateId:
                    query = query.filter(PrintTemplate.Id==templateId)
                    return query.delete()
            except DBAPIError, ex:
                raise SettingException(ex,'Error while deleting print templates')
        return 0
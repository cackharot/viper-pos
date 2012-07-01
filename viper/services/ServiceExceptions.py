
class SettingException(Exception):
    '''
    Tenant Setting Exception
    '''


    def __init__(self,ex=None,message=None):
        '''
        Constructor
        '''
        self.InnerException = ex
        self.message = message
        

class TenantException(Exception):
    '''
    Tenant Exception
    '''


    def __init__(self,ex=None,message=None):
        '''
        Constructor
        '''
        self.InnerException = ex
        self.message = message
        
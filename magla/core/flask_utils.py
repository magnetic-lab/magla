class FlaskLoginUser(object):
    def __init__(self):
        self._authenticated = False
    
    def is_authenticated(self):
        return self._authenticated
    
    def is_active(self):
        return self.active
    
    def is_anonumous(self):
        return False
    
    def get_id(self):
        return str(self.id).encode("utf-8")
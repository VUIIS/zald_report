import os,json
from flask.ext.wtf import Form
from wtforms.fields import TextField, TextAreaField, SubmitField, PasswordField,HiddenField
from wtforms.validators import Required
import ExtractDataRedcap

class SignupForm(Form):
    username = TextField("Username (Project ID)",  [Required("Please enter your project name / username (same variable).")])
    password = PasswordField("Password",  [Required("Please enter your password.")])
    key = PasswordField("Api Key",  [Required("Please enter your api key for REDCap.")])
    main = TextField('Main Library', [Required("Please enter a main library name on REDCap.")])
    submit = SubmitField("Add project")
    
    def __init__(self, *args, **kwargs):
      Form.__init__(self, *args, **kwargs)
    
    def validate(self):
      if not Form.validate(self):
        return False
       
      info = json.load(open(os.environ['REPORT_CONFIG']))
      if self.username.data in info.keys():
        self.username.errors.append("This project ID already exists. If you don't know the password, ask the admin.")
        return False
      else:
          if not ExtractDataRedcap.check_key(self.key.data):
            self.key.errors.append("KeyError: The API Key was not found in the metadata on REDCap.")
            return False
          else:
            return True

class SigninForm(Form):
    username = TextField("Username",  [Required("Please enter your username.")])
    password = PasswordField('Password', [Required("Please enter your password.")])
    succeed = HiddenField("succeed")
    submit = SubmitField("Sign In")
     
    def __init__(self, *args, **kwargs):
      Form.__init__(self, *args, **kwargs)
    
    def validate(self):
      if not Form.validate(self):
        return False
       
      info = json.load(open(os.environ['REPORT_CONFIG']))
      if self.username.data in info.keys() and self.password.data==info[self.username.data]['password']:
          return True
      else:
        self.username.errors.append("Invalid username or password")
        return False

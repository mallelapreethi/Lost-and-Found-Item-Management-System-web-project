import secrets
import string
def genpwd():
    letters=string.ascii_letters
    digits=string.digits
    alphabet=letters+digits
    pwd_length=8
    while True:
        pwd=''
        for i in range(pwd_length):
            pwd += ''.join(secrets.choice(alphabet)) 
        return pwd
        
            
    


from PIL import Image
try: 
    img  = Image.open("notfound.jpg") 
    img.show()
except IOError:
    pass

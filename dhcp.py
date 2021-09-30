from flask import Flask, render_template, request, redirect, url_for, flash
from suds.client import Client
import requests
import xml.etree.ElementTree as ElementTree 

# directory = "/etc/dhcpd.conf"

xml = """<?xml version="1.0" encoding="utf-8"?>
<soap12:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap12="http://www.w3.org/2003/05/soap-envelope">
  <soap12:Body>
    <TCKimlikNoDogrula xmlns="http://tckimlik.nvi.gov.tr/WS">
      <TCKimlikNo></TCKimlikNo>
      <Ad></Ad>
      <Soyad></Soyad>
      <DogumYili></DogumYili>
    </TCKimlikNoDogrula>
  </soap12:Body>
</soap12:Envelope>"""
headers = {
    'Content-Type': 'application/soap+xml; charset=utf-8',
}

def check_tc_id(person_id, name, surname, birth_year):
    element = ElementTree.fromstring(xml)
    element[0][0][0].text = str(person_id)
    element[0][0][1].text = str(name).replace('i', 'İ').upper()
    element[0][0][2].text = str(surname).replace('i', 'İ').upper()
    element[0][0][3].text = str(birth_year)
    data = ElementTree.tostring(element, encoding="UTF-8")
    request = requests.post(
        "https://tckimlik.nvi.gov.tr/Service/KPSPublic.asmx",
        data=data,
        headers=headers,
    )

    response_element = ElementTree.fromstring(request.content)
    response_txt = response_element[0][0][0].text
    print(response_element)
    print("deneeme36")
    if response_txt == "true":
        return True
    else:
        
        #return True #geliştirme için tc kontrolü kapatıldı açmayı UNUTMA
        return False
    
# print(check_tc_id('38869500188', 'ali', 'kılıç', '1950'))

class Deneme : 
    
    def __init__(self):
        self.logged_in = False
    
user = Deneme()  



# WSDL_URL="https://tckimlik.nvi.gov.tr/Service/KPSPublic.asmx?WSDL"
# client=Client(WSDL_URL)



# def tcKimlikDogrula(params):
#     try:
#         print("Hata/service")
#         return  client.service.TCKimlikNoDogrula(**params)
#     except Exception as e:
#         return False

# from flask_mysqldb import MySQL

app = Flask(__name__)
app.secret_key = "aaa"

#configure

# app.config["MYSQL_HOST"] = 'localhost'
# app.config["MYSQL_USER"] = 'root'
# app.config["MYSQL_PASSWORD"] = 'facebook66'
# app.config["MYSQL_DB"] = 'deneme'


# mysql = MySQL(app)


 
@app.route("/")
def form():
    
    return redirect(url_for("login"))


@app.route("/login")
def login():
    
    return render_template("login.html")

 
@app.route("/login",methods = ["GET","POST"])
def login_first():
    # flash("You have to log in")
  
    if request.method == "POST":
        # post ve kontrol
        tc = request.form.get("tc")
        isim = request.form.get("isim")
        soyisim = request.form.get("soyisim")
        dogum = request.form.get("dogum")
        
        isim = isim.upper()
        soyisim = soyisim.upper()

        args={
        "TCKimlikNo":tc,
        "Ad":isim,
        "Soyad":soyisim,
        "DogumYili":dogum
        }
        
        print("aaa")
        
        
            
        if check_tc_id(tc, isim, soyisim, dogum):
            user.logged_in = True
            userLogin = open("userLogin.txt","a",encoding='utf-8')
            userLogin.write("\n")
            userLogin.write("TC :{} ;".format(tc)) 
            userLogin.write("\n") 
            userLogin.write("Name :{} ;".format(isim)) 
            userLogin.write("\n") 
            userLogin.write("Surname :{} ;".format(soyisim)) 
            userLogin.write("\n")
            userLogin.write("BirthDate :{} ;".format(dogum)) 
            userLogin.write("\n")  
            print("check tc")
            return redirect(url_for("form_config"))
        else:
            flash("Wrong Login Attempt")
            return redirect(url_for("login"))    
                
    
    return render_template("login.html")
        

@app.route("/dhcpdconf")     
def form_config():
   
    if(user.logged_in == True):         
        user.logged_in = False
        return render_template("index.html") 
        
    else:
        flash("You have to log in")
        return redirect(url_for("login"))

               
@app.route("/dhcpdconf",methods = ["GET","POST"])
def config():
    if request.method == "POST":
       
        subnet = request.form.get("subnet")
        netmask = request.form.get("netmask")
        routers = request.form.get("routers")
        # gateway  = request.form.get("gateway")
        dns = request.form.get("dns")
        broadcast = request.form.get("broadcast")
        start  = request.form.get("start")
        end  = request.form.get("end")
      
        file = open("dhcpd.conf","w",encoding='utf-8') 

        file.write("subnet {} ".format(subnet))
        file.write("netmask {} ".format(netmask))
        # file.write("\n")     
        file.write(" {")
        file.write("\n") 

        file.write("option subnet-mask 255.255.255.0 ;")
        file.write("\n") 

        file.write("option routers {} ;".format(routers))
        file.write("\n") 

        file.write("default-lease-time 1036800 ;")
        file.write("\n")

        file.write("max-lease-time 1036800 ;")
        file.write("\n")

        file.write("option domain-name-servers {} ;".format(dns)) 
        file.write("\n") 

        file.write("option broadcast-address {} ;".format(broadcast)) 
        file.write("\n") 

        file.write("range {} {} ;".format(start,end))
        file.write("\n")

        # file.write("start : {}".format(start)) 
        # file.write("\n") 
        # file.write("end : {}".format(end)) 
        file.write("}")
        file.close()        

        flash("SAVED")
        return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)
   
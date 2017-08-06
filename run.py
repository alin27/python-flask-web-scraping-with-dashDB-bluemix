"""Cloud Foundry test"""
from flask import Flask, jsonify, abort
import json
import os
import ibm_db

app = Flask(__name__)

if 'VCAP_SERVICES' in os.environ:
    db2info = json.loads(os.environ['VCAP_SERVICES'])['dashDB'][0]  
    db2cred = db2info["credentials"]  
   
db2conn = ibm_db.connect("DATABASE="+db2cred['db']+";HOSTNAME="+db2cred['hostname']+";PORT="+str(db2cred['port'])+";UID="+db2cred['username']+";PWD="+db2cred['password']+";","","")  

@app.route('/')
def index():  
   page = '<title>Property Statistics Database</title>'  
   page += '<h1>Welcome to IBM Watson Tax Advisor Property Statistics Database</h1>'  
   if db2conn:  
    # we have a DB2 connection, so obtain system information via ENV_SYS_INFO:  
    stmt = ibm_db.exec_immediate(db2conn,"select host_name,os_name,os_version,total_cpus,configured_cpus, total_memory,os_kernel_version,os_arch_type, os_release,os_full_version from sysibmadm.env_sys_info")  
    # fetch the result  
    result = ibm_db.fetch_assoc(stmt)  
    print 'result:', result
    page += "OS Name: "+result["OS_NAME"]+"<br/>OS Version: "+result["OS_VERSION"]   
    print 'OS Name ok'
    page += "<br/>Hostname: "+result["HOST_NAME"]+"<br/> Total CPUs: "+str(result["TOTAL_CPUS"])  
    page += "<br/>Configured CPUs: "+str(result["CONFIGURED_CPUS"])+"<br/>Total memory: "+str(result["TOTAL_MEMORY"])+" MB"  
    page += "<br/>OS Kernel Version: "+result["OS_KERNEL_VERSION"]+"<br/>OS Architecture Tpye: "+result["OS_ARCH_TYPE"]  
    page += "<br/>OS Release: "+result["OS_RELEASE"]+"<br/>OS full version: "+result["OS_FULL_VERSION"] 
    page += "<br/><br/>Author: Amy Lin"
    page += "<br/><br/>Project: Watson Tax Advisor"
    page += "<br/><br/>Release Date: 1 June 2016"
    
    page += "<br/><br/>Call '/v1/nz/property/location/locations' to get a list of locations with property price information available"
    page += "<br/><br/>Call '/v1/nz/rent/location/locations' to get a list of locations with rental price information available"
    page += "<br/><br/>Call '/v1/nz/sales/location/locations' to get a list of locations with sales price information available"
    
   return page 
   
def capitalise(location): # seperated by '%20' aka space
    location = location.split('%20')
    print 'location:', location
    cap_words = ''
    for word in location:
        print 'word', word
        word = word.capitalize()
        print 'cap word:', word
        cap_words += word
    return cap_words
    
@app.route('/v1/nz/property/location/<location_value>', methods=['GET'])
def property_price(location_value):
    j_dict = []
    location_value = location_value.replace('%20', ' ')
    
    query = "SELECT * FROM PROPERTY_INFO_TABLE WHERE AREA LIKE '%" + location_value + "%'"
    print query
    result = ibm_db.exec_immediate(db2conn, query)
    dictionary = ibm_db.fetch_assoc(result)

    if dictionary == False:
        abort(404)
    
    while dictionary != False:
        temp = {"Area": dictionary["AREA"], "Property Price": dictionary["AVERAGEVALUEAPRIL2016"], "Currency": "NZD"}
        j_dict.append(temp)
        dictionary = ibm_db.fetch_assoc(result)
    
    return (jsonify({'Search Result': j_dict}))
   
        
@app.route('/v1/nz/sales/location/<location_value>', methods=['GET'])
def sale_price(location_value):
    j_dict = []
    location_value = location_value.replace('%20', ' ')
    query = "SELECT * FROM SALES_INFO_TABLE WHERE SUBURB LIKE '%" + location_value + "%'"
    print query
    result = ibm_db.exec_immediate(db2conn, query)
    dictionary = ibm_db.fetch_assoc(result)

    if dictionary == False:
        abort(404)
            
    while dictionary != False:
        temp = {"Area": dictionary["SUBURB"], "Sales Price": dictionary["MEDIANSALEPRICE"], "Currency": "NZD"}
        j_dict.append(temp)
        dictionary = ibm_db.fetch_assoc(result)
   
    return (jsonify({'Search Result': j_dict}))
    
@app.route('/v1/nz/rent/location/<location_value>', methods=['GET'])
def rent_price(location_value):
    j_dict = []
    print 'b4:', location_value
    location_value = location_value.replace('%20', ' ')
    location_value = location_value.title()
    print 'after:', location_value
    query = "SELECT * FROM RENT_INFO_TABLE WHERE SUBURBS LIKE '%" + location_value + "%'"
    print query
    result = ibm_db.exec_immediate(db2conn, query)
    dictionary = ibm_db.fetch_assoc(result)

    if dictionary == False:
        abort(404)
    
    while dictionary != False:
        temp = {"Area": dictionary["SUBURBS"], "Sales Price": dictionary["MEDIANRENT"], "Currency": "NZD"}
        j_dict.append(temp)
        dictionary = ibm_db.fetch_assoc(result)
   
    return (jsonify({'Search Result': j_dict}))
     
@app.route('/v1/nz/property/location/locations')
def property_locations():  
   page = '<title>IBM Watson Tax Advisor Property Statistics Database</title>'  
   page += '<h1>Property Statistics Database</h1>'
   page += '<br/>Property Value'
   
   page += "<br/><br/>Author: Amy Lin"
   page += "<br/><br/>Project: Watson Tax Advisor"
   page += "<br/><br/>Release Date: 1 June 2016"
   page += "<br/><br/>List of locations:"
    
   query = "SELECT AREA FROM PROPERTY_INFO_TABLE"
   result = ibm_db.exec_immediate(db2conn, query)
   dictionary = ibm_db.fetch_assoc(result)
        
   while dictionary != False:
       location = "<br/>" + dictionary["AREA"]
       page += location
       dictionary = ibm_db.fetch_assoc(result)
    
   page += "<br/><br/>Call '/v1/nz/property/location/location name' to get the property price of the location"
   return page 
  
@app.route('/v1/nz/rent/location/locations')
def rent_locations():  
   page = '<title>IBM Watson Tax Advisor Property Statistics Database</title>'  
   page += '<h1>Property Statistics Database</h1>'
   page += '<br/>Property Rental Price' 
   
   page += "<br/><br/>Author: Amy Lin"
   page += "<br/><br/>Project: Watson Tax Advisor"
   page += "<br/><br/>Release Date: 1 June 2016"
   page += "<br/><br/>List of locations:"
    
   query = "SELECT SUBURBS FROM RENT_INFO_TABLE"
   result = ibm_db.exec_immediate(db2conn, query)
   dictionary = ibm_db.fetch_assoc(result)
        
   while dictionary != False:
       location = "<br/>" + dictionary["SUBURBS"]
       page += location
       dictionary = ibm_db.fetch_assoc(result)
    
   page += "<br/><br/>Call '/v1/nz/rent/location/location name' to get the weekly rent of the location"
   return page 
  
@app.route('/v1/nz/sales/location/locations')
def sales_locations():  
   page = '<title>IBM Watson Tax Advisor Property Statistics Database</title>'  
   page += '<h1>Property Statistics Database</h1>'
   page += '<br/>Property Sales Price'
   
   page += "<br/><br/>Author: Amy Lin"
   page += "<br/><br/>Project: Watson Tax Advisor"
   page += "<br/><br/>Release Date: 1 June 2016"
   page += "<br/><br/>List of locations:"
    
   query = "SELECT SUBURB FROM SALES_INFO_TABLE"
   result = ibm_db.exec_immediate(db2conn, query)
   dictionary = ibm_db.fetch_assoc(result)
        
   while dictionary != False:
       location = "<br/>" + dictionary["SUBURB"]
       page += location
       dictionary = ibm_db.fetch_assoc(result)
    
   page += "<br/><br/>Call '/v1/nz/sales/location/location name' to get the sales price of the location"
   return page 
    
# On Bluemix, get the port number from the environment variable VCAP_APP_PORT
# When running this app on the local machine, default the port to 8080
port = int(os.getenv('VCAP_APP_PORT', 8080))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port)
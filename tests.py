from datetime import timedelta
from datetime import datetime

account=""
username=""
password=""

import requests
try:
    url="https://api.kansasgasservice.com/api/login"
    data = '{"email":"' + username + '","password":"' + password + '","auditInfo":{"csrId":null,"isCSR":false,"registeredUsername":"' + username + '","ldcProvider":"KGS","isApp":false,"isMobile":false,"isWeb":false},"culture":"en-US"}'
    headers = {
      'Accept': '*/*',
      'Content-Type': 'application/json',
      'Host': 'api.kansasgasservice.com',
      'Origin': 'https://www.kansasgasservice.com',
      'Referer': 'https://www.kansasgasservice.com/',
      'Content-Length': str(len(data)),
      'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0.1; Nexus 10 Build/MOB31T) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36',
      'Accept-Language': 'en-US,en;q=0.9'
    }

    r = requests.Session()
    loginData = r.post(url, data=data, headers=headers, verify=True)
    #grab data

    if (loginData):
      accessToken = (loginData.json())['accessToken']
      
      if (len(accessToken) > 0 ):
          
          if (len(account) > 5):
            print("Account number from config")
            billingAccountNumber = account
          else:
            print("Account number primary from account")
            billingAccountNumber = (loginData.json())['registeredUser']['userInfo']['billingAccounts'][0]['billingAccountNumber']
    
          if ((loginData.json())['registeredUser']['userInfo']['billingAccounts']):
            
              #get account summary
              url = "https://api.kansasgasservice.com/api/getaccountsummary"
              data = '{"billingAccountNumber":"' + billingAccountNumber + '","auditInfo":{"csrId":null,"isCSR":false,"registeredUsername":"' + username + '","ldcProvider":"KGS","isApp":false,"isMobile":true,"isWeb":false}}'
              headers = {
                'Accept': '*/*',
                'Content-Type': 'application/json',
                'Host': 'api.kansasgasservice.com',
                'Origin': 'https://www.kansasgasservice.com',
                'Referer': 'https://www.kansasgasservice.com/',
                'Content-Length': str(len(data)),
                'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0.1; Nexus 10 Build/MOB31T) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36',
                'Accept-Language': 'en-US,en;q=0.9',
                'Authorization-Token': accessToken
              }

              r = requests.Session()
              loginData = r.post(url, data=data, headers=headers, verify=True)
              
              print("Status: " + loginData.json()['accountStatus'])
              print("Credit Rating: " + loginData.json()['creditRating'])
              print("Consumption: " + str(loginData.json()['services'][0]['consumption']))
              print("Address: " + loginData.json()['serviceAddress']['streetAddress1'])
              date_time = datetime.strptime(loginData.json()['lastPaymentDate'].split("T")[0], "%Y-%m-%d")
              print("Last Payment Date: " + str(date_time.strftime("%m/%d/%y")))    
              print("Last Payment: " + str(loginData.json()['lastPaymentAmount']))
              print("Ammount Due: " + str(loginData.json()['currentBill']['amountDue']))
              print("Past Due: " + str(loginData.json()['currentBill']['amountPastDue']))
              date_time = datetime.strptime(loginData.json()['currentBill']['dueDate'].split("T")[0], "%Y-%m-%d")
              print("Due Date: " + str(date_time.strftime("%m/%d/%y")))
              
    else:
     print("Cannot get Billing Account Number")

except Exception as err:
  print(err)

import logging

from datetime import timedelta
from datetime import datetime
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.util import Throttle

REQUIREMENTS = ['requests']

CONF_USERNAME="username"
CONF_PASSWORD="password"
CONF_ACCOUNT_NUM="account"

ICON = 'mdi:gas-cylinder'

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(hours=12)

def setup_platform(hass, config, add_entities, discovery_info=None):
    username = str(config.get(CONF_USERNAME))
    password = str(config.get(CONF_PASSWORD))
    account = str(config.get(CONF_ACCOUNT_NUM))
    add_entities([
	  ks_gas_sensor(username=username, password=password, account=account, getattribute="Status", interval=SCAN_INTERVAL),
      ks_gas_sensor(username=username, password=password, account=account, getattribute="Credit Rating", interval=SCAN_INTERVAL),
      ks_gas_sensor(username=username, password=password, account=account, getattribute="Consumption", interval=SCAN_INTERVAL),
      ks_gas_sensor(username=username, password=password, account=account, getattribute="Address", interval=SCAN_INTERVAL),
      ks_gas_sensor(username=username, password=password, account=account, getattribute="Last Payment Date", interval=SCAN_INTERVAL),
      ks_gas_sensor(username=username, password=password, account=account, getattribute="Last Payment", interval=SCAN_INTERVAL),
      ks_gas_sensor(username=username, password=password, account=account, getattribute="Ammount Due", interval=SCAN_INTERVAL),
      ks_gas_sensor(username=username, password=password, account=account, getattribute="Due Date", interval=SCAN_INTERVAL),
      ks_gas_sensor(username=username, password=password, account=account, getattribute="Past Due", interval=SCAN_INTERVAL)
	], True) 


class ks_gas_sensor(Entity):
    def __init__(self, username, password, account, getattribute, interval):
        self._username = username
        self._password = password
        self._account = account
        self._getattribute = getattribute
        self.update = Throttle(interval)(self._update)

    def _update(self):
        import requests
        try:
            url="https://api.kansasgasservice.com/api/login"
            data = '{"email":"' + self._username + '","password":"' + self._password + '","auditInfo":{"csrId":null,"isCSR":false,"registeredUsername":"' + self._username + '","ldcProvider":"KGS","isApp":false,"isMobile":false,"isWeb":false},"culture":"en-US"}'
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
            
            if (loginData):
                #grab data
                accessToken = (loginData.json())['accessToken']
                
                if (len(accessToken) > 0 ):
                
                    if (len(self._account) > 5):
                        billingAccountNumber = self._account
                    else:
                        #pull first account number on account
                        billingAccountNumber = (loginData.json())['registeredUser']['userInfo']['billingAccounts'][0]['billingAccountNumber']
                        
                    #get account summery
                    url = "https://api.kansasgasservice.com/api/getaccountsummary"
                    data = '{"billingAccountNumber":"' + billingAccountNumber + '","auditInfo":{"csrId":null,"isCSR":false,"registeredUsername":"' + self._username + '","ldcProvider":"KGS","isApp":false,"isMobile":true,"isWeb":false}}'
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
                    if (loginData):      
                        if self._getattribute=="Status":
                          self._state = (loginData.json())['accountStatus']
                        if self._getattribute=="Credit Rating":
                          self._state = (loginData.json())['creditRating']
                        if self._getattribute=="Consumption":
                          self._state = str((loginData.json())['services'][0]['consumption'])
                        if self._getattribute=="Address":
                          self._state = str((loginData.json())['serviceAddress']['streetAddress1'])
                        if self._getattribute=="Last Payment Date":
                          date_time = datetime.strptime(loginData.json()['lastPaymentDate'].split("T")[0], "%Y-%m-%d")
                          self._state = str(date_time.strftime("%m/%d/%y"))
                        if self._getattribute=="Last Payment":
                          self._state = str((loginData.json())['lastPaymentAmount'])
                        if self._getattribute=="Amount Due":
                          self._state = str((loginData.json())['currentBill']['amountDue'])                          
                        if self._getattribute=="Due Date":
                          date_time = datetime.strptime(loginData.json()['currentBill']['dueDate'].split("T")[0], "%Y-%m-%d")
                          self._state = str(date_time.strftime("%m/%d/%y"))
                        if self._getattribute=="Past Due":
                          self._state = str((loginData.json())['currentBill']['amountPastDue'])
                    else:
                      self._state = "Unknown"
                      
                    self._attributes = {}
                    self._attributes['last_update'] = datetime.now()
                else:
                  _LOGGER.error("Error getting account login token.")
            else:
              _LOGGER.error("Error logging in.")
              
        except Exception as err:
            _LOGGER.error(err)


    @property
    def name(self):
        name = "KS Gas " + self._getattribute
        return name

    @property
    def state(self):
        return self._state

    @property
    def icon(self):
        return ICON

    @property
    def device_state_attributes(self):
        """Return the attributes of the sensor."""
        return self._attributes

    @property
    def should_poll(self):
        """Return the polling requirement for this sensor."""
        return True


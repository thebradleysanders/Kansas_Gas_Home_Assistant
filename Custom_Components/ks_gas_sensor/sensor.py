import logging

from datetime import timedelta
from datetime import datetime
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.util import Throttle

REQUIREMENTS = ['requests']

CONF_USERNAME="username"
CONF_PASSWORD="password"

ICON = 'mdi:gas-cylinder'

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(hours=12)

def setup_platform(hass, config, add_entities, discovery_info=None):
    username = str(config.get(CONF_USERNAME))
    password = str(config.get(CONF_PASSWORD))
    add_entities([
	  ks_gas_sensor(username=username, password=password, getattribute="status", interval=SCAN_INTERVAL),
      ks_gas_sensor(username=username, password=password, getattribute="lastpayment", interval=SCAN_INTERVAL),
      ks_gas_sensor(username=username, password=password, getattribute="creditRating", interval=SCAN_INTERVAL),
      ks_gas_sensor(username=username, password=password, getattribute="dueDate", interval=SCAN_INTERVAL),
      ks_gas_sensor(username=username, password=password, getattribute="consumption", interval=SCAN_INTERVAL),
      ks_gas_sensor(username=username, password=password, getattribute="address", interval=SCAN_INTERVAL)
	], True) 


class ks_gas_sensor(Entity):
    def __init__(self, username, password, getattribute, interval):
        self._username = username
        self._password = password
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
            #grab data
            accessToken = (loginData.json())['accessToken']
            billingAccountNumber = (loginData.json())['registeredUser']['userInfo']['billingAccounts'][1]['billingAccountNumber']


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

            if self._getattribute=="status":
              self._state = (loginData.json())['accountStatus']
            if self._getattribute=="lastpayment":
              self._state = (loginData.json())['lastPaymentAmount']
            if self._getattribute=="creditRating":
              self._state = (loginData.json())['creditRating']
            if self._getattribute=="dueDate":
              self._state = (loginData.json())['currentBill']['dueDate']
            if self._getattribute=="consumption":
              self._state = (loginData.json())['services'][0]['consumption']
            if self._getattribute=="address":
              self._state = (loginData.json())['serviceAddress']['streetAddress1']
			
   
            self._attributes = {}
            self._attributes['last_update'] = datetime.now()
        except Exception as err:
            _LOGGER.error(err)


    @property
    def name(self):
        name = "ks_gas_sensor_" +  self._getattribute
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


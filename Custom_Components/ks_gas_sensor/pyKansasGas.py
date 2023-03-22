from aiohttp import ClientSession, client_exceptions

KSGAS_CONST = {
        "proto": "https",
        "remote_host": "api.kansasgasservice.com",
        "endpoint": "api"
}


class Client:

    """
    Returns a string: URL(host, endpoint, resource)
    """
    def url(self, config, resource) -> str:
        return "%s://%s/%s/%s" % (config["proto"], config["remote_host"], config["endpoint"], resource)


    """
    Returns default headers as understood by the Kansas Gas API
    Not invoked when retrieving a token.
    """
    def headers(self, config, token):
        return {
            "Host": config['remote_host'],
            "Content-Type": "application/json",
            "Connection": "keep-alive",
            "Accept": "application/json",
            "Accept-Language": "en",
            "Accept-Encoding": "br, gzip, deflate",
            "User-Agent": "Winston/3.9.0 (iPhone; iOS 13.5; Build:2399; Scale/3.0)",
            "Authorization-Token": "%s" % token
    }

    """
    Performs AIO request. Covers all verbs.
    Returns json payload.
    Raises exception if received http error code.
    """
    async def request(
            self,
            config,
            method: str,
            resource: str,
            headers: dict = None,
            json: dict = None,
            ) -> dict:
        if not headers:
            headers = {}

        async with self._websession.request(
                method,
                self.url(config, resource),
                headers=headers,
                json=json) as r:
            r.raise_for_status()
            return await r.json(encoding='UTF-8')


    """
    Helper to retrieve a single resource, such as '/getaccountsummary'
    """
    async def get_resource(self, config, token, resource):
        return await self.request(
                config,
                method='post',
                resource=resource,
                headers=self.headers(config, token)
                json={
                    "auditInfo": {
                        "appVersion": "65f2a17a",
                        "csrId": null,
                        "isCSR": false,
                        "registeredUsername": self._username,
                        "ldcProvider": "KGS",
                        "sessionId": "",
                        "isApp": false,
                        "isMobile": false,
                        "isWeb": false
                    },
                    "ldcProvider": "KGS",
                    "culture": "en-US",
                    "billingAccountNumber": self._accountNumber
                })


    """
    Attempts login with credentials provided in init()
    Returns authorization token for future requests.
    """
    async def login(self, config) -> str:
        return (await self.request(
                config,
                method='post',
                resource='login',
                json={
                    "auditInfo": {
                        "appVersion": "65f2a17a",
                        "csrId": null,
                        "isCSR": false,
                        "ldcProvider": "KGS",
                        "sessionId": "",
                        "isApp": false,
                        "isMobile": false,
                        "isWeb": false
                    },
                    "ldcProvider": "KGS",
                    "culture": "en-US",
                    "email": self._username,
                    "password": self._password
                }))

    async def get_accountsummary(self):
        return await self.get_resource(self._config, self._token, 'getaccountsummary')

    async def get_disconnectnotices(self):
        return await self.get_resource(self._config, self._token, 'getdisconnectnotices')

    async def get_usagehistory(self):
        return await self.get_resource(self._config, self._token, 'getusagehistory')
      
    async def get_paymenthistory(self):
        return await self.get_resource(self._config, self._token, 'getpaymenthistory')
      
     async def get_statements(self):
        return await self.get_resource(self._config, self._token, 'getstatements')
      
      async def get_BillingHistory(self):
        return await self.get_resource(self._config, self._token, 'getBillingHistory')


    async def async_init(self, ksgas_const = KSGAS_CONST) -> None:
        self._config = ksgas_const
        if self._token is None:
            loginData = await self.login(self._config)
            self._token = loginData['accessToken']
            self._accountNumber = loginData['registeredUser']['userInfo']['defaultAccountNumber']
        
    def __init__(
            self,
            username: str,
            password: str,
            websession: ClientSession
            ) -> None:
        self._config = None
        self._token = None
        self._username = username
        self._password = password
        self._accountNumber = None
        self._websession = websession

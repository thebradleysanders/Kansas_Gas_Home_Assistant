 <h1 style="color:#ff0000">This integration is currently not working due to security improvments from KS Gas</h1>

## Kansas Gas Sensor For Home Assistant

```yaml
sensor:
  - platform: ks_gas_sensor
    username: !secret ks_gas_username
    password: !secret ks_gas_password
    account: 12345678 (optional)	
```

#### Supported Sensors:
   * Status
   * Credit Rating
   * Consumption
   * Address
   * Last Payment Date
   * Last Payment
   * Ammount Due
   * Due Date
   * Past Due

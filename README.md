Kansas Gas Sensor For Home Assistant

```yaml
sensor:
  - platform: ks_gas_sensor
    username: !secret ks_gas_username
    password: !secret ks_gas_password
    account (optional): 12345678
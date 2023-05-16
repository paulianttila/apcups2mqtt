# apcups2mqtt

Simple modbus TCP client to monitor APC UPS and forward values to MQTT broker.
Support APC UPS, which have network connector and modbus support.
Application supports only read operations.
Tested with SMT1500IC, but should support SMX/SMT, SRT and SURTD models.

Available UPS variables can vary per UPS model.

Run multiple docker container instances if information need to be fetched from multiple UPS devices.

## Environament variables

See common environment variables from [MQTT-Framework](https://github.com/paulianttila/MQTT-Framework).

| **Variable**               | **Default** | **Descrition**                                                                                                |
|----------------------------|-------------|---------------------------------------------------------------------------------------------------------------|
| CFG_APP_NAME               | apcups2mqtt | Name of the app.                                                                                              |
| CFG_APC_HOST               | None        | APC UPS to connect.                                                                                           |
| CFG_APC_PORT               | 502         | TCP port to connect.                                                                                          |
| CFG_CACHE_TIME             | 300         | Cache time in seconds for UPS values. During cache time, values are only updeted to MQTT if value changed.    |

## Example docker-compose.yaml

```yaml
version: "3.5"

services:
  apcups2mqtt:
    container_name: apcups2mqtt
    image: paulianttila/apcups2mqtt:1.0.0
    restart: unless-stopped
    environment:
      - CFG_LOG_LEVEL=DEBUG
      - CFG_MQTT_BROKER_URL=127.0.0.1
      - CFG_MQTT_BROKER_PORT=1883
      - CFG_APC_HOST=192.168.10.2
      - CFG_CACHE_TIME=300
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/healthy"]
      interval: 60s
      timeout: 3s
      start_period: 5s
      retries: 3
 ```
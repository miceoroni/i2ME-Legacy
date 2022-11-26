# i2RecordCollector
This software handles data collection and processing for The Weather Channel's IntelliStar 2 software using a mix of TWC's v1, v2, and v3 APIs. 

# Requirements
* Firewall on the stock I2 image fixed to allow incoming connections from ``224.1.1.77`` on ports ``7787`` and ``7788``
* [Python 3.8.0](https://www.python.org/downloads/release/python-380/)

## Records
- [x] ADRecord - Airport Delays
- [x] BERecord - Alerts
- [ ] ClimatologyRecord - Record highs/lows
- [x] DDRecord - Daypart Forecast
- [x] DFRecord - Daily Forecast (7 Day Forecast)
- [x] ESRecord - Air Quality
- [x] IDRecord - Pollen
- [x] MORecord - Current Conditions
- [x] TIRecord - Tides
- [ ] TFRecord - Traffic Flow
- [ ] TNRecord - Traffic Incidents
- [ ] WMRecord - Marine Forecast

# Usage instructions
[Download a release](https://github.com/the5dcrew/i2MessageEncoder-Rewrite/releases) for the most stable version, or clone the repository.

``git clone https://github.com/opentelecom/i2MessageEncoder-Rewrite``

*(If downloading this as a zip, extract to the directory of your choosing.)*

Install the requirements in ``requirements.txt``

``py -3 -m pip install -r requirements.txt``

Drop your IntelliStar 2's ``MachineProductCfg.xml`` file into the root of the directory of the encoder, then run ``main.py``. 

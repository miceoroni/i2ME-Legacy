<p align="center">
    <img src="https://cdn.discordapp.com/attachments/1035585006724194311/1046646391730077736/opentelecom2k_blue_clean.png">
</p> 

<h1 align="center"><strong>IntelliStar 2 Data Collector</strong></h1>
<style>img {width: 80%}</style>


# Requirements
* Properly set up interface for UDP.
* [Python 3.8.0](https://www.python.org/downloads/release/python-380/)

## Completed Records
- [X] Aches and Pains
- [X] Air Quality
- [X] Airport Delays + National Airport delays
- [X] Alerts *(BERecord)*
- [X] Breathing
- [X] Current Conditions
- [X] Daily Forecasts
- [X] Hourly Forecasts
- [X] Heating and Cooling
- [X] Mosquito Activity
- [X] Pollen Forecasts
- [X] Tide Station Forecasts
- [X] Watering Needs
- [] Marine Forecasts
- [] Traffic Forecasts **(API access missing)**

# Usage instructions
1) Ensure that [Python 3.8 is installed](https://www.python.org/downloads/release/python-380/).
2) [Download a release](https://github.com/Open-Telecom/i2MessageEncoder-Rewrite/releases/tag/v2.0.2), and unzip to the wanted directory.
3) Use command prompt to enter the directory of the scripts, then install package requirements:<br/>
```py -3 -m pip install -r requirements.txt``` <br/>
4) Drop your unit's **MachineProductConfiguration.xml** file into the root of the script
5) Run ``main.py``

### Attributions & Disclaimers
Air Quality reports are powered by Copernicus Atmosphere Monitoring Service Information 2022.
Neither the European Commission nor ECMWF is responsible for any use that may be made of the Copernicus Information or Data it contains.

### Copyright Notice

Copyright © 2022 OpenTelecom

The i2DataCollector project cannot be copied/distributed without the express permission of the OpenTelecom group.
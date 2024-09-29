# NFL Football Data Collection

## Overview

## Design

## Usage

### Application

#### Local
`$ make start`

`$ make logs`

`$ make stop`


#### API Docs
`http://127.0.0.1:8000/docs`
#### Queue UI
`http://localhost:15672`
### CLI

#### Discover


`$ python3 nfl_data.py discover --type=positions`


#### Collect

`$ python3 nfl_data.py collect --type=positions`

#### Export

`$ python3 nfl_data.py export --type=positions --filename=<...>`

### OLD
Data Types:
* All (all) - 
* Player Positions (positions) - 
* NFL Teams (teams) - 
* Players (players) -
* Games (games) - 

```
$ nfl_data discover --type=<Data Type> --start=<Start Year> --end=<End Year>
```

```
$ nfl_data collect --type=<Data Type> --start=<Start Year> --end=<End Year>
```

```
nfl_data export --type=<Data Type> --dir=<Desitnation directory>
```
## Development

## TODO
* Is there a use case for --force?
* Spinner
* Log statements
* contsants
* push button run
* Add discover mode to make idepodent?
* add exports?
* exception handling
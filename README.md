# NFL Football Data Collection

## 1.0 Overview
This project collects NFL data that can be used for machine learning algorithm training.  The data is collected from ESPN apis documented by the following [GitHub repo](https://gist.github.com/nntrn/ee26cb2a0716de0947a0a4e9a157bc1c).  Since there are multiple types of data and many years of data this project provides an asynchronous and idempotent solution for data collection to streamline this process.
The NFL Football Data collection application will start a REST api to take requests and tasks to a queue.  From there various backend processes will pull from the queue to perform the data collection tasks.  Users of this project will be able to do the following:
* **Discover** data records for supported data types.
* **Collect** data records for supported data types.
* **Export** data records in a csv file.

### 1.1 Supported Data Types
The following data types are currently supported:
#### 1.1.1 Positions
NFL Player positions including the following features:

* **id** - Player positions unique identifier (e.g., 1)
* **name** - Player position name (e.g. Wide Receiver)
* **abbreviation** - Short representation of the player position name (WR)

#### 1.1.2 Teams
NFL Team data including the following features:

* **id** - NFL team unique identifier (e.g, 20)
* **name** - NFL Team name (e.g., New York Jets)
* **location** - NFL Team location (e.g., New York)
* **abbreviation** - Short representation of the team name (e.g., NYJ)

#### 1.1.3 Players
NFL Player data including the following features:

* **id** - NFL player's unique identifier (e.g., 3134666)
* **name** - NFL player's first and last name (e.g., Brian Allen)
* **weight** - NFL player's weight in pounds (e.g., 303.0)
* **height** - NFL player's height in inches (e.g. 74.0)
* **experience** - Years of experience (e.g, 6)
* **active** - NFL player's active status (e.g., True)
* **status** - NFL player's current status (e.g., FA)
* **position** - NFL player's position ID (e.g., 4)
* **age** - NFL player's current age (e.g., 28)
* **team** - The team ID the player plays on (e.g., 5)

#### 1.1.4 Games
_Coming Soon..._

## 2.0 Design

_Coming Soon..._

## 3.0 Usage
There are two parts of this project the application and the CLI.  
1. The application is a python based REST API that acts as the front door for recording user requests with back processes that carry out the desired user request.  
2. The CLI is a convenient way to interact with the backend application from a command line terminal.

### 3.1 Application
There are two methods for deploying the application a local deployment on your laptop and a remote deployment in a Cloud.  It should be noted that both methods will be accessible from the local CLI.
#### 3.1.1 Local
Docker (TODO REF) must be installed to build and run the project locally using docker compose.

The user can **start the application** locally with docker compose using the following:

`$ make start`

Once the application is running you can view the API documentation through the following URL:

[API Documentation](http://127.0.0.1:8000/docs)

If required, the RabbitMQ dashboard can be viewed at:

[Queue Dashboard](http://localhost:15672)

The above command will start the application as a background process.  If you would like to **view logs** please run:

`$ make logs`

Finally, to **stop the application** run:

`$ make stop`

#### 3.1.2 Cloud

_Coming soon..._


### 3.2 CLI
 _TODO overview of CLI structure_

_TODO Installation_

`$  nfl_data.py {all,discover,collect,export,status} --data_type {all,positions,teams,players} [--start START] [--end END] [--dest DEST] [--wait] [-h]`
#### 3.2.1 All

`$ python3 nfl_data.py all --data_type=<all|positions|teams|players> --dest=<directory path> [--wait]`

#### 3.2.2 Discover
`$ python3 nfl_data.py discover --data_type=<all|positions|players> [--wait]`

`$ python3 nfl_data.py discover --data_type=teams --start=<Starting Year> --end=<Ending Year> [--wait]`


#### 3.2.3 Collect
`$ python3 nfl_data.py collect --data_type=<all|positions|teams|players> [--wait]`

#### 3.2.4 Export
`$ python3 nfl_data.py export --data_type=<all|positions|teams|players> --dest=<directory path> [--wait]`


## 4.0 Development
_Coming soon..._

## 5.0 References

* [1] - https://gist.github.com/nntrn/ee26cb2a0716de0947a0a4e9a157bc1c
## Monitoring and Analysis of the Bid-Ask Spread for MXN_BTC and USD_MXN

### Project Objective

The goal of this project is to develop an automated system to monitor and analyze the bid-ask spread for the currency pairs MXN_BTC and USD_MXN in real-time. This system will enable the "Markets" team to perform custom analyses of the spread.

The system will handle the following tasks:

1. **Data Collection:** Retrieve the order books for the MXN_BTC and USD_MXN pairs every second.
2. **Value Extraction:** Extract the necessary bid-ask spread values for analysis.
3. **Data Storage:** Save observations into a file every 10 minutes, totaling 600 records per file.
4. **Data Partitioning:** Store the files in the data lake using defined partitions to facilitate access and subsequent analysis.


## Technologies Used

- **Docker**: For containerization and management of development environments.
- **Python**: For data processing and transformation.
- **PostgreSQL**: As the database for storing and managing processed data.
- **pgAdmin**: For administration and management of the PostgreSQL database.
- **Airflow**: For orchestration and managment partition process.
- **Spark**: For data partition.


## Relevant

### Data Partitioning

I chose to partition the data by date. The reason for this decision is to enable the team to receive alerts and, depending on the alert, query the data within a specific time window. The data is partitioned by:

- Year
- Month
- Day
- Hour
- Minute

This approach provides more granularity when querying the data.

To see the data partitioning, you can check the folder:
`s3_datalake/spread_books_partitioned`

There is an additional folder that contains the data collected every 10 minutes, resulting in 600 records per file:
`s3_datalake/spread_book_20240712203433_20240712202433.csv`


### Project Architecture

The project architecture is based on 5 interconnected containers, all working together to handle the entire data processing workflow.

**Python Script Request Data:**
This container is isolated and its sole task is to generate requests and send data to the webhook every second.

**Webhook:**
The webhook is responsible for receiving the information and passing it to the database in the correct format.

**Database:**
The database is configured in another container and continuously receives requests.

**pgAdmin:**
pgAdmin manages the database through a user interface.

**Airflow and Spark:**
These two services run in the same container. Airflow is responsible for orchestrating the data partitioning DAG every 10 minutes, while Spark retrieves the data from PostgreSQL and partitions it.


The following image shows a diagram of the architecture:
![diagrama bitsorepo](https://github.com/user-attachments/assets/6bd8f546-9ed9-465b-a1d8-2871d3ec750b)




## Prerequisites

- Docker and Docker Compose installed on your machine.
- Python 3.8 or higher.
- Git to clone the repository.


## Installation Instructions

1. Clone the repository:

   ```bash
   git clone https://github.com/isaycast/monitor-bids-asks-bitso.git
   cd tu_repositorio
   ```
2. Environment Variables

Set the following environment variables for the project:

```bash
API_KEY=<your_api_key>
API_SECRET=<your_api_secret>
BASE_API_URL=<your_base_api_url>
WEBHOOK_URL=<your_webhook_url>
HTTP_METHOD=<your_http_method>
REQUEST_PATH=<your_request_path>
REQUESTED_BOOKS=<your_requested_books> string separed by commas usd_mxn,btc_mxn
DB_HOST=<your_db_host>
DB_NAME=<your_db_name>
DB_USER=<your_db_user>
DB_PASSWORD=<your_db_password>
PGADMIN_DEFAULT_EMAIL=<your_pgadmin_email>
PGADMIN_DEFAULT_PASSWORD=<your_pgadmin_password>
```
The application is prepared to receive and make requests to more than one book. For this, you need a Bitso verification token to allow more than 60 calls per minute.


## Usage Instructions
To use the project, you have the following options:

1. Using Docker Compose:
    You can start all services using Docker Compose. To do this, run the following command in your terminal:

    ```bash
    docker-compose build
    docker-compose up
    ```

    You can add the `-d` flag to run the containers in the background if you do not wish to see the logs:

    ```bash
    docker-compose build
    docker-compose up -d
    ```


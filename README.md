# FPL Classic League Data Pipeline

## Overview
This project utilises the FPL API endpoints to extract player and manager data for a specified Invitational Classic League. This data is then visualised and showcased on my Dash web app: [www.fpldashboard.com](http://www.fpldashboard.com/)


*   Provisison required GCP cloud infrastructure using Terraform. 
*   Docker-compose is used to run a multi-container Dagster deployment which orchestrates the whole data pipeline.
*   A sensor checks if a gameweek has been completed - If it has then successful the data pipeline is initiated for the recently completed gameweek.
*   Data is extracted using the FPL API endpoints and loaded into a GCS bucket as Parquet files.
*   Parquet files are loaded into BigQuery Tables for ad-hoc analysis,scheduled queries and visualisation using Looker Studio (Optional).
*   Pre-defined queries are run on BigQuery tables and the contents stored once again in GCS to service Dash web app.



## Pipeline functionality


1.   Run terraform to deploy Google VM, and other GCP services and initiate docker deployment using  a start-up script.
2.   Four docker containers are created for the deployment of Dagster.
    * Postgres - Used for Dagster storage such as event logs and sensor ticks.
    * User code - Location of your code to enable easy redeployment of code changes.
    * Dagster daemon - Long running process which runs the sensors and queues asset materialization. 
    * Dagit - Dagster's UI to manually inspect pipeline and run backfills.
3. Sensor runs every 12 hours checking if a new gameweek has been completed. If so, a new partition is added corresponding to the gameweek and the extraction is initiatied for the given partition.
4. Gameweek data such as player stats and manager picks are extracted,transformed and loaded into a GCS bucket.
5. Data is loaded from the bucket into three BigQuery tables:
    * player_gameweek - Stats for all players in the Premier League for all completed gameweeks.
    * manager_gameweek - Stats for all players picked by a manager in the specified invitational league for all completed gameweeks. Each row represents a player picked by a single manager in your specifed invitational league.
    * manager_gameweek_performance - Stats for all managers in the specified invitational league for each gameweek such as points gained in a gameweek.
6. Analytical queries are run using the three tables and output is saved to a Google Storage bucket.
7. Data is showcased via a Dash web app.



## Data Flow Diagram

![Data Flow Diagram](https://user-images.githubusercontent.com/99501368/241185212-53756a4a-d1a7-46ac-99f5-050e914822d3.jpg)

# Sidemen YouTube Channel Analytics

This project is a data pipeline that collects, transforms, and stores video statistics from the Sidemen YouTube channel using the YouTube Data API. The purpose of the project is to track and analyze the growth of the channel and performance of its videos over time.

## Project Overview

The idea is to pull video data (views, likes, comments, etc.) from the Sidemen channel every week, transform the raw API response into a structured format, and store it in a MongoDB database. Over time, this allows us to analyze trends, performance, and audience engagement across videos.

## Features

- Fetches up-to-date statistics from the Sidemen YouTube channel
- Extracts channel-level and video-level data using the YouTube Data API
- Transforms nested JSON into a flat, structured format
- Stores cleaned data in a MongoDB collection
- Designed to run as a weekly ETL job using Apache Airflow

## Tech Stack

- Python
- YouTube Data API v3
- MongoDB
- Apache Airflow (for scheduling)
- tqdm (for progress visualization)


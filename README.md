# Singlestore + Google BigQuery Demo

## Overview

This repository showcases a demo application integrating **Singlestore** and **Google BigQuery** to deliver both real-time and historical data analytics. The demo features:

- **Real-Time Data Ingestion**: Streaming data using Apache Kafka.
- **Real-Time Map Visualization**: A dynamic map powered by Singlestore that refreshes in real-time.
- **Real-Time Analytics**: Immediate data analysis using Singlestore.
- **Historical Analytics**: Deep-dive analytics on historical data stored in Google BigQuery.
- **LLM Function Integration**: A language model function that leverages data from both Singlestore and BigQuery, powered by **Gemini**.
- **Interactive UI Built with Gradio**: A user-friendly interface for data visualization and interaction.

## Table of Contents

- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Setup Instructions](#setup-instructions)
- [Usage](#usage)
- [Components](#components)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

## Architecture

![Architecture Diagram](architecture_diagram.png)

The system architecture comprises:

1. **Data Producers**: Simulated data sources sending real-time data to Kafka.
2. **Apache Kafka**: Serves as the data ingestion pipeline.
3. **Singlestore**: Stores and processes real-time data.
4. **Google BigQuery**: Stores historical data for in-depth analysis.
5. **Application Server**: Orchestrates data flow between components.
6. **Frontend Application (Gradio)**: Provides an interactive UI for data visualization.
7. **Gemini LLM**: Processes queries using data from both Singlestore and BigQuery.

## Prerequisites

Before you begin, ensure you have the following installed and configured:

- **SinglestoreDB**: [Installation Guide](https://docs.singlestore.com/managed-service/en/getting-started-with-singlestoredb-cloud.html)
- **Google BigQuery**: Access via a Google Cloud project
- **Apache Kafka**: [Download and Installation](https://kafka.apache.org/quickstart)
- **Python 3.8+**: For running the Gradio application
- **Docker**: For containerization (optional)
- **Google Cloud SDK**: For BigQuery interactions
- **Gemini API Access**: Credentials for Gemini LLM services
- **Git**: For cloning the repository
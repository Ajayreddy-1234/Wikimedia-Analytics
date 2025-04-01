# Wikimedia Trend Analytics Platform

[![License](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

A scalable analytics pipeline for processing 2.2B+ Wikimedia records to uncover user engagement patterns and content trends.

## 📌 Project Overview

**Objective:** Analyze Wikimedia's massive datasets (pageviews, geo-edits, mediacounts, unique devices) to:
- Track global editor engagement patterns
- Optimize content delivery through device usage trends
- Identify high-impact media categories using Commons metrics

**Key Datasets Processed:**
- `Commons Impact Metrics` (GLAM cultural heritage analysis)
- `GeoEditors` (country-level contributor tracking)
- `Mediacounts` (media file transfer analytics)
- `Unique Devices` (privacy-focused access trends)

## 🚀 Key Features

- **Scalable ETL Pipeline**  
  Processes 2TB+/day using PySpark on Hadoop cluster
- **Cloud-Optimized Infrastructure**  
  Jetstream2-powered Hadoop/Hive environment with Apache Tez acceleration
- **Interactive Analytics**  
  Streamlit dashboards with geospatial editing visualizations
- **Cost-Efficient Storage**  
  HDFS/Hive partitioning strategies for 2.2B+ monthly records

## 🛠️ Technologies Used

| Category              | Technologies                          |
|-----------------------|---------------------------------------|
| **Data Processing**   | PySpark, Hadoop, Hive, Apache Tez     |
| **Cloud Infrastructure** | Jetstream2, HDFS                   |
| **Visualization**     | Streamlit, PyHive, Matplotlib         |
| **Workflow**          | Linux, Bash, Jupyter, PyCharm         |

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- Hadoop 3.3.4
- Hive 3.1.2
- Jetstream2 cloud access

### Installation
- git clone https://github.com/Ajayreddy-1234/Wikimedia-Analytics.git
- cd Wikimedia-Analytics

### Install Python dependencies
- pip install -r requirements.txt

## Configure Hadoop/Hive (see configs/hadoop-setup-guide.md)

### Usage
- Sample PySpark ETL job
```
from pyspark.sql import SparkSession

spark = SparkSession.builder
.appName("WikimediaETL")
.enableHiveSupport()
.getOrCreate()

df = spark.read.format("csv").option("header", "true").load("hdfs:///raw/geoeditors")
df.write.format("parquet").saveAsTable("processed.geoeditors")
```


## 📊 Key Insights
- **Global Editor Distribution:** US leads with 25K+ monthly editors
- **Device Trends:** 43% mobile traffic, peaking at 2.2B devices (Oct 2024)
- **Content Strategy:** Spanish/French wikis show 8K+ active editors monthly

## 🤝 Contributing
1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📚 References
- [Wikimedia Dataset Documentation](https://wikitech.wikimedia.org/wiki/Analytics)
- [Jetstream2 Cloud Docs](https://jetstream-cloud.org/)

## 📄 License
Distributed under MIT License. See `LICENSE` for details.


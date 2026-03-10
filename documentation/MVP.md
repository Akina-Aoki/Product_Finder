# MVP – Company Inventory Events Platform

## Team Information

**Team Name:** Sportwear AB

**Members:**  
- Rikard  
- Aira  
- Samuel  
- Robin

**Product Owners:** Aira & Samuel  
**Scrum Master:** Rikard  
**Developers:** Aira, Samuel, Rikard, Robin

---

# Project Overview

## What is being built?

**Company Inventory Events Platform**

A system that tracks the movement of products across company inventory and records **purchase, inventory updates and restocking events**.

The platform enables the company to:

- Track product movement across inventory
- Monitor product sales activity
- Detect restocking events
- Analyze revenue performance of products
- Identify top and low performing container products

The system:

1. Collects source product data from **structured JSONL datasets**
2. Processes the data through an **ETL pipeline**
3. Stores the processed data in a **PostgreSQL database**
4. Uses **Kafka event streaming** to track inventory events such as:
   - Purchases
   - Restocking
   - Inventory updates

---

# Idea Evolution

Initially the team explored two different approaches.

## Idea 1 — Retail API Integration

The original concept was to integrate **e-commerce APIs from physical stores in Stockholm**.

However, this approach was abandoned because:

- Retailers require long approval times
- API access is not guaranteed
- The project timeframe is only **4 weeks**

## Idea 2 — Web Scraping

Web scraping was considered but deprioritized due to:

- Time constraints
- Maintenance complexity

## Final Decision

The team decided to:

- Generate a **realistic synthetic dataset** using tools such as **Mockaroo**
- Refactor and structure the dataset with **LLM assistance**

This approach allows the team to:

- Maintain full control of the **data schema**
- Simulate **real-world product datasets**
- Focus on implementing the **ETL pipeline and data platform**

---

# Minimum Viable Product (MVP)

## User Story
![User Story Diagram](../assets/User_Story_Version2.jpeg)

## Core Value of the Project

The core value of the project is to demonstrate that a company can **internally track and analyze inventory movements in near real-time using a data platform**.

Instead of relying on static reports or manual updates:

- Inventory events are **streamed through a data pipeline**
- Events include:
  - Product sales 
  - Restocking
  - Inventory updates

These events are:

1. Processed in the ETL pipeline
2. Stored in a structured database
3. Made available for monitoring and analytics.



---

# MVP Features

The MVP focuses on the **smallest usable system that managers can actually use**.

## 1. Track Product Movement

The system tracks product inventory data **events/topics** across events such as:

- Sales
- Updates
- Restocking

---

## 2. Detect Restocking Events

The system records when products are restocked and can answer questions like:

- Which products are frequently restocked?
- Which products sell out quickly?

---

## 3. Real-Time Inventory Updates

Inventory updates are processed through **Kafka event streaming**.

Streaming frequency may be simulated (for example):

- Every 0.5 seconds
- Every few minutes
- Or scheduled intervals

---

## 4. Monitor Sales Activity

Managers can view product performance such as:

- Sales activity
- Product demand
- Inventory turnover

---

## 5. Data for Analytics

The platform stores processed data in a **PostgreSQL database**.

This allows:

- Data analysts
- Business intelligence teams

to perform analysis using tools such as **PGAdmin or Supabase**.

---

## 6. Event Monitoring

The ETL pipeline performs:

- Data validation
- Data transformation
- Data cleaning

to ensure the data pipeline remains healthy.

---

## 7. Analyze Revenue Performance

Managers can analyze:

- Which products generate the most revenue
- Which products underperform

---

## 8. Identify Top and Low Performing Products

The system allows identification of:

- Top performing products
- Low performing products

This helps companies make better inventory decisions.

---

# What is NOT Included in the MVP

The following features are **out of scope** for the MVP:

- FastAPI interactive UI demonstrations
- Complex dashboards
- Forecasting models
- Predictive analytics
- Multi-store logistics
- Multiple cities or regions
- Integration with many retailers
- Real-time external APIs
- Product images

These features may be considered for **future iterations** of the platform.

---

# Tech Stack

The platform uses the following technologies:

### Python
- ETL orchestration
- Data ingestion and transformation
- Kafka producers and consumers

### PostgreSQL
- Stores cleaned product and inventory data
- Used for analytics queries

### Docker & Docker Compose
- Runs platform services in containers
- Ensures consistent deployment

### Apache Kafka
- Simulates real-time inventory updates
- Streams inventory events

### FastAPI / Postman / Thunder Client
- Used to test API endpoints and platform functionality

### Evidence Dashboard
- Displays processed data and inventory insights from the curated database.

---

# Libraries

- Pydantic  
- Psycopg3  
- Pandas  
- Numpy  
- FastAPI
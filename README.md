# Pflanze_app
# Crop Monitoring Application

## Overview
The Crop Monitoring Application is a mobile-based precision agriculture platform designed to support crop health assessment, early disease detection, and localized weather monitoring. The system integrates satellite remote sensing, computer vision, and AI-driven analysis into a unified application tailored for Indian agricultural conditions.

The primary goal is to provide farmers with early-stage, data-driven insights without relying on expensive hardware or continuous expert intervention.

---

## Core Features

### Satellite-Based Crop Health Monitoring (NDVI)
- Vegetation health analysis using Normalized Difference Vegetation Index (NDVI)
- Dual map visualization (standard map and satellite imagery)
- Field-level identification of stressed or low-vigor crop zones
- Supports large-area monitoring without physical inspection

### AI-Based Plant Disease Detection
- Plant disease identification using image-based analysis
- Probability-ranked disease predictions with confidence scores
- AI-generated explanations and treatment suggestions using Groq AI
- Designed for early-stage symptom recognition

### Weather Monitoring and Alerts
- GPS-based hyperlocal weather data
- Hourly and daily forecasts
- Severe weather alerts relevant to agricultural operations
- Supports irrigation, spraying, and harvest planning

---

## Technology Stack

**Mapping and Visualization**
- Leaflet.js

**Satellite and Remote Sensing Data**
- NASA GIBS
- Sentinel-2
- Landsat-8

**AI and Image Analysis**
- Plant.ID API (Kindwise)
- Crop.Health API (Kindwise)
- Groq AI (LLM-based contextual analysis)

**Weather Data**
- OpenWeatherMap API

---

## System Workflow

1. User selects or detects farm location
2. Satellite imagery and NDVI layers are rendered for crop health visualization
3. User captures plant image for disease analysis
4. Image is processed using Plant.ID and Crop.Health APIs
5. Consolidated results are analyzed by Groq AI for explanation and recommendations
6. Weather data and alerts are fetched based on farm location

---

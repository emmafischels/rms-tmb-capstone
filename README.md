# Pediatric Rhabdomyosarcoma Tumor Mutational Burden Analysis

## Project Overview

This project is an interactive Python application for exploring the relationship between tumor mutational burden (TMB) and overall survival in pediatric rhabdomyosarcoma (RMS) patients. The application combines data preprocessing, exploratory data analysis, interactive visualization, and survival analysis into a reproducible workflow built with Streamlit.

Clinical and genomic data were obtained from the publicly available MSK Precision Oncology 2023 Rhabdomyosarcoma dataset available through cBioPortal. Rather than producing a single static analysis, the application provides an interactive interface that allows users to explore the dataset, customize analyses, and generate publication-quality visualizations.

Link to current working tool: https://rms-tmb-capstone-efischels.streamlit.app/

⸻

## Research Objective

The primary objective of this project is to investigate whether pediatric rhabdomyosarcoma patients with higher tumor mutational burden exhibit differences in overall survival compared to patients with lower tumor mutational burden.

Specifically, the application allows users to:

* Explore clinical and genomic characteristics of the cohort
* Assess data quality and missing values
* Generate descriptive statistics
* Visualize relationships among clinical variables
* Compare patient-level and sample-level analyses
* Perform Kaplan–Meier survival analysis using customizable TMB thresholds
* Evaluate survival differences using the log-rank test
* Export processed datasets and summary tables

⸻

# Features

## Data Overview

* Dataset summary
* Variable descriptions
* Missing value visualization
* Missing value summary table
* Descriptive statistics
* Download processed data

## Exploratory Data Analysis

Interactive visualizations including:

* Histograms
* Scatter plots
* Box plots
* Violin plots
* Correlation heatmaps
* Frequency plots

Users can choose between:

* Sample-level analysis
* Patient-level analysis

Patient-level data can be aggregated using:

* Mean
* Median
* Minimum
* Maximum

⸻

# Survival Analysis

The application includes an interactive survival analysis workflow featuring:

* Kaplan–Meier survival curves
* Log-rank hypothesis testing
* Confidence interval display
* Median or custom TMB cutoffs
* Patient/sample analysis selection
* Multiple patient aggregation methods
* Group summary statistics
* Median survival estimates
* Downloadable survival tables

⸻

# Dataset

The project uses publicly available clinical and genomic data from:

MSK Precision Oncology 2023 Pediatric Rhabdomyosarcoma Cohort

Available through cBioPortal.

Variables include:

* Tumor Mutational Burden (nonsynonymous)
* Overall Survival (months)
* Overall Survival Status
* Mutation Count
* Fraction Genome Altered
* Tumor Purity
* Sex
* Race
* Ethnicity
* Sample Type
* Gene Panel
* MSI Score
* MSI Type

____
# Repository Structure

rms-tmb-capstone/
│
├── data/
│   └── soft_tissue_msk_2023_clinical_data.tsv
│
├── scripts/
│   ├── app.py
│   ├── data_processing.py
│   ├── survival_analysis.py
│   └── visualizations.py
│
├── figures/
├── requirements.txt
├── setup_env.sh
├── environment.yml
├── README.md
└── .gitignore

⸻

# Installation

Clone the repository
git clone https://github.com/emmafischels/rms-tmb-capstone.git
cd rms-tmb-capstone

Create the environment
conda env create -f environment.yml
conda activate rms-tmb-capstone

⸻

# Running the Application

Launch the Streamlit application:
streamlit run scripts/app.py

The application will open in your web browser and provide an interactive interface for data exploration and survival analysis.

⸻

# Statistical Methods

The application incorporates several statistical approaches including:

* Descriptive statistics
* Missing data assessment
* Correlation analysis
* Kaplan–Meier survival estimation
* Log-rank hypothesis testing
* Patient-level aggregation methods

Visualizations are generated using Plotly for interactive exploration.

⸻

# Software

Developed using

* Python
* Streamlit
* pandas
* NumPy
* Plotly
* lifelines
* SciPy
* Matplotlib

⸻

# Current Status

Current development includes:

* Modular application architecture
* Interactive Streamlit interface
* Data preprocessing module
* Visualization module
* Survival analysis module
* Downloadable analysis outputs
* Flexible patient/sample analysis workflow
* GitHub version control
* Reproducible environment setup

⸻

# Future Improvements

Potential future enhancements include:

* Cox proportional hazards regression
* Multivariable survival modeling
* Additional clinical covariates
* User-uploaded datasets
* Expanded statistical testing
* Additional publication-quality visualizations

⸻

# Data Source

The clinical data used in this project are publicly available through cBioPortal.

Cerami E, Gao J, Dogrusoz U, et al. The cBio Cancer Genomics Portal: An Open Platform for Exploring Multidimensional Cancer Genomics Data. Cancer Discovery. 2012.

⸻

# Author

Emma Fischels

Biomedical Sciences Graduate Program 
The Ohio State University 
Columbus, OH

⸻

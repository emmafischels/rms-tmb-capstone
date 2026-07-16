### Read me for Capstone project 

## Project Overview 

This project aims to develop a reproducible Python-based data analysis and visualization tool for exploring the relationship between tumor mutational burden (TMB) and overall survival in pediatric rhabdomyosarcoma (RMS) patients. The project utilizes publicly available clinical and genomic data obtained from cBioPortal and is designed to provide an interactive workflow for exploratory data analysis, statistical visualization, and survival analysis. 

Rather than producing a single static analysis, this project is being developed as a reusable application capable of generating multiple visualization and statistical summaries from uploaded datasets. 

## Research Objectives 

The primary objective of this project is to investigate whether pediatric rhabdomyosarcoma patients with higher tumor mutational burden demonstrate different overall survival compared to patients with lower tumor mutational burden.

The completed application will allow users to:

* Load clinical and genomic datasets
* Explore patient characteristics through multiple visualizations
* Generate descriptive statistics
* Perform Kaplan-Meier survival analysis
* Compare survival between user-defined patient groups
* Visualize relationships among clinical variables

## Dataset 

The project uses publicly available pediatric rhabdomyosarcoma data downloaded from cBioPortal.

The dataset contains clinical and genomic variables including, but not limited to:

* Tumor Mutational Burden (TMB)
* Overall Survival (months)
* Survival Status
* Mutation Count
* Fraction Genome Altered
* Tumor Purity
* Demographic variables


## Current Progress 

The following components have been completed:

* Project directory structure created
* Conda environment configuration (environment.yml)
* Python package requirements (requirements.txt)
* Automated OSC setup script (setup_env.sh)
* Jupyter kernel registration for the project environment
* Dataset uploaded to the project directory
* GitHub repository initialized for version control

## Software Requirements 

## Project Structure 

## Planned Features 
The completed application will include:

* Interactive dataset loading
* Data quality assessment
* Missing value summaries
* Descriptive statistics
* Histograms
* Scatter plots
* Boxplots
* Correlation visualizations
* Kaplan-Meier survival curves
* Log-rank statistical testing
* Publication-quality figure generation
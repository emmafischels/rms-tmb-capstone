#!/usr/bin/env python
# coding: utf-8

# # Rhabdomyosarcoma Tumor Mutational Burden Survival Analysis
# 
# This notebook investigates whether pediatric rhabdomyosarcoma patients with higher tumor mutational burden (TMB) have different overall survival than patients with lower TMB.

# In[ ]:


import pandas as pd
import numpy as np

from lifelines import KaplanMeierFitter
from lifelines.statistics import logrank_test

import matplotlib.pyplot as plt
import seaborn as sns


# ## Load the Dataset

# In[ ]:


df = pd.read_csv("../data/rms_dataset.csv")

df.head()


# In[ ]:





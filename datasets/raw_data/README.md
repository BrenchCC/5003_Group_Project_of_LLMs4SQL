# 文件夹概述

本仓库包含我们论文中所述各项任务及数据集研究所需的核心组件。以下是主要内容的概述：

## 目录与文件

- **任务**：包含研究中使用的五项任务数据集：
  - 语法错误任务
  - 缺失词元任务
  - 等价性任务
  - 性能预测任务
  - SQL转文本任务

- **统计数据**：存储四个数据集的统计分析CSV文件：
  - SDSS
  - SQLShare
  - Join Order
  - Spider

- **datasets_stats.ipynb**：该Jupyter notebook阐述论文中使用的统计特性，包含图1-4的可视化分析。

- **data_transform.ipynb** ：该Jupyter notebook包含数据转换脚本，用于将原始数据集转换为我们研究中使用的类型标签。

## 目的
`Tasks`目录提供特定研究任务的数据与脚本，而`Stats`目录包含用于综合统计分析的聚合数据。笔记本`datasets_stats.ipynb`深入阐释了学术论文中呈现的统计方法与结果。笔记本`data_transform.ipynb`包含数据转换脚本，用于将原始数据集转换为我们研究中使用的类型标签。


> # Folder Overview
> 
> This repository contains core components required for the tasks and datasets described in the paper. Below is an overview of the main contents:
> 
> ## Directories and Files
> 
> - **Tasks**: Contains five task datasets used in the research:
>   - Syntactic Error Task
>   - Missing Morpheme Task
>   - Equivalence Task
>   - Performance Prediction Task
>   - SQL-to-Text task
> 
> - **Statistical Analysis**: Stores CSV files with statistical analyses for four datasets:
>   - SDSS
>   - SQLShare
>   - Join Order
>   - Spider
> 
> - **datasets_stats.ipynb**: This Jupyter notebook details the statistical features used in the paper, including visualizations for Figures 1 to 4.
> 
> - **data_transform.ipynb**: This Jupyter notebook contains data transformation scripts to convert raw datasets into the typed labels used in the research.
> 
> ## Purpose
> The `Tasks` directory provides data and scripts required for specific research tasks, while the `Stats` directory contains aggregated data for comprehensive statistical analysis. The notebook `datasets_stats.ipynb` provides an in-depth explanation of the statistical methods and results presented in the academic paper. The notebook `data_transform.ipynb` contains data transformation scripts used to convert the raw dataset into the typed labels adopted in this study.
> 
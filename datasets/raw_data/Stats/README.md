## 原数据概述
本目录包含四个 CSV 文件，提供实验中不同数据集所用 SQL 查询的统计分析。
每个文件记录以下指标：
- 查询长度/字符计数
- 词汇量计数
- 查询类型
- 聚合函数
- 表计数
- 连接计数
- 嵌套层级
- 列数
- 函数数
- 谓词数
 **这些指标有助于理解查询结构与语法特征，从而评估大型语言模型在SQL任务中的表现。** 
### 文件概述（采样后的结果）
* sdss_stats.csv：斯隆数字天空调查（SDSS）数据集的查询统计。使用2023年采集的285条查询。
* sqlshare_stats.csv：SQLShare数据集查询统计（数量：251）
* join-order_stats.csv：Join-Order基准测试查询统计（数量：157）
* spider_stats.csv：Spider基准测试查询详细统计（数量：200）

> ## Raw Data Overview
> This directory contains four CSV files providing statistical analysis of SQL queries used across different datasets in the experiment.
> Each file records the following metrics:
> - Query length/character count
> - Vocabulary count
> - Query type
> - Aggregate functions
> - Table count
> - Join count
> - Nesting level
> - Column count
> - Function count
> - Predicate count
> **These metrics aid in understanding query structure and syntactic characteristics, thereby evaluating large language models' performance on SQL tasks.**
> ### File Overview
> * sdss_stats.csv: Query statistics for the Sloan Digital Sky Survey (SDSS) dataset. Uses 285 queries from 2023.
> * sqlshare_stats.csv: Query statistics for the SQLShare dataset. (num: 251)
> * join-order_stats.csv: Query statistics for the Join-Order benchmark. (num: 157)
> * spider_stats.csv: Detailed statistics for Spider benchmark queries. (num: 200)
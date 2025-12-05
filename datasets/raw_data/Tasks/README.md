# 数据集

本仓库包含多个子文件夹，每个文件夹存放用于评估本研究中特定SQL相关任务的数据集。每个数据集旨在测试大型语言模型（LLMs）处理SQL查询的不同方面。以下是各项任务及其关联数据集的详细说明：

## 等价性任务

- **包含数据集：** SDSS、SQLShare、Join-Order
- **描述：** 用于评估LLM判断语法不同查询是否等价的能力。此处“等价”指查询在所有数据库实例中返回相同结果。该能力对查询优化和推荐等任务至关重要。数据集包含SQL查询等价性判定结果及评估的等价类型。

## 缺失令牌任务

- **包含数据集：** SDSS、SQLShare、Join-Order
- **描述：** 本子文件夹包含用于测试大型语言模型识别并正确填补SQL查询中缺失令牌能力的数据集。提供二进制答案表明SQL查询是否存在缺失令牌，并详细说明缺失令牌的类型和位置。

## 性能预测任务

- **包含数据集：** SDSS
- **描述：** 本数据集包含运行时数据，用于判断SQL查询的执行耗时高低。

## SQL转文本任务

- **包含数据集：** Spider
- **描述：** 该任务涉及SQL转文本转换，将LLM生成的自然语言描述（解释特定SQL查询功能）作为结果存储。

## 语法错误任务

- **包含数据集：** SDSS, SQLShare, Join-Order
- **任务描述：** 该任务需识别超越基础语法错误（如括号缺失）的高级语法问题，包括跨SQL子句的属性错位或连接操作中属性类型不当等复杂错误。此任务评估LLM对SQL语法与语义的深度理解能力，包含二元答案（判断SQL查询是否存在语法错误）及具体错误类型说明。

> # Datasets
> 
> This repository contains a collection of subfolders, each hosting datasets used for specific SQL-related tasks evaluated in our study. Each dataset is designed to test different aspects of SQL query handling by large language models (LLMs). Below are the detailed descriptions of the tasks and the datasets associated with them:
> 
> ## Equivalence Task
> 
> - **Datasets Included:** SDSS, SQLShare, Join-Order
> - **Description:** These datasets are used to assess LLMs' ability to determine if two syntactically different queries are equivalent. Here, 'equivalence' refers to the queries returning the same result for all database instances. This is crucial for tasks like query optimization and recommendation. The datasets include information on whether the SQL queries are equivalent and the types of equivalence assessed.
> 
> ## Missing Token Task
> 
> - **Datasets Included:** SDSS, SQLShare, Join-Order
> - **Description:** This subfolder includes datasets for testing LLMs' ability to identify and correctly impute missing tokens in SQL queries. It provides a binary answer indicating whether an SQL query has a missing token and details the type and position of the missing token.
> 
> ## Performance Prediction Task
> 
> - **Datasets Included:** SDSS
> - **Description:** This dataset contains runtime data used to determine whether an SQL query will take a high or low amount of time to run.
> 
> ## SQLToText Task
> 
> - **Datasets Included:** Spider
> - **Description:** This task involves the SQLToText conversion, where the results of LLMs are stored as they generate a natural language description of what a given SQL query does.
> 
> ## Syntax Error Task
> 
> - **Datasets Included:** SDSS, SQLShare, Join-Order
> - **Description:** This task involves identifying advanced syntax errors that go beyond simple mistakes, such as missing parentheses, to more complex errors like misalignment of attributes across SQL clauses or inappropriate attribute types in joins. This assesses a deeper level of syntactic and semantic understanding of SQL by LLMs. It includes a binary answer indicating whether an SQL query has any syntax error, and also details the types of errors.
> 
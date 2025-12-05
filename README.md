# 5003 Group Project of LLMs4SQL
> A group project repository focused on evaluating large language models’ understanding of SQL.
> It assesses models across five task-specific metrics, providing a comprehensive measurement of their SQL query comprehension and execution capabilities.

**How to get repo files:**
- 1. using git clone command as follow command **(ensure you have installed git)**:
    ``` bash
    git clone https://github.com/BrenchCC/5003_Group_Project_of_LLMs4SQL
    ```
- 2. using download zip file

## 1. Python Environment Installation Guidance
### 1.1 Create a Python Environment by conda command
```bash
conda create -n llms4sql python==3.10 

conda activate llms4sql
```

### 1.2 Install the Required Packages
```bash
pip install -r requirements.txt
```

## 2. Dataset Instruction 
- Details in [datasets](datasets/raw_data)

## 3. Model Using Overview
- Doubao-Seed-1.6-251015 ~ no reasoning
- qwen3-next-80b-a3b-instruct ~ no reasoning
- glm-4.6 ~ no reasoning
- DeepSeek-V3.1-Terminus(deepseek-v3.1)~ no reasoning
- DeepSeek-V3.1-Terminus(deepseek-v3.1)~ reasoning


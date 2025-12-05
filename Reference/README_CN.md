# 仓库概述
> https://github.com/AnanyaRahaman/LLMs_SQL_Understanding
本仓库包含一系列工具和数据集，旨在评估大型语言模型（LLMs）对SQL查询的理解能力。我们的研究聚焦SQL处理的多个方面，包括语法错误检测、缺失令牌识别、查询性能预测、查询等价性检查以及SQL到测试用例的转换。

## 目录与文件说明

### 代码（Code）
该目录存放项目核心脚本和工具：
- **ANTLR**：包含与ANTLR相关的文件和脚本，这些文件对SQL查询的解析和分析至关重要。
- **llms_interaction.ipynb**：一份Jupyter笔记本，演示如何与不同语言模型（包括GPT-4、GPT-3.5、Llama3、Mistralai和Gemini）交互，展示它们处理各类SQL任务的表现。

### 数据集（Datasets）
该目录包含两个文件夹和一份Jupyter笔记本：
- **统计数据（Stats）**：存储与所评估SQL任务相关的统计数据及分析结果。
- **任务（Tasks）**：包含针对各SQL任务的数据集和资源，例如语法错误识别、缺失令牌识别、性能预测和查询等价性任务。
- **datasets_stats.ipynb**：一份Jupyter笔记本，提供研究中使用的详细统计评估，分析统计特性对各类SQL任务的影响。

### results.ipynb
这份Jupyter笔记本呈现了我们的分析结果，展示了统计特性对语法错误识别、缺失令牌识别、性能预测和查询等价性等SQL任务在不同数据集上的影响。结果涵盖五种LLM：GPT-4、GPT-3.5、Llama3、Mistralai和Gemini。尽管并非所有图表都纳入论文，但所呈现的图表最能说明研究变量之间存在的显著关联或无关联。

# LLM中的SQL任务评估
本仓库致力于评估语言学习模型（LLMs）处理复杂SQL任务的能力。我们的研究调查了多项任务，这些任务能够展现LLM超越基础语法检查、理解和操作SQL查询的能力。

## SQL相关任务

### 1. 语法错误识别（Syntax Error Identification）
该任务评估LLM识别影响SQL查询结构和语义的高级语法错误的能力。与括号缺失等简单错误不同，高级错误包括`SELECT`、`GROUP BY`、`HAVING`子句中属性与函数的不匹配、连接操作中的类型不兼容以及无效连接操作。这项评估反映了LLM对SQL“理解”的深度。

### 2. 缺失令牌识别（Missing Token Identification）
识别并精确定位SQL查询中的缺失令牌，对查询推荐系统和自动补全功能至关重要。该任务不仅评估令牌缺失的识别能力，还包括对缺失令牌的精确类型和位置的定位，为查询构建应用的优化提供支持。

### 3. 查询性能评估（Query Performance Estimation）
仅基于文本估算SQL查询的运行时性能具有挑战性，因为这会受到数据库模式、数据细节和查询负载等因素的影响。我们探究LLM对查询执行成本的预测能力，尤其是针对复杂查询、涉及多表连接或包含多个谓词条件的查询。

### 4. 查询等价性（Query Equivalence）
在所有数据库实例中产生相同结果的两个查询被视为等价，这对查询优化和推荐至关重要。该任务通过向LLM提供带标签的查询对（等价和非等价），评估其识别查询等价性的有效性，进而助力实现更简洁、高效的查询执行策略。

### 5. 查询可解释性（Query Explainability）
我们评估LLM通过描述SQL查询的预期输出来解释查询的能力。该任务类似于为代码生成文档或为图像添加说明，用于衡量模型的理解深度。评估涵盖一系列复杂查询，包括涉及多表、嵌套子查询和复杂逻辑条件的查询。

# 查询等价性与非等价性

## 查询等价性类型
由于论文篇幅限制，我们无法详细讨论各类查询等价性转换。以下概述了用于测试LLM理解和操作SQL查询能力的几种关键转换类型：

1. **嵌套顺序交换（Swapping Nestedness）**
   - 改变查询中的嵌套顺序，评估模型对不同查询结构的理解灵活性。
   - **示例**：
     ```sql
     -- 原始查询
     SELECT objID
     FROM PhotoObj
     WHERE objID IN (
     SELECT objID
     FROM PhotoTag
     WHERE u > 18);

     -- 等价查询
     SELECT objID
     FROM PhotoTag
     WHERE u > 18
     AND objID IN (
     SELECT objID
     FROM PhotoObj);

     ```

2. **连接顺序调整（Changing Join Order）**
   - 调整连接子句中表的顺序。
   - **示例**：
     ```sql
     -- 原始查询
     SELECT p.objID, s.specObjID
     FROM PhotoObj AS p, SpecObj AS s
     WHERE p.objID = s.objID AND p.u < 19;

     
     -- 等价查询
     SELECT p.objID, s.specObjID
     FROM SpecObj AS s, PhotoObj AS p
     WHERE p.objID = s.objID AND p.u < 19;

     ```

3. **连接方式转换（Converting Joins）**
   - 测试模型理解并在显式连接语法与隐式连接语法之间转换的能力。
   - **示例**：
     ```sql
     -- 原始查询
     SELECT p.objID, s.specObjID
     FROM PhotoObj p, SpecObj s
     WHERE p.objID = s.objID;

 
     -- 等价查询
     SELECT p.objID, s.specObjID
     FROM PhotoObj p
     JOIN SpecObj s ON p.objID = s.objID;

     ```

4. **子查询应用（Using Subqueries）**
   - **连接转嵌套示例（Join to Nested Example）**：
     将连接操作替换为子查询。
     ```sql
     -- 原始查询
     SELECT p.objID, p.ra, p.dec
     PhotoObj p
     JOIN Field f ON p.fieldID = f.fieldID
     WHERE f.ra > 250;

     
     -- 等价查询
     SELECT p.objID, p.ra, p.dec
     FROM PhotoObj p
     WHERE p.fieldID IN (
     SELECT fieldID
     FROM Field
     WHERE ra > 250);

     ```
   - **条件转嵌套示例（Condition to Nested Example）**：
     将`WHERE`子句中的直接条件检查替换为子查询。
     ```sql
     -- 原始查询
     SELECT objID, ra, dec
     FROM PhotoObj
     WHERE fieldID = 100;

     
     -- 等价查询
     SELECT objID, ra, dec
     FROM PhotoObj
     WHERE fieldID = (SELECT fieldID FROM Field WHERE fieldID = 100);

     ```

5. **公共表表达式（CTEs）应用（Using Common Table Expressions）**
   - 考察模型使用CTE组织复杂查询的熟练度。
   - **示例**：
     ```sql
     -- 原始查询
     SELECT text 
     FROM DBObjects 
     WHERE name = 'PhotoTag';
     
     -- 等价查询
     WITH FilteredObjects AS (
         SELECT text
         FROM DBObjects
         WHERE name = 'PhotoTag'
     )
     SELECT text
     FROM FilteredObjects;
     ```

6. **UNION/INTERSECT ALL应用（Using UNION or INTERSECT ALL）**
   - 利用集合运算及其含义构建等价查询。
   - **示例**：
     ```sql
     -- 原始查询
     SELECT objID
     FROM PhotoObj
     WHERE ra < 180 OR ra > 185;

     
     -- 等价查询
     SELECT objID
     FROM PhotoObj
     WHERE ra < 180
     UNION
     SELECT objID
     FROM PhotoObj
     WHERE ra > 185;

     ```

7. **EXISTS应用（Using EXISTS）**
   - 在子查询中使用`EXISTS`逻辑运算符，复制连接或复杂条件的效果。
   - **示例**：
     ```sql
     -- 原始查询
     SELECT p.objID
     FROM PhotoObj p
     JOIN SpecObj s ON p.objID = s.objID
     WHERE s.z > 0.1;

     
     -- 等价查询
     SELECT objID
     FROM PhotoObj p
     WHERE EXISTS (
     SELECT 1
     FROM SpecObj s
     WHERE p.objID = s.objID AND s.z > 0.1);

     ```

8. **CASE语句应用（Using CASE Statements）**
   - 在查询中使用条件逻辑（`CASE`和`WHEN`）构建等价查询。
   - **示例**：
     ```sql
     -- 原始查询
     SELECT p.objID,
       p.type,
       o.priority_modifier,
       p.magnitude * (1 - o.priority_modifier) AS adjusted_magnitude
       FROM PhotoObj p
       LEFT JOIN ObjectTypes o
       ON p.type = o.type;

     
     -- 等价查询
     SELECT objID,
       type,
       magnitude,
       CASE
           WHEN type = 'STAR' THEN magnitude * 0.95  -- 恒星优先级略低
           WHEN type = 'GALAXY' THEN magnitude * 0.90  -- 星系优先级中等
           WHEN type = 'QSO' THEN magnitude * 0.85  -- 类星体优先级高
           ELSE magnitude  -- 未知类型不调整
       END AS adjusted_magnitude FROM PhotoObj;

     ```

9. **简化与直接应用（Simplification and Direct Application）**
   - 在保持相同逻辑条件和输出的前提下简化复杂查询。
   - **示例**：
     ```sql
     -- 原始查询（含子查询的复杂查询）
     SELECT MAX(redshift) AS max_redshift,
       MIN(redshift) AS min_redshift,
       AVG(redshift) AS avg_redshift,
       COUNT(*) AS total_count
     FROM (
     SELECT objID, redshift
     FROM SpecObj
     WHERE class = 'GALAXY'
     AND redshift > 0.1
     AND redshift < 0.3
     ) x
     ORDER BY redshift DESC;

     
     -- 等价查询（简化版）
     SELECT MAX(redshift) AS max_redshift,
       MIN(redshift) AS min_redshift,
       AVG(redshift) AS avg_redshift,
       COUNT(*) AS total_count
     FROM SpecObj
     WHERE class = 'GALAXY'
     AND redshift > 0.1
     AND redshift < 0.3;

     ```

10. **条件顺序重排（Reordering the Conditions）**
    - 测试模型在`WHERE`子句条件重排后是否仍能保持查询完整性。
    - **示例**：
      ```sql
      -- 原始查询
      SELECT objID, ra, dec
      FROM PhotoObj
      WHERE objID = 12345 AND ra > 180 AND dec < 0;

      
      -- 等价查询
      SELECT objID, ra, dec
      FROM PhotoObj
      WHERE dec < 0 AND ra > 180 AND objID = 12345;

      ```

## 非等价查询构建
我们还探索了生成非等价查询以进一步考验LLM。这些测试包括：

1. **聚合函数替换（Using Different Aggregate Functions）**
   - 修改聚合函数，观察分组结果的变化。
   - **示例**：
     ```sql
     -- 原始查询
     SELECT class, AVG(redshift) FROM SpecObj WHERE class = 'GALAXY' GROUP BY class;
     
     -- 非等价查询
     SELECT class, SUM(redshift) FROM SpecObj WHERE class = 'GALAXY' GROUP BY class;

     ```

2. **连接条件修改（Changing Join Conditions）**
   - 调整连接类型，测试连接条件对结果的影响。
   - **示例**：
     ```sql
     -- 原始查询
     SELECT p.objID, s.specObjID FROM PhotoObj AS p INNER JOIN SpecObj AS s ON p.objID = s.objID AND s.class = 'STAR';

     
     -- 非等价查询
     SELECT p.objID, s.specObjID FROM PhotoObj AS p LEFT JOIN SpecObj AS s ON p.objID = s.objID AND s.class = 'STAR';

     ```

3. **分组条件调整（Modifying Grouping Criteria）**
   - 更改分组字段，观察其对聚合结果的影响。
   - **示例**：
     ```sql
     -- 原始查询
     SELECT fieldID, COUNT(*) FROM PhotoObj GROUP BY fieldID;

     
     -- 非等价查询
     SELECT type, fieldID, COUNT(*) FROM PhotoObj GROUP BY type, fieldID;

     ```

4. **细微修改引入（Introducing Subtle Changes）**
   - 包括逻辑条件、数值和运算符修改，评估模型对查询细节的敏感度。
   - **逻辑条件示例**：
     ```sql
     -- 原始查询
     SELECT objID FROM PhotoObj WHERE type = 'GALAXY' AND ra > 180;
     
     -- 非等价查询
     SELECT objID FROM PhotoObj WHERE type = 'GALAXY' OR ra > 180;
     ```
   - **数值修改示例**：
     ```sql
     -- 原始查询
     SELECT objID FROM PhotoObj WHERE mag_u < 18;
     
     -- 非等价查询
     SELECT objID FROM PhotoObj WHERE mag_u < 20;
     ```
   - **运算符修改示例**：
     ```sql
     -- 原始查询
     SELECT objID FROM PhotoObj WHERE mag_u > 18;
     
     -- 非等价查询
     SELECT objID FROM PhotoObj WHERE mag_u < 18;
     ```

5. **排序与限制调整（Changing Sorting and Limiting）**
   - 改变排序方式和分页参数，观察其对查询输出的影响。
   - **示例**：
     ```sql
     -- 原始查询
     SELECT objID, ra FROM PhotoObj ORDER BY ra DESC LIMIT 10;

     
     -- 非等价查询
     SELECT objID, ra FROM PhotoObj ORDER BY ra ASC LIMIT 10;

     ```

6. **排序字段修改（Modifying Order By Criteria）**
   - 调整`ORDER BY`的排序依据，测试排序规则的重要性。
   - **示例**：
     ```sql
     -- 原始查询
     SELECT objID, ra FROM PhotoObj ORDER BY ra;
     
     -- 非等价查询
     SELECT objID, dec FROM PhotoObj ORDER BY dec;

     ```

7. **列引用模糊化（Ambiguous Column References）**
   - 在列引用中引入错误，评估模型的错误检测能力。
     ```sql
     -- 原始查询
     SELECT objID, ra, dec FROM PhotoObj;

     -- 非等价查询
     SELECT objID, ra FROM PhotoObj;
     ```

8. **表名修改（Change Table Name）**
   - 在表名中引入错误。
     ```sql
     -- 原始查询
     SELECT objID, ra FROM PhotoObj;
     
     -- 非等价查询
     SELECT objID, ra FROM PhotoObject;

     ```

这些分类有助于全面评估LLM在SQL查询操作和理解方面的适应性与准确性。

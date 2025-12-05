# Repository Overview

This repository contains a collection of tools and datasets designed to evaluate the understanding of SQL queries by large language models (LLMs). Our focus is on various aspects of SQL processing, including syntax error detection, missing token identification, query performance prediction, and query equivalence checking and SQL to Test Conversion.

## Directory and File Descriptions

### Code
This directory houses the essential scripts and utilities for our project:
- **ANTLR**: Contains ANTLR-related files and scripts which are crucial for parsing and analyzing SQL queries.
- **llms_interaction.ipynb**: A Jupyter notebook that demonstrates the interaction with different language models including GPT-4, GPT-3.5, Llama3, Mistralai, and Gemini, showcasing their handling of various SQL tasks.

### Datasets
This directory contains two folders and a Jupyter notebook:
- **Stats**: Holds statistical data and analyses relevant to the SQL tasks we evaluated.
- **Tasks**: Contains datasets and resources specific to each SQL task such as Syntax Error Identification, Missing Token Identification, Performance Prediction, and Query Equivalence.
- **datasets_stats.ipynb**: A Jupyter notebook that provides detailed statistical evaluations used in our research, analyzing the impact of statistical properties on various SQL tasks.

### results.ipynb
This Jupyter notebook presents the results of our analysis, showing the impact of statistical properties on SQL tasks such as Syntax Error Identification, Missing Token Identification, Performance Prediction, and Query Equivalence across different datasets. Results are shown for five LLMs: GPT-4, GPT-3.5, Llama3, Mistralai, and Gemini. While not all figures made it into the paper, those included best illustrate the significant relationships or their absence among the variables studied.

# SQL Task Evaluation in LLMs

This repository is dedicated to evaluating the capability of Language Learning Models (LLMs) to handle complex SQL tasks. Our research investigates several tasks that showcase an LLM's ability to understand and manipulate SQL queries beyond basic syntax checking.

## SQL Related Tasks

### 1. Syntax Error Identification
This task assesses the ability of LLMs to identify advanced syntax errors that impact the structure and semantics of SQL queries. Unlike simple mistakes (such as missing parentheses), advanced errors include misalignment of attributes and functions among `SELECT`, `GROUP BY`, `HAVING` clauses, type mismatches in joins, and invalid join operations. This evaluation reflects the depth of an LLM’s SQL "understanding."

### 2. Missing Token Identification
The ability to identify and precisely locate missing tokens in SQL queries is crucial for query recommendation systems and auto-completion functionalities. This task evaluates not just the recognition but also the pinpointing of the exact type and location of missing tokens, facilitating enhancements in query-building applications.

### 3. Query Performance Estimation
Estimating the runtime performance of SQL queries based solely on their text is challenging due to influences like database schema, data specifics, and query workload. We explore how well LLMs can predict the execution costs of queries, particularly those that are complex, involve multiple joins, or have several predicate conditions.

### 4. Query Equivalence
Two queries that yield identical results across all database instances are considered equivalent, crucial for query optimization and recommendation. This task involves evaluating LLMs with labeled query pairs (equivalent and non-equivalent) to determine their effectiveness in recognizing query equivalence, thus aiding in simpler and faster query execution strategies.

### 5. Query Explainability
We assess LLMs on their ability to explain SQL queries by describing their expected outputs. This task is akin to generating documentation for code or captions for images, measuring the model's depth of understanding. Our evaluation includes a range of complex queries involving multiple tables, nested subqueries, and intricate logical conditions.

# Query Equivalence and Non-Equivalence

## Query Equivalence Types

Due to page limitations in our paper, we were unable to include detailed discussions on various types of query equivalence transformations. Here, we outline several key transformations used to test the capability of LLMs to understand and manipulate SQL queries:

1. **Swapping Nestedness** ("Swapping_Nestedness")
   - Changes the order of nestedness in queries to evaluate flexibility in understanding different query structures.
   - **Example**:
     ```sql
     -- Original Query
     SELECT objID
     FROM PhotoObj
     WHERE objID IN (
     SELECT objID
     FROM PhotoTag
     WHERE u > 18);

     -- Equivalent Query
     SELECT objID
     FROM PhotoTag
     WHERE u > 18
     AND objID IN (
     SELECT objID
     FROM PhotoObj);

     ```

2. **Changing Join Order** ("Join_Order")
   - This involves altering the order of tables in the join clause.
   - **Example**:
     ```sql
     -- Original Query
     SELECT p.objID, s.specObjID
     FROM PhotoObj AS p, SpecObj AS s
     WHERE p.objID = s.objID AND p.u < 19;

     
     -- Equivalent Query
     SELECT p.objID, s.specObjID
     FROM SpecObj AS s, PhotoObj AS p
     WHERE p.objID = s.objID AND p.u < 19;

     ```

3. **Converting Joins** ("Explicit_Implicit_Joins")
   - Tests the model's ability to interpret and convert between explicit and implicit join syntax.
   - **Example**:
     ```sql
     -- Original Query
     SELECT p.objID, s.specObjID
     FROM PhotoObj p, SpecObj s
     WHERE p.objID = s.objID;

 
     -- Equivalent Query
     SELECT p.objID, s.specObjID
     FROM PhotoObj p
     JOIN SpecObj s ON p.objID = s.objID;

     ```

4. **Using Subqueries** ("Join_Nested", "Condition_Nested")
   - **Join to Nested Example**:
   - This involves replacing a join operation with a subquery. 
     ```sql
     -- Original Query
     SELECT p.objID, p.ra, p.dec
     PhotoObj p
     JOIN Field f ON p.fieldID = f.fieldID
     WHERE f.ra > 250;

     
     -- Equivalent Query
     SELECT p.objID, p.ra, p.dec
     FROM PhotoObj p
     WHERE p.fieldID IN (
     SELECT fieldID
     FROM Field
     WHERE ra > 250);

     ```
   - **Condition to Nested Example**:
   - This technique replaces direct condition checks in the WHERE clause with subqueries. 
     ```sql
     -- Original Query
     SELECT objID, ra, dec
     FROM PhotoObj
     WHERE fieldID = 100;

     
     -- Equivalent Query
     SELECT objID, ra, dec
     FROM PhotoObj
     WHERE fieldID = (SELECT fieldID FROM Field WHERE fieldID = 100);

     ```


5. **Using Common Table Expressions (CTEs)** ("CTEs")
   - Examines the model's proficiency in utilizing CTEs to organize complex queries.
   - **Example**:
     ```sql
     -- Original Query
     SELECT text 
     FROM DBObjects 
     WHERE name = 'PhotoTag';
     
     -- Equivalent Query
     WITH FilteredObjects AS (
         SELECT text
         FROM DBObjects
         WHERE name = 'PhotoTag'
     )
     SELECT text
     FROM FilteredObjects;
     ```

6. **Using UNION or INTERSECT ALL** ("Condition_IntersectUnion")
   - This Techniques use set operations and their implications to make equivalent queries.
   - **Example**:
     ```sql
     -- Original Query
     SELECT objID
     FROM PhotoObj
     WHERE ra < 180 OR ra > 185;

     
     -- Equivalent Query
     SELECT objID
     FROM PhotoObj
     WHERE ra < 180
     UNION
     SELECT objID
     FROM PhotoObj
     WHERE ra > 185;

     ```

7. **Using EXISTS** ("Condition_EXISTs")
   - Using EXISTS logical operator within subqueries that can replicate the effects of joins or complex conditions.
   - **Example**:
     ```sql
     -- Original Query
     SELECT p.objID
     FROM PhotoObj p
     JOIN SpecObj s ON p.objID = s.objID
     WHERE s.z > 0.1;

     
     -- Equivalent Query
     SELECT objID
     FROM PhotoObj p
     WHERE EXISTS (
     SELECT 1
     FROM SpecObj s
     WHERE p.objID = s.objID AND s.z > 0.1);

     ```

8. **Using CASE Statements** ("Case_Statement")
   - Using conditional logic (CASE and WHEN) within queries to produce equivalent queries.
   - **Example**:
     ```sql
     -- Original Query
     SELECT p.objID,
       p.type,
       o.priority_modifier,
       p.magnitude * (1 - o.priority_modifier) AS adjusted_magnitude
       FROM PhotoObj p
       LEFT JOIN ObjectTypes o
       ON p.type = o.type;

     
     -- Equivalent Query
     SELECT objID,
       type,
       magnitude,
       CASE
           WHEN type = 'STAR' THEN magnitude * 0.95  -- Slightly lower priority for stars
           WHEN type = 'GALAXY' THEN magnitude * 0.90  -- Medium priority for galaxies
           WHEN type = 'QSO' THEN magnitude * 0.85  -- High priority for quasars
           ELSE magnitude  -- No adjustment for unknown types
       END AS adjusted_magnitude FROM PhotoObj;

     ```

9. **Simplification and Direct Application** ("Simplification")
   - Focuses on simplifying complex queries while maintaining the same logical conditions and outputs.
   - **Example**:
     ```sql
     -- Original Query
     -- Original complex query with a subquery.
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

     
     -- Equivalent Query
     -- Simplified equivalent query.
     SELECT MAX(redshift) AS max_redshift,
       MIN(redshift) AS min_redshift,
       AVG(redshift) AS avg_redshift,
       COUNT(*) AS total_count
     FROM SpecObj
     WHERE class = 'GALAXY'
     AND redshift > 0.1
     AND redshift < 0.3;

     ```

10. **Reordering the Conditions**
    - Tests whether the model maintains query integrity despite reordering of WHERE clause conditions.
    - **Example**:
      ```sql
      -- Original Query
      SELECT objID, ra, dec
      FROM PhotoObj
      WHERE objID = 12345 AND ra > 180 AND dec < 0;

      
      -- Equivalent Query
      SELECT objID, ra, dec
      FROM PhotoObj
      WHERE dec < 0 AND ra > 180 AND objID = 12345;

      ```

## Creating Non-Equivalent Queries

We also explored generating non-equivalent queries to further challenge the LLMs. These tests include:

1. **Using Different Aggregate Functions** ("Aggregate_Function")
   - Modifies aggregate functions to observe changes in group results.
   - **Example**:
     ```sql
     -- Original Query
     SELECT class, AVG(redshift) FROM SpecObj WHERE class = 'GALAXY' GROUP BY class;
     
     -- Non-equivalent Query
     SELECT class, SUM(redshift) FROM SpecObj WHERE class = 'GALAXY' GROUP BY class;

     ```

2. **Changing Join Conditions** ("Change_Join_Condition")
   - Alters join types to test how join conditions affect the results.
   - **Example**:
     ```sql
     -- Original Query
     SELECT p.objID, s.specObjID FROM PhotoObj AS p INNER JOIN SpecObj AS s ON p.objID = s.objID AND s.class = 'STAR';

     
     -- Non-equivalent Query
     SELECT p.objID, s.specObjID FROM PhotoObj AS p LEFT JOIN SpecObj AS s ON p.objID = s.objID AND s.class = 'STAR';

     ```

3. **Modifying Grouping Criteria** ("Group_by_Criteria")
   - Changes grouping fields and observes its impact on aggregation.
   - **Example**:
     ```sql
     -- Original Query
     SELECT fieldID, COUNT(*) FROM PhotoObj GROUP BY fieldID;

     
     -- Non-equivalent Query
     SELECT type, fieldID, COUNT(*) FROM PhotoObj GROUP BY type, fieldID;

     ```

4. **Introducing Subtle Changes**
   - Includes logical conditions, value changes, and operator modifications to assess sensitivity to query specifics.
   - **Logical Conditions Example**:
     ```sql
     -- Original Query
     SELECT objID FROM PhotoObj WHERE type = 'GALAXY' AND ra > 180;
     
     -- Non-equivalent Query
     SELECT objID FROM PhotoObj WHERE type = 'GALAXY' OR ra > 180;
     ```
   - **Changing Values Example**:
     ```sql
     -- Original Query
     SELECT objID FROM PhotoObj WHERE mag_u < 18;
     
     -- Non-equivalent Query
     SELECT objID FROM PhotoObj WHERE mag_u < 20;
     ```
   - **Operators Example**:
     ```sql
     -- Original Query
     SELECT objID FROM PhotoObj WHERE mag_u > 18;
     
     -- Non-equivalent Query
     SELECT objID FROM PhotoObj WHERE mag_u < 18;
     ```

5. **Changing Sorting and Limiting** ("Change_Sorting_Limiting")
   - Varies ordering and pagination to see its effect on the query output.
   - **Example**:
     ```sql
     -- Original Query
     SELECT objID, ra FROM PhotoObj ORDER BY ra DESC LIMIT 10;

     
     -- Non-equivalent Query
     SELECT objID, ra FROM PhotoObj ORDER BY ra ASC LIMIT 10;

     ```

6. **Modifying Order By Criteria** ("Order_by_Column")
   - Adjusts Order By criteria to test the order significance.
   - **Example**:
     ```sql
     -- Original Query
     SELECT objID, ra FROM PhotoObj ORDER BY ra;
     
     -- Non-equivalent Query
     SELECT objID, dec FROM PhotoObj ORDER BY dec;

     ```

7. **Ambiguous Column References**
   - Introduces errors in column references to evaluate error detection capabilities.
     ```sql
     -- Original Query
     SELECT objID, ra, dec FROM PhotoObj;

     -- Non Equivalent Query
     SELECT objID, ra FROM PhotoObj;
     ```
8. - **Change Table Name**:
   - Introduces errors in table names.
     ```sql
     -- Original Query
     SELECT objID, ra FROM PhotoObj;
     
     -- Non Equivalent Query
     SELECT objID, ra FROM PhotoObject;

     ```

These categories help in thoroughly evaluating the adaptability and accuracy of LLMs in SQL query manipulation and understanding.

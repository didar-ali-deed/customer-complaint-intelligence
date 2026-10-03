
-- 01_complaints_by_year
SELECT year,COUNT(*) complaints FROM fact_complaints GROUP BY year ORDER BY year;
-- 02_complaints_by_month
SELECT year_month,COUNT(*) complaints FROM fact_complaints GROUP BY year_month ORDER BY year_month;
-- 03_month_over_month_growth
WITH m AS (SELECT year_month,COUNT(*) complaints FROM fact_complaints GROUP BY year_month), p AS (SELECT *,LAG(complaints) OVER(ORDER BY year_month) prior_month FROM m) SELECT *,complaints-prior_month change,1.0*(complaints-prior_month)/NULLIF(prior_month,0) change_pct FROM p ORDER BY year_month;
-- 04_year_over_year_growth
WITH m AS (SELECT year,COUNT(*) complaints FROM fact_complaints GROUP BY year), p AS (SELECT *,LAG(complaints) OVER(ORDER BY year) prior_year FROM m) SELECT *,complaints-prior_year change,1.0*(complaints-prior_year)/NULLIF(prior_year,0) change_pct FROM p ORDER BY year;
-- 05_top_products
SELECT p.product,COUNT(*) complaints,RANK() OVER(ORDER BY COUNT(*) DESC) rank FROM fact_complaints f JOIN dim_product p USING(product_id) GROUP BY p.product ORDER BY complaints DESC;
-- 06_top_issues
SELECT i.issue,COUNT(*) complaints,RANK() OVER(ORDER BY COUNT(*) DESC) rank FROM fact_complaints f JOIN dim_issue i USING(issue_id) GROUP BY i.issue ORDER BY complaints DESC LIMIT 100;
-- 07_top_sub_issues
SELECT sub_issue,COUNT(*) complaints FROM fact_complaints WHERE sub_issue IS NOT NULL GROUP BY sub_issue ORDER BY complaints DESC LIMIT 100;
-- 08_top_companies
SELECT c.company,COUNT(*) complaints,RANK() OVER(ORDER BY COUNT(*) DESC) rank FROM fact_complaints f JOIN dim_company c USING(company_id) GROUP BY c.company ORDER BY complaints DESC LIMIT 100;
-- 09_timely_response_by_company
SELECT c.company,COUNT(*) complaints,AVG(timely_response_flag)*100 timely_response_pct FROM fact_complaints f JOIN dim_company c USING(company_id) WHERE timely_response_flag IS NOT NULL GROUP BY c.company HAVING COUNT(*)>=100 ORDER BY timely_response_pct;
-- 10_timely_response_by_product
SELECT p.product,COUNT(*) eligible,AVG(timely_response_flag)*100 timely_response_pct FROM fact_complaints f JOIN dim_product p USING(product_id) WHERE timely_response_flag IS NOT NULL GROUP BY p.product ORDER BY eligible DESC;
-- 11_company_response_categories
SELECT COALESCE(company_response_to_consumer,'Unknown') response,COUNT(*) complaints FROM fact_complaints GROUP BY response ORDER BY complaints DESC;
-- 12_complaints_by_state
SELECT g.state,COUNT(*) complaints FROM fact_complaints f JOIN dim_geography g USING(state_id) GROUP BY g.state ORDER BY complaints DESC;
-- 13_submission_channel
SELECT ch.submitted_via channel,COUNT(*) complaints FROM fact_complaints f JOIN dim_channel ch USING(channel_id) GROUP BY ch.submitted_via ORDER BY complaints DESC;
-- 14_product_year_growth
WITH y AS(SELECT p.product,year,COUNT(*) n FROM fact_complaints f JOIN dim_product p USING(product_id) GROUP BY 1,2), l AS(SELECT *,LAG(n) OVER(PARTITION BY product ORDER BY year) prev FROM y) SELECT *,n-prev change,1.0*(n-prev)/NULLIF(prev,0) growth_pct FROM l ORDER BY year DESC,growth_pct DESC;
-- 15_issue_year_growth
WITH y AS(SELECT i.issue,year,COUNT(*) n FROM fact_complaints f JOIN dim_issue i USING(issue_id) GROUP BY 1,2), l AS(SELECT *,LAG(n) OVER(PARTITION BY issue ORDER BY year) prev FROM y) SELECT *,n-prev change,1.0*(n-prev)/NULLIF(prev,0) growth_pct FROM l WHERE prev>=100 ORDER BY year DESC,growth_pct DESC LIMIT 500;
-- 16_product_issue_combinations
SELECT p.product,i.issue,COUNT(*) complaints,DENSE_RANK() OVER(PARTITION BY p.product ORDER BY COUNT(*) DESC) issue_rank FROM fact_complaints f JOIN dim_product p USING(product_id) JOIN dim_issue i USING(issue_id) GROUP BY 1,2 ORDER BY complaints DESC LIMIT 250;
-- 17_company_product_combinations
SELECT c.company,p.product,COUNT(*) complaints,AVG(timely_response_flag)*100 timely_pct FROM fact_complaints f JOIN dim_company c USING(company_id) JOIN dim_product p USING(product_id) GROUP BY 1,2 ORDER BY complaints DESC LIMIT 250;
-- 18_rolling_3_month
WITH m AS(SELECT year_month,COUNT(*) n FROM fact_complaints GROUP BY 1) SELECT year_month,n,SUM(n) OVER(ORDER BY year_month ROWS BETWEEN 2 PRECEDING AND CURRENT ROW) rolling_3_month FROM m ORDER BY year_month;
-- 19_rolling_12_month
WITH m AS(SELECT year_month,COUNT(*) n FROM fact_complaints GROUP BY 1) SELECT year_month,n,SUM(n) OVER(ORDER BY year_month ROWS BETWEEN 11 PRECEDING AND CURRENT ROW) rolling_12_month FROM m ORDER BY year_month;
-- 20_company_ranks_by_year
WITH y AS(SELECT c.company,year,COUNT(*) n FROM fact_complaints f JOIN dim_company c USING(company_id) GROUP BY 1,2) SELECT *,RANK() OVER(PARTITION BY year ORDER BY n DESC) company_rank FROM y ORDER BY year,company_rank LIMIT 1000;
-- 21_product_ranks_by_year
WITH y AS(SELECT p.product,year,COUNT(*) n FROM fact_complaints f JOIN dim_product p USING(product_id) GROUP BY 1,2) SELECT *,RANK() OVER(PARTITION BY year ORDER BY n DESC) product_rank FROM y ORDER BY year,product_rank;
-- 22_state_year_growth
WITH y AS(SELECT g.state,year,COUNT(*) n FROM fact_complaints f JOIN dim_geography g USING(state_id) GROUP BY 1,2), l AS(SELECT *,LAG(n) OVER(PARTITION BY state ORDER BY year) prev FROM y) SELECT *,n-prev change,1.0*(n-prev)/NULLIF(prev,0) growth_pct FROM l WHERE prev>=100 ORDER BY year DESC,growth_pct DESC;
-- 23_narrative_availability
SELECT year,COUNT(*) complaints,SUM(has_narrative) narratives,100.0*AVG(has_narrative) narrative_pct FROM fact_complaints GROUP BY year ORDER BY year;
-- 24_response_time
SELECT company_response_to_consumer,COUNT(*) complaints,AVG(response_days) avg_days,MEDIAN(response_days) median_days,MAX(response_days) max_days FROM fact_complaints WHERE response_days>=0 GROUP BY company_response_to_consumer ORDER BY complaints DESC;
-- 25_company_concentration
WITH c AS(SELECT company_id,COUNT(*) n FROM fact_complaints GROUP BY 1), t AS(SELECT SUM(n) total FROM c), r AS(SELECT n,ROW_NUMBER() OVER(ORDER BY n DESC) rn FROM c) SELECT COUNT(*) companies,SUM(CASE WHEN rn<=10 THEN n ELSE 0 END) top_10_count,1.0*SUM(CASE WHEN rn<=10 THEN n ELSE 0 END)/(SELECT total FROM t) top_10_share FROM r;
-- 26_product_concentration
WITH p AS(SELECT product_id,COUNT(*) n FROM fact_complaints GROUP BY 1),r AS(SELECT n,ROW_NUMBER() OVER(ORDER BY n DESC) rn FROM p) SELECT SUM(CASE WHEN rn<=3 THEN n ELSE 0 END) top_3_product_count,1.0*SUM(CASE WHEN rn<=3 THEN n ELSE 0 END)/(SELECT COUNT(*) FROM fact_complaints) top_3_product_share FROM r;
-- 27_issue_concentration
WITH i AS(SELECT issue_id,COUNT(*) n FROM fact_complaints GROUP BY 1),r AS(SELECT n,ROW_NUMBER() OVER(ORDER BY n DESC) rn FROM i) SELECT SUM(CASE WHEN rn<=10 THEN n ELSE 0 END) top_10_issue_count,1.0*SUM(CASE WHEN rn<=10 THEN n ELSE 0 END)/(SELECT COUNT(*) FROM fact_complaints) top_10_issue_share FROM r;
-- 28_response_days_by_product
SELECT p.product,COUNT(response_days) observations,AVG(response_days) mean_days,MEDIAN(response_days) median_days FROM fact_complaints f JOIN dim_product p USING(product_id) WHERE response_days>=0 GROUP BY p.product ORDER BY median_days DESC;
-- 29_channel_month_trend
SELECT ch.submitted_via channel,year_month,COUNT(*) complaints,SUM(COUNT(*)) OVER(PARTITION BY ch.submitted_via ORDER BY year_month) cumulative FROM fact_complaints f JOIN dim_channel ch USING(channel_id) GROUP BY 1,2 ORDER BY 1,2;
-- 30_timely_response_trend
SELECT year_month,COUNT(*) eligible,SUM(timely_response_flag) timely,100.0*AVG(timely_response_flag) timely_pct FROM fact_complaints WHERE timely_response_flag IS NOT NULL GROUP BY year_month ORDER BY year_month;
-- 31_same_period_yoy_comparison
WITH m AS(SELECT MAX(date_received) max_date FROM fact_complaints), y AS(SELECT CAST(strftime('%Y',max_date) AS INTEGER) current_year,max_date,date(max_date,'-1 year') prior_cutoff FROM m), c AS(SELECT COUNT(*) n FROM fact_complaints,y WHERE date_received BETWEEN printf('%04d-01-01',current_year) AND max_date), p AS(SELECT COUNT(*) n FROM fact_complaints,y WHERE date_received BETWEEN printf('%04d-01-01',current_year-1) AND prior_cutoff) SELECT current_year,max_date current_cutoff,prior_cutoff,current_year-1 prior_year,c.n current_ytd,p.n prior_ytd,c.n-p.n change,1.0*(c.n-p.n)/NULLIF(p.n,0) change_pct FROM y,c,p;
-- 32_same_period_issue_growth
WITH m AS(SELECT MAX(date_received) max_date FROM fact_complaints), y AS(SELECT CAST(strftime('%Y',max_date) AS INTEGER) current_year,max_date,date(max_date,'-1 year') prior_cutoff FROM m), counts AS(SELECT i.issue,SUM(CASE WHEN f.date_received BETWEEN printf('%04d-01-01',y.current_year) AND y.max_date THEN 1 ELSE 0 END) current_n,SUM(CASE WHEN f.date_received BETWEEN printf('%04d-01-01',y.current_year-1) AND y.prior_cutoff THEN 1 ELSE 0 END) prior_n,y.current_year,y.max_date,y.prior_cutoff FROM fact_complaints f JOIN dim_issue i USING(issue_id) CROSS JOIN y WHERE f.date_received BETWEEN printf('%04d-01-01',y.current_year-1) AND y.max_date GROUP BY i.issue) SELECT *,current_n-prior_n change,1.0*(current_n-prior_n)/NULLIF(prior_n,0) growth_pct FROM counts WHERE prior_n>=100 ORDER BY growth_pct DESC LIMIT 100;

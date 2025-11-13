-- Steps Distribution

SELECT
  step_name,
  COUNT(1) AS total_events
FROM
  `ppltx-ba-course.final_project.tutorial`
GROUP BY
  1
ORDER BY
  1

/*
step_name				total_events
	184352
0_Welcome_to_the_app	16494
1_Profile_creation		17518
2_Navigation_overview	17088
3_Feature_discovery		16689
4_Setting_preferences	16243
5_Connecting_accounts	15834
6_Creating_first_item	15404
7_Sharing_content		14823
8_Tutorial_completion	13325
*/

-- Sample User

SELECT
  user_id,
  step_name,
  COUNT(1) AS total_events,
  MIN(timestamp) AS ts
FROM
  `ppltx-ba-course.final_project.tutorial`
WHERE
  TRUE
  AND user_id = 'aed6e2f7'
  AND step_name IS NOT NULL
GROUP BY
  1,
  2
ORDER BY
  1,
  2

/*
user_id		step_name				total_events	ts
aed6e2f7	0_Welcome_to_the_app	1				2025-03-05 06:14:10.636179 UTC
aed6e2f7	1_Profile_creation		1				2025-03-05 06:14:39.872084 UTC
aed6e2f7	2_Navigation_overview	1				2025-03-05 06:15:00.172911 UTC
aed6e2f7	3_Feature_discovery		1				2025-03-05 06:15:29.184737 UTC
aed6e2f7	4_Setting_preferences	1				2025-03-05 06:16:08.883552 UTC
aed6e2f7	5_Connecting_accounts	1				2025-03-05 06:16:36.859046 UTC
aed6e2f7	6_Creating_first_item	1				2025-03-05 06:17:04.003845 UTC
*/
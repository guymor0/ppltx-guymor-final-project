/*
step_name             total_users
                      15000
0_Welcome_to_the_app  15000
1_Profile_creation    14650
2_Navigation_overview 14355
3_Feature_discovery   14015
4_Setting_preferences 13670
5_Connecting_accounts 13337
6_Creating_first_item 13018
7_Sharing_content     12674
8_Tutorial_completion 12323
*/

SELECT
  step_name,
  COUNT(DISTINCT user_id) AS total_users
FROM
  `ppltx-ba-course.final_project.tutorial`
WHERE
  step_name IS NOT NULL
GROUP BY
  1
ORDER BY
  1

-- Funnels by step and app_version

SELECT
  step_name,
  app_version,
  COUNT(DISTINCT user_id) AS total_users
FROM
  `ppltx-ba-course.final_project.tutorial`
WHERE
  step_name IS NOT NULL
GROUP BY
  1, 2
ORDER BY
  1, 2
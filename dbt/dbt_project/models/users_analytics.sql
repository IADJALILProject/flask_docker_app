-- Modèle analytique simple
SELECT 
    subscription_type,
    COUNT(*) AS user_count,
    AVG(monthly_spend) AS avg_spend
FROM {{ ref('stg_users_csv') }}
GROUP BY 1

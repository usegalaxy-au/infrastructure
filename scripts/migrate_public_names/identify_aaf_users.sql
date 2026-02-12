DROP VIEW IF EXISTS aaf_user_flags;

CREATE TEMP VIEW aaf_user_flags AS
WITH custos_tokens AS (
  SELECT
    t.user_id,
    t.expiration_time,
    (
      convert_from(
        decode(
          (
            replace(replace(split_part(COALESCE(NULLIF(t.id_token, ''), t.refresh_token), '.', 2), '-', '+'), '_', '/')
            || repeat('=', (4 - length(replace(replace(split_part(COALESCE(NULLIF(t.id_token, ''), t.refresh_token), '.', 2), '-', '+'), '_', '/')) % 4) % 4)
          ),
          'base64'
        ),
        'utf8'
      )
    )::jsonb AS claims
  FROM custos_authnz_token t
  WHERE COALESCE(NULLIF(t.id_token, ''), t.refresh_token) IS NOT NULL
),
custos_agg AS (
  SELECT
    ct.user_id,
    bool_or(ct.claims->>'iss' = 'https://central.aaf.edu.au') AS has_aaf,
    max(
      GREATEST(
        ct.expiration_time,
        to_timestamp(
          COALESCE((ct.claims->>'auth_time')::double precision, (ct.claims->>'iat')::double precision)
        )
      )
    ) AS last_aaf_login_at,
    max(ct.expiration_time) AS max_token_exp,
    max(ct.claims->>'email') FILTER (
      WHERE ct.claims->>'iss' = 'https://central.aaf.edu.au' AND ct.claims->>'email' IS NOT NULL
    ) AS aaf_email
  FROM custos_tokens ct
  GROUP BY ct.user_id
),
session_agg AS (
  SELECT
    s.user_id,
    max(s.last_action) AS last_session_action
  FROM galaxy_session s
  GROUP BY s.user_id
),
history_agg AS (
  SELECT
    h.user_id,
    max(h.update_time) AS last_history_update
  FROM history h
  GROUP BY h.user_id
),
base AS (
  SELECT
    u.id,
    u.email,
    u.username,
    u.create_time,
    u.password,
    ca.has_aaf,
    ca.last_aaf_login_at,
    ca.max_token_exp,
    CASE
      WHEN ca.aaf_email IS NOT NULL AND lower(ca.aaf_email) <> lower(u.email) THEN ca.aaf_email
      ELSE NULL
    END AS mismatching_aaf_email,
    GREATEST(sa.last_session_action, ha.last_history_update) AS last_activity_time,
    CASE
      WHEN ca.has_aaf
           AND ca.last_aaf_login_at IS NOT NULL
           AND GREATEST(sa.last_session_action, ha.last_history_update) BETWEEN ca.last_aaf_login_at - interval '7 days'
                                           AND ca.last_aaf_login_at + interval '7 days'
        THEN 'likely_aaf'
      WHEN ca.has_aaf
           AND ca.last_aaf_login_at IS NOT NULL
           AND GREATEST(sa.last_session_action, ha.last_history_update) > ca.last_aaf_login_at + interval '7 days'
        THEN 'likely_local'
      WHEN COALESCE(ca.has_aaf, false) = false THEN 'local'
      ELSE 'unknown'
    END AS last_login_method_guess
  FROM galaxy_user u
  LEFT JOIN custos_agg ca ON ca.user_id = u.id
  LEFT JOIN session_agg sa ON sa.user_id = u.id
  LEFT JOIN history_agg ha ON ha.user_id = u.id
  WHERE u.purged = false
),
proposed AS (
  SELECT
    b.*,
    CASE
      WHEN b.mismatching_aaf_email IS NULL THEN NULL
      WHEN b.last_login_method_guess = 'likely_aaf' THEN b.mismatching_aaf_email
      WHEN b.last_login_method_guess = 'likely_local' THEN b.email
      ELSE NULL
    END AS proposed_email
  FROM base b
)
SELECT
  p.*,
  CASE
    WHEN p.proposed_email IS NULL THEN false
    ELSE EXISTS (
      SELECT 1
      FROM base b2
      WHERE lower(b2.email) = lower(p.proposed_email)
        AND b2.id <> p.id
    )
  END AS proposed_email_conflict,
  CASE
    WHEN p.proposed_email IS NULL THEN NULL
    WHEN EXISTS (
      SELECT 1
      FROM base b2
      WHERE lower(b2.email) = lower(p.proposed_email)
        AND b2.id <> p.id
    ) THEN p.proposed_email
    ELSE NULL
  END AS conflicting_email,
  (
    SELECT string_agg(b2.id::text, ',' ORDER BY b2.id)
    FROM base b2
    WHERE p.proposed_email IS NOT NULL
      AND lower(b2.email) = lower(p.proposed_email)
      AND b2.id <> p.id
  ) AS conflicting_user_ids
FROM proposed p;

-- Export detailed results
\copy (SELECT id, email, username, create_time, password, has_aaf, last_aaf_login_at, mismatching_aaf_email, proposed_email, proposed_email_conflict, conflicting_email, conflicting_user_ids, last_activity_time, last_login_method_guess FROM aaf_user_flags ORDER BY id) TO 'aaf_user_flags.csv' WITH (FORMAT csv, HEADER true);

-- Export aggregate counts
\copy (SELECT count(*) AS total_users, count(*) FILTER (WHERE last_login_method_guess = 'local') AS local_count, count(*) FILTER (WHERE last_login_method_guess = 'likely_local') AS last_login_likely_local, count(*) FILTER (WHERE last_login_method_guess = 'likely_aaf') AS last_login_likely_aaf, count(*) FILTER (WHERE last_login_method_guess = 'unknown') AS unknown_count, count(*) FILTER (WHERE has_aaf) AS has_aaf_count, count(*) FILTER (WHERE mismatching_aaf_email IS NOT NULL) AS mismatching_email_count, count(*) FILTER (WHERE mismatching_aaf_email IS NOT NULL AND last_login_method_guess = 'likely_aaf') AS mismatching_emails_last_login_aaf_count, count(*) FILTER (WHERE proposed_email_conflict) AS conflict_count FROM aaf_user_flags) TO 'aaf_user_flags_aggregate.csv' WITH (FORMAT csv, HEADER true);

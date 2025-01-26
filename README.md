## Question 1: Understanding Docker First Run

Run the following Docker command to start a Python container with an interactive Bash shell:

```bash
docker run -it --entrypoint bash python:3.12.8
```

Once inside the container, verify the pip version:

```bash
pip --version
```

---

## Question 3: Trip Segmentation Count

```sql
SELECT
    COUNT(*) AS total_trips,
    CASE
        WHEN trip_distance <= 1.0 THEN '0-1'
        WHEN trip_distance > 1.0 AND trip_distance <= 3.0 THEN '1-3'
        WHEN trip_distance > 3.0 AND trip_distance <= 7.0 THEN '3-7'
        WHEN trip_distance > 7.0 AND trip_distance <= 10.0 THEN '7-10'
        ELSE '>10'
    END AS distance_range
FROM public.tripdata
WHERE
    lpep_pickup_datetime::DATE BETWEEN '2019-10-01' AND '2019-10-31'
    AND lpep_dropoff_datetime::DATE BETWEEN '2019-10-01' AND '2019-10-31'
GROUP BY distance_range
ORDER BY distance_range;
```

Uncomment the relevant distance range as needed.

---

## Question 4: Longest Trip for Each Day

```sql
SELECT lpep_pickup_datetime::DATE
FROM public.green_taxi
WHERE lpep_pickup_datetime::DATE IN ('2019-10-11', '2019-10-24', '2019-10-26', '2019-10-31')
GROUP BY lpep_pickup_datetime::DATE
ORDER BY MAX(trip_distance) DESC
LIMIT 1;
```

---

## Question 5: Three Biggest Pickup Zones

```sql
SELECT tzl."Zone", SUM(td.total_amount) AS total_amount_sum
FROM public.tripdata AS td
INNER JOIN public.taxi_zone_lookup AS tzl
ON td."PULocationID" = tzl."LocationID"
WHERE td.lpep_pickup_datetime::DATE = '2019-10-18'
GROUP BY tzl."Zone"
HAVING SUM(td.total_amount) > 13000
ORDER BY total_amount_sum DESC
LIMIT 3;
```

---

## Question 6: Largest Tip

```sql
SELECT do_tzl."Zone"
FROM public.tripdata AS td
INNER JOIN public.taxi_zone_lookup AS pu_tzl ON td."PULocationID" = pu_tzl."LocationID"
INNER JOIN public.taxi_zone_lookup AS do_tzl ON td."DOLocationID" = do_tzl."LocationID"
WHERE TO_CHAR(td.lpep_pickup_datetime, 'YYYY-MM') = '2019-10'
  AND pu_tzl."Zone" = 'East Harlem North'
ORDER BY td.tip_amount DESC
LIMIT 1;
```


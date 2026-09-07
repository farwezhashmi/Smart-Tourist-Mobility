INSERT INTO locations (name, location_type, zone, point, accessibility_notes)
SELECT seed.name, seed.location_type, seed.zone, ST_SetSRID(ST_MakePoint(seed.longitude, seed.latitude), 4326)::geography, seed.accessibility_notes
FROM (VALUES
    ('Secunderabad Railway Station', 'transport_hub', 'Secunderabad', 78.5011, 17.4399, 'Railway concourse and road-level pickup access'),
    ('Charminar', 'attraction', 'Old City', 78.4747, 17.3616, 'Pedestrian approaches can be crowded'),
    ('Hussain Sagar Lake', 'attraction', 'Tank Bund', 78.4734, 17.4239, 'Accessible promenade sections vary'),
    ('Golconda Fort', 'attraction', 'Golconda', 78.4011, 17.3833, 'Historic site with uneven surfaces'),
    ('Rajiv Gandhi International Airport', 'transport_hub', 'Shamshabad', 78.4294, 17.2403, 'Terminal drop-off and accessible facilities'),
    ('Nampally', 'transport_hub', 'Nampally', 78.4677, 17.3936, 'Rail and road interchange with busy approaches')
) AS seed(name, location_type, zone, longitude, latitude, accessibility_notes)
WHERE NOT EXISTS (SELECT 1 FROM locations WHERE locations.name = seed.name);

INSERT INTO transport_modes (code, name, is_public, supports_accessibility, emission_factor_g_per_km)
VALUES
    ('auto', 'Auto-rickshaw', FALSE, FALSE, 115.00),
    ('cab', 'Cab', FALSE, TRUE, 140.00),
    ('bus', 'City bus', TRUE, TRUE, 80.00),
    ('metro', 'Metro', TRUE, TRUE, 35.00),
    ('walking', 'Walking', TRUE, TRUE, 0.00)
ON CONFLICT (code) DO UPDATE SET
    name = EXCLUDED.name,
    is_public = EXCLUDED.is_public,
    supports_accessibility = EXCLUDED.supports_accessibility,
    emission_factor_g_per_km = EXCLUDED.emission_factor_g_per_km;

WITH route_seed(origin_name, destination_name, mode_code, distance_km, duration_min, walking_distance_m, transfer_count, is_accessible) AS (VALUES
    ('Secunderabad Railway Station', 'Charminar', 'auto', 7.4, 28, 250, 0, FALSE), ('Secunderabad Railway Station', 'Charminar', 'cab', 7.8, 25, 180, 0, TRUE), ('Secunderabad Railway Station', 'Charminar', 'bus', 8.2, 42, 450, 1, TRUE), ('Secunderabad Railway Station', 'Charminar', 'metro', 9.0, 38, 350, 1, TRUE),
    ('Secunderabad Railway Station', 'Hussain Sagar Lake', 'auto', 4.5, 18, 180, 0, FALSE), ('Secunderabad Railway Station', 'Hussain Sagar Lake', 'cab', 4.8, 16, 120, 0, TRUE), ('Secunderabad Railway Station', 'Hussain Sagar Lake', 'bus', 5.2, 28, 300, 1, TRUE), ('Secunderabad Railway Station', 'Hussain Sagar Lake', 'metro', 5.8, 25, 250, 1, TRUE),
    ('Secunderabad Railway Station', 'Golconda Fort', 'auto', 12.5, 42, 300, 0, FALSE), ('Secunderabad Railway Station', 'Golconda Fort', 'cab', 13.0, 38, 220, 0, TRUE), ('Secunderabad Railway Station', 'Golconda Fort', 'bus', 14.0, 70, 650, 2, TRUE), ('Secunderabad Railway Station', 'Golconda Fort', 'metro', 15.0, 62, 500, 2, TRUE),
    ('Rajiv Gandhi International Airport', 'Charminar', 'auto', 19.5, 58, 350, 0, FALSE), ('Rajiv Gandhi International Airport', 'Charminar', 'cab', 20.0, 48, 250, 0, TRUE), ('Rajiv Gandhi International Airport', 'Charminar', 'bus', 22.0, 95, 900, 2, TRUE), ('Rajiv Gandhi International Airport', 'Charminar', 'metro', 23.0, 82, 700, 2, TRUE),
    ('Nampally', 'Charminar', 'auto', 3.8, 18, 180, 0, FALSE), ('Nampally', 'Charminar', 'cab', 4.0, 15, 120, 0, TRUE), ('Nampally', 'Charminar', 'bus', 4.5, 25, 300, 1, TRUE), ('Nampally', 'Charminar', 'metro', 5.0, 23, 250, 1, TRUE),
    ('Nampally', 'Golconda Fort', 'auto', 8.5, 32, 250, 0, FALSE), ('Nampally', 'Golconda Fort', 'cab', 9.0, 28, 180, 0, TRUE), ('Nampally', 'Golconda Fort', 'bus', 9.8, 52, 500, 1, TRUE), ('Nampally', 'Golconda Fort', 'metro', 10.5, 47, 450, 1, TRUE)
)
INSERT INTO routes (origin_location_id, destination_location_id, mode_id, provider, provider_route_id, distance_km, duration_min, walking_distance_m, transfer_count, is_accessible, source_type, source_reference)
SELECT origin.id, destination.id, mode.id, 'hyderabad_demo', route_seed.mode_code || '-' || route_seed.origin_name || '-' || route_seed.destination_name, route_seed.distance_km, route_seed.duration_min, route_seed.walking_distance_m, route_seed.transfer_count, route_seed.is_accessible, 'synthetic_demo', 'phase-2-demo-seed'
FROM route_seed
JOIN locations origin ON origin.name = route_seed.origin_name
JOIN locations destination ON destination.name = route_seed.destination_name
JOIN transport_modes mode ON mode.code::text = route_seed.mode_code
WHERE NOT EXISTS (
    SELECT 1 FROM routes existing
    WHERE existing.origin_location_id = origin.id
      AND existing.destination_location_id = destination.id
      AND existing.mode_id = mode.id
);

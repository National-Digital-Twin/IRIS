{% macro drop_tables() %}
    DO $$
    DECLARE
        r RECORD;
    BEGIN
        FOR r IN (SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public')
        LOOP
            EXECUTE 'DROP TABLE IF EXISTS ' || r.table_name || ' CASCADE';
        END LOOP;
    END $$;
{% endmacro %}

-- Run this if you are updating an existing database to ensure all fields exist

-- 1. Ensure user_profiles has birth_date
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='user_profiles' AND column_name='birth_date') THEN
        ALTER TABLE user_profiles ADD COLUMN birth_date DATE;
    END IF;
END $$;

-- 2. Ensure orders has imei and delivery_address
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='orders' AND column_name='imei') THEN
        ALTER TABLE orders ADD COLUMN imei TEXT;
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='orders' AND column_name='delivery_address') THEN
        ALTER TABLE orders ADD COLUMN delivery_address JSONB;
    END IF;
END $$;

-- 3. Ensure contract_url exists in orders
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='orders' AND column_name='contract_url') THEN
        ALTER TABLE orders ADD COLUMN contract_url TEXT;
    END IF;
END $$;

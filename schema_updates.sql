-- Run this to fix the missing phone column in user_profiles
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='user_profiles' AND column_name='phone') THEN
        ALTER TABLE user_profiles ADD COLUMN phone TEXT;
    END IF;
END $$;

-- Previous updates (kept for safety)
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='user_profiles' AND column_name='birth_date') THEN
        ALTER TABLE user_profiles ADD COLUMN birth_date DATE;
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='orders' AND column_name='imei') THEN
        ALTER TABLE orders ADD COLUMN imei TEXT;
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='orders' AND column_name='delivery_address') THEN
        ALTER TABLE orders ADD COLUMN delivery_address JSONB;
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='orders' AND column_name='contract_url') THEN
        ALTER TABLE orders ADD COLUMN contract_url TEXT;
    END IF;
END $$;

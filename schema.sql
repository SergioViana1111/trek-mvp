-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. COMPANIES Table
CREATE TABLE IF NOT EXISTS companies (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    cnpj TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    address TEXT,
    responsible_cpf TEXT,
    logo_url TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now())
);

-- 2. USERS Table (Custom profile management)
CREATE TABLE IF NOT EXISTS user_profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID REFERENCES companies(id),
    name TEXT NOT NULL,
    cpf TEXT UNIQUE NOT NULL,
    birth_date DATE,
    role TEXT CHECK (role IN ('admin', 'hr', 'employee', 'dispatch')),
    email TEXT,
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now())
);

-- 3. PRODUCTS Table (Phones)
CREATE TABLE IF NOT EXISTS products (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    brand TEXT NOT NULL,
    model TEXT NOT NULL,
    description TEXT,
    image_url TEXT,
    monthly_price NUMERIC(10, 2),
    insurance_price NUMERIC(10, 2),
    residual_value NUMERIC(10, 2),
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now())
);

-- 4. MOVEMENTS Table (HR Uploads)
CREATE TABLE IF NOT EXISTS movements (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID REFERENCES companies(id),
    filename TEXT,
    type TEXT CHECK (type IN ('admissao', 'demissao')),
    processed_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now())
);

-- 5. ORDERS Table
CREATE TABLE IF NOT EXISTS orders (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES user_profiles(id),
    product_id UUID REFERENCES products(id),
    company_id UUID REFERENCES companies(id),
    status TEXT CHECK (status IN ('created', 'contract_signed', 'imei_linked', 'dispatched', 'cancelled', 'returned')) DEFAULT 'created',
    contract_url TEXT,
    signed_at TIMESTAMP WITH TIME ZONE,
    imei TEXT,
    delivery_address JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now())
);

-- RLS Policies (Optional for MVP if using Service Key, but good practice)
-- Enabling RLS
ALTER TABLE companies ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE products ENABLE ROW LEVEL SECURITY;
ALTER TABLE movements ENABLE ROW LEVEL SECURITY;
ALTER TABLE orders ENABLE ROW LEVEL SECURITY;

-- For MVP simplicity, we might allow public read/write if using Service Role in backend, 
-- or specific policies if using Anon Key. 
-- For now, letting everything be accessible given the requirements imply backend logic (Streamlit) handles auth.
CREATE POLICY "Enable all access for service role" ON companies FOR ALL USING (true);
CREATE POLICY "Enable all access for service role" ON user_profiles FOR ALL USING (true);
CREATE POLICY "Enable all access for service role" ON products FOR ALL USING (true);
CREATE POLICY "Enable all access for service role" ON movements FOR ALL USING (true);
CREATE POLICY "Enable all access for service role" ON orders FOR ALL USING (true);

-- Insert Test Company
INSERT INTO companies (id, cnpj, name, address) 
VALUES 
('00000000-0000-0000-0000-000000000001', '00.000.000/0001-00', 'Empresa Demo', 'Rua Exemplo, 123');

-- Insert Test Users
INSERT INTO user_profiles (company_id, name, cpf, birth_date, role)
VALUES 
-- Admin (IBUG)
('00000000-0000-0000-0000-000000000001', 'Admin Trek', '00000000000', '1990-01-01', 'admin'),
-- Functionário (Employee)
('00000000-0000-0000-0000-000000000001', 'João Silva', '11122233344', '1995-05-20', 'employee'),
-- Expedição (Dispatch)
('00000000-0000-0000-0000-000000000001', 'Expedição', '99988877766', '1985-10-10', 'dispatch');

-- Insert Test Products
INSERT INTO products (brand, model, description, monthly_price, image_url, active)
VALUES
('Samsung', 'Galaxy S23', '128GB, Tela 6.1, 5G', 149.90, 'https://images.samsung.com/is/image/samsung/p6pim/br/sm-s911bzkpzto/gallery/br-galaxy-s23-s911-sm-s911bzkpzto-534853685?$650_519_PNG$', TRUE),
('Apple', 'iPhone 14', '128GB, Tela 6.1, 5G', 199.90, 'https://store.storeimages.cdn-apple.com/4982/as-images.apple.com/is/iphone-14-model-unselect-gallery-2-202209?wid=5120&hei=2880&fmt=p-jpg', TRUE);

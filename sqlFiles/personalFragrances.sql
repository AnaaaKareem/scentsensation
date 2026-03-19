-- Emporio Armani - Because It’s You
INSERT INTO PRODUCTS (brand, product_name, description, price, personalisable)
VALUES ('Emporio Armani', 'Because It’s You', 'A romantic floral fruity fragrance', 95.00, TRUE);
SET @product_id = LAST_INSERT_ID();
INSERT INTO PERSONAL_FRAGRANCES (product_id, size, fragrance_family, gender, concentration, personalisation_options)
VALUES
(@product_id, '50ml', 'Floral', 'F', 'Eau de Parfum', 'Custom Text Available'),
(@product_id, '100ml', 'Floral', 'F', 'Eau de Parfum', 'Custom Text Available');
INSERT INTO PRODUCT_IMAGES (product_id, image) VALUES
(@product_id, '/images/armani/because_its_you_1.jpg'),
(@product_id, '/images/armani/because_its_you_2.jpg'),
(@product_id, '/images/armani/because_its_you_3.jpg');

-- Emporio Armani - Sí Passione
INSERT INTO PRODUCTS (brand, product_name, description, price, personalisable)
VALUES ('Emporio Armani', 'Sí Passione', 'A bold and passionate floral scent', 85.00, TRUE);
SET @product_id = LAST_INSERT_ID();
INSERT INTO PERSONAL_FRAGRANCES (product_id, size, fragrance_family, gender, concentration, personalisation_options)
VALUES
(@product_id, '30ml', 'Floral', 'F', 'Eau de Parfum', 'No Engraving'),
(@product_id, '50ml', 'Floral', 'F', 'Eau de Parfum', 'No Engraving');
INSERT INTO PRODUCT_IMAGES (product_id, image) VALUES
(@product_id, '/images/armani/si_passione_1.jpg'),
(@product_id, '/images/armani/si_passione_2.jpg');

-- Emporio Armani - Code Absolu
INSERT INTO PRODUCTS (brand, product_name, description, price, personalisable)
VALUES ('Emporio Armani', 'Code Absolu', 'A seductive oriental spicy fragrance', 110.00, TRUE);
SET @product_id = LAST_INSERT_ID();
INSERT INTO PERSONAL_FRAGRANCES (product_id, size, fragrance_family, gender, concentration, personalisation_options)
VALUES
(@product_id, '60ml', 'Oriental', 'M', 'Eau de Parfum', 'Custom Text Available'),
(@product_id, '100ml', 'Oriental', 'M', 'Eau de Parfum', 'Custom Text Available');
INSERT INTO PRODUCT_IMAGES (product_id, image) VALUES
(@product_id, '/images/armani/code_absolu_1.jpg'),
(@product_id, '/images/armani/code_absolu_2.jpg'),
(@product_id, '/images/armani/code_absolu_3.jpg');

-- Givenchy - L’Interdit
INSERT INTO PRODUCTS (brand, product_name, description, price, personalisable)
VALUES ('Givenchy', 'L’Interdit', 'A daring floral woody scent', 90.00, TRUE);
SET @product_id = LAST_INSERT_ID();
INSERT INTO PERSONAL_FRAGRANCES (product_id, size, fragrance_family, gender, concentration, personalisation_options)
VALUES
(@product_id, '30ml', 'Floral', 'F', 'Eau de Parfum', 'No Engraving'),
(@product_id, '50ml', 'Floral', 'F', 'Eau de Parfum', 'No Engraving');
INSERT INTO PRODUCT_IMAGES (product_id, image) VALUES
(@product_id, '/images/givenchy/linterdit_1.jpg'),
(@product_id, '/images/givenchy/linterdit_2.jpg');

-- Hugo Boss - Intense
INSERT INTO PRODUCTS (brand, product_name, description, price, personalisable)
VALUES ('Hugo Boss', 'Intense', 'A powerful and bold fragrance', 80.00, TRUE);
SET @product_id = LAST_INSERT_ID();
INSERT INTO PERSONAL_FRAGRANCES (product_id, size, fragrance_family, gender, concentration, personalisation_options)
VALUES
(@product_id, '50ml', 'Woody', 'M', 'Eau de Parfum', 'Custom Text Available'),
(@product_id, '100ml', 'Woody', 'M', 'Eau de Parfum', 'Custom Text Available');
INSERT INTO PRODUCT_IMAGES (product_id, image) VALUES
(@product_id, '/images/hugoboss/intense_1.jpg'),
(@product_id, '/images/hugoboss/intense_2.jpg'),
(@product_id, '/images/hugoboss/intense_3.jpg');

-- Hugo Boss - Femme Elegance
INSERT INTO PRODUCTS (brand, product_name, description, price, personalisable)
VALUES ('Hugo Boss', 'Femme Elegance', 'A refined feminine scent', 75.00, TRUE);
SET @product_id = LAST_INSERT_ID();
INSERT INTO PERSONAL_FRAGRANCES (product_id, size, fragrance_family, gender, concentration, personalisation_options)
VALUES
(@product_id, '30ml', 'Floral', 'F', 'Eau de Toilette', 'No Engraving'),
(@product_id, '50ml', 'Floral', 'F', 'Eau de Toilette', 'No Engraving'),
(@product_id, '100ml', 'Floral', 'F', 'Eau de Toilette', 'No Engraving');
INSERT INTO PRODUCT_IMAGES (product_id, image) VALUES
(@product_id, '/images/hugoboss/femme_elegance_1.jpg'),
(@product_id, '/images/hugoboss/femme_elegance_2.jpg');

-- Hugo Boss - Urban Fusion
INSERT INTO PRODUCTS (brand, product_name, description, price, personalisable)
VALUES ('Hugo Boss', 'Urban Fusion', 'A modern urban-inspired fragrance', 85.00, TRUE);
SET @product_id = LAST_INSERT_ID();
INSERT INTO PERSONAL_FRAGRANCES (product_id, size, fragrance_family, gender, concentration, personalisation_options)
VALUES
(@product_id, '50ml', 'Fresh', 'Unisex', 'Eau de Parfum', 'Custom Text Available'),
(@product_id, '100ml', 'Fresh', 'Unisex', 'Eau de Parfum', 'Custom Text Available');
INSERT INTO PRODUCT_IMAGES (product_id, image) VALUES
(@product_id, '/images/hugoboss/urban_fusion_1.jpg'),
(@product_id, '/images/hugoboss/urban_fusion_2.jpg'),
(@product_id, '/images/hugoboss/urban_fusion_3.jpg');

-- Hugo Boss - Velocity
INSERT INTO PRODUCTS (brand, product_name, description, price, personalisable)
VALUES ('Hugo Boss', 'Velocity', 'A dynamic and fresh scent', 70.00, TRUE);
SET @product_id = LAST_INSERT_ID();
INSERT INTO PERSONAL_FRAGRANCES (product_id, size, fragrance_family, gender, concentration, personalisation_options)
VALUES
(@product_id, '50ml', 'Fresh', 'M', 'Eau de Toilette', 'No Engraving'),
(@product_id, '100ml', 'Fresh', 'M', 'Eau de Toilette', 'No Engraving');
INSERT INTO PRODUCT_IMAGES (product_id, image) VALUES
(@product_id, '/images/hugoboss/velocity_1.jpg'),
(@product_id, '/images/hugoboss/velocity_2.jpg');

-- Hugo Boss - Radiant Bloom
INSERT INTO PRODUCTS (brand, product_name, description, price, personalisable)
VALUES ('Hugo Boss', 'Radiant Bloom', 'A vibrant floral fragrance', 65.00, TRUE);
SET @product_id = LAST_INSERT_ID();
INSERT INTO PERSONAL_FRAGRANCES (product_id, size, fragrance_family, gender, concentration, personalisation_options)
VALUES
(@product_id, '30ml', 'Floral', 'F', 'Eau de Parfum', 'Custom Text Available'),
(@product_id, '50ml', 'Floral', 'F', 'Eau de Parfum', 'Custom Text Available');
INSERT INTO PRODUCT_IMAGES (product_id, image) VALUES
(@product_id, '/images/hugoboss/radiant_bloom_1.jpg'),
(@product_id, '/images/hugoboss/radiant_bloom_2.jpg'),
(@product_id, '/images/hugoboss/radiant_bloom_3.jpg');

-- Paco Rabanne - Invicta
INSERT INTO PRODUCTS (brand, product_name, description, price, personalisable)
VALUES ('Paco Rabanne', 'Invicta', 'An invigorating masculine scent', 85.00, TRUE);
SET @product_id = LAST_INSERT_ID();
INSERT INTO PERSONAL_FRAGRANCES (product_id, size, fragrance_family, gender, concentration, personalisation_options)
VALUES
(@product_id, '50ml', 'Woody', 'M', 'Eau de Parfum', 'Custom Text Available'),
(@product_id, '100ml', 'Woody', 'M', 'Eau de Parfum', 'Custom Text Available');
INSERT INTO PRODUCT_IMAGES (product_id, image) VALUES
(@product_id, '/images/pacorabanne/invicta_1.jpg'),
(@product_id, '/images/pacorabanne/invicta_2.jpg');

-- Paco Rabanne - Belle Allure
INSERT INTO PRODUCTS (brand, product_name, description, price, personalisable)
VALUES ('Paco Rabanne', 'Belle Allure', 'An elegant feminine fragrance', 80.00, TRUE);
SET @product_id = LAST_INSERT_ID();
INSERT INTO PERSONAL_FRAGRANCES (product_id, size, fragrance_family, gender, concentration, personalisation_options)
VALUES
(@product_id, '30ml', 'Floral', 'F', 'Eau de Toilette', 'No Engraving'),
(@product_id, '50ml', 'Floral', 'F', 'Eau de Toilette', 'No Engraving'),
(@product_id, '100ml', 'Floral', 'F', 'Eau de Toilette', 'No Engraving');
INSERT INTO PRODUCT_IMAGES (product_id, image) VALUES
(@product_id, '/images/pacorabanne/belle_allure_1.jpg'),
(@product_id, '/images/pacorabanne/belle_allure_2.jpg'),
(@product_id, '/images/pacorabanne/belle_allure_3.jpg');

-- Paco Rabanne - Element
INSERT INTO PRODUCTS (brand, product_name, description, price, personalisable)
VALUES ('Paco Rabanne', 'Element', 'A fresh elemental scent', 75.00, TRUE);
SET @product_id = LAST_INSERT_ID();
INSERT INTO PERSONAL_FRAGRANCES (product_id, size, fragrance_family, gender, concentration, personalisation_options)
VALUES
(@product_id, '50ml', 'Fresh', 'Unisex', 'Eau de Parfum', 'Custom Text Available'),
(@product_id, '100ml', 'Fresh', 'Unisex', 'Eau de Parfum', 'Custom Text Available');
INSERT INTO PRODUCT_IMAGES (product_id, image) VALUES
(@product_id, '/images/pacorabanne/element_1.jpg'),
(@product_id, '/images/pacorabanne/element_2.jpg');

-- Paco Rabanne - Eclipse Noir
INSERT INTO PRODUCTS (brand, product_name, description, price, personalisable)
VALUES ('Paco Rabanne', 'Eclipse Noir', 'A mysterious dark fragrance', 90.00, TRUE);
SET @product_id = LAST_INSERT_ID();
INSERT INTO PERSONAL_FRAGRANCES (product_id, size, fragrance_family, gender, concentration, personalisation_options)
VALUES
(@product_id, '50ml', 'Oriental', 'Unisex', 'Eau de Parfum', 'No Engraving'),
(@product_id, '100ml', 'Oriental', 'Unisex', 'Eau de Parfum', 'No Engraving');
INSERT INTO PRODUCT_IMAGES (product_id, image) VALUES
(@product_id, '/images/pacorabanne/eclipse_noir_1.jpg'),
(@product_id, '/images/pacorabanne/eclipse_noir_2.jpg'),
(@product_id, '/images/pacorabanne/eclipse_noir_3.jpg');

-- Paco Rabanne - Radiance
INSERT INTO PRODUCTS (brand, product_name, description, price, personalisable)
VALUES ('Paco Rabanne', 'Radiance', 'A luminous floral scent', 70.00, TRUE);
SET @product_id = LAST_INSERT_ID();
INSERT INTO PERSONAL_FRAGRANCES (product_id, size, fragrance_family, gender, concentration, personalisation_options)
VALUES
(@product_id, '30ml', 'Floral', 'F', 'Eau de Parfum', 'Custom Text Available'),
(@product_id, '50ml', 'Floral', 'F', 'Eau de Parfum', 'Custom Text Available');
INSERT INTO PRODUCT_IMAGES (product_id, image) VALUES
(@product_id, '/images/pacorabanne/radiance_1.jpg'),
(@product_id, '/images/pacorabanne/radiance_2.jpg');

-- Tom Ford - Noir Essence
INSERT INTO PRODUCTS (brand, product_name, description, price, personalisable)
VALUES ('Tom Ford', 'Noir Essence', 'A rich and enigmatic scent', 250.00, TRUE);
SET @product_id = LAST_INSERT_ID();
INSERT INTO PERSONAL_FRAGRANCES (product_id, size, fragrance_family, gender, concentration, personalisation_options)
VALUES
(@product_id, '50ml', 'Oriental', 'Unisex', 'Eau de Parfum', 'Custom Text Available'),
(@product_id, '100ml', 'Oriental', 'Unisex', 'Eau de Parfum', 'Custom Text Available');
INSERT INTO PRODUCT_IMAGES (product_id, image) VALUES
(@product_id, '/images/tomford/noir_essence_1.jpg'),
(@product_id, '/images/tomford/noir_essence_2.jpg'),
(@product_id, '/images/tomford/noir_essence_3.jpg');

-- Tom Ford - Velvet Bloom
INSERT INTO PRODUCTS (brand, product_name, description, price, personalisable)
VALUES ('Tom Ford', 'Velvet Bloom', 'A luxurious floral fragrance', 230.00, TRUE);
SET @product_id = LAST_INSERT_ID();
INSERT INTO PERSONAL_FRAGRANCES (product_id, size, fragrance_family, gender, concentration, personalisation_options)
VALUES
(@product_id, '30ml', 'Floral', 'F', 'Eau de Parfum', 'No Engraving'),
(@product_id, '50ml', 'Floral', 'F', 'Eau de Parfum', 'No Engraving');
INSERT INTO PRODUCT_IMAGES (product_id, image) VALUES
(@product_id, '/images/tomford/velvet_bloom_1.jpg'),
(@product_id, '/images/tomford/velvet_bloom_2.jpg');

-- Tom Ford - Urban Mist
INSERT INTO PRODUCTS (brand, product_name, description, price, personalisable)
VALUES ('Tom Ford', 'Urban Mist', 'A sophisticated urban scent', 240.00, TRUE);
SET @product_id = LAST_INSERT_ID();
INSERT INTO PERSONAL_FRAGRANCES (product_id, size, fragrance_family, gender, concentration, personalisation_options)
VALUES
(@product_id, '50ml', 'Fresh', 'Unisex', 'Eau de Parfum', 'Custom Text Available'),
(@product_id, '100ml', 'Fresh', 'Unisex', 'Eau de Parfum', 'Custom Text Available');
INSERT INTO PRODUCT_IMAGES (product_id, image) VALUES
(@product_id, '/images/tomford/urban_mist_1.jpg'),
(@product_id, '/images/tomford/urban_mist_2.jpg'),
(@product_id, '/images/tomford/urban_mist_3.jpg');

-- Tom Ford - Amber Infusion
INSERT INTO PRODUCTS (brand, product_name, description, price, personalisable)
VALUES ('Tom Ford', 'Amber Infusion', 'A warm amber fragrance', 260.00, TRUE);
SET @product_id = LAST_INSERT_ID();
INSERT INTO PERSONAL_FRAGRANCES (product_id, size, fragrance_family, gender, concentration, personalisation_options)
VALUES
(@product_id, '50ml', 'Oriental', 'Unisex', 'Eau de Parfum', 'No Engraving'),
(@product_id, '100ml', 'Oriental', 'Unisex', 'Eau de Parfum', 'No Engraving');
INSERT INTO PRODUCT_IMAGES (product_id, image) VALUES
(@product_id, '/images/tomford/amber_infusion_1.jpg'),
(@product_id, '/images/tomford/amber_infusion_2.jpg');

-- Tom Ford - Radiant Florale
INSERT INTO PRODUCTS (brand, product_name, description, price, personalisable)
VALUES ('Tom Ford', 'Radiant Florale', 'A radiant floral masterpiece', 235.00, TRUE);
SET @product_id = LAST_INSERT_ID();
INSERT INTO PERSONAL_FRAGRANCES (product_id, size, fragrance_family, gender, concentration, personalisation_options)
VALUES
(@product_id, '30ml', 'Floral', 'F', 'Eau de Parfum', 'Custom Text Available'),
(@product_id, '50ml', 'Floral', 'F', 'Eau de Parfum', 'Custom Text Available');
INSERT INTO PRODUCT_IMAGES (product_id, image) VALUES
(@product_id, '/images/tomford/radiant_florale_1.jpg'),
(@product_id, '/images/tomford/radiant_florale_2.jpg'),
(@product_id, '/images/tomford/radiant_florale_3.jpg');

-- Dior - Tempest
INSERT INTO PRODUCTS (brand, product_name, description, price, personalisable)
VALUES ('Dior', 'Tempest', 'A stormy and intense fragrance', 120.00, TRUE);
SET @product_id = LAST_INSERT_ID();
INSERT INTO PERSONAL_FRAGRANCES (product_id, size, fragrance_family, gender, concentration, personalisation_options)
VALUES
(@product_id, '50ml', 'Woody', 'Unisex', 'Eau de Parfum', 'Custom Text Available'),
(@product_id, '100ml', 'Woody', 'Unisex', 'Eau de Parfum', 'Custom Text Available');
INSERT INTO PRODUCT_IMAGES (product_id, image) VALUES
(@product_id, '/images/dior/tempest_1.jpg'),
(@product_id, '/images/dior/tempest_2.jpg');

-- Dior - Fleur de Jour
INSERT INTO PRODUCTS (brand, product_name, description, price, personalisable)
VALUES ('Dior', 'Fleur de Jour', 'A bright daily floral scent', 110.00, TRUE);
SET @product_id = LAST_INSERT_ID();
INSERT INTO PERSONAL_FRAGRANCES (product_id, size, fragrance_family, gender, concentration, personalisation_options)
VALUES
(@product_id, '30ml', 'Floral', 'F', 'Eau de Toilette', 'No Engraving'),
(@product_id, '50ml', 'Floral', 'F', 'Eau de Toilette', 'No Engraving'),
(@product_id, '100ml', 'Floral', 'F', 'Eau de Toilette', 'No Engraving');
INSERT INTO PRODUCT_IMAGES (product_id, image) VALUES
(@product_id, '/images/dior/fleur_de_jour_1.jpg'),
(@product_id, '/images/dior/fleur_de_jour_2.jpg'),
(@product_id, '/images/dior/fleur_de_jour_3.jpg');

-- Dior - Horizon
INSERT INTO PRODUCTS (brand, product_name, description, price, personalisable)
VALUES ('Dior', 'Horizon', 'A vast and open fragrance', 115.00, TRUE);
SET @product_id = LAST_INSERT_ID();
INSERT INTO PERSONAL_FRAGRANCES (product_id, size, fragrance_family, gender, concentration, personalisation_options)
VALUES
(@product_id, '50ml', 'Fresh', 'Unisex', 'Eau de Parfum', 'Custom Text Available'),
(@product_id, '100ml', 'Fresh', 'Unisex', 'Eau de Parfum', 'Custom Text Available');
INSERT INTO PRODUCT_IMAGES (product_id, image) VALUES
(@product_id, '/images/dior/horizon_1.jpg'),
(@product_id, '/images/dior/horizon_2.jpg');

-- Dior - Obsidian
INSERT INTO PRODUCTS (brand, product_name, description, price, personalisable)
VALUES ('Dior', 'Obsidian', 'A dark and mysterious scent', 125.00, TRUE);
SET @product_id = LAST_INSERT_ID();
INSERT INTO PERSONAL_FRAGRANCES (product_id, size, fragrance_family, gender, concentration, personalisation_options)
VALUES
(@product_id, '50ml', 'Oriental', 'Unisex', 'Eau de Parfum', 'No Engraving'),
(@product_id, '100ml', 'Oriental', 'Unisex', 'Eau de Parfum', 'No Engraving');
INSERT INTO PRODUCT_IMAGES (product_id, image) VALUES
(@product_id, '/images/dior/obsidian_1.jpg'),
(@product_id, '/images/dior/obsidian_2.jpg'),
(@product_id, '/images/dior/obsidian_3.jpg');

-- Dior - Serene
INSERT INTO PRODUCTS (brand, product_name, description, price, personalisable)
VALUES ('Dior', 'Serene', 'A calm and peaceful fragrance', 105.00, TRUE);
SET @product_id = LAST_INSERT_ID();
INSERT INTO PERSONAL_FRAGRANCES (product_id, size, fragrance_family, gender, concentration, personalisation_options)
VALUES
(@product_id, '30ml', 'Floral', 'F', 'Eau de Parfum', 'Custom Text Available'),
(@product_id, '50ml', 'Floral', 'F', 'Eau de Parfum', 'Custom Text Available');
INSERT INTO PRODUCT_IMAGES (product_id, image) VALUES
(@product_id, '/images/dior/serene_1.jpg'),
(@product_id, '/images/dior/serene_2.jpg');

-- Chanel - Allure Noire
INSERT INTO PRODUCTS (brand, product_name, description, price, personalisable)
VALUES ('Chanel', 'Allure Noire', 'A captivating dark allure', 130.00, TRUE);
SET @product_id = LAST_INSERT_ID();
INSERT INTO PERSONAL_FRAGRANCES (product_id, size, fragrance_family, gender, concentration, personalisation_options)
VALUES
(@product_id, '50ml', 'Oriental', 'F', 'Eau de Parfum', 'Custom Text Available'),
(@product_id, '100ml', 'Oriental', 'F', 'Eau de Parfum', 'Custom Text Available');
INSERT INTO PRODUCT_IMAGES (product_id, image) VALUES
(@product_id, '/images/chanel/allure_noire_1.jpg'),
(@product_id, '/images/chanel/allure_noire_2.jpg'),
(@product_id, '/images/chanel/allure_noire_3.jpg');

-- Chanel - Belle Étoile
INSERT INTO PRODUCTS (brand, product_name, description, price, personalisable)
VALUES ('Chanel', 'Belle Étoile', 'A starry elegant scent', 125.00, TRUE);
SET @product_id = LAST_INSERT_ID();
INSERT INTO PERSONAL_FRAGRANCES (product_id, size, fragrance_family, gender, concentration, personalisation_options)
VALUES
(@product_id, '30ml', 'Floral', 'F', 'Eau de Toilette', 'No Engraving'),
(@product_id, '50ml', 'Floral', 'F', 'Eau de Toilette', 'No Engraving'),
(@product_id, '100ml', 'Floral', 'F', 'Eau de Toilette', 'No Engraving');
INSERT INTO PRODUCT_IMAGES (product_id, image) VALUES
(@product_id, '/images/chanel/belle_etoile_1.jpg'),
(@product_id, '/images/chanel/belle_etoile_2.jpg');

-- Chanel - Enigma
INSERT INTO PRODUCTS (brand, product_name, description, price, personalisable)
VALUES ('Chanel', 'Enigma', 'A mysterious and intriguing fragrance', 135.00, TRUE);
SET @product_id = LAST_INSERT_ID();
INSERT INTO PERSONAL_FRAGRANCES (product_id, size, fragrance_family, gender, concentration, personalisation_options)
VALUES
(@product_id, '50ml', 'Woody', 'Unisex', 'Eau de Parfum', 'Custom Text Available'),
(@product_id, '100ml', 'Woody', 'Unisex', 'Eau de Parfum', 'Custom Text Available');
INSERT INTO PRODUCT_IMAGES (product_id, image) VALUES
(@product_id, '/images/chanel/enigma_1.jpg'),
(@product_id, '/images/chanel/enigma_2.jpg'),
(@product_id, '/images/chanel/enigma_3.jpg');

-- Chanel - Lumière
INSERT INTO PRODUCTS (brand, product_name, description, price, personalisable)
VALUES ('Chanel', 'Lumière', 'A luminous and radiant scent', 120.00, TRUE);
SET @product_id = LAST_INSERT_ID();
INSERT INTO PERSONAL_FRAGRANCES (product_id, size, fragrance_family, gender, concentration, personalisation_options)
VALUES
(@product_id, '30ml', 'Floral', 'F', 'Eau de Parfum', 'No Engraving'),
(@product_id, '50ml', 'Floral', 'F', 'Eau de Parfum', 'No Engraving');
INSERT INTO PRODUCT_IMAGES (product_id, image) VALUES
(@product_id, '/images/chanel/lumiere_1.jpg'),
(@product_id, '/images/chanel/lumiere_2.jpg');

-- Chanel - D'or
INSERT INTO PRODUCTS (brand, product_name, description, price, personalisable)
VALUES ('Chanel', 'D''or', 'A golden luxurious fragrance', 140.00, TRUE);
SET @product_id = LAST_INSERT_ID();
INSERT INTO PERSONAL_FRAGRANCES (product_id, size, fragrance_family, gender, concentration, personalisation_options)
VALUES
(@product_id, '50ml', 'Oriental', 'Unisex', 'Eau de Parfum', 'Custom Text Available'),
(@product_id, '100ml', 'Oriental', 'Unisex', 'Eau de Parfum', 'Custom Text Available');
INSERT INTO PRODUCT_IMAGES (product_id, image) VALUES
(@product_id, '/images/chanel/dor_1.jpg'),
(@product_id, '/images/chanel/dor_2.jpg'),
(@product_id, '/images/chanel/dor_3.jpg');

-- Lancôme - L'Essence
INSERT INTO PRODUCTS (brand, product_name, description, price, personalisable)
VALUES ('Lancôme', 'L''Essence', 'The essence of elegance', 95.00, TRUE);
SET @product_id = LAST_INSERT_ID();
INSERT INTO PERSONAL_FRAGRANCES (product_id, size, fragrance_family, gender, concentration, personalisation_options)
VALUES
(@product_id, '30ml', 'Floral', 'F', 'Eau de Parfum', 'No Engraving'),
(@product_id, '50ml', 'Floral', 'F', 'Eau de Parfum', 'No Engraving');
INSERT INTO PRODUCT_IMAGES (product_id, image) VALUES
(@product_id, '/images/lancome/lessence_1.jpg'),
(@product_id, '/images/lancome/lessence_2.jpg');

-- Lancôme - Vitalité
INSERT INTO PRODUCTS (brand, product_name, description, price, personalisable)
VALUES ('Lancôme', 'Vitalité', 'A vibrant and lively scent', 100.00, TRUE);
SET @product_id = LAST_INSERT_ID();
INSERT INTO PERSONAL_FRAGRANCES (product_id, size, fragrance_family, gender, concentration, personalisation_options)
VALUES
(@product_id, '50ml', 'Fresh', 'F', 'Eau de Parfum', 'Custom Text Available'),
(@product_id, '100ml', 'Fresh', 'F', 'Eau de Parfum', 'Custom Text Available');
INSERT INTO PRODUCT_IMAGES (product_id, image) VALUES
(@product_id, '/images/lancome/vitalite_1.jpg'),
(@product_id, '/images/lancome/vitalite_2.jpg'),
(@product_id, '/images/lancome/vitalite_3.jpg');

-- Lancôme - Éclat Intense
INSERT INTO PRODUCTS (brand, product_name, description, price, personalisable)
VALUES ('Lancôme', 'Éclat Intense', 'An intense burst of brilliance', 90.00, TRUE);
SET @product_id = LAST_INSERT_ID();
INSERT INTO PERSONAL_FRAGRANCES (product_id, size, fragrance_family, gender, concentration, personalisation_options)
VALUES
(@product_id, '30ml', 'Floral', 'F', 'Eau de Toilette', 'No Engraving'),
(@product_id, '50ml', 'Floral', 'F', 'Eau de Toilette', 'No Engraving');
INSERT INTO PRODUCT_IMAGES (product_id, image) VALUES
(@product_id, '/images/lancome/eclat_intense_1.jpg'),
(@product_id, '/images/lancome/eclat_intense_2.jpg');

-- Lancôme - Sublime Rose
INSERT INTO PRODUCTS (brand, product_name, description, price, personalisable)
VALUES ('Lancôme', 'Sublime Rose', 'A sublime rose fragrance', 85.00, TRUE);
SET @product_id = LAST_INSERT_ID();
INSERT INTO PERSONAL_FRAGRANCES (product_id, size, fragrance_family, gender, concentration, personalisation_options)
VALUES
(@product_id, '30ml', 'Floral', 'F', 'Eau de Parfum', 'Custom Text Available'),
(@product_id, '50ml', 'Floral', 'F', 'Eau de Parfum', 'Custom Text Available');
INSERT INTO PRODUCT_IMAGES (product_id, image) VALUES
(@product_id, '/images/lancome/sublime_rose_1.jpg'),
(@product_id, '/images/lancome/sublime_rose_2.jpg'),
(@product_id, '/images/lancome/sublime_rose_3.jpg');

-- Lancôme - Envoûtant
INSERT INTO PRODUCTS (brand, product_name, description, price, personalisable)
VALUES ('Lancôme', 'Envoûtant', 'An enchanting scent', 105.00, TRUE);
SET @product_id = LAST_INSERT_ID();
INSERT INTO PERSONAL_FRAGRANCES (product_id, size, fragrance_family, gender, concentration, personalisation_options)
VALUES
(@product_id, '50ml', 'Oriental', 'F', 'Eau de Parfum', 'No Engraving'),
(@product_id, '100ml', 'Oriental', 'F', 'Eau de Parfum', 'No Engraving');
INSERT INTO PRODUCT_IMAGES (product_id, image) VALUES
(@product_id, '/images/lancome/envoutant_1.jpg'),
(@product_id, '/images/lancome/envoutant_2.jpg');

-- Yves Saint Laurent - Noir Absolu
INSERT INTO PRODUCTS (brand, product_name, description, price, personalisable)
VALUES ('Yves Saint Laurent', 'Noir Absolu', 'An absolute dark fragrance', 115.00, TRUE);
SET @product_id = LAST_INSERT_ID();
INSERT INTO PERSONAL_FRAGRANCES (product_id, size, fragrance_family, gender, concentration, personalisation_options)
VALUES
(@product_id, '50ml', 'Oriental', 'Unisex', 'Eau de Parfum', 'Custom Text Available'),
(@product_id, '100ml', 'Oriental', 'Unisex', 'Eau de Parfum', 'Custom Text Available');
INSERT INTO PRODUCT_IMAGES (product_id, image) VALUES
(@product_id, '/images/ysl/noir_absolu_1.jpg'),
(@product_id, '/images/ysl/noir_absolu_2.jpg'),
(@product_id, '/images/ysl/noir_absolu_3.jpg');

-- Yves Saint Laurent - Belle Étoile
INSERT INTO PRODUCTS (brand, product_name, description, price, personalisable)
VALUES ('Yves Saint Laurent', 'Belle Étoile', 'A beautiful starry scent', 110.00, TRUE);
SET @product_id = LAST_INSERT_ID();
INSERT INTO PERSONAL_FRAGRANCES (product_id, size, fragrance_family, gender, concentration, personalisation_options)
VALUES
(@product_id, '30ml', 'Floral', 'F', 'Eau de Toilette', 'No Engraving'),
(@product_id, '50ml', 'Floral', 'F', 'Eau de Toilette', 'No Engraving'),
(@product_id, '100ml', 'Floral', 'F', 'Eau de Toilette', 'No Engraving');
INSERT INTO PRODUCT_IMAGES (product_id, image) VALUES
(@product_id, '/images/ysl/belle_etoile_1.jpg'),
(@product_id, '/images/ysl/belle_etoile_2.jpg');

-- Yves Saint Laurent - Urban Mystique
INSERT INTO PRODUCTS (brand, product_name, description, price, personalisable)
VALUES ('Yves Saint Laurent', 'Urban Mystique', 'A mystical urban fragrance', 120.00, TRUE);
SET @product_id = LAST_INSERT_ID();
INSERT INTO PERSONAL_FRAGRANCES (product_id, size, fragrance_family, gender, concentration, personalisation_options)
VALUES
(@product_id, '50ml', 'Woody', 'Unisex', 'Eau de Parfum', 'Custom Text Available'),
(@product_id, '100ml', 'Woody', 'Unisex', 'Eau de Parfum', 'Custom Text Available');
INSERT INTO PRODUCT_IMAGES (product_id, image) VALUES
(@product_id, '/images/ysl/urban_mystique_1.jpg'),
(@product_id, '/images/ysl/urban_mystique_2.jpg'),
(@product_id, '/images/ysl/urban_mystique_3.jpg');

-- Yves Saint Laurent - Lumière
INSERT INTO PRODUCTS (brand, product_name, description, price, personalisable)
VALUES ('Yves Saint Laurent', 'Lumière', 'A light-filled scent', 105.00, TRUE);
SET @product_id = LAST_INSERT_ID();
INSERT INTO PERSONAL_FRAGRANCES (product_id, size, fragrance_family, gender, concentration, personalisation_options)
VALUES
(@product_id, '30ml', 'Floral', 'F', 'Eau de Parfum', 'No Engraving'),
(@product_id, '50ml', 'Floral', 'F', 'Eau de Parfum', 'No Engraving');
INSERT INTO PRODUCT_IMAGES (product_id, image) VALUES
(@product_id, '/images/ysl/lumiere_1.jpg'),
(@product_id, '/images/ysl/lumiere_2.jpg');

-- Yves Saint Laurent - Infini
INSERT INTO PRODUCTS (brand, product_name, description, price, personalisable)
VALUES ('Yves Saint Laurent', 'Infini', 'An infinite fragrance experience', 125.00, TRUE);
SET @product_id = LAST_INSERT_ID();
INSERT INTO PERSONAL_FRAGRANCES (product_id, size, fragrance_family, gender, concentration, personalisation_options)
VALUES
(@product_id, '50ml', 'Woody', 'Unisex', 'Eau de Parfum', 'Custom Text Available'),
(@product_id, '100ml', 'Woody', 'Unisex', 'Eau de Parfum', 'Custom Text Available');
INSERT INTO PRODUCT_IMAGES (product_id, image) VALUES
(@product_id, '/images/ysl/infini_1.jpg'),
(@product_id, '/images/ysl/infini_2.jpg'),
(@product_id, '/images/ysl/infini_3.jpg');

-- Prada - Intenso
INSERT INTO PRODUCTS (brand, product_name, description, price, personalisable)
VALUES ('Prada', 'Intenso', 'An intense and deep scent', 100.00, TRUE);
SET @product_id = LAST_INSERT_ID();
INSERT INTO PERSONAL_FRAGRANCES (product_id, size, fragrance_family, gender, concentration, personalisation_options)
VALUES
(@product_id, '50ml', 'Woody', 'M', 'Eau de Parfum', 'Custom Text Available'),
(@product_id, '100ml', 'Woody', 'M', 'Eau de Parfum', 'Custom Text Available');
INSERT INTO PRODUCT_IMAGES (product_id, image) VALUES
(@product_id, '/images/prada/intenso_1.jpg'),
(@product_id, '/images/prada/intenso_2.jpg');

-- Prada - Divina
INSERT INTO PRODUCTS (brand, product_name, description, price, personalisable)
VALUES ('Prada', 'Divina', 'A divine feminine fragrance', 95.00, TRUE);
SET @product_id = LAST_INSERT_ID();
INSERT INTO PERSONAL_FRAGRANCES (product_id, size, fragrance_family, gender, concentration, personalisation_options)
VALUES
(@product_id, '30ml', 'Floral', 'F', 'Eau de Toilette', 'No Engraving'),
(@product_id, '50ml', 'Floral', 'F', 'Eau de Toilette', 'No Engraving'),
(@product_id, '100ml', 'Floral', 'F', 'Eau de Toilette', 'No Engraving');
INSERT INTO PRODUCT_IMAGES (product_id, image) VALUES
(@product_id, '/images/prada/divina_1.jpg'),
(@product_id, '/images/prada/divina_2.jpg'),
(@product_id, '/images/prada/divina_3.jpg');

-- Prada - Aura
INSERT INTO PRODUCTS (brand, product_name, description, price, personalisable)
VALUES ('Prada', 'Aura', 'A radiant aura scent', 90.00, TRUE);
SET @product_id = LAST_INSERT_ID();
INSERT INTO PERSONAL_FRAGRANCES (product_id, size, fragrance_family, gender, concentration, personalisation_options)
VALUES
(@product_id, '50ml', 'Floral', 'F', 'Eau de Parfum', 'Custom Text Available'),
(@product_id, '100ml', 'Floral', 'F', 'Eau de Parfum', 'Custom Text Available');
INSERT INTO PRODUCT_IMAGES (product_id, image) VALUES
(@product_id, '/images/prada/aura_1.jpg'),
(@product_id, '/images/prada/aura_2.jpg');

-- Prada - Enigma
INSERT INTO PRODUCTS (brand, product_name, description, price, personalisable)
VALUES ('Prada', 'Enigma', 'An enigmatic fragrance', 105.00, TRUE);
SET @product_id = LAST_INSERT_ID();
INSERT INTO PERSONAL_FRAGRANCES (product_id, size, fragrance_family, gender, concentration, personalisation_options)
VALUES
(@product_id, '50ml', 'Woody', 'Unisex', 'Eau de Parfum', 'No Engraving'),
(@product_id, '100ml', 'Woody', 'Unisex', 'Eau de Parfum', 'No Engraving');
INSERT INTO PRODUCT_IMAGES (product_id, image) VALUES
(@product_id, '/images/prada/enigma_1.jpg'),
(@product_id, '/images/prada/enigma_2.jpg'),
(@product_id, '/images/prada/enigma_3.jpg');

-- Prada - Serenade
INSERT INTO PRODUCTS (brand, product_name, description, price, personalisable)
VALUES ('Prada', 'Serenade', 'A serene and melodic scent', 85.00, TRUE);
SET @product_id = LAST_INSERT_ID();
INSERT INTO PERSONAL_FRAGRANCES (product_id, size, fragrance_family, gender, concentration, personalisation_options)
VALUES
(@product_id, '30ml', 'Floral', 'F', 'Eau de Parfum', 'Custom Text Available'),
(@product_id, '50ml', 'Floral', 'F', 'Eau de Parfum', 'Custom Text Available');
INSERT INTO PRODUCT_IMAGES (product_id, image) VALUES
(@product_id, '/images/prada/serenade_1.jpg'),
(@product_id, '/images/prada/serenade_2.jpg');

-- Penhaligon's - Midnight Rose
INSERT INTO PRODUCTS (brand, product_name, description, price, personalisable)
VALUES ('Penhaligon''s', 'Midnight Rose', 'A romantic rose at midnight', 150.00, TRUE);
SET @product_id = LAST_INSERT_ID();
INSERT INTO PERSONAL_FRAGRANCES (product_id, size, fragrance_family, gender, concentration, personalisation_options)
VALUES
(@product_id, '50ml', 'Floral', 'F', 'Eau de Parfum', 'Custom Text Available'),
(@product_id, '100ml', 'Floral', 'F', 'Eau de Parfum', 'Custom Text Available');
INSERT INTO PRODUCT_IMAGES (product_id, image) VALUES
(@product_id, '/images/penhaligons/midnight_rose_1.jpg'),
(@product_id, '/images/penhaligons/midnight_rose_2.jpg'),
(@product_id, '/images/penhaligons/midnight_rose_3.jpg');

-- Penhaligon's - Ember Nocturne
INSERT INTO PRODUCTS (brand, product_name, description, price, personalisable)
VALUES ('Penhaligon''s', 'Ember Nocturne', 'A warm nocturnal scent', 160.00, TRUE);
SET @product_id = LAST_INSERT_ID();
INSERT INTO PERSONAL_FRAGRANCES (product_id, size, fragrance_family, gender, concentration, personalisation_options)
VALUES
(@product_id, '50ml', 'Oriental', 'Unisex', 'Eau de Parfum', 'No Engraving'),
(@product_id, '100ml', 'Oriental', 'Unisex', 'Eau de Parfum', 'No Engraving');
INSERT INTO PRODUCT_IMAGES (product_id, image) VALUES
(@product_id, '/images/penhaligons/ember_nocturne_1.jpg'),
(@product_id, '/images/penhaligons/ember_nocturne_2.jpg');

-- Penhaligon's - Whisper
INSERT INTO PRODUCTS (brand, product_name, description, price, personalisable)
VALUES ('Penhaligon''s', 'Whisper', 'A soft whispering fragrance', 145.00, TRUE);
SET @product_id = LAST_INSERT_ID();
INSERT INTO PERSONAL_FRAGRANCES (product_id, size, fragrance_family, gender, concentration, personalisation_options)
VALUES
(@product_id, '50ml', 'Floral', 'Unisex', 'Eau de Parfum', 'Custom Text Available'),
(@product_id, '100ml', 'Floral', 'Unisex', 'Eau de Parfum', 'Custom Text Available');
INSERT INTO PRODUCT_IMAGES (product_id, image) VALUES
(@product_id, '/images/penhaligons/whisper_1.jpg'),
(@product_id, '/images/penhaligons/whisper_2.jpg'),
(@product_id, '/images/penhaligons/whisper_3.jpg');

-- Penhaligon's - Verdant
INSERT INTO PRODUCTS (brand, product_name, description, price, personalisable)
VALUES ('Penhaligon''s', 'Verdant', 'A lush green scent', 140.00, TRUE);
SET @product_id = LAST_INSERT_ID();
INSERT INTO PERSONAL_FRAGRANCES (product_id, size, fragrance_family, gender, concentration, personalisation_options)
VALUES
(@product_id, '30ml', 'Fresh', 'Unisex', 'Eau de Toilette', 'No Engraving'),
(@product_id, '50ml', 'Fresh', 'Unisex', 'Eau de Toilette', 'No Engraving');
INSERT INTO PRODUCT_IMAGES (product_id, image) VALUES
(@product_id, '/images/penhaligons/verdant_1.jpg'),
(@product_id, '/images/penhaligons/verdant_2.jpg');

-- Penhaligon's - Eclipse
INSERT INTO PRODUCTS (brand, product_name, description, price, personalisable)
VALUES ('Penhaligon''s', 'Eclipse', 'A celestial eclipse fragrance', 155.00, TRUE);
SET @product_id = LAST_INSERT_ID();
INSERT INTO PERSONAL_FRAGRANCES (product_id, size, fragrance_family, gender, concentration, personalisation_options)
VALUES
(@product_id, '50ml', 'Woody', 'Unisex', 'Eau de Parfum', 'Custom Text Available'),
(@product_id, '100ml', 'Woody', 'Unisex', 'Eau de Parfum', 'Custom Text Available');
INSERT INTO PRODUCT_IMAGES (product_id, image) VALUES
(@product_id, '/images/penhaligons/eclipse_1.jpg'),
(@product_id, '/images/penhaligons/eclipse_2.jpg'),
(@product_id, '/images/penhaligons/eclipse_3.jpg');
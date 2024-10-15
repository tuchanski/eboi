-- Populando tabela Usuario
INSERT INTO Usuario (Nome, Email, Senha, Tipo) VALUES
('João Silva', 'joao.silva@email.com', 'senha123', 'comum'),
('admin', 'admin', 'admin', 'admin'),
('Carlos Pereira', 'carlos.pereira@email.com', 'senha789', 'comum');

-- Populando tabela Fazenda
INSERT INTO Fazenda (CNPJ, Endereco, Telefone, Email) VALUES
('12.345.678/0001-99', 'Rua das Fazendas, 123', '(41) 99999-9999', 'fazenda1@email.com'),
('98.765.432/0001-88', 'Estrada Rural, 456', '(41) 88888-8888', 'fazenda2@email.com');

-- Populando tabela Bovino
INSERT INTO Bovino (Raca, Data_Nascimento, Peso, FazendaID) VALUES
('Nelore', '2020-01-01', 450.50, 1),
('Angus', '2019-05-15', 520.75, 1),
('Holandês', '2021-03-30', 300.40, 2);

-- Populando tabela ESP_Gps
INSERT INTO ESP_Gps (Localizacao, Data_Instalacao, BovinoID) VALUES
('Fazenda 1 - Posição 1', '2023-01-10', 1),
('Fazenda 1 - Posição 2', '2023-02-20', 2),
('Fazenda 2 - Posição 1', '2023-03-15', 3);

-- Populando tabela Sensor_Posicao
INSERT INTO Sensor_Posicao (ESP_GpsID) VALUES
(1), (2), (3);

-- Populando tabela ESP_Portao
INSERT INTO ESP_Portao (Localizacao, Data_Instalacao, FazendaID) VALUES
('Entrada Principal', '2023-01-01', 1),
('Portão Sul', '2023-02-15', 2);

-- Populando tabela Sensor_Distancia
INSERT INTO Sensor_Distancia (ESP_PortaoID) VALUES
(1), (2);

-- Populando tabela Buzzer
INSERT INTO Buzzer (ESP_PortaoID) VALUES
(1), (2);

-- Populando tabela LED
INSERT INTO LED (ESP_PortaoID) VALUES
(1), (2);

-- Populando tabela Sensor_Temperatura
INSERT INTO Sensor_Temperatura (ESP_PortaoID) VALUES
(1), (2);

-- SCRIPT criado para rodar em um banco Postgresql.

CREATE DATABASE eBoi;

\c eBoi;

CREATE TABLE Usuario (
    ID SERIAL PRIMARY KEY,
    Nome VARCHAR(100) NOT NULL,
    Email VARCHAR(100) NOT NULL UNIQUE,
    Senha VARCHAR(255) NOT NULL,
    Tipo VARCHAR(10) CHECK (Tipo IN ('comum', 'admin')) DEFAULT 'comum'
);

CREATE TABLE Fazenda (
    ID SERIAL PRIMARY KEY,
    CNPJ VARCHAR(20) NOT NULL,
    Endereco VARCHAR(255) NOT NULL,
    Telefone VARCHAR(20),
    Email VARCHAR(100)
);

CREATE TABLE Bovino (
    ID SERIAL PRIMARY KEY,
    Raca VARCHAR(50),
    Data_Nascimento DATE,
    Peso DECIMAL(5,2),
    FazendaID INT,
    FOREIGN KEY (FazendaID) REFERENCES Fazenda(ID)
);

CREATE TABLE ESP_Gps (
    ID SERIAL PRIMARY KEY,
    Localizacao VARCHAR(100),
    Data_Instalacao DATE,
    BovinoID INT,
    FOREIGN KEY (BovinoID) REFERENCES Bovino(ID)
);

CREATE TABLE Sensor_Posicao (
    ID SERIAL PRIMARY KEY,
    ESP_GpsID INT,
    FOREIGN KEY (ESP_GpsID) REFERENCES ESP_Gps(ID)
);

CREATE TABLE ESP_Portao (
    ID SERIAL PRIMARY KEY,
    Localizacao VARCHAR(100),
    Data_Instalacao DATE,
    FazendaID INT,
    FOREIGN KEY (FazendaID) REFERENCES Fazenda(ID)
);

CREATE TABLE Sensor_Distancia (
    ID SERIAL PRIMARY KEY,
    ESP_PortaoID INT,
    FOREIGN KEY (ESP_PortaoID) REFERENCES ESP_Portao(ID)
);

CREATE TABLE Buzzer (
    ID SERIAL PRIMARY KEY,
    ESP_PortaoID INT,
    FOREIGN KEY (ESP_PortaoID) REFERENCES ESP_Portao(ID)
);

CREATE TABLE LED (
    ID SERIAL PRIMARY KEY,
    ESP_PortaoID INT,
    FOREIGN KEY (ESP_PortaoID) REFERENCES ESP_Portao(ID)
);

CREATE TABLE Sensor_Temperatura (
    ID SERIAL PRIMARY KEY,
    ESP_PortaoID INT,
    FOREIGN KEY (ESP_PortaoID) REFERENCES ESP_Portao(ID)
);

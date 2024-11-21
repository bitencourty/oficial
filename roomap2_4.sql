-- Criação do banco de dados e seleção
CREATE DATABASE IF NOT EXISTS roomap;
USE roomap;

-- Criação das tabelas principais
CREATE TABLE IF NOT EXISTS salas (
    id_sala INT AUTO_INCREMENT PRIMARY KEY,
    nome_sala VARCHAR(100) NOT NULL,         
    capac_sala INT NOT NULL,                 
    loc_sala VARCHAR(15) NOT NULL,             
    status_sala VARCHAR(15) NOT NULL,          
    quant_equip_sala INT NOT NULL              
);

CREATE TABLE IF NOT EXISTS equipamentos (
    id_equip INT AUTO_INCREMENT PRIMARY KEY,
    nome_equip VARCHAR(100) NOT NULL,
    loc_equip VARCHAR(15) NOT NULL,
    desc_equip VARCHAR(100) NOT NULL,
    status_equip VARCHAR(100) NOT NULL,
    quant_equip INT NOT NULL
);

CREATE TABLE IF NOT EXISTS mapa (
    id_mapa INT AUTO_INCREMENT PRIMARY KEY,
    desc_mapa VARCHAR(100) NOT NULL,
    loc_img VARCHAR(15) NOT NULL
);

CREATE TABLE docentes (
    id_doc INT AUTO_INCREMENT PRIMARY KEY,
    nome_doc VARCHAR(100) NOT NULL,
    email_doc VARCHAR(100) NOT NULL UNIQUE,
    senha_doc VARCHAR(255) NOT NULL, 
    cargo_doc VARCHAR(100) NOT NULL,
    tel_doc VARCHAR(100) NOT NULL
);
CREATE TABLE reservas (
    id_reserva INT AUTO_INCREMENT PRIMARY KEY,
    data_hora_inicio DATETIME NOT NULL,
    data_hora_fim DATETIME NOT NULL,
    status_reserva VARCHAR(15) NOT NULL,
    email_doc VARCHAR(100) NOT NULL,
    id_sala INT,
    FOREIGN KEY (id_sala) REFERENCES salas(id_sala),
    FOREIGN KEY (email_doc) REFERENCES docentes(email_doc)
);
CREATE TABLE IF NOT EXISTS administrador (
    id_admin INT AUTO_INCREMENT PRIMARY KEY,
    nome_adm VARCHAR(100) NOT NULL,
    senha_adm VARCHAR(6) NOT NULL
);



CREATE TABLE IF NOT EXISTS reservasadmin (
    id_reserva INT AUTO_INCREMENT PRIMARY KEY,
    data_hora_inicio DATETIME NOT NULL,
    data_hora_fim DATETIME NOT NULL,
    status_reserva VARCHAR(15) NOT NULL,
    nome_adm VARCHAR(100) NOT NULL,
    id_sala INT,
    FOREIGN KEY (id_sala) REFERENCES salas(id_sala)
);

CREATE TABLE IF NOT EXISTS validacao (
    email VARCHAR(100) NOT NULL,
    senha VARCHAR(6) NOT NULL
);

-- Inserção de dados iniciais
INSERT INTO docentes (nome_doc, email_doc, senha_doc, cargo_doc, tel_doc) 
VALUES 
('Maria', 'maria@gmail.com', '5678', 'Professor', '1234-5678'),
('João', 'joao@gmail.com', '91011', 'Coordenador', '9876-5432'),
('Carlos', 'carlos@hotmail.com', '8765', 'Professora', '4321-8765');

INSERT INTO administrador (nome_adm, senha_adm) 
VALUES ('Admin', '1234');

INSERT INTO salas (nome_sala, capac_sala, loc_sala, status_sala, quant_equip_sala) 
VALUES 
('Auditório', 120, 'Bloco A', 'Disponível', 15),
('Oficina Elétrica 1', 25, 'Bloco B', 'Disponível', 10),
('Laboratório CAD', 30, 'Bloco B', 'Disponível', 10),
('Biblioteca', 50, 'Bloco C', 'Disponível', 20);

INSERT INTO reservas (data_hora_inicio, data_hora_fim, status_reserva, email_doc, id_sala) 
VALUES 
('2024-10-10 09:00:00', '2024-10-10 10:00:00', 'Confirmada', 'maria@gmail.com', 1),  
('2024-10-11 11:00:00', '2024-10-11 12:00:00', 'Confirmada', 'joao@gmail.com', 2);

INSERT INTO reservasadmin (data_hora_inicio, data_hora_fim, status_reserva, nome_adm, id_sala) 
VALUES 
('2024-10-10 09:00:00', '2024-10-10 10:00:00', 'Confirmada', 'Admin', 1),  
('2024-10-11 11:00:00', '2024-10-11 12:00:00', 'Confirmada', 'Admin', 2);

INSERT INTO equipamentos (nome_equip, loc_equip, desc_equip, status_equip, quant_equip)
VALUES
('Computador', 'TI', 'PC com 32GB RAM e i9', 'Indisponível', 10),
('Switch de Rede', 'TI', 'Switch de 48 portas para laboratório', 'Disponível', 2);

INSERT INTO mapa (desc_mapa, loc_img)
VALUES
('Mapa do Prédio Principal', 'prédio A'),
('Mapa da Oficina de Usinagem', 'usinagem');

-- Criar trigger para sincronizar dados entre docentes e validação
    DELIMITER //

CREATE TRIGGER after_insert_docentes
AFTER INSERT ON docentes
FOR EACH ROW
BEGIN
    INSERT INTO validacao (email, senha)
    VALUES (NEW.email_doc, NEW.senha_doc);
END //

DELIMITER ;

-- Criação de views
CREATE OR REPLACE VIEW view_salas AS
SELECT 
    id_sala,
    nome_sala,
    capac_sala,
    loc_sala,
    status_sala
FROM 
    salas;

CREATE OR REPLACE VIEW reservas_ultima_semana_admin AS
SELECT 
    id_reserva,
    nome_adm,
    data_hora_inicio,
    data_hora_fim,
    status_reserva,
    id_sala
FROM 
    reservasadmin
WHERE 
    DATE(data_hora_inicio) >= CURDATE() - INTERVAL 7 DAY
  AND 
    DATE(data_hora_inicio) < CURDATE()
ORDER BY 
    data_hora_inicio DESC;

CREATE OR REPLACE VIEW reservas_dia_atual_admin AS
SELECT 
    r.id_reserva,
    r.nome_adm,
    r.data_hora_inicio,
    r.data_hora_fim,
    r.status_reserva,
    r.id_sala,
    s.nome_sala
FROM 
    reservasadmin r
JOIN 
    salas s ON r.id_sala = s.id_sala
WHERE 
    DATE(r.data_hora_inicio) = CURDATE()
ORDER BY 
    r.data_hora_inicio ASC;

-- Teste final para verificar tabelas e dados
SELECT * FROM salas;
SELECT * FROM view_salas;

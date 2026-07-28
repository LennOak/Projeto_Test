-- 1. Tabela CLIENTES
CREATE TABLE CLIENTES (
    id_cliente INT IDENTITY(1, 1) PRIMARY KEY,
    nome_cliente VARCHAR(100) NOT NULL,
    idade_cliente INT NOT NULL,
    telefone_cliente VARCHAR(20) NOT NULL UNIQUE,
    Bairro VARCHAR(100) NOT NULL
);

-- 2. Tabela PETS
CREATE TABLE PETS (
    id_pet INT IDENTITY(1, 1) PRIMARY KEY,
    id_cliente INT NOT NULL,
    nome_pet VARCHAR(100) NOT NULL,
    especie_pet VARCHAR(100) NOT NULL DEFAULT 'Cachorro',
    raca_pet VARCHAR(100) NOT NULL,
    porte_pet VARCHAR(50) NOT NULL,
    pelagem_pet VARCHAR(50) NOT NULL,
    alergia_pet VARCHAR(50) NOT NULL,
    temperamento_pet VARCHAR(50) NOT NULL,
    FOREIGN KEY (id_cliente) REFERENCES CLIENTES(id_cliente)
);

-- 3. Tabela SERVICOS
CREATE TABLE SERVICOS (
    id_servico INT IDENTITY(1, 1) PRIMARY KEY,
    nome_servico VARCHAR(100) NOT NULL,
    valor_servico DECIMAL(10, 2) NOT NULL
);

-- 4. Tabela AGENDAMENTOS
CREATE TABLE AGENDAMENTOS (
    id_agendamento INT IDENTITY(1, 1) PRIMARY KEY,
    id_cliente INT NOT NULL,
    id_pet INT NOT NULL,
    data_hora DATETIME NOT NULL,
    valor_total DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    forma_pagamento VARCHAR(30) NULL,
    status_agendamento VARCHAR(20) DEFAULT 'Agendado',
    FOREIGN KEY (id_cliente) REFERENCES CLIENTES(id_cliente),
    FOREIGN KEY (id_pet) REFERENCES PETS(id_pet)
);

-- 5. Tabela Associativa AGENDAMENTOS_SERVICOS
CREATE TABLE AGENDAMENTOS_SERVICOS (
    id_agendamento INT NOT NULL,
    id_servico INT NOT NULL,
    valor_unitario DECIMAL(10, 2) NOT NULL,
    PRIMARY KEY (id_agendamento, id_servico),
    FOREIGN KEY (id_agendamento) REFERENCES AGENDAMENTOS(id_agendamento) ON DELETE CASCADE,
    FOREIGN KEY (id_servico) REFERENCES SERVICOS(id_servico)
);

INSERT INTO SERVICOS (nome_servico, valor_servico) VALUES 
('Banho Completo', 50.00),
('Tosa Higiênica', 35.00),
('Tosa Geral', 60.00),
('Corte de Unhas', 15.00);
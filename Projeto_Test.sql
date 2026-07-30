-- 1. TABELA DE USUÁRIOS
CREATE TABLE USUARIOS (
    id_usuario INT IDENTITY(1,1) PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    senha VARCHAR(100) NOT NULL,
    perfil VARCHAR(20) NOT NULL CHECK (perfil IN ('Dono', 'Funcionario'))
);

-- 2. TABELA DE CLIENTES
CREATE TABLE CLIENTES (
    id_cliente INT IDENTITY(1,1) PRIMARY KEY,
    nome_cliente VARCHAR(150) NOT NULL,
    idade_cliente INT NOT NULL DEFAULT 0,
    telefone_cliente VARCHAR(20) NOT NULL,
    Bairro VARCHAR(100) NOT NULL
);

-- 3. TABELA DE PETS
CREATE TABLE PETS (
    id_pet INT IDENTITY(1,1) PRIMARY KEY,
    id_cliente INT NOT NULL,
    nome_pet VARCHAR(100) NOT NULL,
    especie_pet VARCHAR(50) NOT NULL,
    raca_pet VARCHAR(50) NOT NULL,
    porte_pet VARCHAR(20) NOT NULL,
    pelagem_pet VARCHAR(20) NOT NULL,
    alergia_pet VARCHAR(100) DEFAULT 'Nenhuma',
    temperamento_pet VARCHAR(50) DEFAULT 'Calmo',
    clubinho VARCHAR(3) DEFAULT 'Não',
    FOREIGN KEY (id_cliente) REFERENCES CLIENTES(id_cliente) ON DELETE CASCADE
);

-- 4. TABELA DE SERVIÇOS
CREATE TABLE SERVICOS (
    id_servico INT IDENTITY(1,1) PRIMARY KEY,
    nome_servico VARCHAR(100) NOT NULL,
    valor_servico DECIMAL(10,2) NOT NULL
);

INSERT INTO SERVICOS (nome_servico, valor_servico) VALUES 
('Banho Simples', 50.00),
('Tosa Higiênica', 30.00),
('Tosa Completa', 80.00),
('Corte de Unhas', 15.00),
('Hidratação', 40.00),
('Limpeza de Ouvidos', 20.00);

-- 5. TABELA DE AGENDAMENTOS
CREATE TABLE AGENDAMENTOS (
    id_agendamento INT IDENTITY(1,1) PRIMARY KEY,
    id_cliente INT NOT NULL,
    id_pet INT NOT NULL,
    data_hora DATETIME NOT NULL,
    valor_total DECIMAL(10,2) NOT NULL,
    forma_pagamento VARCHAR(50) NOT NULL,
    status_agendamento VARCHAR(30) DEFAULT 'Agendado',
    FOREIGN KEY (id_cliente) REFERENCES CLIENTES(id_cliente),
    FOREIGN KEY (id_pet) REFERENCES PETS(id_pet)
);

-- 6. TABELA DE SERVIÇOS DO AGENDAMENTO
CREATE TABLE AGENDAMENTOS_SERVICOS (
    id_agendamento_servico INT IDENTITY(1,1) PRIMARY KEY,
    id_agendamento INT NOT NULL,
    id_servico INT NOT NULL,
    valor_unitario DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (id_agendamento) REFERENCES AGENDAMENTOS(id_agendamento) ON DELETE CASCADE,
    FOREIGN KEY (id_servico) REFERENCES SERVICOS(id_servico)
);

import datetime
import urllib.parse
import pandas as pd
import sqlalchemy as sa
import streamlit as st
from sqlalchemy import create_engine, text


# -----------------------------------------------------------------------------
# 1. CONEXÃO COM O AZURE SQL SERVER (USANDO SECRETS.TOML)
# -----------------------------------------------------------------------------
@st.cache_resource
def get_engine():
    secrets = st.secrets["azure_sql"]
    params = urllib.parse.quote_plus(
        f"DRIVER={{{secrets['driver']}}};"
        f"SERVER={secrets['server']};"
        f"DATABASE={secrets['database']};"
        f"UID={secrets['username']};"
        f"PWD={secrets['password']};"
        "Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"
    )
    return create_engine(f"mssql+pyodbc:///?odbc_connect={params}")


try:
    engine = get_engine()
except Exception as e:
    st.error(f"Erro ao conectar ao Azure SQL: {e}")

# Configuração da página Streamlit
st.set_page_config(
    page_title="Gestão Petshop", page_icon="🐾", layout="wide"
)
st.title(" Sistema de Gestão do Petshop ")

# Criação das Abas
aba1, aba2, aba3, aba4 = st.tabs(
    [
        "Cadastrar Cliente",
        "Cadastrar Pet",
        "Novo Agendamento",
        "Agendamentos Dia/Semana",
    ]
)

# =============================================================================
# ABA 1: CADASTRAR CLIENTE
# =============================================================================
with aba1:
    st.header("Cadastrar Cliente")
    with st.form("form_cliente", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            nome = st.text_input("Nome Completo*")
            idade = st.number_input(
                "Idade*", min_value=18, max_value=120, value=25, step=1
            )
        with col2:
            telefone = st.text_input("Telefone / WhatsApp*")
            bairro = st.text_input("Bairro*")

        submitted_cliente = st.form_submit_button("Salvar Cliente")

    if submitted_cliente:
        if nome and telefone and bairro:
            try:
                query = text("""
                    INSERT INTO CLIENTES (nome_cliente, idade_cliente, telefone_cliente, Bairro)
                    VALUES (:nome, :idade, :telefone, :bairro)
                """)
                with engine.begin() as conn:
                    conn.execute(
                        query,
                        {
                            "nome": nome.strip().title(),
                            "idade": idade,
                            "telefone": telefone.strip(),
                            "bairro": bairro.strip().title(),
                        },
                    )
                st.success(f"Cliente '{nome}' cadastrado com sucesso!")
            except Exception as e:
                st.error(f"Erro ao salvar cliente: {e}")
        else:
            st.warning("Preencha todos os campos obrigatórios.")

# =============================================================================
# ABA 2: CADASTRAR PET
# =============================================================================
with aba2:
    st.header("Cadastrar Pet")

    # Carrega a lista de clientes para vincular ao Pet
    try:
        df_clientes = pd.read_sql(
            "SELECT id_cliente, nome_cliente, telefone_cliente FROM CLIENTES ORDER BY nome_cliente",
            engine,
        )
    except Exception:
        df_clientes = pd.DataFrame()

    if df_clientes.empty:
        st.info("Cadastre pelo menos um cliente na Aba 1 antes de registrar um pet.")
    else:
        dict_clientes = {
            f"{row['nome_cliente']} ({row['telefone_cliente']})": row["id_cliente"]
            for _, row in df_clientes.iterrows()
        }

        with st.form("form_pet", clear_on_submit=True):
            cliente_selecionado = st.selectbox(
                "Dono / Cliente*", options=list(dict_clientes.keys())
            )

            col1, col2, col3 = st.columns(3)
            with col1:
                nome_pet = st.text_input("Nome do Pet*")
                especie_pet = st.selectbox("Espécie*", ["Cachorro", "Gato", "Outro"])
                raca_pet = st.text_input("Raça*")
            with col2:
                porte_pet = st.selectbox("Porte*", ["Pequeno", "Médio", "Grande", "Gigante"])
                pelagem_pet = st.selectbox("Pelagem*", ["Curta", "Média", "Longa", "Dupla"])
            with col3:
                alergia_pet = st.selectbox(
                    "Alergia/Sensibilidade*",
                    ["Nenhuma", "Shampoo Normal", "Pele Sensível", "Outra"],
                )
                temperamento_pet = st.selectbox(
                    "Temperamento*",
                    ["Calmo", "Agitado", "Bravo / Arredio", "Tímido"],
                )

            submitted_pet = st.form_submit_button("Salvar Pet")

        if submitted_pet:
            if nome_pet and raca_pet:
                try:
                    id_cliente_fk = dict_clientes[cliente_selecionado]
                    query = text("""
                        INSERT INTO PETS (id_cliente, nome_pet, especie_pet, raca_pet, porte_pet, pelagem_pet, alergia_pet, temperamento_pet)
                        VALUES (:id_cliente, :nome, :especie, :raca, :porte, :pelagem, :alergia, :temperamento)
                    """)
                    with engine.begin() as conn:
                        conn.execute(
                            query,
                            {
                                "id_cliente": id_cliente_fk,
                                "nome": nome_pet.strip().title(),
                                "especie": especie_pet,
                                "raca": raca_pet.strip().title(),
                                "porte": porte_pet,
                                "pelagem": pelagem_pet,
                                "alergia": alergia_pet,
                                "temperamento": temperamento_pet,
                            },
                        )
                    st.success(f"Pet '{nome_pet}' cadastrado com sucesso!")
                except Exception as e:
                    st.error(f"Erro ao salvar Pet: {e}")
            else:
                st.warning("Preencha o Nome e a Raça do Pet.")

# =============================================================================
# ABA 3: NOVO AGENDAMENTO
# =============================================================================
with aba3:
    st.header("Novo Agendamento")

    try:
        df_pets_clientes = pd.read_sql(
            """
            SELECT p.id_pet, p.nome_pet, c.id_cliente, c.nome_cliente 
            FROM PETS p 
            INNER JOIN CLIENTES c ON p.id_cliente = c.id_cliente
        """,
            engine,
        )

        df_servicos = pd.read_sql(
            "SELECT id_servico, nome_servico, valor_servico FROM SERVICOS",
            engine,
        )
    except Exception:
        df_pets_clientes = pd.DataFrame()
        df_servicos = pd.DataFrame()

    if df_pets_clientes.empty or df_servicos.empty:
        st.warning(
            "Cadastre pelo menos um Pet e certifique-se de que existem Serviços cadastrados no banco para agendar."
        )
    else:
        dict_pets = {
            f"{row['nome_pet']} (Dono: {row['nome_cliente']})": (
                row["id_pet"],
                row["id_cliente"],
            )
            for _, row in df_pets_clientes.iterrows()
        }

        dict_servicos = {
            f"{row['nome_servico']} - R$ {row['valor_servico']:.2f}": (
                row["id_servico"],
                float(row["valor_servico"]),
            )
            for _, row in df_servicos.iterrows()
        }

        with st.form("form_agendamento"):
            pet_selecionado = st.selectbox(
                "Selecione o Pet / Cliente*", options=list(dict_pets.keys())
            )

            col1, col2 = st.columns(2)
            with col1:
                data_agendamento = st.date_input("Data*", min_value=datetime.date.today())
                hora_agendamento = st.time_input("Horário*")
            with col2:
                forma_pagamento = st.selectbox(
                    "Forma de Pagamento",
                    ["PIX", "Cartão de Crédito", "Cartão de Débito", "Dinheiro"],
                )

            servicos_escolhidos = st.multiselect(
                "Selecione o(s) Serviço(s)*",
                options=list(dict_servicos.keys()),
            )

            valor_total_preview = sum([dict_servicos[s][1] for s in servicos_escolhidos])
            st.markdown(f"### **Valor Total: R$ {valor_total_preview:.2f}**")

            submitted_agendamento = st.form_submit_button("Confirmar Agendamento")

        if submitted_agendamento:
            if servicos_escolhidos:
                try:
                    id_pet, id_cliente = dict_pets[pet_selecionado]
                    data_hora_final = datetime.datetime.combine(
                        data_agendamento, hora_agendamento
                    )

                    with engine.begin() as conn:
                        # Insere na tabela principal AGENDAMENTOS
                        query_agendamento = text("""
                            INSERT INTO AGENDAMENTOS (id_cliente, id_pet, data_hora, valor_total, forma_pagamento, status_agendamento)
                            OUTPUT INSERTED.id_agendamento
                            VALUES (:id_cliente, :id_pet, :data_hora, :valor_total, :forma_pagamento, 'Agendado')
                        """)
                        result = conn.execute(
                            query_agendamento,
                            {
                                "id_cliente": id_cliente,
                                "id_pet": id_pet,
                                "data_hora": data_hora_final,
                                "valor_total": valor_total_preview,
                                "forma_pagamento": forma_pagamento,
                            },
                        )
                        id_novo_agendamento = result.scalar()

                        # Insere os itens na tabela associativa AGENDAMENTOS_SERVICOS
                        query_itens = text("""
                            INSERT INTO AGENDAMENTOS_SERVICOS (id_agendamento, id_servico, valor_unitario)
                            VALUES (:id_agendamento, :id_servico, :valor_unitario)
                        """)

                        for servico_str in servicos_escolhidos:
                            id_serv, valor_unit = dict_servicos[servico_str]
                            conn.execute(
                                query_itens,
                                {
                                    "id_agendamento": id_novo_agendamento,
                                    "id_servico": id_serv,
                                    "valor_unitario": valor_unit,
                                },
                            )

                    st.success("Agendamento realizado com sucesso!")
                except Exception as e:
                    st.error(f"Erro ao salvar agendamento: {e}")
            else:
                st.warning("Selecione pelo menos um serviço.")

# =============================================================================
# ABA 4: AGENDAMENTOS DIA/SEMANA
# =============================================================================
with aba4:
    st.header("Agendamentos Dia/Semana/Mês")

    filtro_tempo = st.radio(
        "Filtrar visão por:",
        ["Dia", "Semana", "Mês", "Todos"],
        horizontal=True,
    )

    data_referencia = st.date_input("Data de Referência", datetime.date.today())

    sql_base = """
        SELECT 
            a.id_agendamento AS [ID],
            a.data_hora AS [Data/Hora],
            c.nome_cliente AS [Cliente],
            p.nome_pet AS [Pet],
            p.porte_pet AS [Porte],
            p.temperamento_pet AS [Temperamento],
            a.valor_total AS [Valor Total (R$)],
            a.forma_pagamento AS [Pagamento],
            a.status_agendamento AS [Status]
        FROM AGENDAMENTOS a
        INNER JOIN CLIENTES c ON a.id_cliente = c.id_cliente
        INNER JOIN PETS p ON a.id_pet = p.id_pet
    """

    if filtro_tempo == "Dia":
        sql_base += " WHERE CAST(a.data_hora AS DATE) = :data"
        params = {"data": data_referencia}
    elif filtro_tempo == "Semana":
        sql_base += " WHERE DATEPART(WEEK, a.data_hora) = DATEPART(WEEK, :data) AND YEAR(a.data_hora) = YEAR(:data)"
        params = {"data": data_referencia}
    elif filtro_tempo == "Mês":
        sql_base += " WHERE MONTH(a.data_hora) = MONTH(:data) AND YEAR(a.data_hora) = YEAR(:data)"
        params = {"data": data_referencia}
    else:
        params = {}

    sql_base += " ORDER BY a.data_hora ASC"

    try:
        df_agenda = pd.read_sql(text(sql_base), engine, params=params)

        if not df_agenda.empty:
            st.dataframe(df_agenda, use_container_width=True)

            st.subheader("Atualizar Status")
            col1, col2, col3 = st.columns(3)
            with col1:
                id_atualizar = st.selectbox("ID do Agendamento", df_agenda["ID"])
            with col2:
                novo_status = st.selectbox(
                    "Novo Status", ["Agendado", "Concluído", "Cancelado"]
                )
            with col3:
                st.write("")
                st.write("")
                btn_atualizar = st.button("Atualizar Status")

            if btn_atualizar:
                with engine.begin() as conn:
                    query_update = text("""
                        UPDATE AGENDAMENTOS 
                        SET status_agendamento = :status 
                        WHERE id_agendamento = :id
                    """)
                    conn.execute(
                        query_update,
                        {"status": novo_status, "id": id_atualizar},
                    )
                st.success(f"Status do agendamento #{id_atualizar} alterado para {novo_status}!")
                st.rerun()
        else:
            st.info("Nenhum agendamento encontrado para o período selecionado.")

    except Exception as e:
        st.error(f"Erro ao carregar agenda: {e}")
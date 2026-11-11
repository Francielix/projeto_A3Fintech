"""
=============================================================================
UNIFG - MATEMÁTICA APLICADA COMPUTACIONAL (2026.2)
PROJETO INTEGRADO A3: AUDITORIA FORENSE E TOPOLOGIA DE REDE FINTECH
Script Oficial do Aluno: gerador_fintech.py
Autoria:
Prof. Ciro Chaves (Colaboração Gemini)
=============================================================================
Instruções de Execução (Jupyter Notebook, Codespaces, Colab ou Terminal):
1. Basta executar a célula contendo este script (ou rodar `python gerador_fintech.py`).
2. Quando solicitado na caixa de entrada, informe:
   - O código da sua equipe (ex: EQ01, EQ02, ..., EQ07), OU
   - Os 4 RAs da equipe separados por vírgula, OU
   - A Semente Determinística S_eq da equipe.
3. Os 3 arquivos CSV exclusivos serão gerados automaticamente no diretório atual:
   - contas_clientes.csv
   - dispositivos_autenticados.csv
   - transacoes_financeiras.csv

   Os arquivos .csv gerados por este Script irão fornecer os dados necessários para as
   equipes fazerem os cálculos e apresentarem em arguição oral no dia da entrega do trabalho.
=============================================================================
"""

import re
import sys
import numpy as np
import pandas as pd

# Mapeamento oficial das 7 Equipes da Turma P1 (#01 a #28)
SEMENTES_OFICIAIS_P1 = {
    "EQ01": 4050457891,
    "EQ02": 13163970240,
    "EQ03": 4050466758,
    "EQ04": 4050371607,
    "EQ05": 13163959165,
    "EQ06": 4050476484,
    "EQ07": 4050469011,
}

# Mapeamento reverso de RA individual -> Equipe P1 (caso o aluno digite apenas 1 RA)
RA_PARA_EQUIPE_P1 = {
    "1012616526": "EQ01", "1012613521": "EQ01", "1012612829": "EQ01", "1012615015": "EQ01",
    "1012619488": "EQ02", "1012618984": "EQ02", "10126110763": "EQ02", "1012621005": "EQ02",
    "1012618819": "EQ03", "1012615372": "EQ03", "1012618913": "EQ03", "1012613654": "EQ03",
    "1012616934": "EQ04", "1012521740": "EQ04", "1012616215": "EQ04", "1012616718": "EQ04",
    "1012616605": "EQ05", "10126110903": "EQ05", "1012616734": "EQ05", "1012614923": "EQ05",
    "1012618403": "EQ06", "1012619363": "EQ06", "1012619481": "EQ06", "1012619237": "EQ06",
    "1012619599": "EQ07", "1012617135": "EQ07", "1012615178": "EQ07", "1012617099": "EQ07",
}


def calcular_semente(entrada_str: str) -> int:
    """
    Interpreta de forma resiliente a entrada do aluno:
    - Aceita código da equipe ('EQ01' a 'EQ07', 'eq1', 'equipe 1')
    - Aceita lista de RAs separados por vírgula, ponto e vírgula ou espaço
    - Aceita um único RA (identificando automaticamente a equipe correspondente na P1)
    - Aceita a Semente S_eq direta
    """
    if not entrada_str or not str(entrada_str).strip():
        raise ValueError("Entrada vazia. Informe o código da equipe (ex: EQ01), os RAs ou a semente S_eq.")

    texto = str(entrada_str).strip().upper()

    # 1. Verifica se digitou o código da equipe (ex: EQ01, EQ1, EQUIPE 01)
    match_eq = re.search(r"EQ(?:UIPE)?\s*0?([1-7])\b", texto)
    if match_eq:
        cod_eq = f"EQ0{match_eq.group(1)}"
        s_eq = SEMENTES_OFICIAIS_P1[cod_eq]
        print(f"[INFO] Equipe {cod_eq} identificada! Semente oficial S_eq = {s_eq}")
        return s_eq

    # 2. Extrai todos os blocos numéricos da string
    numeros_str = re.findall(r"\d+", texto)
    if not numeros_str:
        raise ValueError(
            f"Nenhum RA, código de equipe (EQ01..EQ07) ou semente válido encontrado em: '{entrada_str}'"
        )

    # Se digitou apenas 1 número que corresponde ao RA de um aluno da P1, usa a semente da equipe dele
    if len(numeros_str) == 1 and numeros_str[0] in RA_PARA_EQUIPE_P1:
        cod_eq = RA_PARA_EQUIPE_P1[numeros_str[0]]
        s_eq = SEMENTES_OFICIAIS_P1[cod_eq]
        print(f"[INFO] RA {numeros_str[0]} pertence à {cod_eq}. Usando Semente oficial da equipe: S_eq = {s_eq}")
        return s_eq

    valores = [int(n) for n in numeros_str]
    return sum(valores)


def obter_argumentos_cli_limpos() -> list:
    """
    Filtra argumentos internos injetados pelo kernel do Jupyter Notebook / Google Colab
    (como '-f', '--ip=...', caminhos de arquivos '.json', etc.).
    """
    if "ipykernel" in sys.modules or "google.colab" in sys.modules:
        return []

    args_limpos = []
    ignorar_proximo = False
    for arg in sys.argv[1:]:
        if ignorar_proximo:
            ignorar_proximo = False
            continue
        if arg in ("-f", "--f", "--Session.key", "--Session.signature_scheme"):
            ignorar_proximo = True
            continue
        if arg.startswith("-") or arg.endswith(".json") or "kernel" in arg.lower():
            continue
        args_limpos.append(arg)
    return args_limpos


def gerar_datasets_fintech(s_eq: int, salvar_csv: bool = True, prefixo: str = ""):
    """
    Gera os 3 DataFrames determinísticos do Projeto A3 a partir da Semente S_eq.
    """
    seed_32 = int(s_eq) % (2**32 - 1)
    rng = np.random.default_rng(seed_32)

    # Constante de configuração em nível de byte derivada da semente
    config_base = int(s_eq % 256)
    config_compliance_4bits = config_base & 0x0F

    # -------------------------------------------------------------------------
    # 1. TABELA A: contas_clientes.csv (Conjunto A de Contas Homologadas)
    # -------------------------------------------------------------------------
    n_contas = 120
    ids_contas = [f"CTA_{1000 + i}" for i in range(n_contas)]
    tipos_conta = rng.choice(["PF_Varejo", "PF_Prime", "PJ_MEI", "PJ_Corporate"], size=n_contas, p=[0.45, 0.20, 0.25, 0.10])
    regioes = rng.choice(["Nordeste", "Sudeste", "Sul", "Centro-Oeste"], size=n_contas, p=[0.40, 0.35, 0.15, 0.10])
    scores = rng.integers(320, 980, size=n_contas)

    limites_map = {"PF_Varejo": 2500.0, "PF_Prime": 12000.0, "PJ_MEI": 8000.0, "PJ_Corporate": 45000.0}
    limites = np.array([limites_map[t] * rng.uniform(0.8, 1.3) for t in tipos_conta]).round(2)

    bytes_conta = rng.integers(0, 256, size=n_contas)
    status_conta_hex = [f"0x{b:02X}" for b in bytes_conta]

    df_contas = pd.DataFrame({
        "id_conta": ids_contas,
        "tipo_conta": tipos_conta,
        "regiao": regioes,
        "score_credito": scores,
        "limite_operacional": limites,
        "status_conta_hex": status_conta_hex
    })

    # -------------------------------------------------------------------------
    # 2. TABELA D: dispositivos_autenticados.csv
    # -------------------------------------------------------------------------
    n_devices = 95
    ids_devices = [f"DEV_{500 + i}" for i in range(n_devices)]
    contas_amostra = list(rng.choice(ids_contas[:100], size=n_devices - 6, replace=True))
    contas_fantasma_dev = [f"CTA_99{i}" for i in range(1, 7)]
    contas_vinculadas = contas_amostra + contas_fantasma_dev
    rng.shuffle(contas_vinculadas)

    sistemas = rng.choice(["Android", "iOS", "Web_Linux", "Web_Windows"], size=n_devices, p=[0.50, 0.30, 0.08, 0.12])
    bytes_dev = rng.integers(0, 256, size=n_devices)
    flag_seguranca_hex = [f"0x{b:02X}" for b in bytes_dev]

    df_devices = pd.DataFrame({
        "id_device": ids_devices,
        "id_conta": contas_vinculadas,
        "sistema_operacional": sistemas,
        "flag_seguranca_hex": flag_seguranca_hex
    })

    # -------------------------------------------------------------------------
    # 3. TABELA B: transacoes_financeiras.csv
    # -------------------------------------------------------------------------
    n_tx = 1500
    ids_tx = [f"TX_{10000 + i}" for i in range(n_tx)]

    contas_ativas = ids_contas[:100]
    n_fantasmas = int(rng.integers(5, 10))
    contas_fantasma_tx = [f"CTA_88{i:02d}" for i in range(1, n_fantasmas + 1)]

    origens_normais = rng.choice(contas_ativas, size=n_tx - 45, replace=True)
    origens_fantasma = rng.choice(contas_fantasma_tx, size=45, replace=True)
    origens = np.concatenate([origens_normais, origens_fantasma])
    rng.shuffle(origens)

    destinos = rng.choice(contas_ativas, size=n_tx, replace=True)
    devices_tx = rng.choice(ids_devices, size=n_tx, replace=True)

    canais = rng.choice(["PIX", "TED", "Boleto"], size=n_tx, p=[0.65, 0.20, 0.15])
    faixas_horarias = rng.choice(["Comercial", "Noturno", "Madrugada"], size=n_tx, p=[0.55, 0.30, 0.15])

    canal_outlier = ["PIX", "TED", "Boleto"][int(s_eq % 3)]
    valores = np.zeros(n_tx)
    for i in range(n_tx):
        if canais[i] == canal_outlier and rng.random() < 0.08:
            valores[i] = round(rng.uniform(45000.0, 180000.0), 2)
        elif canais[i] == "TED":
            valores[i] = round(rng.lognormal(mean=7.2, sigma=0.7), 2)
        elif canais[i] == "PIX":
            valores[i] = round(rng.lognormal(mean=5.8, sigma=0.8), 2)
        else:
            valores[i] = round(rng.lognormal(mean=6.1, sigma=0.6), 2)

    flags_tx_int = rng.integers(0, 256, size=n_tx)
    flag_status_hex = [f"0x{b:02X}" for b in flags_tx_int]

    alerta_fraude = np.zeros(n_tx, dtype=int)
    for i in range(n_tx):
        b_xor = flags_tx_int[i] ^ config_base
        critico_bit = ((b_xor & 0b10100000) == 0b10100000) and ((b_xor & 0b00000101) == 0)
        prob_base = 0.06
        if faixas_horarias[i] == "Madrugada":
            prob_base += 0.38
        if origens[i] in contas_fantasma_tx:
            prob_base += 0.45
        if critico_bit or valores[i] > 25000:
            prob_base += 0.35
        alerta_fraude[i] = 1 if rng.random() < min(prob_base, 0.95) else 0

    df_tx = pd.DataFrame({
        "id_transacao": ids_tx,
        "id_conta_origem": origens,
        "id_conta_destino": destinos,
        "id_device": devices_tx,
        "canal": canais,
        "faixa_horaria": faixas_horarias,
        "valor": valores,
        "flag_status_hex": flag_status_hex,
        "alerta_fraude": alerta_fraude
    })

    idx_remover = (df_tx["canal"] == "Boleto") & (df_tx["faixa_horaria"] == "Madrugada") & (df_tx["valor"] > 9000)
    df_tx.loc[idx_remover, "faixa_horaria"] = "Comercial"

    # -------------------------------------------------------------------------
    # 4. NÚCLEO DE ALTA SUSPEIÇÃO (DÍGRAFO 10x10 CONTAS PARA ETAPA 4)
    # -------------------------------------------------------------------------
    nucleo_10 = [f"CTA_{1000 + i}" for i in range(10)]
    mask_nucleo = df_tx["id_conta_origem"].isin(nucleo_10) & df_tx["id_conta_destino"].isin(nucleo_10)
    df_tx.loc[mask_nucleo, "id_conta_destino"] = "CTA_1050"

    arestas_plantadas = []
    n_loops = int(rng.integers(1, 3))
    nos_loop = rng.choice(nucleo_10, size=n_loops, replace=False)
    for no in nos_loop:
        arestas_plantadas.append((no, no))

    pares_disp = [n for n in nucleo_10 if n not in nos_loop]
    u1, v1, u2, v2 = pares_disp[0], pares_disp[1], pares_disp[2], pares_disp[3]
    arestas_plantadas.extend([(u1, v1), (v1, u1), (u2, v2), (v2, u2)])

    w1, w2, w3 = pares_disp[4], pares_disp[5], pares_disp[6]
    arestas_plantadas.extend([(w1, w2), (w2, w3), (w3, w1)])
    arestas_plantadas.extend([(pares_disp[5], pares_disp[6]), (pares_disp[6], pares_disp[7])])

    for idx_aresta, (orig_n, dest_n) in enumerate(arestas_plantadas):
        df_tx.loc[idx_aresta, "id_conta_origem"] = orig_n
        df_tx.loc[idx_aresta, "id_conta_destino"] = dest_n
        df_tx.loc[idx_aresta, "alerta_fraude"] = 1
        df_tx.loc[idx_aresta, "valor"] = round(float(rng.uniform(15000, 42000)), 2)

    if salvar_csv:
        p = f"{prefixo}_" if prefixo else ""
        df_contas.to_csv(f"{p}contas_clientes.csv", index=False)
        df_devices.to_csv(f"{p}dispositivos_autenticados.csv", index=False)
        df_tx.to_csv(f"{p}transacoes_financeiras.csv", index=False)
        print("=" * 72)
        print(f"[SUCESSO] Datasets gerados para a Semente S_eq = {s_eq}")
        print(f"[PARAMETRO] CONFIG_BASE (Byte completo)      = 0x{config_base:02X} ({config_base})")
        print(f"[PARAMETRO] CONFIG_COMPLIANCE (4 bits baixos)= 0x{config_compliance_4bits:02X} ({config_compliance_4bits})")
        print(f"[ARQUIVOS]  {p}contas_clientes.csv ({len(df_contas)} linhas)")
        print(f"            {p}dispositivos_autenticados.csv ({len(df_devices)} linhas)")
        print(f"            {p}transacoes_financeiras.csv ({len(df_tx)} linhas)")
        print("=" * 72)

    return df_contas, df_devices, df_tx, config_base


if __name__ == "__main__":
    print("=== GERADOR OFICIAL DE DADOS - PROJETO A3 FINTECH (UNIFG 2026.2) ===")
    args_cli = obter_argumentos_cli_limpos()

    if args_cli:
        entrada_usuario = ",".join(args_cli)
    else:
        print("Dica: Você pode digitar o código da equipe (ex: EQ01), os 4 RAs separados por vírgula ou a Semente S_eq.")
        entrada_usuario = input("Informe a Equipe (EQ01..EQ07), os RAs ou a Semente S_eq: ").strip()

    semente_calculada = calcular_semente(entrada_usuario)
    gerar_datasets_fintech(semente_calculada, salvar_csv=True)
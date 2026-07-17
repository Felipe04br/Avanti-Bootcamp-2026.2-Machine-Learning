import os
import json
import hashlib
import pandas as pd
from PIL import Image
from collections import defaultdict

# ==========================================
# 0. SISTEMA DE LOG PARA EXPORTAÇÃO
# ==========================================
linhas_relatorio = []


def registrar(texto=""):
    """Imprime no console e guarda na memória para o TXT"""
    print(texto)
    linhas_relatorio.append(texto)


# ==========================================
# 1. CONFIGURAÇÃO E VARREDURA DOS DIRETÓRIOS
# ==========================================
caminho_base = 'C:\\Projetos\\Avanti-Bootcamp-2026.2-Machine-Learning\\Dados\\archive'

arquivos_por_exame = defaultdict(list)
metadados_lista = []
todas_imagens_paths = {}
formatos_encontrados = set()

registrar("Iniciando varredura e processamento das pastas...\n")

if not os.path.exists(caminho_base):
    registrar(f"ATENÇÃO: O diretório '{caminho_base}' não foi encontrado.")
else:
    for raiz, _, arquivos in os.walk(caminho_base):
        for arquivo in arquivos:
            if arquivo.startswith('.'):
                continue

            caminho_completo = os.path.join(raiz, arquivo)

            nome_base = arquivo.replace('_mask_consensus.png', '') \
                .replace('_bbox.png', '') \
                .replace('.jpg', '') \
                .replace(' meta.json', '')

            arquivos_por_exame[nome_base].append(caminho_completo)

            classe_da_pasta = os.path.basename(raiz)

            if arquivo.endswith('.json'):
                try:
                    with open(caminho_completo, 'r', encoding='utf-8') as f:
                        dados = json.load(f)
                        dados['nome_base_exame'] = nome_base
                        dados['classe_tumor'] = classe_da_pasta

                        metadados_lista.append(dados)
                except Exception as e:
                    registrar(f"Erro ao ler {arquivo}: {e}")

            elif arquivo.lower().endswith(('.jpg', '.jpeg', '.png')):
                todas_imagens_paths[arquivo] = caminho_completo
                formatos_encontrados.add(os.path.splitext(arquivo)[1].lower())

df_metadados = pd.DataFrame(metadados_lista)

# ==========================================
# 2. AGRUPAMENTO POR EXAME (Regra dos 4 Arquivos)
# ==========================================
registrar("=== 0. INTEGRIDADE DOS AGRUPAMENTOS ===")
exames_incompletos = {}
exames_completos_count = 0

for nome_exame, lista_de_arquivos in arquivos_por_exame.items():
    if len(lista_de_arquivos) == 4:
        exames_completos_count += 1
    else:
        exames_incompletos[nome_exame] = lista_de_arquivos

registrar(f"Total de exames únicos encontrados: {len(arquivos_por_exame)}")
registrar(f"Exames com os 4 arquivos completos: {exames_completos_count}")
registrar(f"Exames com divergência (incompletos/extras): {len(exames_incompletos)}")

# ==========================================
# 3. INTEGRIDADE DOS ARQUIVOS (Existência)
# ==========================================
registrar("\n=== 1. INTEGRIDADE DOS ARQUIVOS ===")
if not df_metadados.empty and 'filename' in df_metadados.columns:
    imagens_listadas_json = set(df_metadados['filename'].dropna())
    imagens_no_diretorio = set(arq for arq in todas_imagens_paths.keys() if arq.endswith('.jpg'))

    faltam_no_dir = imagens_listadas_json - imagens_no_diretorio
    faltam_no_json = imagens_no_diretorio - imagens_listadas_json

    registrar(f"Imagens nos JSONs, mas ausentes nas pastas: {len(faltam_no_dir)}")
    registrar(f"Imagens .jpg nas pastas, mas sem JSON correspondente: {len(faltam_no_json)}")

# ==========================================
# 4. VALIDAÇÃO FÍSICA: METADADOS VS IMAGEM REAL
# ==========================================
registrar("\n=== 2. CONSISTÊNCIA FÍSICA (Metadados vs Imagem) ===")
divergencias_dimensao = []

if not df_metadados.empty and 'filename' in df_metadados.columns:
    for index, row in df_metadados.iterrows():
        nome_img_alvo = row.get('filename')

        if pd.notna(nome_img_alvo) and nome_img_alvo in todas_imagens_paths:
            caminho_img_real = todas_imagens_paths[nome_img_alvo]

            try:
                with Image.open(caminho_img_real) as img:
                    largura_real, altura_real = img.size

                    largura_json = row.get('width')
                    altura_json = row.get('height')

                    if largura_real != largura_json or altura_real != altura_json:
                        divergencias_dimensao.append({
                            'exame': row.get('nome_base_exame'),
                            'real': f"{largura_real}x{altura_real}",
                            'json': f"{largura_json}x{altura_json}"
                        })
            except Exception:
                pass

registrar(f"Imagens cujas dimensões reais divergem do JSON: {len(divergencias_dimensao)}")

# ==========================================
# 5. QUALIDADE DAS IMAGENS
# ==========================================
registrar("\n=== 3. QUALIDADE DAS IMAGENS ===")
imagens_corrompidas = []

for nome_arq, img_path in todas_imagens_paths.items():
    try:
        with Image.open(img_path) as img:
            img.verify()
    except Exception:
        imagens_corrompidas.append(nome_arq)

registrar(f"Total de imagens corrompidas: {len(imagens_corrompidas)}")

# ==========================================
# 6. DISTRIBUIÇÃO DAS CLASSES
# ==========================================
registrar("\n=== 4. DISTRIBUIÇÃO DAS CLASSES ===")
registrar("\nArquivos com problemas nos metadados não são contabilizados")
if not df_metadados.empty and 'classe_tumor' in df_metadados.columns:
    pivot_tab = df_metadados['classe_tumor'].value_counts().reset_index()
    pivot_tab.columns = ['Classe do Tumor (Pasta)', 'Quantidade de Exames']

    chart_bar = pivot_tab.to_dict(orient='records')

    registrar(pivot_tab.to_string(index=False))

# ==========================================
# 7. DUPLICATAS
# ==========================================
registrar("\n=== 5. VERIFICAÇÃO DE DUPLICATAS ===")
if not df_metadados.empty:
    colunas_para_checar = [col for col in df_metadados.columns if col not in ['nome_base_exame']]

    # CORREÇÃO: Converte os dados das colunas para string para evitar o erro de 'unhashable type'
    df_para_checar = df_metadados[colunas_para_checar].astype(str)
    duplicatas_json = df_para_checar.duplicated().sum()

    registrar(f"JSONs com conteúdos exatamente iguais: {duplicatas_json}")

hashes = {}
imagens_duplicadas = []

for nome_arquivo, img_path in todas_imagens_paths.items():
    # Ignora qualquer arquivo que não seja .jpg
    if not nome_arquivo.lower().endswith('.jpg'):
        continue

    if nome_arquivo in imagens_corrompidas:
        continue

    with open(img_path, "rb") as f:
        file_hash = hashlib.md5(f.read()).hexdigest()

    if file_hash in hashes:
        imagens_duplicadas.append((nome_arquivo, hashes[file_hash]))
    else:
        hashes[file_hash] = nome_arquivo

registrar(f"Imagens de tumor (.jpg) exatamente duplicadas: {len(imagens_duplicadas)}")

if imagens_duplicadas:
    # Cria um dicionário para agrupar as cópias por imagem original
    agrupamento_duplicatas = defaultdict(list)

    for copia, original in imagens_duplicadas:
        agrupamento_duplicatas[original].append(copia)

    # Exibe no formato solicitado
    for original, copias in agrupamento_duplicatas.items():
        quantidade = len(copias)
        # Formata a lista de cópias separando por vírgula
        nomes_copias = ", ".join([f"'{c}'" for c in copias])

        registrar(f" - A imagem '{original}' foi copiada {quantidade} vezes e chamada de: {nomes_copias}")

# ==========================================
# 8. EXPORTAÇÃO PARA TXT
# ==========================================
registrar("\n===========================================")
registrar("Análise concluída.")

exportar = input("\nDeseja exportar este relatório para um arquivo TXT? (s/n): ")

if exportar.lower() in ['s', 'sim', 'y', 'yes']:
    nome_arquivo = 'relatorio_qualidade_dataset.txt'
    try:
        with open(nome_arquivo, 'w', encoding='utf-8') as f:
            f.write('\n'.join(linhas_relatorio))
        print(f"\n[+] Sucesso! O relatório foi salvo como '{nome_arquivo}' na pasta atual.")
    except Exception as e:
        print(f"\n[-] Erro ao salvar o arquivo: {e}")
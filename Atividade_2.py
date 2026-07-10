# 1. Escreva uma função que receba uma lista de números e retorne outra lista com os números ímpares.
def numeros_impares(lista):
    return [num for num in lista if num % 2 != 0]

# 2. Escreva uma função que receba uma lista de números e retorne outra lista com os números primos presentes.
def numeros_primos(lista):
    def eh_primo(n):
        if n < 2:
            return False
        for i in range(2, int(n ** 0.5) + 1):
            if n % i == 0:
                return False
        return True
    return [num for num in lista if eh_primo(num)]

# 3. Escreva uma função que receba duas listas e retorne outra lista com os elementos que estão presentes em apenas uma das listas.
def elementos_unicos(lista1, lista2):
    set1 = set(lista1)
    set2 = set(lista2)
    return list(set1.symmetric_difference(set2))

# 4. Dada uma lista de números inteiros, escreva uma função para encontrar o segundo maior valor na lista.
def segundo_maior(lista):
    unique_numbers = list(set(lista))
    unique_numbers.sort(reverse=True)
    return unique_numbers[1] if len(unique_numbers) > 1 else None

# 5. Crie uma função que receba uma lista de tuplas, cada uma contendo o nome e a idade de uma pessoa, e retorne a lista ordenada pelo nome das pessoas em ordem alfabética.
def ordenar_por_nome(pessoas):
    return sorted(pessoas, key=lambda x: x[0])

# 6. Como identificar e tratar outliers em uma coluna numérica usando desvio padrão ou quartis?
# Usando quartis (IQR):
Q1 = df["coluna"].quantile(0.25)
Q3 = df["coluna"].quantile(0.75)
IQR = Q3 - Q1
outliers = df[(df["coluna"] < Q1 - 1.5 * IQR) |
              (df["coluna"] > Q3 + 1.5 * IQR)]
# Tratamento: remover os outliers ou substituí-los por valores como a mediana.
df_sem_outliers = df[(df["coluna"] >= Q1 - 1.5 * IQR) &
                     (df["coluna"] <= Q3 + 1.5 * IQR)]

# 7. Como concatenar vários DataFrames (empilhando linhas ou colunas), mesmo que tenham colunas diferentes?
import pandas as pd
# Empilhando linhas
resultado_linhas = pd.concat([df1, df2], axis=0)
# Juntando colunas
resultado_colunas = pd.concat([df1, df2], axis=1)

# 8. Utilizando pandas, como realizar a leitura de um arquivo CSV em um DataFrame e exibir as primeiras linhas?
import pandas as pd
df = pd.read_csv("arquivo.csv")
print(df.head())

# 9. Utilizando pandas, como selecionar uma coluna específica e filtrar linhas em um DataFrame com base em uma condição?
# Selecionar uma coluna
coluna = df["idade"]
# Filtrar linhas
filtrado = df[df["idade"] >= 18]

# 10. Utilizando pandas, como lidar com valores ausentes (NaN) em um DataFrame?
# Verificar valores ausentes
print(df.isnull().sum())
# Remover linhas com NaN
df = df.dropna()
# Substituir NaN por um valor
df = df.fillna(0)
# Substituir NaN pela média da coluna
df["idade"] = df["idade"].fillna(df["idade"].mean())
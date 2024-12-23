from flask import Flask, render_template, request, jsonify
import pandas as pd
import random
from collections import Counter

app = Flask(__name__)

# Função para calcular a frequência de cada número
def calcular_frequencia(df):
    frequencias = {i: 0 for i in range(1, 61)}
    for i in range(len(df)):
        for j in range(0, 6):
            numero = int(df.iloc[i, j])
            frequencias[numero] += 1
    return frequencias

# Função para determinar números quentes e frios
def numeros_quentes_frios(frequencias):
    quentes = sorted(frequencias, key=frequencias.get, reverse=True)[:20]
    frios = sorted(frequencias, key=frequencias.get)[:20]
    return quentes, frios

# Função para gerar números da sequência de Fibonacci entre 1 e 60
def gerar_fibonacci():
    fib = [1, 2]
    while True:
        next_fib = fib[-1] + fib[-2]
        if next_fib > 60:
            break
        fib.append(next_fib)
    return fib

# Função para gerar um jogo equilibrado
def gerar_jogo_equilibrado(quentes, frios, fibonacci, numeros_por_jogo):
    jogo = set()
    jogo.update(random.sample(quentes, min(3, len(quentes))))
    jogo.update(random.sample(frios, min(3, len(frios))))
    fibonacci_disponiveis = [num for num in fibonacci if num not in jogo]
    jogo.update(random.sample(fibonacci_disponiveis, min(1, len(fibonacci_disponiveis))))
    restante = [x for x in range(1, 61) if x not in jogo]
    while len(jogo) < numeros_por_jogo:
        jogo.add(random.choice(restante))
    return sorted(jogo)

def simulacao_monte_carlo(frequencias, quentes, frios, fibonacci, numeros_por_jogo, n_simulacoes=1000, n_jogos=6):
    melhores_jogos = []
    for _ in range(n_simulacoes):
        jogo = gerar_jogo_equilibrado(quentes, frios, fibonacci, numeros_por_jogo)
        melhores_jogos.append(jogo)
        if len(melhores_jogos) >= n_jogos:
            break
    return melhores_jogos[:n_jogos]

# Função para gerar jogos
def gerar_jogos(df, numeros_por_jogo=10, n_jogos=6):
    frequencias = calcular_frequencia(df)
    quentes, frios = numeros_quentes_frios(frequencias)
    fibonacci = gerar_fibonacci()
    jogos = simulacao_monte_carlo(frequencias, quentes, frios, fibonacci, numeros_por_jogo, n_simulacoes=1000, n_jogos=n_jogos)
    return jogos[:n_jogos]

# Leitura do arquivo CSV
def ler_csv(arquivo):
    df = pd.read_csv(arquivo, delimiter=';', usecols=['bola 1', 'bola 2', 'bola 3', 'bola 4', 'bola 5', 'bola 6'])
    return df

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/gerar_jogos', methods=['POST'])
def gerar_jogos_api():
    try:
        arquivo = 'mega_sena.csv'
        df = ler_csv(arquivo)

        # Receber parâmetros via formulário
        numeros_por_jogo = int(request.form.get('numeros_por_jogo', 6))
        n_jogos = int(request.form.get('n_jogos', 3))

        # Gerar jogos
        jogos = gerar_jogos(df, numeros_por_jogo, n_jogos)

        return jsonify(jogos)  # Retorna os jogos gerados em JSON
    except Exception as e:
        return jsonify({'erro': str(e)}), 500  # Retorna um erro em JSON caso algo dê errado


if __name__ == "__main__":
    app.run(debug=True)

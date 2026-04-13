# Leilão de Entregas — Trabalho de IA

Este projeto implementa o problema **Leilão de Entregas** proposto na disciplina de Inteligência Artificial, utilizando **duas abordagens diferentes** para selecionar a melhor sequência de entregas e maximizar o lucro total obtido com bônus.

## Abordagens implementadas

1. **Versão A\***  
   Modela o problema como uma busca determinística, tratando o objetivo como **minimização da perda de bônus**.

2. **Versão Meta-heurística**  
   Utiliza **Simulated Annealing** para buscar uma solução boa para o problema de forma combinatória/estocástica.

Além disso, o projeto também inclui:

- comparação de desempenho entre as duas versões;
- gráficos comparativos de **lucro** e **tempo de execução**;
- simulação visual interativa com `pygame`.

---

## Objetivo do problema

Uma startup de entregas urbanas deseja selecionar, entre várias entregas disponíveis no dia, quais devem ser realizadas para **maximizar o lucro total dos bônus recebidos**.

Cada entrega possui:

- um **horário programado de saída**;
- um **destino**;
- um **valor de bônus**.

O entregador:

- sempre sai do ponto **A**;
- pode transportar **uma carga por vez**;
- precisa considerar o tempo de **ida e volta**;
- pode esperar em **A** até o horário de início de uma entrega;
- perde a entrega se o horário programado já tiver passado quando estiver disponível para sair.

---

## Estrutura do projeto

- `leilao_entregas.py` → código principal com as duas soluções
- `comparacao_resultados.py` → geração de benchmark e gráficos comparativos
- `simulacao_pygame.py` → simulação visual interativa
- `exemplo_entrada.txt` → arquivo de entrada para teste
- `grafico_bonus.png` → gráfico comparativo de lucro
- `grafico_tempo.png` → gráfico comparativo de tempo

---

## Como executar

### 1. Executar as duas versões

```bash
python leilao_entregas.py --file exemplo_entrada.txt --algo both
```

### 2. Executar apenas a versão com A*

```bash
python leilao_entregas.py --file exemplo_entrada.txt --algo astar
```

### 3. Executar apenas a versão meta-heurística

```bash
python leilao_entregas.py --file exemplo_entrada.txt --algo sa
```

### 4. Gerar comparação e gráficos

```bash
python comparacao_resultados.py
```

### 5. Abrir a simulação visual interativa

```bash
python simulacao_pygame.py
```

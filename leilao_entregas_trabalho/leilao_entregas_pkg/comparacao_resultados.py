import os
import random
import time
import statistics
import matplotlib.pyplot as plt
from leilao_entregas import Delivery, solve_a_star, solve_simulated_annealing


OUT_DIR = os.path.dirname(__file__)


def generate_test_case(seed: int, n: int = 12):
    random.seed(seed)
    deliveries = []
    current_time = 0
    for _ in range(n):
        current_time += random.randint(1, 8)
        destination = chr(ord('B') + random.randint(0, 4))
        bonus = random.randint(2, 20)
        duration = random.randint(4, 16)
        deliveries.append(Delivery(current_time, destination, bonus, duration))
    return deliveries


def benchmark(runs: int = 20):
    astar_times, sa_times = [], []
    astar_profits, sa_profits = [], []

    for i in range(runs):
        deliveries = generate_test_case(i)

        t0 = time.perf_counter()
        astar_result = solve_a_star(deliveries)
        t1 = time.perf_counter()

        t2 = time.perf_counter()
        sa_result = solve_simulated_annealing(deliveries, seed=i)
        t3 = time.perf_counter()

        astar_times.append((t1 - t0) * 1000)
        sa_times.append((t3 - t2) * 1000)
        astar_profits.append(astar_result["profit"])
        sa_profits.append(sa_result["profit"])

    return astar_times, sa_times, astar_profits, sa_profits


def save_chart(values_a, values_b, labels, title, ylabel, filename):
    plt.figure(figsize=(8, 5))
    plt.bar(labels, [statistics.mean(values_a), statistics.mean(values_b)])
    plt.title(title)
    plt.ylabel(ylabel)
    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, filename), dpi=150)
    plt.close()


def main():
    astar_times, sa_times, astar_profits, sa_profits = benchmark()

    save_chart(
        astar_profits,
        sa_profits,
        ["A*", "Simulated Annealing"],
        "Comparação de lucro médio",
        "Lucro médio",
        "grafico_bonus.png",
    )

    save_chart(
        astar_times,
        sa_times,
        ["A*", "Simulated Annealing"],
        "Comparação de tempo médio de execução",
        "Tempo médio (ms)",
        "grafico_tempo.png",
    )

    print("Resumo do benchmark")
    print(f"A*  -> lucro médio: {statistics.mean(astar_profits):.2f} | tempo médio: {statistics.mean(astar_times):.4f} ms")
    print(f"SA  -> lucro médio: {statistics.mean(sa_profits):.2f} | tempo médio: {statistics.mean(sa_times):.4f} ms")


if __name__ == "__main__":
    main()

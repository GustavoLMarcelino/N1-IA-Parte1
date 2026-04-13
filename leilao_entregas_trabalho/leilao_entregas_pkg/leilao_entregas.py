import argparse
import heapq
import math
import random
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional


@dataclass
class Delivery:
    start: int
    destination: str
    bonus: int
    duration: int  # ida + volta


def parse_input_file(path: str):
    """
    Formato esperado:
    [NODES]
    A,B,C,D

    [MATRIX]
    0,5,0,2
    5,0,3,0
    0,3,0,8
    2,0,8,0

    [DELIVERIES]
    0,B,1
    5,C,10
    10,D,8
    """
    with open(path, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip() and not line.strip().startswith("#")]

    section = None
    nodes = []
    matrix = []
    raw_deliveries = []

    for line in lines:
        if line.upper() == "[NODES]":
            section = "nodes"
            continue
        if line.upper() == "[MATRIX]":
            section = "matrix"
            continue
        if line.upper() == "[DELIVERIES]":
            section = "deliveries"
            continue

        if section == "nodes":
            nodes = [item.strip() for item in line.split(",")]
        elif section == "matrix":
            row = [int(item.strip()) for item in line.split(",")]
            matrix.append(row)
        elif section == "deliveries":
            start, dest, bonus = [item.strip() for item in line.split(",")]
            raw_deliveries.append((int(start), dest, int(bonus)))

    if not nodes or not matrix:
        raise ValueError("Arquivo inválido: faltam nós ou matriz.")

    graph = matrix_to_graph(nodes, matrix)
    deliveries = build_deliveries(graph, raw_deliveries, origin="A")
    deliveries.sort(key=lambda d: (d.start, d.destination, d.bonus))
    return graph, deliveries


def matrix_to_graph(nodes: List[str], matrix: List[List[int]]) -> Dict[str, List[Tuple[str, int]]]:
    graph = {node: [] for node in nodes}
    for i, origin in enumerate(nodes):
        for j, destination in enumerate(nodes):
            weight = matrix[i][j]
            if i != j and weight > 0:
                graph[origin].append((destination, weight))
    return graph


def dijkstra(graph: Dict[str, List[Tuple[str, int]]], start: str) -> Dict[str, int]:
    dist = {node: math.inf for node in graph}
    dist[start] = 0
    pq = [(0, start)]

    while pq:
        current_dist, node = heapq.heappop(pq)
        if current_dist > dist[node]:
            continue
        for neighbor, weight in graph[node]:
            new_dist = current_dist + weight
            if new_dist < dist[neighbor]:
                dist[neighbor] = new_dist
                heapq.heappush(pq, (new_dist, neighbor))
    return dist


def build_deliveries(graph, raw_deliveries, origin="A") -> List[Delivery]:
    distances = dijkstra(graph, origin)
    deliveries = []
    for start, destination, bonus in raw_deliveries:
        if destination not in distances or distances[destination] is math.inf:
            raise ValueError(f"Destino {destination} não é alcançável a partir de {origin}.")
        duration = distances[destination] * 2
        deliveries.append(Delivery(start, destination, bonus, duration))
    return deliveries


# -----------------------------------------------------------------------------
# A* — minimizando perda de bônus
# -----------------------------------------------------------------------------

def heuristic_remaining_loss(deliveries: List[Delivery], index: int, current_time: int) -> int:
    """
    Heurística admissível: soma dos bônus das entregas que já estão definitivamente perdidas
    porque current_time > start. Isso é perda inevitável.
    """
    loss = 0
    for i in range(index, len(deliveries)):
        if current_time > deliveries[i].start:
            loss += deliveries[i].bonus
    return loss


def solve_a_star(deliveries: List[Delivery]):
    total_bonus = sum(d.bonus for d in deliveries)
    n = len(deliveries)

    # estado = (f, g, index, current_time, chosen_indices)
    pq = []
    start_state = (heuristic_remaining_loss(deliveries, 0, 0), 0, 0, 0, [])
    heapq.heappush(pq, start_state)

    best_cost = {}
    best_solution = None
    best_profit = -1

    while pq:
        f, g, index, current_time, chosen = heapq.heappop(pq)
        state_key = (index, current_time)
        if best_cost.get(state_key, math.inf) <= g:
            continue
        best_cost[state_key] = g

        if index == n:
            profit = sum(deliveries[i].bonus for i in chosen)
            if profit > best_profit:
                best_profit = profit
                best_solution = chosen[:]
            continue

        delivery = deliveries[index]

        # opção 1: pular a entrega
        skip_loss = g + delivery.bonus
        h_skip = heuristic_remaining_loss(deliveries, index + 1, current_time)
        heapq.heappush(pq, (skip_loss + h_skip, skip_loss, index + 1, current_time, chosen[:]))

        # opção 2: fazer a entrega, se possível
        if current_time <= delivery.start:
            next_time = delivery.start + delivery.duration
            h_take = heuristic_remaining_loss(deliveries, index + 1, next_time)
            new_chosen = chosen[:] + [index]
            heapq.heappush(pq, (g + h_take, g, index + 1, next_time, new_chosen))

    chosen_deliveries = [deliveries[i] for i in (best_solution or [])]
    profit = sum(d.bonus for d in chosen_deliveries)
    return {
        "algorithm": "A*",
        "chosen_deliveries": chosen_deliveries,
        "profit": profit,
        "loss": total_bonus - profit,
    }


# -----------------------------------------------------------------------------
# Simulated Annealing — meta-heurística
# -----------------------------------------------------------------------------

def evaluate_subset(order_bits: List[int], deliveries: List[Delivery]) -> Tuple[int, List[Delivery]]:
    current_time = 0
    chosen = []
    profit = 0
    for bit, delivery in zip(order_bits, deliveries):
        if not bit:
            continue
        if current_time <= delivery.start:
            current_time = delivery.start + delivery.duration
            chosen.append(delivery)
            profit += delivery.bonus
    return profit, chosen


def random_solution(n: int) -> List[int]:
    return [random.randint(0, 1) for _ in range(n)]


def neighbor(solution: List[int]) -> List[int]:
    new_solution = solution[:]
    idx = random.randrange(len(solution))
    new_solution[idx] = 1 - new_solution[idx]
    return new_solution


def solve_simulated_annealing(deliveries: List[Delivery], iterations=4000, temperature=50.0, cooling=0.995, seed=42):
    random.seed(seed)
    if not deliveries:
        return {"algorithm": "Simulated Annealing", "chosen_deliveries": [], "profit": 0}

    current = random_solution(len(deliveries))
    current_profit, current_chosen = evaluate_subset(current, deliveries)

    best = current[:]
    best_profit = current_profit
    best_chosen = current_chosen[:]
    temp = temperature

    for _ in range(iterations):
        candidate = neighbor(current)
        candidate_profit, candidate_chosen = evaluate_subset(candidate, deliveries)
        delta = candidate_profit - current_profit

        if delta >= 0:
            accept = True
        else:
            accept = random.random() < math.exp(delta / max(temp, 1e-9))

        if accept:
            current = candidate
            current_profit = candidate_profit
            current_chosen = candidate_chosen

        if current_profit > best_profit:
            best = current[:]
            best_profit = current_profit
            best_chosen = current_chosen[:]

        temp *= cooling

    return {
        "algorithm": "Simulated Annealing",
        "chosen_deliveries": best_chosen,
        "profit": best_profit,
        "bitmask": best,
    }


def format_solution(result: dict) -> str:
    deliveries = result.get("chosen_deliveries", [])
    if not deliveries:
        seq = "Nenhuma entrega selecionada"
    else:
        seq = " -> ".join(f"({d.start}, {d.destination}, {d.bonus})" for d in deliveries)
    return (
        f"Algoritmo: {result['algorithm']}\n"
        f"Sequência escolhida: {seq}\n"
        f"Lucro total: {result['profit']}\n"
    )


def run(path: str, algo: str):
    _, deliveries = parse_input_file(path)

    outputs = []
    if algo in ("astar", "both"):
        outputs.append(solve_a_star(deliveries))
    if algo in ("sa", "both"):
        outputs.append(solve_simulated_annealing(deliveries))

    for result in outputs:
        print(format_solution(result))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Leilão de Entregas — A* e Simulated Annealing")
    parser.add_argument("--file", required=True, help="Caminho do arquivo de entrada")
    parser.add_argument("--algo", choices=["astar", "sa", "both"], default="both")
    args = parser.parse_args()
    run(args.file, args.algo)

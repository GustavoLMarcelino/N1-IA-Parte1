import copy
import time
import pygame
from leilao_entregas import parse_input_file, solve_a_star, solve_simulated_annealing

WIDTH, HEIGHT = 1280, 760
WHITE = (255, 255, 255)
BLACK = (20, 20, 20)
BLUE = (60, 120, 220)
GREEN = (30, 160, 70)
GRAY = (220, 220, 220)
RED = (190, 50, 50)
YELLOW = (255, 215, 0)
LIGHT_BLUE = (210, 230, 255)
LIGHT_GREEN = (220, 255, 220)
LIGHT_RED = (255, 220, 220)
DARK_GREEN = (0, 110, 40)
DARK_RED = (130, 20, 20)
ORANGE = (255, 165, 0)


def draw_text(screen, text, x, y, font, color=BLACK):
    surface = font.render(text, True, color)
    screen.blit(surface, (x, y))


def delivery_equals(d1, d2):
    return (
        d1.start == d2.start
        and d1.destination == d2.destination
        and d1.bonus == d2.bonus
    )


def timed_run(func, deliveries):
    start = time.perf_counter()
    result = func(deliveries)
    elapsed_ms = (time.perf_counter() - start) * 1000
    return result, elapsed_ms


def recalculate(deliveries):
    astar_result, astar_time = timed_run(solve_a_star, deliveries)
    meta_result, meta_time = timed_run(solve_simulated_annealing, deliveries)
    return {
        "astar": astar_result,
        "astar_time": astar_time,
        "meta": meta_result,
        "meta_time": meta_time,
    }


def format_sequence(result):
    if not result["chosen_deliveries"]:
        return "Nenhuma entrega selecionada"
    return " -> ".join(
        f"({d.start}, {d.destination}, {d.bonus})"
        for d in result["chosen_deliveries"]
    )


def get_sequence_index(delivery, chosen_deliveries):
    for i, chosen in enumerate(chosen_deliveries):
        if delivery_equals(delivery, chosen):
            return i + 1
    return None


def draw_delivery_card(screen, delivery, x, y, w, h, font, small, is_selected=False, seq_index=None, chosen_color=None):
    bg = YELLOW if is_selected else GRAY
    pygame.draw.rect(screen, bg, (x, y, w, h), border_radius=12)
    pygame.draw.rect(screen, BLACK, (x, y, w, h), width=2, border_radius=12)

    if chosen_color and seq_index is not None:
        pygame.draw.circle(screen, chosen_color, (x + w - 22, y + 22), 16)
        pygame.draw.circle(screen, BLACK, (x + w - 22, y + 22), 16, 2)
        num = font.render(str(seq_index), True, WHITE)
        num_rect = num.get_rect(center=(x + w - 22, y + 22))
        screen.blit(num, num_rect)

    draw_text(screen, f"Destino: {delivery.destination}", x + 10, y + 10, small)
    draw_text(screen, f"Saída: {delivery.start}", x + 10, y + 38, small)
    draw_text(screen, f"Bônus: {delivery.bonus}", x + 10, y + 66, small)


def draw_algorithm_panel(screen, title, result, exec_time, deliveries, x, y, w, h, title_color, chosen_color, font, small, tiny):
    pygame.draw.rect(screen, WHITE, (x, y, w, h), border_radius=14)
    pygame.draw.rect(screen, BLACK, (x, y, w, h), width=2, border_radius=14)

    draw_text(screen, title, x + 15, y + 12, font, title_color)
    draw_text(screen, f"Lucro: {result['profit']}", x + 15, y + 52, small)
    draw_text(screen, f"Tempo: {exec_time:.4f} ms", x + 15, y + 80, small)
    draw_text(screen, f"Entregas selecionadas: {len(result['chosen_deliveries'])}", x + 15, y + 108, small)

    draw_text(screen, "Processo/resultado visual:", x + 15, y + 142, small, BLACK)

    card_w = 180
    card_h = 105
    card_x = x + 15
    card_y = y + 175

    for i, delivery in enumerate(deliveries):
        seq_index = get_sequence_index(delivery, result["chosen_deliveries"])
        draw_delivery_card(
            screen,
            delivery,
            card_x,
            card_y,
            card_w,
            card_h,
            small,
            tiny,
            is_selected=False,
            seq_index=seq_index,
            chosen_color=chosen_color if seq_index is not None else None,
        )
        card_x += 195
        if card_x + card_w > x + w - 10:
            card_x = x + 15
            card_y += 120

    draw_text(screen, "Sequência escolhida:", x + 15, y + h - 75, small)
    draw_text(screen, format_sequence(result), x + 15, y + h - 45, tiny)


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Simulação Interativa do Leilão de Entregas")
    clock = pygame.time.Clock()

    font = pygame.font.SysFont("Arial", 24)
    small = pygame.font.SysFont("Arial", 19)
    tiny = pygame.font.SysFont("Arial", 16)

    _, original_deliveries = parse_input_file("exemplo_entrada.txt")
    deliveries = copy.deepcopy(original_deliveries)
    selected_index = 0
    results = recalculate(deliveries)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    selected_index = 0
                elif event.key == pygame.K_2 and len(deliveries) > 1:
                    selected_index = 1
                elif event.key == pygame.K_3 and len(deliveries) > 2:
                    selected_index = 2

                elif event.key == pygame.K_UP:
                    deliveries[selected_index].bonus += 1
                    results = recalculate(deliveries)

                elif event.key == pygame.K_DOWN:
                    deliveries[selected_index].bonus = max(0, deliveries[selected_index].bonus - 1)
                    results = recalculate(deliveries)

                elif event.key == pygame.K_RIGHT:
                    deliveries[selected_index].start += 1
                    results = recalculate(deliveries)

                elif event.key == pygame.K_LEFT:
                    deliveries[selected_index].start = max(0, deliveries[selected_index].start - 1)
                    results = recalculate(deliveries)

                elif event.key == pygame.K_r:
                    deliveries = copy.deepcopy(original_deliveries)
                    selected_index = 0
                    results = recalculate(deliveries)

        screen.fill(LIGHT_BLUE)

        draw_text(screen, "Leilão de Entregas — Simulação Interativa", 20, 15, font, BLUE)

        instructions = [
            "Teclas:",
            "1 / 2 / 3 = selecionar entrega para editar",
            "↑ / ↓ = aumentar / diminuir bônus",
            "→ / ← = aumentar / diminuir horário",
            "R = restaurar valores originais",
        ]

        y_instr = 52
        for line in instructions:
            draw_text(screen, line, 20, y_instr, tiny)
            y_instr += 22

        draw_text(screen, "Entregas editáveis:", 20, 170, small)

        x = 20
        y = 205
        for i, delivery in enumerate(deliveries):
            draw_delivery_card(
                screen,
                delivery,
                x,
                y,
                210,
                105,
                small,
                tiny,
                is_selected=(i == selected_index),
                seq_index=None,
                chosen_color=None,
            )
            x += 225

        draw_text(screen, "Amarelo = entrega selecionada para edição", 20, 325, tiny, ORANGE)
        draw_text(screen, "Círculo verde/vermelho = ordem em que o algoritmo escolheu a entrega", 20, 347, tiny, BLACK)

        draw_algorithm_panel(
            screen,
            "A*",
            results["astar"],
            results["astar_time"],
            deliveries,
            20,
            380,
            600,
            340,
            DARK_GREEN,
            GREEN,
            font,
            small,
            tiny,
        )

        draw_algorithm_panel(
            screen,
            "Meta-heurística (Simulated Annealing)",
            results["meta"],
            results["meta_time"],
            deliveries,
            650,
            380,
            600,
            340,
            DARK_RED,
            RED,
            font,
            small,
            tiny,
        )

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()
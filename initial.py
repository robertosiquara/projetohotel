import flet as ft
from models.gerenciador import GerenciadorDeReservas

PRIMARY_COLOR = "#4a6fa5"
SECONDARY_COLOR = "#166088"
TERTIARY_COLOR = "#dbe9ee"
ACCENT_COLOR = "#4fc3f7"
CARD_COLOR = "#ffffff"
ERROR_COLOR = "#e63946"
SUCCESS_COLOR = "#2a9d8f"


def tela_inicial(page: ft.Page, gerenciador: GerenciadorDeReservas):
    page.title = "Dete Aluguéis Imobiliários - Dashboard"
    page.controls.clear()
    page.scroll = ft.ScrollMode.AUTO

    # =========================
    # HEADER
    # =========================
    header = ft.Container(
        content=ft.Row(
            [
                ft.Icon(name=ft.Icons.HOTEL, color=ft.Colors.WHITE, size=30),
                ft.Text(
                    "Dete Aluguéis Imobiliários",
                    size=24,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.WHITE,
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=10,
        ),
        padding=20,
        bgcolor=PRIMARY_COLOR,
        border_radius=ft.BorderRadius(10, 10,10,10),
    )

    # =========================
    # DADOS (SEM disponibilidade)
    # =========================
    quartos = gerenciador.listar_quartos()
    quartos_disponiveis = gerenciador.listar_quartos_disponiveis()

    numeros_disponiveis = {q["numero"] for q in quartos_disponiveis}

    disponiveis = len(numeros_disponiveis)
    ocupados = len(quartos) - disponiveis

    # =========================
    # CARDS DE STATUS
    # =========================
    status_cards = ft.Row(
        [
            ft.Container(
                content=ft.Column(
                    [
                        ft.Text("Quartos Disponíveis", size=16, color=ft.Colors.WHITE),
                        ft.Text(
                            str(disponiveis),
                            size=28,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.WHITE,
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                padding=20,
                width=200,
                height=100,
                bgcolor=SUCCESS_COLOR,
                border_radius=10,
            ),
            ft.Container(
                content=ft.Column(
                    [
                        ft.Text("Quartos Ocupados", size=16, color=ft.Colors.WHITE),
                        ft.Text(
                            str(ocupados),
                            size=28,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.WHITE,
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                padding=20,
                width=200,
                height=100,
                bgcolor=ERROR_COLOR,
                border_radius=10,
            ),
        ],
        spacing=20,
        alignment=ft.MainAxisAlignment.CENTER,
    )

    # =========================
    # LISTA DE QUARTOS
    # =========================
    lista_quartos = ft.Column(spacing=10)

    for quarto in quartos:
        disponivel = quarto["numero"] in numeros_disponiveis

        status = "Disponível" if disponivel else "Ocupado"
        status_color = SUCCESS_COLOR if disponivel else ERROR_COLOR
        checkout = quarto.get('checkout', '') if status == 'Ocupado' else ''

        card = ft.Card(
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.ListTile(
                            leading=ft.Icon(
                                name=ft.Icons.KING_BED,
                                color=PRIMARY_COLOR,
                            ),
                            title=ft.Text(
                                f"Quarto {quarto['numero']} - {quarto['tipo'].capitalize()}"
                            ),
                            subtitle=ft.Text(
                                f"R$ {quarto['preco']:.2f} / noite - checkout:  {checkout}"
                            ),
                            trailing=ft.Container(
                                content=ft.Text(
                                    status,
                                    color=ft.Colors.WHITE,
                                ),                                                         
                                padding=ft.Padding(
                                    left=10, right=10, top=5, bottom=5
                                ),
                                bgcolor=status_color,
                                border_radius=20,
                            ),
                        ),
                    ]
                ),
                padding=10,
            ),
            elevation=5,
            margin=ft.Margin(top=5, bottom=5, left=0, right=0),
        )

        lista_quartos.controls.append(card)

    # =========================
    # MENU
    # =========================
    menu = ft.NavigationBar(
        destinations=[
            ft.NavigationBarDestination(icon=ft.Icons.HOTEL, label="Inicio"),
            ft.NavigationBarDestination(icon=ft.Icons.CALENDAR_TODAY, label="Reservar"),
            ft.NavigationBarDestination(icon=ft.Icons.PEOPLE, label="Clientes"),
            ft.NavigationBarDestination(icon=ft.Icons.LIST_ALT, label="Reservas"),
        ],
        on_change=lambda e: page.go(
            "/"
            if e.control.selected_index == 0
            else "/reservar"
            if e.control.selected_index == 1
            else "/clientes"
            if e.control.selected_index == 2
            else "/reservas"
        ),
        bgcolor=PRIMARY_COLOR,
        indicator_color=ACCENT_COLOR,
        selected_index=0,
    )

    # =========================
    # LAYOUT FINAL
    # =========================
    layout = ft.Column(
        controls=[
            header,
            ft.Container(content=status_cards, padding=20),
            ft.Text(
                "Quartos",
                size=20,
                weight=ft.FontWeight.BOLD,
                text_align=ft.TextAlign.CENTER,
            ),
            ft.Container(content=lista_quartos, padding=20),
        ],
        spacing=0,
        expand=True,
    )

    page.add(layout, menu)
    page.update()
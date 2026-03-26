import flet as ft
from models.gerenciador import GerenciadorDeReservas
from initial import tela_inicial
from client import tela_clientes
from reserve import tela_reservas
from viewreserve import tela_visualizar_reservas

# Configurações de tema
PRIMARY_COLOR = "#4a6fa5"
SECONDARY_COLOR = "#166088"
TERTIARY_COLOR = "#dbe9ee"
ACCENT_COLOR = "#4fc3f7"
BACKGROUND_COLOR = "#f8f9fa"
CARD_COLOR = "#ffffff"
ERROR_COLOR = "#e63946"
SUCCESS_COLOR = "#2a9d8f"

gerenciador = GerenciadorDeReservas()

def main(page: ft.Page):
    page.theme = ft.Theme(
        color_scheme=ft.ColorScheme(
            primary=PRIMARY_COLOR,
            secondary=SECONDARY_COLOR,
            surface=TERTIARY_COLOR,
        ),
    )
    
    
    def rotas(e):
        page.controls.clear()

        if page.route == "/":
            tela_inicial(page, gerenciador)
        elif page.route == "/clientes":
            tela_clientes(page, gerenciador)
        elif page.route == "/reservar":
            tela_reservas(page, gerenciador)
        elif page.route == "/reservas":
            tela_visualizar_reservas(page, gerenciador)
        
        page.update()

    page.on_route_change = rotas
    page.go("/")

ft.app(target=main, view=ft.WEB_BROWSER)

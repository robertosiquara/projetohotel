import flet as ft
from models.gerenciador import GerenciadorDeReservas

gerenciador = GerenciadorDeReservas()

PRIMARY_COLOR = "#4a6fa5"
SECONDARY_COLOR = "#166088"
CARD_COLOR = "#2b2929"
BGCARD_COLOR = "#0a0a0a"
ERROR_COLOR = "#e63946"
SUCCESS_COLOR = "#2a9d8f"
ACCENT_COLOR = "#4fc3f7"

def tela_clientes(page: ft.Page, gerenciador: GerenciadorDeReservas):
    page.title = "Clientes - Refúgio dos Sonhos"
    page.controls.clear()

    header = ft.Container(
        content=ft.Row([
            ft.IconButton(icon=ft.Icons.ARROW_BACK,icon_color=ft.Colors.WHITE, on_click=lambda e: page.go("/")),
            ft.Text("Gerenciar Clientes", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=10
        ),
        padding=20,
        bgcolor=PRIMARY_COLOR,
        border_radius=ft.BorderRadius(top_left=10, top_right=10, bottom_left=10,bottom_right=10)
    )

    nome = ft.TextField(label="Nome completo", border_radius=10, border_color=PRIMARY_COLOR, width=600,)
    telefone = ft.TextField(label="Telefone", border_radius=10, border_color=PRIMARY_COLOR, width=600,)
    email = ft.TextField(label="E-mail", border_radius=10, border_color=PRIMARY_COLOR, width=600,)
    mensagem = ft.Text("", color=ERROR_COLOR)

    lista_clientes = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Nome", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Telefone", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("E-mail", weight=ft.FontWeight.BOLD)),
        ],
        rows=[],
        border=ft.Border(1, PRIMARY_COLOR),
        border_radius=10,
        heading_row_color=SECONDARY_COLOR,
        heading_text_style=ft.TextStyle(color=ft.Colors.WHITE),
    )

    lista_clientes = ft.Row(spacing=10, scroll=ft.ScrollMode.AUTO,wrap=True)

    def carregar_clientes():
        lista_clientes.controls.clear()

        try:
            clientes = gerenciador.listar_clientes()

            if not clientes:
                lista_clientes.controls.append(
                    ft.Text("Nenhum cliente cadastrado.", color=ERROR_COLOR)
                )
            else:
                for c in clientes:
                    card = ft.Card(
                        content=ft.Container(
                            width= 200,
                            padding=15,
                            bgcolor=CARD_COLOR,
                            border_radius=10,
                            content=ft.Column(
                                [
                                    ft.Text(f"👤 {c.get('nome', 'N/A')}", size=16, weight=ft.FontWeight.BOLD),
                                    ft.Text(f"📞 {c.get('telefone', 'N/A')}"),
                                    ft.Text(f"✉️ {c.get('email', 'N/A')}"),
                                ],
                                spacing=5
                            )
                        ),
                        elevation=3,
                        margin=ft.Margin(top=5, bottom=5, right=0, left=0)
                    )
                    lista_clientes.controls.append(card)
        except Exception as e:
            lista_clientes.controls.append(
                ft.Text(f"Erro ao carregar clientes: {e}", color=ERROR_COLOR)
            )

        page.update()


    def adicionar_cliente(e):
        if nome.value and telefone.value and email.value:
            sucesso = gerenciador.adicionar_cliente(nome.value, telefone.value, email.value)
            if sucesso:
                mensagem.value = "Cliente adicionado com sucesso!"
                mensagem.color = SUCCESS_COLOR
                nome.value = telefone.value = email.value = ""
            else:
                mensagem.value = "Erro ao adicionar cliente!"
                mensagem.color = ERROR_COLOR
            carregar_clientes()
        else:
            mensagem.value = "Preencha todos os campos!"
            mensagem.color = ERROR_COLOR
        page.update()

    menu = ft.NavigationBar(
        destinations=[
            ft.NavigationBarDestination(icon=ft.Icons.HOTEL, label="Inicio"),
            ft.NavigationBarDestination(icon=ft.Icons.CALENDAR_TODAY, label="Reservar"),
            ft.NavigationBarDestination(icon=ft.Icons.PEOPLE, label="Clientes"),
            ft.NavigationBarDestination(icon=ft.Icons.LIST_ALT, label="Reservas"),
        ],
        on_change=lambda e: page.go(
            "/" if e.control.selected_index == 0 else
            "/reservar" if e.control.selected_index == 1 else
            "/clientes" if e.control.selected_index == 2 else
            "/reservas"
        ),
        bgcolor=PRIMARY_COLOR,
        indicator_color=ACCENT_COLOR,
        selected_index=2
    )

    layout = ft.Column([
        header,
        ft.Container(
            content=ft.Column([
                ft.Text("Adicionar Novo Cliente", size=18, weight=ft.FontWeight.BOLD),
                nome,
                telefone,
                email,
                ft.ElevatedButton(
                    "Salvar Cliente",
                    on_click=adicionar_cliente,
                    bgcolor=PRIMARY_COLOR,
                    color=ft.Colors.WHITE,
                    width=600, height=50
                ),
                mensagem,
                ft.Divider(height=20),
                ft.Text("Clientes Cadastrados", size=18, weight=ft.FontWeight.BOLD),
                ft.Container(
                    content=lista_clientes,
                    padding=10,
                    border_radius=10,
                    bgcolor=BGCARD_COLOR
                ),
            ],horizontal_alignment="center", spacing=15, scroll=ft.ScrollMode.AUTO),
            
        )
    ])
    
    page.add(layout,menu)
    carregar_clientes()

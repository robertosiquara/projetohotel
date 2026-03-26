import flet as ft
from models.gerenciador import GerenciadorDeReservas
from datetime import datetime

gerenciador = GerenciadorDeReservas()

PRIMARY_COLOR = "#4a6fa5"
SECONDARY_COLOR = "#166088"
ERROR_COLOR = "#e63946"
SUCCESS_COLOR = "#2a9d8f"
ACCENT_COLOR = "#4fc3f7"

def tela_visualizar_reservas(page: ft.Page, gerenciador):
    page.title = "Reservas Atuais - Refúgio dos Sonhos"
    page.controls.clear()
    page.scroll = ft.ScrollMode.AUTO
    
    data_selecionada = None

    def ao_selecionar_data(e):
        nonlocal data_selecionada
        if e.control.value:
            # Mantemos o valor interno no formato que o filtro espera comparar
            data_selecionada = e.control.value.strftime("%d/%m/%Y") 
            filtro_data.value = data_selecionada
            page.update()

    date_picker = ft.DatePicker(
        first_date=datetime.now(),
        last_date=datetime.now().replace(year=datetime.now().year + 1),
        on_change=ao_selecionar_data
    )

    page.overlay.append(date_picker)

    def abrir_calendario(e):
        date_picker.open = True
        page.update()


    header = ft.Container(
        content=ft.Row([
            ft.IconButton(icon=ft.Icons.ARROW_BACK, icon_color=ft.Colors.WHITE, on_click=lambda e: page.go("/")),
            ft.Text("Reservas Atuais", size=24, weight="bold", color=ft.Colors.WHITE),
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=10
        ),
        padding=20,
        bgcolor=PRIMARY_COLOR,
        border_radius=ft.BorderRadius(top_left=10, top_right=10, bottom_left=10,bottom_right=10)
    )

    mensagem = ft.Text("", color=ERROR_COLOR)
    lista_reservas = ft.Column(spacing=10)

    filtro_cliente = ft.TextField(label="Cliente", width=600, border_color=PRIMARY_COLOR)
    filtro_quarto = ft.TextField(label="Quarto", width=600, border_color=PRIMARY_COLOR)
    
    filtro_data = ft.TextField(
        label="Check-in",
        width=600,
        read_only=True,
        border_color=PRIMARY_COLOR,
        on_click= abrir_calendario
    )

    filtro_status = ft.Dropdown(
        label="Status",
        options=[
            ft.dropdown.Option("ativa"),
            ft.dropdown.Option("cancelada"),
        ],
        border_color=PRIMARY_COLOR,
        width=600
    )

    botao_filtrar = ft.ElevatedButton(
        "Filtrar",
        on_click=lambda e: filtrar_e_limpar(e),
        bgcolor=PRIMARY_COLOR,
        color=ft.Colors.WHITE,
        width=600, height=50
    )

    

    def carregar_reservas():
        lista_reservas.controls.clear()
        
        # IMPORTANTE: Como as datas agora são strings (devido ao DATE_FORMAT no SQL),
        # a ordenação por r["checkin"] pode ficar alfabética (errada). 
        # O ideal é que o SQL já traga ordenado, mas mantemos aqui por segurança.
        reservas = gerenciador.listar_reservas()

        cliente = filtro_cliente.value.lower() if filtro_cliente.value else ''
        quarto = filtro_quarto.value
        
        # Mudamos o formato aqui para bater com o que o DatePicker coloca no campo
        data_filtro = filtro_data.value if filtro_data.value else None
        status = filtro_status.value
        
        reservas_filtradas = []

        for r in reservas:
            # CORREÇÃO DO ERRO: 
            # Como o banco já manda DD/MM/AAAA, usamos %d/%m/%Y para validar
            if isinstance(r["checkin"], str):
                try:
                    # Tenta converter para objeto date para comparar com precisão se necessário
                    checkin_r_obj = datetime.strptime(r["checkin"], "%d/%m/%Y").date()
                    checkin_str = r["checkin"]
                except ValueError:
                    # Caso ainda venha algum resquício no formato antigo
                    checkin_r_obj = datetime.strptime(r["checkin"], "%Y-%m-%d").date()
                    checkin_str = checkin_r_obj.strftime("%d/%m/%Y")
            else:
                checkin_r_obj = r["checkin"]
                checkin_str = checkin_r_obj.strftime("%d/%m/%Y")

            # Lógica de Filtros
            if cliente and cliente not in r['cliente'].lower():
                continue

            if quarto and quarto != str(r["numero"]):
                continue

            # Compara a string da data formatada
            if data_filtro and checkin_str != data_filtro:
                continue

            if status and status != r["status"]:
                continue

            reservas_filtradas.append(r)

        if not reservas_filtradas:
            lista_reservas.controls.append(ft.Text("Nenhuma reserva encontrada."))
            page.update()
            return        

        for r in reservas_filtradas:
            status_color = SUCCESS_COLOR if r["status"] == "ativa" else ERROR_COLOR
            mode_color = ERROR_COLOR if r["status"] == "ativa" else "grey"
            
            lista_reservas.controls.append(
                ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.ListTile(
                                leading=ft.Icon(ft.Icons.CALENDAR_TODAY, color=PRIMARY_COLOR),
                                title=ft.Text(f"{r['cliente']} - Quarto {r['numero']}"),
                                # Exibe as datas que já vêm formatadas do banco
                                subtitle=ft.Text(f"Estadia: {r['checkin']} até {r['checkout']}"),
                                trailing=ft.Container(
                                    content=ft.Text(r["status"].capitalize(), color=ft.Colors.WHITE),
                                    bgcolor=status_color,
                                    padding=ft.Padding(left=10,right=10,top= 5, bottom=5),
                                    border_radius=20
                                )
                            ),
                            ft.Row([
                                ft.ElevatedButton(
                                    "Cancelar Reserva",
                                    on_click=lambda e, id=r["id"]: cancelar_reserva(id),
                                    disabled=r["status"] != "ativa",
                                    bgcolor=mode_color,
                                    color=ft.Colors.WHITE
                                )
                            ], alignment="end")
                        ]),
                        padding=10
                    )
                )
            )
        page.update()

    def filtrar_e_limpar(e):
        carregar_reservas()  # aplica os filtros

        # 🔥 limpa depois de filtrar
        filtro_cliente.value = ""
        filtro_quarto.value = ""
        filtro_data.value = ""
        filtro_status.value = ""

        page.update()

    def cancelar_reserva(reserva_id):
        sucesso = gerenciador.cancelar_reserva(reserva_id)
        if sucesso:
            mensagem.value = "Reserva cancelada com sucesso!"
            mensagem.color = SUCCESS_COLOR
        else:
            mensagem.value = "Erro ao cancelar reserva!"
            mensagem.color = ERROR_COLOR
        carregar_reservas()
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
        selected_index=3
    )

    layout = ft.Column([
        header,
        filtro_cliente,
        filtro_quarto,
        filtro_data,
        filtro_status,
        botao_filtrar,
        ft.Divider(height=20),
        ft.Container(
            content=ft.Column([
                ft.Text("Lista de Reservas", size=18, weight="bold"),
                mensagem,
                lista_reservas
            ], spacing=15),
            padding=20,
        )
    ],horizontal_alignment="center")

    page.add(layout, menu)
    carregar_reservas()

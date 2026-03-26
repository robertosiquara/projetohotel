import flet as ft
from models.gerenciador import GerenciadorDeReservas
from datetime import datetime, timedelta
import calendar

# Cores do Sistema
PRIMARY_COLOR = "#4a6fa5"
SECONDARY_COLOR = "#166088"
ACCENT_COLOR = "#4fc3f7"
ERROR_COLOR = "#e63946"
SUCCESS_COLOR = "#2a9d8f"
DISABLED_COLOR = "#e0e0e0"

def tela_reservas(page: ft.Page, gerenciador: GerenciadorDeReservas):
    page.title = "Nova Reserva - Refúgio dos Sonhos"
    page.controls.clear()
    page.scroll = ft.ScrollMode.AUTO

    # Estado da Tela
    datas_bloqueadas = set()
    data_checkin_valor = None
    data_checkout_valor = None
    hoje = datetime.now().date()
    data_base = datetime.now().replace(day=1)

    # =========================
    # COMPONENTES DE INTERFACE
    # =========================
    header = ft.Container(
        content=ft.Row([
            ft.IconButton(icon=ft.Icons.ARROW_BACK, icon_color=ft.Colors.WHITE, on_click=lambda _: page.go("/")),
            ft.Text("Nova Reserva", size=24, weight="bold", color=ft.Colors.WHITE),
        ], alignment=ft.MainAxisAlignment.CENTER),
        padding=20, bgcolor=PRIMARY_COLOR,
        border_radius=ft.BorderRadius(10, 10, 10, 10)
    )

    dropdown_clientes = ft.Dropdown(
        label="Cliente",
        options=[ft.dropdown.Option(text=c["nome"], key=str(c["id"])) for c in gerenciador.listar_clientes()],
        width=600, border_radius=10, border_color=PRIMARY_COLOR
    )

    dropdown_quartos = ft.Dropdown(
        label="Selecione o Quarto para ver disponibilidade",
        options=[ft.dropdown.Option(
            text=f'Quarto {q["numero"]} - {q["tipo"].capitalize()}',
            key=str(q["numero"])
        ) for q in gerenciador.listar_quartos()],
        width=600, border_radius=10, border_color=PRIMARY_COLOR
    )

    data_checkin = ft.TextField(label="Check-in", read_only=True, width=290, border_radius=10, border_color=PRIMARY_COLOR)
    data_checkout = ft.TextField(label="Check-out", read_only=True, width=290, border_radius=10, border_color=PRIMARY_COLOR)
    mensagem = ft.Text("", size=16, weight="bold")

    calendario_container = ft.Column(spacing=10, horizontal_alignment=ft.CrossAxisAlignment.CENTER)

    # =========================
    # LÓGICA DO CALENDÁRIO
    # =========================

    def selecionar_data(data_str):
        nonlocal data_checkin_valor, data_checkout_valor
        
        if data_str in datas_bloqueadas:
            return 

        if not data_checkin_valor or (data_checkin_valor and data_checkout_valor):
            data_checkin_valor = data_str
            data_checkout_valor = None
            data_checkin.value = datetime.strptime(data_str, "%Y-%m-%d").strftime("%d/%m/%Y")
            data_checkout.value = ""
        elif not data_checkout_valor:
            if data_str <= data_checkin_valor:
                mensagem.value = "O Checkout deve ser após o Check-in!"
                mensagem.color = ERROR_COLOR
            else:
                data_checkout_valor = data_str
                data_checkout.value = datetime.strptime(data_str, "%Y-%m-%d").strftime("%d/%m/%Y")
                mensagem.value = ""
        
        renderizar_calendario()

    def gerar_dias(ano, mes):
        cal = calendar.monthcalendar(ano, mes)
        rows = []
        for semana in cal:
            row = ft.Row(alignment=ft.MainAxisAlignment.CENTER, spacing=5)
            for dia in semana:
                if dia == 0:
                    row.controls.append(ft.Container(width=40, height=40))
                    continue
                
                data_atual_loop = f"{ano}-{mes:02d}-{dia:02d}"
                esta_bloqueado = data_atual_loop in datas_bloqueadas
                
                bgcolor = SUCCESS_COLOR
                text_color = ft.Colors.WHITE
                opacity = 1.0
                
                if esta_bloqueado:
                    bgcolor = DISABLED_COLOR
                    text_color = ft.Colors.GREY_500
                    opacity = 0.6
                elif data_atual_loop == data_checkin_valor:
                    bgcolor = SECONDARY_COLOR
                elif data_atual_loop == data_checkout_valor:
                    bgcolor = ACCENT_COLOR
                elif data_checkin_valor and data_checkout_valor and data_checkin_valor < data_atual_loop < data_checkout_valor:
                    bgcolor = ft.Colors.BLUE_50
                    text_color = SECONDARY_COLOR

                row.controls.append(
                    ft.Container(
                        content=ft.Text(str(dia), color=text_color, weight="bold"),
                        alignment=ft.alignment.center,
                        width=40, height=40,
                        bgcolor=bgcolor,
                        border_radius=20,
                        opacity=opacity,
                        on_click=lambda e, d=data_atual_loop: selecionar_data(d) if d not in datas_bloqueadas else None
                    )
                )
            rows.append(row)
        return ft.Column(rows)

    def renderizar_calendario():
        calendario_container.controls.clear()
        
        meses = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", 
                 "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
        mes_nome = meses[data_base.month - 1]
        
        topo = ft.Row([
            ft.IconButton(ft.Icons.CHEVRON_LEFT, on_click=lambda _: mudar_mes(-1)),
            ft.Text(f"{mes_nome} {data_base.year}", size=18, weight="bold"),
            ft.IconButton(ft.Icons.CHEVRON_RIGHT, on_click=lambda _: mudar_mes(1)),
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, width=320)

        dias_semana = ft.Row([
            ft.Text(d, width=40, text_align="center", size=12, weight="bold") 
            for d in ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"]
        ], alignment=ft.MainAxisAlignment.CENTER)

        calendario_container.controls.extend([topo, dias_semana, gerar_dias(data_base.year, data_base.month)])
        page.update()

    def mudar_mes(delta):
        nonlocal data_base
        # Calcula o novo mês
        proximo_mes = data_base.month + delta
        novo_ano = data_base.year
        
        if proximo_mes > 12:
            proximo_mes = 1
            novo_ano += 1
        elif proximo_mes < 1:
            proximo_mes = 12
            novo_ano -= 1
        
        # Garante que nova_data seja um objeto DATE puro (usando .date())
        nova_data = data_base.replace(year=novo_ano, month=proximo_mes).date()
        
        # Agora a comparação funciona: date >= date
        if nova_data >= hoje.replace(day=1):
            # Para continuar as próximas operações, voltamos para datetime se necessário
            # ou apenas mantemos como date se o resto do código suportar
            data_base = datetime.combine(nova_data, datetime.min.time())
            renderizar_calendario()

    def atualizar_disponibilidade(e):
        nonlocal datas_bloqueadas
        datas_bloqueadas.clear()
        
        # 1. Bloquear passado (até ontem)
        d_aux = hoje - timedelta(days=365)
        while d_aux < hoje:
            datas_bloqueadas.add(d_aux.strftime("%Y-%m-%d"))
            d_aux += timedelta(days=1)
        
        # 2. Bloquear datas ocupadas
        if dropdown_quartos.value:
            reservas = gerenciador.buscar_datas_ocupadas(int(dropdown_quartos.value))
            for r in reservas:
                inicio = r["checkin"]
                fim = r["checkout"]
                
                # CORREÇÃO: Se o banco enviou string, converte para date
                if isinstance(inicio, str):
                    inicio = datetime.strptime(inicio, "%d/%m/%Y").date()
                if isinstance(fim, str):
                    fim = datetime.strptime(fim, "%d/%m/%Y").date()
                
                while inicio <= fim:
                    datas_bloqueadas.add(inicio.strftime("%Y-%m-%d"))
                    inicio += timedelta(days=1)
        
        renderizar_calendario()

    dropdown_quartos.on_change = atualizar_disponibilidade

    def confirmar_reserva(e):
        if not all([dropdown_clientes.value, dropdown_quartos.value, data_checkin_valor, data_checkout_valor]):
            mensagem.value = "⚠️ Preencha todos os campos!"
            mensagem.color = ERROR_COLOR
        else:
            sucesso = gerenciador.criar_reserva(
                int(dropdown_clientes.value),
                int(dropdown_quartos.value),
                data_checkin_valor,
                data_checkout_valor
            )
            if sucesso:
                mensagem.value = "✅ Reserva realizada com sucesso!"
                mensagem.color = SUCCESS_COLOR
                atualizar_disponibilidade(None)
            else:
                mensagem.value = "❌ Erro: Conflito de datas."
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
        selected_index=1
    )

    # Layout
    layout = ft.Column([
        header,
        ft.Container(
            content=ft.Column([
                dropdown_clientes,
                dropdown_quartos,
                ft.Row([data_checkin, data_checkout], alignment="center"),
                ft.Divider(),
                ft.Text("Disponibilidade:", weight="bold"),
                calendario_container,
                mensagem,
                ft.ElevatedButton(
                    "Confirmar Reserva", 
                    on_click=confirmar_reserva,
                    bgcolor=PRIMARY_COLOR, color="white",
                    width=600, height=50
                ),
            ], horizontal_alignment="center", spacing=20),
            padding=20
        )
    ], expand=True)

    page.add(layout,menu)
    atualizar_disponibilidade(None)
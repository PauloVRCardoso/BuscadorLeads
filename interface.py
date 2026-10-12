import tkinter as tk
from tkinter import ttk
from tkinter import messagebox, filedialog
from services.categorias import CATEGORIAS
from services.buscar_coordenada import buscar_coordenadas
from services.empresas import buscar_empresas
from services.enriquecimento import enriquecer_empresas
from services.tratamento import tratar_empresas
import threading

def criar_interface():
    janela = tk.Tk()

    janela.title("BuscadorLeads")
    janela.geometry("1100x600")

    df_resultado = None

    #Titulo
    titulo = ttk.Label(
        janela,
        text="Buscador de Leads",
        font=("Arial", 18)
    )

    titulo.pack(pady=20)

    #Endereço
    label_endereco = ttk.Label(
        janela,
        text="Endereço Inicial"
    )

    label_endereco.pack()

    input_endereco = ttk.Entry(
        janela,
        width=60
    )

    input_endereco.pack(pady=(5))

    #Raio
    label_raio = ttk.Label(
        janela,
        text="Raio de pesquisa (km):"
    )

    label_raio.pack(pady=(15,0))

    input_raio = ttk.Entry(
        janela,
        width=20
    )

    input_raio.pack(pady=5)

    #Tipo
    label_tipo = ttk.Label(
        janela,
        text="Tipo de empresa:"
    )

    label_tipo.pack(pady=(15,0))

    input_tipo = ttk.Combobox(
        janela,
        values=list(CATEGORIAS.keys()),
        state="readonly",
        width=30
    )

    input_tipo.pack(pady=5)

    input_tipo.set("Selecione uma categoria:")

    def finalizar_pesquisa(df, estatisticas):

        nonlocal df_resultado

        # Guarda o DataFrame para posteriormente
        # poder exportá-lo para Excel.
        df_resultado = df

        # Para a animação.
        barra_progresso.stop()

        # Libera novamente o botão.
        botao_pesquisar.config(
            state="normal"
        )

        # Atualiza o status.
        label_status.config(
            text=f"{len(df_resultado)} empresas encontradas"
        )

        # Limpa resultados da pesquisa anterior.
        for item in tabela.get_children():
            tabela.delete(item)

        # Insere os novos resultados.
        for _, linha in df_resultado.iterrows():

            tabela.insert(
                "",
                "end",
                values=(
                    linha["Empresa"],
                    linha["Endereço"],
                    linha["Telefone"],
                    linha["Site"]
                )
            )

    def finalizar_sem_endereco():

        barra_progresso.stop()

        botao_pesquisar.config(
            state="normal"
        )

        label_status.config(
            text="Endereço não encontrado"
        )

        messagebox.showwarning(
            "Endereço",
            "Não foi possível localizar o endereço informado."
        )

    def finalizar_sem_resultados():

        barra_progresso.stop()

        botao_pesquisar.config(
            state="normal"
        )

        label_status.config(
            text="Nenhuma empresa encontrada"
        )

        messagebox.showinfo(
            "Pesquisa",
            "Nenhuma empresa foi encontrada."
        )


    def finalizar_com_erro(erro):

        barra_progresso.stop()

        botao_pesquisar.config(
            state="normal"
        )

        label_status.config(
            text="Erro durante a pesquisa"
        )

        messagebox.showerror(
            "Erro",
            f"Não foi possível realizar a pesquisa.\n\n{erro}"
        )

    def executar_pesquisa(endereco, raio_km, tipo_google):

        try:
            latitude, longitude = buscar_coordenadas(endereco)

            if latitude is None or longitude is None:
                janela.after(0,finalizar_sem_endereco)
                return

            empresas = buscar_empresas(
                latitude,
                longitude,
                raio_km,
                tipo_google
            )

            if not empresas:
                janela.after(0,finalizar_sem_resultados)
                return

            empresas, estatisticas = enriquecer_empresas(
                empresas,
                limite=20
            )

            df = tratar_empresas(
                empresas
            )

            janela.after(
                0,
                lambda: finalizar_pesquisa(
                    df,
                    estatisticas
                )
            )


        except Exception as erro:

            janela.after(
                0,
                lambda erro=erro: finalizar_com_erro(
                    erro
                )
            )

    def pesquisar():

        endereco = input_endereco.get().strip()
        raio_texto = input_raio.get().strip()
        categoria = input_tipo.get()

        #Validação do endereço
        if not endereco:
            messagebox.showwarning(
                "Campo obrigatório",
                "Informe o endereço inicial."
            )
            return

        #Validação do raio
        try:
            raio_km = float(
                raio_texto.replace(",", ".")
            )
        except ValueError:
            messagebox.showwarning(
            "Raio inválido",
            "Informe um número válido para o raio."
        )
            return

        if raio_km <= 0 or raio_km > 50:
            messagebox.showwarning(
                "Raio inválido",
                "Informe um raio entre 0 e 50 km."
            )
            return

        # Validação da categoria
        if categoria not in CATEGORIAS:
            messagebox.showwarning(
                "Categoria",
                "Selecione um tipo de empresa."
            )
            return

        tipo_google = CATEGORIAS[categoria]

        #Estado visual da Pesquisa
        label_status.config(
            text="Pesquisando empresas..."
        )

        barra_progresso.start(10)

        botao_pesquisar.config(
            state="disabled"
        )

        #Cria a Thread
        thread = threading.Thread(
            target=executar_pesquisa,
            args=(
                endereco,
                raio_km,
                tipo_google
            ),
            daemon=True
        )

        thread.start()

    def exportar_excel():
    
        if df_resultado is None or df_resultado.empty:
            messagebox.showwarning(
                "Sem dados",
                "Realize uma pesquisa antes de exportar."
            )
            return

        caminho = filedialog.asksaveasfilename(
            title="Salvar relatório",
            defaultextension=".xlsx",
            filetypes=[
                ("Arquivo Excel", "*.xlsx")
            ],
            initialfile="leads.xlsx"
        )

        colunas_exportar = [
            "Empresa",
            "Endereço",
            "Telefone",
            "Site"
        ]

        if not caminho:
            return

        try:
            df_resultado[colunas_exportar].to_excel(
                caminho,
                index=False
            )

            messagebox.showinfo(
                "Exportação concluída",
                "Arquivo Excel salvo com sucesso."
            )

        except Exception as erro:
            messagebox.showerror(
                "Erro",
                f"Não foi possível salvar o arquivo.\n\n{erro}"
            )

    #Botão
    botao_pesquisar = ttk.Button(
        janela,
        text="Pesquisar",
        command=pesquisar
    )

    botao_pesquisar.pack(pady=25)

    botao_exportar = ttk.Button(
            janela,
            text="Exportar Excel",
            command=exportar_excel
        )
    
    botao_exportar.pack(pady=5)

    # Status
    label_status = ttk.Label(
        janela,
        text="Pronto para pesquisar"
    )

    label_status.pack(pady=5)

    #Barra de progresso
    barra_progresso = ttk.Progressbar(
        janela,
        mode="indeterminate",
        length=300
    )

    barra_progresso.pack(pady=5)

    # Área da tabela
    frame_tabela = ttk.Frame(janela)

    frame_tabela.pack(
    fill="both",
    expand=True,
    padx=20,
    pady=10
    )

    colunas = (
    "Empresa",
    "Endereço",
    "Telefone",
    "Site"
    )

    tabela = ttk.Treeview(
    frame_tabela,
    columns=colunas,
    show="headings"
    )

    for coluna in colunas:
        tabela.heading(
            coluna,
            text=coluna
        )

    tabela.column(
        "Empresa",
        width=200
    )

    tabela.column(
        "Endereço",
        width=400
    )

    tabela.column(
        "Telefone",
        width=150
    )

    tabela.column(
        "Site",
        width=250
    )

    # Barra de rolagem vertical
    scroll_vertical = ttk.Scrollbar(
        frame_tabela,
        orient="vertical",
        command=tabela.yview
    )

    # Barra de rolagem horizontal
    scroll_horizontal = ttk.Scrollbar(
        frame_tabela,
        orient="horizontal",
        command=tabela.xview
    )

    # Conecta a tabela às barras
    tabela.configure(
        yscrollcommand=scroll_vertical.set,
        xscrollcommand=scroll_horizontal.set
    )

    # Posicionamento dentro do frame_tabela
    tabela.grid(
        row=0,
        column=0,
        sticky="nsew"
    )

    scroll_vertical.grid(
        row=0,
        column=1,
        sticky="ns"
    )

    scroll_horizontal.grid(
        row=1,
        column=0,
        sticky="ew"
    )

    # Permite que a tabela aumente junto com o frame
    frame_tabela.rowconfigure(
        0,
        weight=1
    )

    frame_tabela.columnconfigure(
        0,
        weight=1
    )

    janela.mainloop()

if __name__ == "__main__":
    criar_interface()
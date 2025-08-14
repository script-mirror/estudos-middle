import requests
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.table as tbl
import io
from datetime import datetime
from middle.message import send_whatsapp_message
from middle.utils import Constants, get_auth_header

class IntercambioAnalyzer:
    def __init__(self):
        """Inicializa a classe com constantes e cabeçalhos de autenticação."""
        self.consts = Constants()
        self.header = get_auth_header()
        self.base_url_api = self.consts.BASE_URL + '/api/v2/decks/'

    def get_dados_banco(self, produto: str, date: str = "") -> pd.DataFrame:
        """Obtém dados da API para o produto e data especificados."""
        res = requests.get(
            f"{self.base_url_api}{produto}",
            params={'data_produto': date},
            headers=self.header
        )
        if res.status_code != 200:
            res.raise_for_status()
        return pd.DataFrame(res.json())

    def res_to_df(self, df: pd.DataFrame) -> pd.DataFrame:
        """Converte os dados brutos em um DataFrame pivotado."""
        df['mes_ano_formatted'] = pd.to_datetime(df['mes_ano']).dt.strftime('%m/%y')
        df_pivot = df.pivot_table(
            index=['re', 'limite'],
            columns=['mes_ano_formatted', 'patamar'],
            values='valor',
            aggfunc='first'
        )
        df_pivot.columns = [
            f"{mes} {patamar.capitalize()}"
            for mes, patamar in df_pivot.columns
        ]
        df_pivot = df_pivot.reset_index().rename(columns={'re': 'RE', 'limite': 'Limite'})
        df_pivot = df_pivot.set_index('RE')
        return df_pivot

    def df_to_image(self, df: pd.DataFrame) -> bytes:
        """Converte um DataFrame em uma imagem de tabela."""
        df = df.reset_index()
        df = df.rename(columns={"RE": "Índice"})
        col_widths = []
        for col in df.columns:
            max_len = max(
                len(str(col)),
                df[col].astype(str).str.len().max()
            )
            col_widths.append(max_len * 0.015)

        total_width = sum(col_widths)
        col_widths = [w / total_width for w in col_widths]
        fig_width = len(df.columns) * 2
        fig_height = len(df) * 0.4
        fig, ax = plt.subplots(figsize=(fig_width, fig_height))
        ax.axis('off')
        table = tbl.table(
            ax,
            cellText=df.values,
            colLabels=df.columns,
            loc='center',
            cellLoc='center',
            colWidths=col_widths
        )
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1, 1.5)
        plt.tight_layout(pad=0)
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight', pad_inches=0)
        buf.seek(0)
        binary_image = buf.getvalue()
        plt.close(fig)  # Fecha a figura para liberar memória
        return binary_image

    def calculate_differences(self) -> None:
        """Calcula as diferenças entre os limites de intercâmbio de duas datas e envia mensagens."""
        df_datas = self.get_dados_banco('restricoes-eletricas/historico')
        df_datas = sorted(list(df_datas[0]), reverse=True)
        if len(df_datas) < 2:
            print("Não há dados suficientes para comparar.")
            return

        df1 = self.res_to_df(self.get_dados_banco(produto='restricoes-eletricas', date=df_datas[0]))
        df2 = self.res_to_df(self.get_dados_banco(produto='restricoes-eletricas', date=df_datas[1]))
        df1_months = [col for col in df1.columns if col != "Limite"]
        df2_months = [col for col in df2.columns if col != "Limite"]
        common_months = sorted(set(df1_months).intersection(df2_months))

        if not common_months:
            print("Nenhum mês comum encontrado entre os dois relatórios.")
            return

        diff_df = pd.DataFrame(index=df1.index)
        diff_df["Limite"] = df1["Limite"]
        for month in common_months:
            diff_df[month] = df2[month] - df1[month]
        diff_df.dropna(how="all", subset=common_months, inplace=True)
        diff_df = diff_df.reset_index()

        data_pmo = datetime.strptime(df_datas[0], '%Y-%m-%d')
        data_ant = datetime.strptime(df_datas[1], '%Y-%m-%d')

        send_whatsapp_message(
            self.consts.WHATSAPP_GILSEU,
            f"Limites de Intercambio para {str(data_pmo.month).zfill(2)}/{data_pmo.year}",
            self.df_to_image(df1)
        )
        send_whatsapp_message(
            self.consts.WHATSAPP_GILSEU,
            f"Diferença dos Limites ({str(data_pmo.month).zfill(2)}/{data_pmo.year}- {str(data_ant.month).zfill(2)}/{data_ant.year})",
            self.df_to_image(diff_df)
        )

    def run(self):
        """Método principal para executar a análise."""
        self.calculate_differences()


if __name__ == '__main__':
    analyzer = IntercambioAnalyzer()
    analyzer.run()
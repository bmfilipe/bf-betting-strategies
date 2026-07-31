from fpdf import FPDF
import datetime

class ReportExporter:
    """Service to export betting slip analyses to TXT and PDF formats."""

    @staticmethod
    def generate_txt_report(boletins_data: list[dict]) -> str:
        """Generate formatted ASCII/UTF-8 TXT report string."""
        now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        txt = f"=================================================================\n"
        txt += f"        RELATÓRIO PREDITIVO DE APOSTAS DESPORTIVAS (+EV)\n"
        txt += f"        Gerado em: {now_str}\n"
        txt += f"=================================================================\n\n"

        total_stake = sum(b["stake"] for b in boletins_data)
        total_retorno = sum(b["retorno"] for b in boletins_data)

        for b in boletins_data:
            txt += f"🎫 BOLETIM #{b['boletim_id']}\n"
            txt += f"-----------------------------------------------------------------\n"
            txt += f"  Stake: {b['stake']:.2f} EUR | Odd Total: {b['odd_total']:.2f} | Ganho Potencial: {b['retorno']:.2f} EUR\n"
            txt += f"  Seleções ({len(b['jogos_detalhe'])} jogos):\n"
            for j in b['jogos_detalhe']:
                txt += f"    • {j}\n"
            txt += f"\n"

        txt += f"=================================================================\n"
        txt += f"RESUMO FINANCEIRO GLOBAL:\n"
        txt += f"  - Quantidade de Boletins: {len(boletins_data)}\n"
        txt += f"  - Stake Total Investida: {total_stake:.2f} EUR\n"
        txt += f"  - Retorno Potencial Máximo: {total_retorno:.2f} EUR\n"
        txt += f"=================================================================\n"

        return txt

    @staticmethod
    def generate_csv_report(boletins_data: list[dict]) -> str:
        """Generate structured CSV report for Excel import."""
        csv = "Boletim_ID,Stake_EUR,Odd_Total,Retorno_Potencial_EUR,Selecao_Detalhe\n"
        for b in boletins_data:
            b_id = b['boletim_id']
            stake = b['stake']
            odd = b['odd_total']
            ret = b['retorno']
            for j in b['jogos_detalhe']:
                clean_j = j.replace('"', '""')
                csv += f'{b_id},{stake:.2f},{odd:.2f},{ret:.2f},"{clean_j}"\n'
        return csv

    @staticmethod
    def generate_pdf_report(boletins_data: list[dict]) -> bytes:
        """Generate structured PDF report bytes using FPDF."""
        pdf = FPDF()
        pdf.add_page()

        def safe_txt(s: str) -> str:
            """Convert text to latin-1 safe string for default PDF fonts."""
            return str(s).encode('latin-1', errors='replace').decode('latin-1')

        # Header
        pdf.set_font("Helvetica", 'B', 16)
        pdf.cell(0, 10, txt=safe_txt("Relatório Preditivo de Apostas - Futebol +EV"), ln=True, align='C')
        pdf.set_font("Helvetica", 'I', 10)
        now_str = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
        pdf.cell(0, 6, txt=safe_txt(f"Data de Emissão: {now_str}"), ln=True, align='C')
        pdf.ln(8)

        total_stake = sum(b["stake"] for b in boletins_data)
        total_retorno = sum(b["retorno"] for b in boletins_data)

        # Overview Box
        pdf.set_font("Helvetica", 'B', 11)
        pdf.cell(0, 7, txt=safe_txt(f"Resumo: {len(boletins_data)} Boletins | Stake Total: {total_stake:.2f} EUR | Retorno Máximo: {total_retorno:.2f} EUR"), ln=True)
        pdf.ln(4)

        # Slips
        for b in boletins_data:
            pdf.set_font("Helvetica", 'B', 12)
            pdf.set_fill_color(240, 242, 246)
            header_str = f"Boletim #{b['boletim_id']} - Stake: {b['stake']:.2f} EUR | Odd: {b['odd_total']:.2f} | Potencial: {b['retorno']:.2f} EUR"
            pdf.cell(0, 8, txt=safe_txt(header_str), ln=True, fill=True)

            pdf.set_font("Helvetica", size=9)
            for jogo in b['jogos_detalhe']:
                pdf.cell(0, 6, txt=safe_txt(f"   • {jogo}"), ln=True)
            pdf.ln(3)

        # Output bytes
        output_data = pdf.output(dest='S')
        if isinstance(output_data, str):
            return output_data.encode('latin-1', errors='replace')
        return bytes(output_data)

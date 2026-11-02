import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, HRFlowable
)
from reportlab.pdfgen import canvas

PDF_FILENAME = "UFC_VS_BANCO_MACHINE_LEARNING_COMPARATIVO.pdf"

class NumberedCanvas(canvas.Canvas):
    """Canvas de duas passadas para inserir numeração de páginas e rodapé técnico."""
    def __init__(self, *args, **kwargs):
        super(NumberedCanvas, self).__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super(NumberedCanvas, self).showPage()
        super(NumberedCanvas, self).save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748b"))
        
        # Cabeçalho (a partir da página 2)
        if self._pageNumber > 1:
            self.drawString(54, 750, "Estudo Comparativo: Machine Learning no Octógono vs. Machine Learning no Setor Bancário")
            self.setStrokeColor(colors.HexColor("#e2e8f0"))
            self.setLineWidth(0.5)
            self.line(54, 742, 558, 742)
            
        # Rodapé
        page_str = f"Página {self._pageNumber} de {page_count}"
        self.drawRightString(558, 36, page_str)
        self.drawString(54, 36, "Engenharia de Dados & Modelagem de Risco • Whitepaper Técnico Comparativo")
        self.setStrokeColor(colors.HexColor("#e2e8f0"))
        self.setLineWidth(0.5)
        self.line(54, 48, 558, 48)
        
        self.restoreState()


def build_banking_pdf(filename=PDF_FILENAME):
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()

    # Paleta visual bancária e técnica
    c_primary = colors.HexColor("#0f172a")     # Slate 900
    c_blue = colors.HexColor("#1e3a8a")        # Navy Blue
    c_emerald = colors.HexColor("#047857")     # Banking Green
    c_accent = colors.HexColor("#b91c1c")      # Red 700
    c_text = colors.HexColor("#334155")        # Slate 700
    c_bg_light = colors.HexColor("#f8fafc")    # Slate 50
    c_border = colors.HexColor("#cbd5e1")      # Slate 300

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=c_primary,
        spaceAfter=6
    )

    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=15,
        textColor=c_emerald,
        spaceAfter=12
    )

    h1_style = ParagraphStyle(
        'SectionH1',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=17,
        textColor=c_blue,
        spaceBefore=12,
        spaceAfter=6,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'SectionH2',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10.5,
        leading=14,
        textColor=c_primary,
        spaceBefore=8,
        spaceAfter=3,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'BodyDark',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=c_text,
        spaceAfter=5
    )

    bullet_style = ParagraphStyle(
        'BulletText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=12,
        textColor=c_text,
        leftIndent=12,
        spaceAfter=2.5
    )

    table_cell = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=10.5,
        textColor=c_text
    )

    table_cell_bold = ParagraphStyle(
        'TableCellBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10.5,
        textColor=c_primary
    )

    table_header = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10.5,
        textColor=colors.white
    )

    story = []

    # ==========================================
    # CAPA / TOPO
    # ==========================================
    story.append(Paragraph("ESTUDO COMPARATIVO DE ARQUITETURA & CIÊNCIA DE DADOS", subtitle_style))
    story.append(Paragraph("Machine Learning no Octógono vs. Machine Learning no Banco", title_style))
    story.append(Paragraph(
        "Como os mesmos princípios matemáticos do algoritmo de predição do UFC regem os modelos de Credit Scoring, "
        "Detecção de Fraudes e Gestão de Risco em grandes instituições financeiras (Fintechs e Bancos Tradicionais).",
        ParagraphStyle('Desc', parent=body_style, fontSize=9.5, leading=13.5, textColor=colors.HexColor("#475569"))
    ))
    story.append(HRFlowable(width="100%", thickness=2, color=c_emerald, spaceBefore=6, spaceAfter=10))

    meta_data = [
        [Paragraph("<b>Domínio A:</b> Previsão Esportiva (UFC Matchups)", table_cell), Paragraph("<b>Domínio B:</b> Risco de Crédito & FinTech (Credit Scoring)", table_cell)],
        [Paragraph("<b>Algoritmo Comum:</b> XGBoost + Platt Scaling", table_cell), Paragraph("<b>Metodologia Comum:</b> Validação Temporal Cega (Out-of-Time)", table_cell)]
    ]
    t_meta = Table(meta_data, colWidths=[250, 254])
    t_meta.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), c_bg_light),
        ('BOX', (0,0), (-1,-1), 0.5, c_border),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(t_meta)
    story.append(Spacer(1, 10))

    # ==========================================
    # 1. A TESE CENTRAL
    # ==========================================
    story.append(Paragraph("1. A Tese Central: Por que o XGBoost Domina Ambos os Mundos?", h1_style))
    story.append(Paragraph(
        "Muitos imaginam que bancos e fintechs como Nubank, Itaú ou JPMorgan utilizam inteligências artificiais místicas ou redes neurais hipercomplexas para analisar crédito. "
        "Na prática corporativa, <b>mais de 90% dos modelos de risco de crédito, detecção de fraude e churn são baseados exatamente no algoritmo que usamos neste projeto: XGBoost / Gradient Boosted Decision Trees</b>.",
        body_style
    ))
    story.append(Paragraph(
        "A razão para isso é tripla: (1) Dados de clientes e lutas são tabulares e heterogêneos (misturam medidas contínuas, inteiros e taxas); "
        "(2) Árvores de decisão capturam interações não-lineares automaticamente sem precisar de transformações manuais complexas; "
        "e (3) Modelos baseados em árvores são auditáveis e permitem extrair a importância exata de cada atributo para atender exigências regulatórias (como LGPD e Banco Central).",
        body_style
    ))

    # ==========================================
    # 2. O DE-PARA ARQUITETURAL COMPLETO
    # ==========================================
    story.append(Paragraph("2. O 'De-Para' Arquitetural: UFC vs. Banco", h1_style))
    story.append(Paragraph("Abaixo está o mapeamento conceitual direto entre os dois universos:", body_style))

    depara_data = [
        [Paragraph("Conceito de Machine Learning", table_header), Paragraph("No Modelo do UFC (Nosso Projeto)", table_header), Paragraph("No Modelo de Crédito Bancário (Fintech/Banco)", table_header)],
        [
            Paragraph("<b>Alvo Preditivo (Target y)</b>", table_cell_bold),
            Paragraph("O Lutador A vence o combate?<br/><b>1 = Vitória / 0 = Derrota</b>", table_cell),
            Paragraph("O cliente pagará a fatura em 90 dias?<br/><b>1 = Bom Pagador / 0 = Inadimplência (Default)</b>", table_cell)
        ],
        [
            Paragraph("<b>Histórico de Treino (Passado)</b>", table_cell_bold),
            Paragraph("11.441 lutas cronológicas realizadas entre 1993 e 2022.", table_cell),
            Paragraph("5 a 10 milhões de contratos de crédito concedidos nos últimos 3 a 5 anos.", table_cell)
        ],
        [
            Paragraph("<b>Conjunto de Teste (Futuro)</b>", table_cell_bold),
            Paragraph("2.143 lutas realizadas de 2023 a 2026 (Out-of-Time).", table_cell),
            Paragraph("Safras de clientes que pegaram crédito nos últimos 12 meses (Safra Cega).", table_cell)
        ],
        [
            Paragraph("<b>Variáveis Cadastrais / Perfil</b>", table_cell_bold),
            Paragraph("Altura, peso, alcance, categoria de peso oficial.", table_cell),
            Paragraph("Idade, renda declarada, estado civil, escolaridade, CEP.", table_cell)
        ],
        [
            Paragraph("<b>Variáveis de Comportamento</b>", table_cell_bold),
            Paragraph("Volume de socos/min, defesa de quedas, absorção de dano.", table_cell),
            Paragraph("Histórico de atrasos de fatura, uso do limite, transações Pix, investimentos.", table_cell)
        ],
        [
            Paragraph("<b>Variável Dinâmica Cumulativa</b>", table_cell_bold),
            Paragraph("<b>Rating Elo Histórico</b> (calculado luta a luta).", table_cell),
            Paragraph("<b>Internal Behavior Score</b> / Score Serasa (recalculado mês a mês).", table_cell)
        ],
        [
            Paragraph("<b>Métrica de Momentum</b>", table_cell_bold),
            Paragraph("<b>Streak Atual</b> (+5 vitórias ou -2 derrotas seguidas).", table_cell),
            Paragraph("<b>Pontualidade Recente</b> (pagou as últimas 6 faturas em dia sem atraso).", table_cell)
        ],
        [
            Paragraph("<b>Saída Matemática (Score)</b>", table_cell_bold),
            Paragraph("Probabilidade calibrada: <i>'67.1% de chance de vitória'</i>.", table_cell),
            Paragraph("Score de Risco (PD): <i>'Probabilidade de Calote: 3.2%'</i>.", table_cell)
        ],
        [
            Paragraph("<b>Decisão de Negócio</b>", table_cell_bold),
            Paragraph("Apostar / Selecionar favorito no fantasy game.", table_cell),
            Paragraph("Aprovar empréstimo de R$ 15.000 ou liberar limite no cartão.", table_cell)
        ]
    ]

    t_depara = Table(depara_data, colWidths=[110, 190, 204])
    t_depara.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_blue),
        ('GRID', (0,0), (-1,-1), 0.5, c_border),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_bg_light]),
        ('TOPPADDING', (0,0), (-1,-1), 3.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3.5),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(t_depara)

    story.append(PageBreak())

    # ==========================================
    # 3. O ELO ESPORTIVO VS. O BEHAVIOR SCORE BANCÁRIO
    # ==========================================
    story.append(Paragraph("3. Feature Engineering: O 'Elo' vs. o 'Score de Comportamento'", h1_style))
    story.append(Paragraph(
        "Um dos passos mais importantes que realizamos no modelo do UFC foi a injeção do <b>Rating Elo</b> como atributo de treino. "
        "Nos bancos, isso se chama <b>Behavior Score</b> (Score Comportamental Interno):",
        body_style
    ))
    story.append(Paragraph(
        "• <b>No UFC:</b> Se Carlos Prates vence um adversário fraco, seu Elo sobe apenas 4 pontos. Se vence um ex-campeão ranqueado, seu Elo salta 28 pontos. "
        "O Elo resume em um único número a qualidade do histórico do lutador.",
        bullet_style
    ))
    story.append(Paragraph(
        "• <b>No Banco:</b> Se um cliente ganha R$ 20.000 mas estoura o cheque especial todo mês, seu Behavior Score desaba. "
        "Se um autônomo ganha R$ 3.000 mas nunca atrasou uma conta de luz em 4 anos, seu Behavior Score é altíssimo. "
        "Ambos os modelos usam uma variável temporal agregada para capturar o momento e a solidez do indivíduo.",
        bullet_style
    ))

    # ==========================================
    # 4. CALIBRAÇÃO E GESTÃO DE RISCO DE RUÍNA
    # ==========================================
    story.append(Paragraph("4. Por que a Calibração de Probabilidades Salva um Banco da Falência?", h1_style))
    story.append(Paragraph(
        "No arquivo MODEL_OVERCONFIDENCE.md diagnosticamos que o XGBoost sem calibração cravava certezas de 90%+ para quase tudo. "
        "Aplicamos o <b>Platt Scaling (CalibratedClassifierCV)</b> para forçar o modelo a falar a verdade probabilística. Veja por que isso é a vida ou a morte de uma instituição financeira:",
        body_style
    ))
    story.append(Paragraph(
        "Nos bancos, a taxa de juros cobrada de um cliente é calculada diretamente pela fórmula da Perda Esperada: "
        "<b>Perda Esperada (EL) = Probabilidade de Calote (PD) * Exposição no Default (EAD) * Perda Dado o Default (LGD)</b>.",
        body_style
    ))
    story.append(Paragraph(
        "Se o modelo do banco for hiperconfiante e disser que a probabilidade de calote de um grupo de clientes é de <b>1%</b>, mas na realidade for de <b>8%</b>, "
        "o banco cobrará uma taxa de juros muito barata, emprestará bilhões de reais e entrará em insolvência quando os calotes reais chegarem. "
        "A calibração de probabilidade é a ferramenta matemática que garante que 5% de risco signifique exatamente 5 calotes em cada 100 clientes.",
        body_style
    ))

    # ==========================================
    # 5. O PARADOXO DOS OUTLIERS: REGULAÇÃO VS. ML PURO
    # ==========================================
    story.append(Paragraph("5. Regras de Negócio e o Paradoxo dos Outliers", h1_style))
    story.append(Paragraph(
        "Quando discutimos o caso de <b>Alex Pereira (39 anos)</b> e <b>Alexander Volkanovski (38 anos)</b>, descobrimos que colocar a idade pura no modelo "
        "tornava o algoritmo 'etarista', rebaixando lendas do esporte para a vala comum dos lutadores medianos.",
        body_style
    ))
    story.append(Paragraph(
        "Nos bancos, acontece exatamente a mesma coisa, mas com amparo legal e regulatório:",
        body_style
    ))
    story.append(Paragraph("• <b>Compliance e Leis Anti-Discriminação:</b> Bancos são proibidos por lei de usar variáveis como raça, religião ou gênero, e existem regras estritas sobre o uso da idade para que idosos ou jovens não sejam negados sumariamente apenas pela faixa etária.", bullet_style))
    story.append(Paragraph("• <b>Regras de Política de Crédito (Hard Rules):</b> Assim como no UFC criamos a função <i>weight_classes_compatible</i> para impedir que um peso-mosca lute com um peso-pesado, bancos têm 'regras de esteira' antes do modelo de IA rodar (ex: se o cliente tiver nome negativado com mais de 5 protestos judiciais, ele é barrado pela política antes mesmo do XGBoost ser acionado).", bullet_style))

    # ==========================================
    # 6. DERIVA DE CONCEITO E MANUTENÇÃO (DATA DRIFT)
    # ==========================================
    story.append(Paragraph("6. Como os Bancos Mantêm seus Modelos Vivos (Data Drift)", h1_style))
    story.append(Paragraph(
        "Você perguntou como se treinam novos dados: no nosso projeto, quando o dono do Kaggle atualizou para 2026, criamos o script <i>update_dataset_2026.py</i> e retreinamos o XGBoost. "
        "No setor bancário, isso é chamado de <b>Monitoramento de Data Drift e Concept Drift</b>:",
        body_style
    ))
    story.append(Paragraph("• <b>No UFC:</b> O esporte muda. O estilo de luta dominante em 2026 envolve muito mais trocação defensiva e grade do que o jiu-jitsu tradicional de 1995.", bullet_style))
    story.append(Paragraph("• <b>No Banco:</b> A economia muda. Um cliente que era 'baixo risco' com taxa de juros Selic a 2% ao ano pode virar 'alto risco' quando a Selic sobe para 14% ao ano. Por isso, os bancos rodam pipelines automáticos mensais (usando ferramentas como Airflow e Kubeflow) para retreinar seus modelos com a safra mais recente de dados.", bullet_style))

    # ==========================================
    # 7. CONCLUSÃO
    # ==========================================
    story.append(Paragraph("7. Conclusão: A Transferência de Habilidade", h1_style))
    story.append(Paragraph(
        "Ao construir e entender este sistema de predição do UFC — dominando a <b>divisão temporal cega (Out-of-Time)</b>, "
        "a <b>engenharia de atributos sequencial sem vazamento (Elo e Streaks)</b>, o <b>treinamento do XGBoost com regularização</b> "
        "e a <b>calibração sigmoidal de probabilidades</b> —, você dominou exatamente o mesmo ferramental técnico, matemático e conceitual "
        "exigido para construir modelos de risco em fintechs de ponta e nos maiores bancos do planeta.",
        body_style
    ))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Relatório comparativo gerado com sucesso: '{filename}'")

if __name__ == '__main__':
    build_banking_pdf()

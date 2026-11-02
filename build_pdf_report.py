import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas

PDF_FILENAME = "DOCUMENTACAO_TECNICA_UFC_PREDICTION.pdf"

class NumberedCanvas(canvas.Canvas):
    """Canvas de duas passadas para inserir numeração de páginas correta e rodapé elegante."""
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
            self.drawString(54, 750, "UFC Fight Prediction System — Relatório Técnico de Engenharia & Machine Learning")
            self.setStrokeColor(colors.HexColor("#e2e8f0"))
            self.setLineWidth(0.5)
            self.line(54, 742, 558, 742)
            
        # Rodapé
        page_str = f"Página {self._pageNumber} de {page_count}"
        self.drawRightString(558, 36, page_str)
        self.drawString(54, 36, "Confidencial & Técnico • Documentação de Projeto de Engenharia de Dados")
        self.setStrokeColor(colors.HexColor("#e2e8f0"))
        self.setLineWidth(0.5)
        self.line(54, 48, 558, 48)
        
        self.restoreState()


def build_pdf(filename=PDF_FILENAME):
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()

    # Cores da identidade visual técnica
    c_primary = colors.HexColor("#0f172a")     # Slate 900
    c_secondary = colors.HexColor("#1e3a8a")   # Blue 900
    c_accent = colors.HexColor("#dc2626")      # Red 600 (UFC Red)
    c_text = colors.HexColor("#334155")        # Slate 700
    c_bg_light = colors.HexColor("#f8fafc")    # Slate 50
    c_border = colors.HexColor("#cbd5e1")      # Slate 300

    # Estilos customizados de parágrafo
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=22,
        leading=26,
        textColor=c_primary,
        spaceAfter=6
    )

    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=12,
        leading=16,
        textColor=c_accent,
        spaceAfter=15
    )

    h1_style = ParagraphStyle(
        'SectionH1',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        textColor=c_secondary,
        spaceBefore=14,
        spaceAfter=8,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'SectionH2',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=15,
        textColor=c_primary,
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'BodyDark',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13.5,
        textColor=c_text,
        spaceAfter=6
    )

    bullet_style = ParagraphStyle(
        'BulletText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=c_text,
        leftIndent=14,
        spaceAfter=3
    )

    code_style = ParagraphStyle(
        'CodeStyle',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=8,
        leading=10.5,
        textColor=colors.HexColor("#0f172a")
    )

    table_cell = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11,
        textColor=c_text
    )

    table_cell_bold = ParagraphStyle(
        'TableCellBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11,
        textColor=c_primary
    )

    table_header = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11,
        textColor=colors.white
    )

    story = []

    # ==========================================
    # CAPA / CABEÇALHO DO DOCUMENTO
    # ==========================================
    story.append(Paragraph("🥊 UFC FIGHT PREDICTION SYSTEM", subtitle_style))
    story.append(Paragraph("Documentação Técnica de Engenharia e Modelagem Preditiva", title_style))
    story.append(Paragraph("Arquitetura de Software, Modelagem Estatística com XGBoost, Sistema Elo e Calibração de Probabilidades", ParagraphStyle('Desc', parent=body_style, fontSize=10.5, leading=14, textColor=colors.HexColor("#475569"))))
    
    story.append(HRFlowable(width="100%", thickness=2, color=c_accent, spaceBefore=8, spaceAfter=12))

    # Tabela de Metadados
    meta_data = [
        [Paragraph("<b>Projeto:</b> UFC Analysis & Fight Prediction", table_cell), Paragraph("<b>Autor Original:</b> Arthur Santos", table_cell)],
        [Paragraph("<b>Dataset:</b> 11.441 Lutas (1993–2026) | 4.581 Atletas", table_cell), Paragraph("<b>Algoritmo:</b> XGBoost + Platt Scaling + Elo", table_cell)],
        [Paragraph("<b>Linguagem:</b> Python 3.11+", table_cell), Paragraph("<b>Status:</b> Produção / Calibrado e Testado", table_cell)]
    ]
    t_meta = Table(meta_data, colWidths=[250, 254])
    t_meta.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), c_bg_light),
        ('BOX', (0,0), (-1,-1), 0.5, c_border),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_meta)
    story.append(Spacer(1, 14))

    # ==========================================
    # 1. RESUMO EXECUTIVO E OBJETIVO
    # ==========================================
    story.append(Paragraph("1. Visão Geral e Arquitetura do Sistema", h1_style))
    story.append(Paragraph(
        "Este projeto implementa uma solução ponta a ponta de aprendizado de máquina supervisionado para previsão probabilística de resultados de lutas no Ultimate Fighting Championship (UFC). "
        "A modelagem resolve três problemas clássicos em esportes de combate: o vazamento temporal de dados (data leakage), a assimetria e viés do corner vermelho (corner bias), e a hiperconfiança de probabilidade (overconfidence) inerente a árvores de decisão.",
        body_style
    ))
    story.append(Paragraph(
        "O pipeline processa 11.441 lutas históricas abrangendo o período de novembro de 1993 a agosto de 2026, transformando dados brutos em 47 atributos preditivos matematicamente formulados.",
        body_style
    ))

    # ==========================================
    # 2. STACK TECNOLÓGICA E DEPENDÊNCIAS
    # ==========================================
    story.append(Paragraph("2. Stack Tecnológica e Bibliotecas Utilizadas", h1_style))
    story.append(Paragraph("O projeto utiliza um ambiente virtual isolado (.venv) sob Python 3.11. Abaixo estão as bibliotecas essenciais e a responsabilidade de cada uma:", body_style))

    stack_data = [
        [Paragraph("Biblioteca", table_header), Paragraph("Versão Mínima", table_header), Paragraph("Função no Sistema", table_header)],
        [Paragraph("<b>xgboost</b>", table_cell_bold), Paragraph(">= 2.0.0", table_cell), Paragraph("Algoritmo central de Gradient Boosted Decision Trees (GBDT). Constrói 120 árvores de decisão aditivas focadas nos erros residuais.", table_cell)],
        [Paragraph("<b>scikit-learn</b>", table_cell_bold), Paragraph(">= 1.3.0", table_cell), Paragraph("Calibração de probabilidades via Platt Scaling (CalibratedClassifierCV), divisão temporal, cálculo de métricas (AUC-ROC, Brier Score, Acurácia).", table_cell)],
        [Paragraph("<b>pandas</b>", table_cell_bold), Paragraph(">= 2.0.0", table_cell), Paragraph("Manipulação vetorial de dados tabulares, junções cronológicas, parsing de datas e cálculos sequenciais.", table_cell)],
        [Paragraph("<b>numpy</b>", table_cell_bold), Paragraph(">= 1.24.0", table_cell), Paragraph("Operações matemáticas de alta performance, cálculo de probabilidades logísticas e métricas numéricas.", table_cell)],
        [Paragraph("<b>kagglehub</b>", table_cell_bold), Paragraph(">= 0.2.0", table_cell), Paragraph("Download programático e sincronização automática das versões do dataset hospedado no Kaggle.", table_cell)],
        [Paragraph("<b>pytest</b>", table_cell_bold), Paragraph(">= 7.0.0", table_cell), Paragraph("Suíte de testes automatizados de regressão, integridade de arquivos e verificação de simetria matemática.", table_cell)],
        [Paragraph("<b>reportlab</b>", table_cell_bold), Paragraph(">= 4.0.0", table_cell), Paragraph("Geração programática e estilização deste relatório técnico oficial em PDF.", table_cell)],
    ]
    t_stack = Table(stack_data, colWidths=[80, 75, 349])
    t_stack.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_secondary),
        ('GRID', (0,0), (-1,-1), 0.5, c_border),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_bg_light]),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(t_stack)
    story.append(Spacer(1, 10))

    # ==========================================
    # 3. FORMULAÇÃO MATEMÁTICA E MODELAGEM
    # ==========================================
    story.append(Paragraph("3. Modelagem Estatística e Algoritmos", h1_style))
    
    story.append(Paragraph("3.1. O Sistema de Rating Elo Sequencial", h2_style))
    story.append(Paragraph(
        "Diferente de modelos convencionais que usam apenas médias estáticas de carreira, o sistema calcula o rating dinâmico de cada atleta estritamente antes do gongo inicial de cada luta. "
        "A habilidade é modelada como uma variável aleatória latente cuja probabilidade de vitória esperada E_A entre dois lutadores com ratings R_A e R_B segue a curva logística:",
        body_style
    ))
    story.append(Paragraph("<b>Equação de Probabilidade Esperada:</b> &nbsp; E_A = 1 / (1 + 10^((R_B - R_A) / 400))", ParagraphStyle('Eq', parent=code_style, backColor=c_bg_light, leftIndent=20, spaceAfter=4)))
    story.append(Paragraph("<b>Regra de Atualização Sequencial:</b> &nbsp; R_A' = R_A + K * (S_A - E_A)", ParagraphStyle('Eq2', parent=code_style, backColor=c_bg_light, leftIndent=20, spaceAfter=6)))
    story.append(Paragraph("Onde K = 32 e S_A representa o resultado empírico (1 para vitória, 0 para derrota, 0.5 para empate). Os ratings iniciam em 1.500 para estreantes.", body_style))

    story.append(Paragraph("3.2. Extreme Gradient Boosting (XGBoost)", h2_style))
    story.append(Paragraph(
        "O classificador minimiza a função de perda de entropia cruzada binária (Log-Loss) através de aproximações polinomiais de Taylor de segunda ordem. "
        "Configuração dos hiperparâmetros de regularização:",
        body_style
    ))
    story.append(Paragraph("• <b>n_estimators:</b> 120 árvores | <b>max_depth:</b> 4 (árvores rasas para evitar sobreajuste)", bullet_style))
    story.append(Paragraph("• <b>learning_rate:</b> 0.05 | <b>subsample:</b> 0.8 | <b>colsample_bytree:</b> 0.8", bullet_style))
    story.append(Paragraph("• <b>min_child_weight:</b> 3 | <b>gamma:</b> 0.5 (penalidades severas contra nós espúrios)", bullet_style))

    story.append(Paragraph("3.3. Calibração Probabilística de Platt (Platt Scaling)", h2_style))
    story.append(Paragraph(
        "Modelos de árvores sofrem de hiperconfiança: os scores brutos tendem a se agrupar perto de 0% e 100%. "
        "Para solucionar isso, encapsulamos o XGBoost em um calibrador sigmoidal (CalibratedClassifierCV com 5-fold cross validation), "
        "ajustando a regressão logística P(y=1 | f(x)) = 1 / (1 + exp(A*f(x) + B)). Isso eliminou previsões irreais acima de 90%, mantendo a média em ~64-67%.",
        body_style
    ))

    story.append(PageBreak())

    # ==========================================
    # 4. ENGENHARIA DE ATRIBUTOS (47 FEATURES)
    # ==========================================
    story.append(Paragraph("4. Engenharia de Atributos (Vetor de 47 Features)", h1_style))
    story.append(Paragraph("O modelo avalia 47 variáveis numéricas padronizadas para cada confronto, agrupadas em seis pilares técnicos:", body_style))

    features_data = [
        [Paragraph("Grupo", table_header), Paragraph("Qtd", table_header), Paragraph("Variáveis / Atributos", table_header), Paragraph("Importância Técnica", table_header)],
        [Paragraph("<b>Rating Elo</b>", table_cell_bold), Paragraph("4", table_cell), Paragraph("r_elo_before, b_elo_before, elo_diff, elo_expected_r", table_cell), Paragraph("Nível competitivo e momento histórico estritamente anterior à luta.", table_cell)],
        [Paragraph("<b>Físico</b>", table_cell_bold), Paragraph("6", table_cell), Paragraph("r/b_height, r/b_weight, r/b_reach, height_diff, reach_diff, weight_diff", table_cell), Paragraph("Vantagens de alavancagem, envergadura e categoria de peso oficial.", table_cell)],
        [Paragraph("<b>Striking</b>", table_cell_bold), Paragraph("8", table_cell), Paragraph("r/b_splm, r/b_str_acc, r/b_sapm, r/b_str_def, splm_diff, str_acc_diff, sapm_diff, str_def_diff", table_cell), Paragraph("Volume de golpes por minuto, acurácia e capacidade defensiva de esquiva.", table_cell)],
        [Paragraph("<b>Grappling</b>", table_cell_bold), Paragraph("8", table_cell), Paragraph("r/b_td_avg, r/b_td_avg_acc, r/b_td_def, r/b_sub_avg, td_avg_diff, td_def_diff", table_cell), Paragraph("Ameaça de quedas, taxa de finalização e defesa de quedas (TDD).", table_cell)],
        [Paragraph("<b>Carreira</b>", table_cell_bold), Paragraph("8", table_cell), Paragraph("r/b_wins, r/b_losses, win_diff, loss_diff, r/b_win_rate, win_rate_diff", table_cell), Paragraph("Bagagem no octógono e aproveitamento percentual pré-luta.", table_cell)],
        [Paragraph("<b>Momento</b>", table_cell_bold), Paragraph("3", table_cell), Paragraph("r_streak, b_streak, streak_diff", table_cell), Paragraph("Sequência ativa de vitórias ou derrotas consecutivas ao entrar no cage.", table_cell)],
        [Paragraph("<b>Diferenciais</b>", table_cell_bold), Paragraph("10", table_cell), Paragraph("Subtrações relativas normalizadas entre lutador A e lutador B", table_cell), Paragraph("Permite simetria matemática e isolamento de vantagens relativas.", table_cell)],
    ]
    t_feat = Table(features_data, colWidths=[70, 25, 230, 179])
    t_feat.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_secondary),
        ('GRID', (0,0), (-1,-1), 0.5, c_border),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_bg_light]),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(t_feat)
    story.append(Spacer(1, 8))

    story.append(Paragraph("4.1. Decisão Metodológica: O Paradoxo da Idade em Campeões de Elite", h2_style))
    story.append(Paragraph(
        "A idade bruta (age_diff) foi propositalmente omitida do modelo final. "
        "Testes empíricos demonstraram que, embora na média da população de 4.581 atletas os lutadores mais velhos sofram declínio, "
        "a inclusão linear da idade causava 'etarismo artificial' (age bias): transformava lendas comprovadamente dominantes como Alex Pereira (39 anos) e Alexander Volkanovski (38 anos) em zebras injustificadas contra adversários mais jovens. "
        "O sistema optou por capturar o declínio físico de forma justa através da queda do Elo e da sequência de vitórias (streak), protegendo os outliers de elite.",
        body_style
    ))

    # ==========================================
    # 5. METODOLOGIA E SIMETRIA DE CORNER
    # ==========================================
    story.append(Paragraph("5. Metodologia de Validação e Simetria de Corners", h1_style))
    story.append(Paragraph(
        "• <b>Divisão Temporal Estrita (Out-of-Time):</b> O dataset foi ordenado por data e dividido temporalmente. "
        "O conjunto de treinamento utiliza 6.636 lutas realizadas até 31/12/2022. O conjunto de teste utiliza 2.143 lutas realizadas de 01/01/2023 a agosto de 2026. Isso garante que o modelo nunca treine com informações do futuro.",
        body_style
    ))
    story.append(Paragraph(
        "• <b>Data Augmentation Simétrico:</b> Historicamente no UFC, o Red Corner é reservado ao favorito ou campeão, vencendo >60% das lutas apenas pelo pareamento da organização. "
        "Para eliminar esse viés, cada amostra de treino é duplicada e invertida (Red vira Blue, diferenciais invertem o sinal e y vira 1-y), totalizando 13.272 amostras de treino. "
        "Isso garante a propriedade de invariância: P(A vence B) + P(B vence A) = 1.0.",
        body_style
    ))

    # ==========================================
    # 6. BENCHMARK E RESULTADOS COMPARATIVOS
    # ==========================================
    story.append(Paragraph("6. Comparativo Estatístico e Resultados de Performance", h1_style))
    story.append(Paragraph("Métricas avaliadas no conjunto cego de teste temporal (2.143 combates reais entre 2023 e 2026):", body_style))

    metrics_data = [
        [Paragraph("Métrica Estatística", table_header), Paragraph("Repositório Original", table_header), Paragraph("Modelo Final Calibrado", table_header), Paragraph("Impacto da Melhoria", table_header)],
        [Paragraph("<b>Acurácia Out-of-Time</b>", table_cell_bold), Paragraph("60.0% – 65.0%", table_cell), Paragraph("<b>70.2%</b>", table_cell_bold), Paragraph("Superioridade de +5% a 10% em dados estritamente futuros.", table_cell)],
        [Paragraph("<b>Área sob a Curva (AUC-ROC)</b>", table_cell_bold), Paragraph("0.60 – 0.65", table_cell), Paragraph("<b>0.7744</b>", table_cell_bold), Paragraph("Forte separabilidade probabilística entre vencedores e perdedores.", table_cell)],
        [Paragraph("<b>Brier Score (Erro Quadrático)</b>", table_cell_bold), Paragraph("~0.2450 (alto erro)", table_cell), Paragraph("<b>0.1952 / 0.2066</b>", table_cell_bold), Paragraph("Redução significativa no desvio probabilístico médio.", table_cell)],
        [Paragraph("<b>Confiança Média</b>", table_cell_bold), Paragraph("83.0% (irreal)", table_cell), Paragraph("<b>60.0% – 64.7%</b>", table_cell_bold), Paragraph("Totalmente alinhado à taxa real de vitória de favoritos no MMA (~65%).", table_cell)],
        [Paragraph("<b>Predições com Certeza > 90%</b>", table_cell_bold), Paragraph("37.7% das lutas", table_cell), Paragraph("<b>0.0%</b>", table_cell_bold), Paragraph("Eliminação total do problema de hiperconfiança infundada.", table_cell)],
        [Paragraph("<b>Lutas Pareadas (50% a 60%)</b>", table_cell_bold), Paragraph("7.3% das lutas", table_cell), Paragraph("<b>54.5%</b>", table_cell_bold), Paragraph("Reconhecimento fiel do equilíbrio e da volatilidade do esporte.", table_cell)],
    ]
    t_metrics = Table(metrics_data, colWidths=[120, 95, 110, 179])
    t_metrics.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_secondary),
        ('GRID', (0,0), (-1,-1), 0.5, c_border),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_bg_light]),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(t_metrics)
    story.append(Spacer(1, 10))

    # ==========================================
    # 7. ESTRUTURA DOS ARQUIVOS DO PROJETO
    # ==========================================
    story.append(Paragraph("7. Estrutura Modular dos Scripts e Responsabilidades", h1_style))

    files_data = [
        [Paragraph("Arquivo", table_header), Paragraph("Tipo", table_header), Paragraph("Responsabilidade no Sistema", table_header)],
        [Paragraph("<b>update_dataset_2026.py</b>", table_cell_bold), Paragraph("Pipeline ETL", table_cell), Paragraph("Ingere master.csv e fighter.csv do Kaggle, converte pés/polegadas para cm e libras para kg, e calcula histórico dinâmico pré-luta.", table_cell)],
        [Paragraph("<b>calculate_elo.py</b>", table_cell_bold), Paragraph("Motor Estatístico", table_cell), Paragraph("Executa a formulação de ratings Elo cronológicos para 4.581 atletas ao longo de 11.441 combates sem lookahead bias.", table_cell)],
        [Paragraph("<b>feature_engineering.py</b>", table_cell_bold), Paragraph("Extrator de Dados", table_cell), Paragraph("Padroniza o vetor de 47 atributos e gera as matrizes de treinamento simétricas (Corner Invariance).", table_cell)],
        [Paragraph("<b>train_xgboost.py</b>", table_cell_bold), Paragraph("Treinamento ML", table_cell), Paragraph("Treina o modelo XGBoost, calibra as probabilidades via Platt Scaling e exporta o binário 'ufc_xgboost_model.pkl'.", table_cell)],
        [Paragraph("<b>test_predictions.py</b>", table_cell_bold), Paragraph("CLI de Produção", table_cell), Paragraph("Interface de linha de comando para predição em tempo real com validação de categorias de peso oficiais do UFC.", table_cell)],
        [Paragraph("<b>run_tests.py</b>", table_cell_bold), Paragraph("QA / Testes", table_cell), Paragraph("Executa bateria completa de 6 testes automatizados (arquivos, dados, inferência, simetria e regras de categoria).", table_cell)],
        [Paragraph("<b>data_loader.py</b>", table_cell_bold), Paragraph("Utilitário", table_cell), Paragraph("Abstrai caminhos de arquivo relativos e garante o download automático das bases de dados se ausentes.", table_cell)],
    ]
    t_files = Table(files_data, colWidths=[120, 75, 309])
    t_files.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_secondary),
        ('GRID', (0,0), (-1,-1), 0.5, c_border),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_bg_light]),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(t_files)

    # Constrói o PDF usando o canvas numerado
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Relatório técnico gerado com sucesso: '{filename}'")

if __name__ == '__main__':
    build_pdf()

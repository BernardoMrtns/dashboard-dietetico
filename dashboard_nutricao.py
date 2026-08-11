import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ==========================================
# CONFIGURAÇÃO INICIAL
# ==========================================
st.set_page_config(page_title="Dashboard de Nutrição PRO", layout="wide")
st.title("Calculadora e Projeção Nutricional (Cutting & Bulking)")

aba_inputs, aba_resultados = st.tabs(["⚙️ Configurações e Dados", "📈 Projeções e Análises"])

with aba_inputs:
    st.markdown("### Preencha os campos abaixo para gerar sua projeção.")
    
    col_dados, col_dieta = st.columns(2)
    
    with col_dados:
        # ==========================================
        # 1. DADOS PESSOAIS
        # ==========================================
        st.subheader("1. Dados Pessoais")
        sexo = st.radio("Sexo", ["Masculino", "Feminino"], index=0, horizontal=True)
        perfil = st.radio("Perfil Físico", ["Saudável / Sobrepeso", "Fisiculturista / Físico Atlético"], index=0, help="Fisiculturistas possuem alta densidade muscular e exigem fórmulas específicas.")
        
        idade = st.number_input("Idade (anos)", value=None, min_value=1, step=1, placeholder="Ex: 25")
        altura = st.number_input("Altura (cm)", value=None, min_value=1, step=1, placeholder="Ex: 175")
        peso = st.number_input("Peso Atual (kg)", value=None, min_value=1.0, step=0.1, placeholder="Ex: 80.0")
        
        st.markdown("---")
        st.markdown("**Percentual de Gordura (BF)**")
        st.caption("Opcional, mas *altamente recomendado* para destravar fórmulas avançadas e os gráficos de composição corporal.")
        
        modo_bf = st.selectbox("Como deseja informar o BF?", ["Não sei / Não informar", "Digitar valor exato", "Estimar por perfil visual"])
        
        bf = None
        if modo_bf == "Digitar valor exato":
            bf = st.number_input("Valor do BF (%)", min_value=1.0, max_value=70.0, step=0.1, value=15.0)
        elif modo_bf == "Estimar por perfil visual":
            if sexo == "Masculino":
                categoria_bf = st.selectbox("Selecione seu perfil visual atual:", [
                    "Atlético / Abdômen visível (10% - 14%)",
                    "Normal / Leve definição (15% - 19%)",
                    "Sobrepeso Leve (20% - 24%)",
                    "Sobrepeso Moderado (25% - 29%)",
                    "Obesidade (30%+)"
                ])
                mapa_bf_m = {"Atlético": 12.0, "Normal": 17.0, "Sobrepeso Leve": 22.0, "Sobrepeso Moderado": 27.0, "Obesidade": 32.0}
                bf = mapa_bf_m[categoria_bf.split(" /")[0]]
            else:
                categoria_bf = st.selectbox("Selecione seu perfil visual atual:", [
                    "Atlética / Alta definição (18% - 22%)",
                    "Normal / Corpo firme (23% - 27%)",
                    "Sobrepeso Leve (28% - 32%)",
                    "Sobrepeso Moderado (33% - 37%)",
                    "Obesidade (38%+)"
                ])
                mapa_bf_f = {"Atlética": 20.0, "Normal": 25.0, "Sobrepeso Leve": 30.0, "Sobrepeso Moderado": 35.0, "Obesidade": 40.0}
                bf = mapa_bf_f[categoria_bf.split(" /")[0]]

        # ==========================================
        # 2. PARÂMETROS METABÓLICOS
        # ==========================================
        st.markdown("---")
        st.subheader("2. Parâmetros Metabólicos")
        
        # Filtra as fórmulas disponíveis com base na presença do BF (Massa Magra)
        if bf is not None:
            opcoes_formulas = ["Harris Benedict", "Mifflin-ST", "Cunningham (MLG)", "Tinsley (P)", "Tinsley (MLG)"]
        else:
            opcoes_formulas = ["Harris Benedict", "Mifflin-ST", "Tinsley (P)"]

        # Lógica de Recomendação Automática
        indice_recomendado = 0
        if peso is not None and altura is not None:
            imc = peso / ((altura / 100) ** 2)
            if perfil == "Fisiculturista / Físico Atlético":
                indice_recomendado = opcoes_formulas.index("Tinsley (MLG)") if bf is not None else opcoes_formulas.index("Tinsley (P)")
                st.success(f"💡 **Fórmula Automática:** {opcoes_formulas[indice_recomendado]} (Ideal para seu perfil).")
            elif imc >= 30:
                indice_recomendado = opcoes_formulas.index("Mifflin-ST")
                st.success(f"💡 **Fórmula Automática:** Mifflin-ST (Ideal para IMC {imc:.1f}).")
            else:
                indice_recomendado = opcoes_formulas.index("Harris Benedict")
                st.success(f"💡 **Fórmula Automática:** Harris-Benedict (Ideal para IMC {imc:.1f}).")

        formula = st.selectbox(
            "Fórmula de Cálculo Basal", 
            opcoes_formulas,
            index=indice_recomendado
        )

        fatores_atividade = {
            1.35: "1.3 a 1.4 - Muito Sedentário",
            1.50: "1.5 - Sedentário Pouco Ativo",
            1.60: "1.6 - Sedentário Mais Ativo",
            1.70: "1.7 - Moderadamente Ativo",
            1.85: "1.8 a 1.9 - Muito Ativo",
            2.00: "2.0 ou mais - Atividade Intensa"
        }

        fator_val = st.selectbox(
            "Fator de Atividade", 
            options=list(fatores_atividade.keys()), 
            index=2, 
            format_func=lambda x: fatores_atividade[x]
        )
        
        st.caption("⚠️ **Dica de Ouro:** Avalie criticamente sua rotina. Trabalhadores braçais necessitam de multiplicadores mais altos do que pessoas que apenas treinam 1h por dia e trabalham sentadas. Comece com uma estimativa conservadora (mais baixa) e ajuste após duas semanas.")

    with col_dieta:
        # ==========================================
        # 3. MACROS DA DIETA E OBJETIVO
        # ==========================================
        st.subheader("3. Configuração da Dieta")
        objetivo = st.radio("Objetivo do Planejamento", ["Cutting (Perda de Gordura)", "Bulking (Ganho de Massa)"], horizontal=True)
        modo_entrada = st.radio("Método de Entrada de Macros", ["Gramas (g)", "Porcentagem (%)"], horizontal=True)

        if modo_entrada == "Gramas (g)":
            proteina = st.number_input("Proteínas (g)", value=150.0, step=5.0)
            carboidrato = st.number_input("Carboidratos (g)", value=150.0, step=5.0)
            gordura = st.number_input("Gorduras (g)", value=50.0, step=5.0)
            
            ingestao_diaria = (proteina * 4) + (carboidrato * 4) + (gordura * 9)
            st.info(f"🔥 **Calorias Totais da Dieta:** {ingestao_diaria:.0f} kcal")

        else:
            ingestao_diaria = st.number_input("Calorias Totais Alvo (kcal)", value=2500.0, step=50.0)
            col_p, col_c, col_g = st.columns(3)
            perc_prot = col_p.number_input("Prot (%)", value=30.0, step=5.0)
            perc_carb = col_c.number_input("Carb (%)", value=50.0, step=5.0)
            perc_fat = col_g.number_input("Fat (%)", value=20.0, step=5.0)
            
            soma_perc = perc_prot + perc_carb + perc_fat
            if soma_perc != 100.0:
                st.warning(f"A soma dos macros está em **{soma_perc}%**. Ajuste para 100%.")
                
            proteina = (ingestao_diaria * (perc_prot / 100)) / 4
            carboidrato = (ingestao_diaria * (perc_carb / 100)) / 4
            gordura = (ingestao_diaria * (perc_fat / 100)) / 9
            st.info(f"**Conversão Estimada (g):**\n\nProt: {proteina:.0f}g | Carb: {carboidrato:.0f}g | Fat: {gordura:.0f}g")

        # ==========================================
        # 4. CONTROLES DE PROJEÇÃO
        # ==========================================
        st.subheader("4. Controles da Projeção")
        semanas_projecao = st.slider("Semanas de Análise", min_value=4, max_value=24, value=12, step=1)

with aba_resultados:
    if peso is None or altura is None or idade is None:
        st.info("👈 Por favor, preencha os **Dados Pessoais básicos** (Idade, Altura e Peso) na aba anterior para gerar os resultados.")
    else:
        # Prepara as variáveis de composição corporal
        massa_magra_inicial = peso * (1 - (bf / 100)) if bf is not None else None
        massa_gorda_inicial = peso * (bf / 100) if bf is not None else None
        
        # CÁLCULO METABÓLICO INICIAL
        if formula == "Harris Benedict":
            bmr_inicial = 66 + (13.8 * peso) + (5.0 * altura) - (6.8 * idade) if sexo == "Masculino" else 655 + (9.6 * peso) + (1.9 * altura) - (4.7 * idade)
        elif formula == "Mifflin-ST":
            bmr_inicial = (10 * peso) + (6.25 * altura) - (5.0 * idade) + 5 if sexo == "Masculino" else (10 * peso) + (6.25 * altura) - (5.0 * idade) - 161
        elif formula == "Cunningham (MLG)":
            bmr_inicial = (22 * massa_magra_inicial) + 500
        elif formula == "Tinsley (P)":
            bmr_inicial = (24.8 * peso) + 10
        elif formula == "Tinsley (MLG)":
            bmr_inicial = (25.9 * massa_magra_inicial) + 284
            
        tdee_inicial = bmr_inicial * fator_val
        balanco_calorico_inicial = ingestao_diaria - tdee_inicial
        alteracao_semanal_kg_inicial = (abs(balanco_calorico_inicial) * 7) / 7700
        
        # KPIs NO TOPO
        col1, col2, col3, col4 = st.columns(4)
        if bf is not None:
            col1.metric("Massa Livre de Gordura", f"{massa_magra_inicial:.1f} kg")
        else:
            col1.metric("Peso Total", f"{peso:.1f} kg")
            
        col2.metric(f"Basal Inicial", f"{bmr_inicial:.0f} kcal")
        col3.metric("Gasto Total (TDEE)", f"{tdee_inicial:.0f} kcal")
        
        status_balanco = "Superávit" if balanco_calorico_inicial > 0 else "Déficit" if balanco_calorico_inicial < 0 else "Manutenção"
        col4.metric(f"Balanço Diário ({status_balanco})", f"{abs(balanco_calorico_inicial):.0f} kcal")
        
        st.markdown("---")
        
        # ANÁLISE DE EVIDÊNCIAS
        st.markdown("### 🔬 Análise Baseada em Evidências (Marco Zero)")
        prot_kg = proteina / peso
        alteracao_perc = (alteracao_semanal_kg_inicial / peso) * 100
        
        col_an1, col_an2 = st.columns(2)
        
        with col_an1:
            if objetivo == "Cutting (Perda de Gordura)":
                if prot_kg >= 2.0:
                    st.success(f"**Proteína ({prot_kg:.2f} g/kg):** Excelente. Restrições moderadas aliadas à alta proteína protegem o tecido muscular.")
                elif prot_kg >= 1.5:
                    st.info(f"**Proteína ({prot_kg:.2f} g/kg):** Boa ingestão. Tente aproximar de 2.0g/kg para garantir máxima retenção.")
                else:
                    st.error(f"**Proteína ({prot_kg:.2f} g/kg):** Risco de Catabolismo! Níveis abaixo de 1.5g/kg farão você perder muita massa magra.")
            else: 
                if prot_kg >= 1.6:
                    st.success(f"**Proteína ({prot_kg:.2f} g/kg):** Ótimo para hipertrofia. A síntese proteica maximiza entre 1.6 e 2.2 g/kg.")
                else:
                    st.warning(f"**Proteína ({prot_kg:.2f} g/kg):** Baixa para Bulking. Consumir menos de 1.6g/kg pode limitar o ganho de massa muscular.")
        
        with col_an2:
            if objetivo == "Cutting (Perda de Gordura)":
                if balanco_calorico_inicial >= 0:
                    st.warning("**Atenção:** Você selecionou Cutting, mas as calorias atuais não geram um déficit.")
                elif alteracao_perc > 1.0:
                    st.error(f"**Déficit Agressivo ({alteracao_perc:.2f}% peso/sem):** Déficits agressivos prejudicam a retenção de massa magra.")
                elif alteracao_perc >= 0.5:
                    st.success(f"**Déficit Moderado ({alteracao_perc:.2f}% peso/sem):** Ideal. Resultados superiores na preservação muscular.")
                else:
                    st.info(f"**Déficit Leve ({alteracao_perc:.2f}% peso/sem):** Perda lenta e sustentável.")
            else: 
                if balanco_calorico_inicial <= 0:
                    st.warning("**Atenção:** Você selecionou Bulking, mas as calorias atuais não geram um superávit.")
                elif alteracao_perc > 0.5:
                    st.error(f"**Superávit Agressivo ({alteracao_perc:.2f}% peso/sem):** Ganhar peso muito rápido resulta em acúmulo de gordura (Dirty Bulk).")
                else:
                    st.success(f"**Lean Bulk ({alteracao_perc:.2f}% peso/sem):** Superávit conservador. Ideal para hipertrofia limpa.")
        
        st.markdown("---")
        
        # PROJEÇÃO RECURSIVA
        if (objetivo == "Cutting (Perda de Gordura)" and balanco_calorico_inicial < 0) or \
           (objetivo == "Bulking (Ganho de Massa)" and balanco_calorico_inicial > 0):
            
            semanas = list(range(semanas_projecao + 1))
            pesos_totais = [peso]
            
            if bf is not None:
                massas_magras = [massa_magra_inicial]
                massas_gordas = [massa_gorda_inicial]
                bfs = [bf]
                mm_atual = massa_magra_inicial
                mg_atual = massa_gorda_inicial
                
            peso_atual = peso
            
            for s in range(1, semanas_projecao + 1):
                
                if formula == "Harris Benedict":
                    bmr_atual = 66 + (13.8 * peso_atual) + (5.0 * altura) - (6.8 * idade) if sexo == "Masculino" else 655 + (9.6 * peso_atual) + (1.9 * altura) - (4.7 * idade)
                elif formula == "Mifflin-ST":
                    bmr_atual = (10 * peso_atual) + (6.25 * altura) - (5.0 * idade) + 5 if sexo == "Masculino" else (10 * peso_atual) + (6.25 * altura) - (5.0 * idade) - 161
                elif formula == "Tinsley (P)":
                    bmr_atual = (24.8 * peso_atual) + 10
                elif bf is not None and formula == "Cunningham (MLG)":
                    bmr_atual = (22 * mm_atual) + 500
                elif bf is not None and formula == "Tinsley (MLG)":
                    bmr_atual = (25.9 * mm_atual) + 284
                
                tdee_atual = bmr_atual * fator_val
                balanco_atual = ingestao_diaria - tdee_atual
                
                if objetivo == "Cutting (Perda de Gordura)":
                    if balanco_atual >= 0:
                        peso_perdido = 0
                        preservacao_magra = 1.0
                    else:
                        peso_perdido = (abs(balanco_atual) * 7) / 7700
                        prot_kg_atual = proteina / peso_atual
                        perda_perc_atual = (peso_perdido / peso_atual) * 100
                        
                        preservacao_magra = 1.0 
                        if prot_kg_atual < 1.5: preservacao_magra = 0.70 
                        elif prot_kg_atual < 2.0: preservacao_magra = 0.95
                        if perda_perc_atual > 1.0: preservacao_magra = min(preservacao_magra, 0.60)
                    
                    peso_atual -= peso_perdido
                    
                    if bf is not None:
                        gordura_alterada = - (peso_perdido * preservacao_magra)
                        magra_alterada = - (peso_perdido * (1 - preservacao_magra))
                        mg_atual = max(0, mg_atual + gordura_alterada)
                        mm_atual = max(0, mm_atual + magra_alterada)
                        
                else: # Bulking
                    if balanco_atual <= 0:
                        peso_ganho = 0
                        proporcao_magra = 0.50
                    else:
                        peso_ganho = (balanco_atual * 7) / 7700
                        prot_kg_atual = proteina / peso_atual
                        ganho_perc_atual = (peso_ganho / peso_atual) * 100
                        
                        proporcao_magra = 0.50
                        if prot_kg_atual < 1.6: proporcao_magra = 0.20 
                        if ganho_perc_atual > 0.5: proporcao_magra = min(proporcao_magra, 0.30)
                            
                    peso_atual += peso_ganho
                    
                    if bf is not None:
                        magra_alterada = peso_ganho * proporcao_magra
                        gordura_alterada = peso_ganho * (1 - proporcao_magra)
                        mg_atual = max(0, mg_atual + gordura_alterada)
                        mm_atual = max(0, mm_atual + magra_alterada)
                
                pesos_totais.append(peso_atual)
                
                if bf is not None:
                    peso_real = mg_atual + mm_atual
                    bf_atual = (mg_atual / peso_real) * 100 if peso_real > 0 else 0
                    massas_magras.append(mm_atual)
                    massas_gordas.append(mg_atual)
                    bfs.append(bf_atual)
            
            # Gráficos
            col_g1, col_g2 = st.columns([2, 1])
            
            with col_g1:
                st.markdown("### 📈 Evolução Dinâmica Recursiva")
                if bf is not None:
                    df_grafico = pd.DataFrame({'Semanas': semanas, 'Peso Total (kg)': pesos_totais, 'Massa Gorda (kg)': massas_gordas, 'Massa Magra (kg)': massas_magras, 'Body Fat (%)': bfs})
                    metrica_y = st.selectbox("Escolha a métrica para o Eixo Y:", ['Peso Total (kg)', 'Massa Gorda (kg)', 'Massa Magra (kg)', 'Body Fat (%)'])
                else:
                    df_grafico = pd.DataFrame({'Semanas': semanas, 'Peso Total (kg)': pesos_totais})
                    metrica_y = 'Peso Total (kg)'
                    st.caption("Métricas avançadas (Massa Magra, Gorda e BF) estão ocultas pois o BF não foi informado.")
                
                fig = px.line(df_grafico, x='Semanas', y=metrica_y, markers=True, title=f"Projeção Realista: {metrica_y}")
                fig.update_traces(line=dict(width=3), marker=dict(size=10))
                fig.update_layout(xaxis=dict(tickmode='linear', tick0=0, dtick=1))
                st.plotly_chart(fig, use_container_width=True)
                
            with col_g2:
                st.markdown("### 📊 Distribuição de Macros")
                labels = ['Proteínas', 'Carboidratos', 'Gorduras']
                values = [proteina * 4, carboidrato * 4, gordura * 9]
                cores = ['#EF553B', '#636EFA', '#00CC96']
                
                fig_pie = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.4, marker_colors=cores)])
                fig_pie.update_layout(annotations=[dict(text=f'{ingestao_diaria:.0f} kcal', x=0.5, y=0.5, font_size=16, showarrow=False)])
                st.plotly_chart(fig_pie, use_container_width=True)
                
            if bf is not None:
                st.markdown("---")
                st.markdown("### 🧬 Distribuição da Composição Corporal Projetada")
                df_comp = pd.DataFrame({
                    'Semana': semanas * 2,
                    'Peso (kg)': massas_magras + massas_gordas,
                    'Composição': ['Massa Magra'] * len(semanas) + ['Massa Gorda'] * len(semanas),
                    'BF (%) Projetado': bfs * 2
                })
                
                fig_comp = px.bar(df_comp, x='Semana', y='Peso (kg)', color='Composição', hover_data={'BF (%) Projetado': ':.1f', 'Semana': False}, color_discrete_map={'Massa Magra': '#2E91E5', 'Massa Gorda': '#E15F99'}, barmode='stack')
                fig_comp.update_layout(xaxis_title="Semanas", yaxis_title="Peso (kg)", xaxis=dict(tickmode='linear', tick0=0, dtick=1))
                st.plotly_chart(fig_comp, use_container_width=True)
        else:
            st.warning("⚠️ Incompatibilidade matemática: Ajuste as macros/calorias para refletir seu objetivo (Déficit para Cutting ou Superávit para Bulking).")
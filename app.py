import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io
import os
import glob
from datetime import datetime

# --- CONFIGURAÇÃO INICIAL ---
st.set_page_config(page_title="Cardápio Fácil", layout="wide")

PASTA_HISTORICO = "history"
if not os.path.exists(PASTA_HISTORICO):
    os.makedirs(PASTA_HISTORICO)

# --- INICIALIZAÇÃO DO ESTADO (SESSION STATE) ---
# Isso serve para a imagem "sobreviver" na memória entre um clique e outro
if 'imagem_preview' not in st.session_state:
    st.session_state['imagem_preview'] = None
if 'sucesso_salvar' not in st.session_state:
    st.session_state['sucesso_salvar'] = False

st.title("🍞 Cardápio Fácil")

# --- CONFIGURAÇÃO DAS COORDENADAS ---
COORDENADAS_DATA = (275, 125)

SECOES = {
    "Pães Macios Tradicionais": [233, 270, 307, 344],
    "Pães Italianos e Rústicos": [425, 462, 499, 536, 572],
    "Pão Francês": [657, 693, 729, 764],
    "Pães Doces e Macios": [855, 892, 927],
    "Bolos e Tortas": [1018, 1055, 1090, 1126, 1161],
    "Doces": [1242, 1278, 1314, 1349],
    "Salgados": [1440, 1476, 1512, 1548]
}

COLUNA_PRODUTO_X = 40
COLUNA_PRECO_X = 670

# --- FUNÇÃO DE GERENCIAMENTO DE HISTÓRICO ---
def salvar_no_historico():
    if st.session_state['imagem_preview']:
        imagem_pil = st.session_state['imagem_preview']
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        caminho_arquivo = os.path.join(PASTA_HISTORICO, f"cardapio_{timestamp}.jpg")
        imagem_pil.save(caminho_arquivo, quality=95)
        
        # Limpeza
        arquivos = sorted(glob.glob(os.path.join(PASTA_HISTORICO, "*.jpg")), key=os.path.getmtime)
        while len(arquivos) > 30:
            os.remove(arquivos[0])
            arquivos.pop(0)
            
        st.session_state['sucesso_salvar'] = True

# --- LAYOUT EM COLUNAS ---
col_form, col_hist = st.columns([2, 1])

with col_form:
    st.markdown("### Preencha os dados do dia")
    
    with st.form("menu_form"):
        data_hoje = st.text_input("Data do Cardápio (ex: 24/10)", "")
        dados_preenchidos = {}
        
        st.write("---")
        for secao, linhas_y in SECOES.items():
            with st.expander(f"📝 {secao}", expanded=False):
                dados_preenchidos[secao] = []
                for i, y in enumerate(linhas_y):
                    c1, c2 = st.columns([3, 1])
                    with c1:
                        prod = st.text_input(f"Produto {i+1}", key=f"p_{secao}_{i}")
                    with c2:
                        preco = st.text_input(f"Preço", key=f"v_{secao}_{i}")
                    
                    if prod:
                        dados_preenchidos[secao].append({"produto": prod, "preco": preco, "y": y})

        # Alterei o nome do botão para ficar claro
        submitted = st.form_submit_button("🔄 Atualizar Preview (Visualizar)")

# --- LÓGICA DE GERAÇÃO (Apenas Gera, NÃO Salva) ---
if submitted:
    st.session_state['sucesso_salvar'] = False # Reseta msg de sucesso
    try:
        img = Image.open("assets/img/cardapio_fundo.jpg")
        draw = ImageDraw.Draw(img)
        TAMANHO_FONTE = 26  
        
        try:
            f_prod = ImageFont.truetype("assets/fonts/Roboto-Regular.ttf", TAMANHO_FONTE)
            f_preco = ImageFont.truetype("assets/fonts/Roboto-ExtraLight.ttf", TAMANHO_FONTE)
            f_data = ImageFont.truetype("assets/fonts/Roboto-Bold.ttf", 36)
        except OSError:
            f_prod = ImageFont.load_default()
            f_preco = ImageFont.load_default()
            f_data = ImageFont.load_default()

        cor_texto = "#3e2723"

        if data_hoje:
            draw.text(COORDENADAS_DATA, data_hoje, fill=cor_texto, font=f_data)

        for secao, itens in dados_preenchidos.items():
            for item in itens:
                draw.text((COLUNA_PRODUTO_X, item['y'] + 4), item['produto'], fill=cor_texto, font=f_prod)
                if item['preco']:
                    draw.text((COLUNA_PRECO_X, item['y'] + 4), item['preco'], fill=cor_texto, font=f_preco)
        
        # Salva no Session State (Memória Temporária)
        st.session_state['imagem_preview'] = img

    except FileNotFoundError:
        st.error("Erro: Verifique a imagem de fundo.")

# --- EXIBIÇÃO E BOTÕES FINAIS (Fora do Form) ---
with col_form:
    if st.session_state['imagem_preview']:
        st.write("---")
        st.subheader("Resultado Final")
        st.image(st.session_state['imagem_preview'], caption="Preview")
        
        # Aqui estão os botões definitivos
        c_save, c_down1, c_down2 = st.columns([2, 1, 1])
        
        with c_save:
            # Botão que efetivamente Grava no Histórico
            if st.button("💾 Confirmar e Salvar no Histórico", type="primary"):
                salvar_no_historico()
        
        # Feedback visual
        if st.session_state['sucesso_salvar']:
            st.success("✅ Salvo no Histórico com sucesso!")

        # Preparar Downloads
        img = st.session_state['imagem_preview']
        buf_jpg = io.BytesIO()
        img.save(buf_jpg, format="JPEG", quality=95)
        byte_jpg = buf_jpg.getvalue()

        buf_pdf = io.BytesIO()
        img.save(buf_pdf, format="PDF", resolution=100.0)
        byte_pdf = buf_pdf.getvalue()

        with c_down1:
            st.download_button("⬇️ JPG", data=byte_jpg, file_name="cardapio.jpg", mime="image/jpeg")
        with c_down2:
            st.download_button("📄 PDF", data=byte_pdf, file_name="cardapio.pdf", mime="application/pdf")

# --- BARRA LATERAL DE HISTÓRICO ---
with col_hist:
    st.markdown("### 🕒 Histórico")
    st.info("O histórico só atualiza quando você clica em 'Confirmar e Salvar'.")
    
    arquivos_hist = sorted(glob.glob(os.path.join(PASTA_HISTORICO, "*.jpg")), key=os.path.getmtime, reverse=True)
    
    if not arquivos_hist:
        st.write("Nenhum histórico ainda.")
    else:
        for arquivo in arquivos_hist[:10]: 
            nome_arquivo_bruto = os.path.basename(arquivo)
            try:
                parte_data = nome_arquivo_bruto.replace("cardapio_", "").replace(".jpg", "")
                data_obj = datetime.strptime(parte_data, "%Y-%m-%d_%H-%M-%S")
                nome_bonito = data_obj.strftime("📅 %d/%m - %H:%M")
            except:
                nome_bonito = f"📁 {nome_arquivo_bruto}"

            with st.expander(nome_bonito):
                img_hist = Image.open(arquivo)
                st.image(img_hist)
                with open(arquivo, "rb") as file:
                    st.download_button(
                        label="📥 Baixar",
                        data=file,
                        file_name=nome_arquivo_bruto,
                        mime="image/jpeg",
                        key=nome_arquivo_bruto
                    )

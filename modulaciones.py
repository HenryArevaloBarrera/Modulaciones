import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

# Configurar el ancho de la página
st.set_page_config(layout="wide")  # Diseño de página ancha

# Parámetros iniciales
fc = 10.0  # Frecuencia de la portadora (Hz)
fm = 1.0   # Frecuencia de la moduladora (Hz)
Ac = 1.0   # Amplitud de la portadora
Am = 0.5   # Amplitud de la moduladora
t = np.linspace(0, 1, 1000)  # Vector de tiempo (1 segundo)

# Función para convertir texto a binario
def texto_a_binario(texto):
    return ''.join(format(ord(char), '08b') for char in texto)  # 8 bits por carácter

# Función para generar la señal digital
def generar_senal_digital(binario, t):
    señal = np.zeros_like(t)
    bits_por_segundo = len(binario)  # Un bit por unidad de tiempo
    for i, bit in enumerate(binario):
        señal[int(i * len(t) / bits_por_segundo):int((i + 1) * len(t) / bits_por_segundo)] = int(bit)
    return señal

# Señal portadora (modificada para recibir parámetros)
def generar_portadora(t, fc, Ac):
    return Ac * np.sin(2 * np.pi * fc * t)

# Señal moduladora analógica (modificada para recibir parámetros)
def generar_moduladora_analogica(t, fm, Am):
    return Am * np.sin(2 * np.pi * fm * t)

# Funciones para cada tipo de modulación (actualizadas)
def modulacion_AM(t, fc, fm, Ac, Am):
    portadora = generar_portadora(t, fc, Ac)
    moduladora = generar_moduladora_analogica(t, fm, Am)
    modulada = (Ac + moduladora) * portadora / Ac  # Manteniendo lógica original
    return modulada, "Modulación AM", portadora, moduladora

def modulacion_FM(t, fc, fm, Ac, Am):
    kf = 5  # Sensibilidad de frecuencia (fijo como en original)
    portadora = generar_portadora(t, fc, Ac)
    moduladora = generar_moduladora_analogica(t, fm, Am)
    modulada = Ac * np.sin(2 * np.pi * fc * t + 2 * np.pi * kf * np.cumsum(moduladora) * (t[1] - t[0]))
    return modulada, "Modulación FM", portadora, moduladora

def modulacion_PM(t, fc, fm, Ac, Am):
    kp = 5  # Sensibilidad de fase (fijo como en original)
    portadora = generar_portadora(t, fc, Ac)
    moduladora = generar_moduladora_analogica(t, fm, Am)
    modulada = Ac * np.sin(2 * np.pi * fc * t + kp * moduladora)
    return modulada, "Modulación PM", portadora, moduladora

def modulacion_ASK(t, fc, Ac, señal_digital):
    portadora = generar_portadora(t, fc, Ac)
    modulada = Ac * señal_digital * portadora
    return modulada, "Modulación ASK", portadora, señal_digital

def modulacion_PSK(t, fc, Ac, señal_digital):
    portadora = generar_portadora(t, fc, Ac)
    modulada = Ac * np.sin(2 * np.pi * fc * t + np.pi * señal_digital)
    return modulada, "Modulación PSK", portadora, señal_digital

def modulacion_FSK(t, fc, Ac, señal_digital):
    f1, f2 = 5, 15  # Frecuencias para 0 y 1 (fijas como en original)
    portadora = generar_portadora(t, fc, Ac)
    modulada = Ac * np.sin(2 * np.pi * (f1 + (f2 - f1) * señal_digital) * t)
    return modulada, "Modulación FSK", portadora, señal_digital

# Interfaz de Streamlit
st.title("📡 Simulador de Modulaciones")

# Crear dos columnas con anchos personalizados
col1, col2 = st.columns([1, 3])  # col1 más estrecha (25%), col2 más ancha (75%)

# Controles en la columna izquierda
with col1:
    st.header("⚙️ Parámetros")

    # Selector de modulación
    seleccion = st.selectbox(
        "Selecciona el tipo de modulación:",
        ["AM", "FM", "PM", "ASK", "PSK", "FSK"]
    )

    # Mostrar parámetros según el tipo de modulación
    if seleccion in ["AM", "FM", "PM"]:
        fc = st.slider("Frecuencia portadora (Hz):", min_value=1.0, max_value=20.0, value=fc, step=0.1)
        fm = st.slider("Frecuencia moduladora (Hz):", min_value=0.1, max_value=5.0, value=fm, step=0.1)
        Ac = st.slider("Amplitud portadora:", min_value=0.1, max_value=2.0, value=Ac, step=0.1)
        Am = st.slider("Amplitud moduladora:", min_value=0.1, max_value=1.0, value=Am, step=0.1)
    elif seleccion in ["ASK", "PSK", "FSK"]:
        mensaje = st.text_input("Ingresa un mensaje:", "Hola")
        binario = texto_a_binario(mensaje)
        st.write(f"🔢 Mensaje en binario: {binario}")
        fc = st.slider("Frecuencia portadora (Hz):", min_value=1.0, max_value=20.0, value=fc, step=0.1)
        Ac = st.slider("Amplitud portadora:", min_value=0.1, max_value=2.0, value=Ac, step=0.1)

# Generar la señal según el tipo de modulación
if seleccion in ["AM", "FM", "PM"]:
    if seleccion == "AM":
        modulada, titulo, portadora, moduladora = modulacion_AM(t, fc, fm, Ac, Am)
    elif seleccion == "FM":
        modulada, titulo, portadora, moduladora = modulacion_FM(t, fc, fm, Ac, Am)
    elif seleccion == "PM":
        modulada, titulo, portadora, moduladora = modulacion_PM(t, fc, fm, Ac, Am)
    señal_adicional = moduladora
else:
    senal_digital = generar_senal_digital(binario, t)
    if seleccion == "ASK":
        modulada, titulo, portadora, señal_adicional = modulacion_ASK(t, fc, Ac, senal_digital)
    elif seleccion == "PSK":
        modulada, titulo, portadora, señal_adicional = modulacion_PSK(t, fc, Ac, senal_digital)
    elif seleccion == "FSK":
        modulada, titulo, portadora, señal_adicional = modulacion_FSK(t, fc, Ac, senal_digital)

# Configurar estilo de gráficos
plt.style.use('seaborn-v0_8')
fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 12))

# Gráfico 1: Señal modulada
ax1.plot(t, modulada, label="Señal modulada", color="#1f77b4", linewidth=2)
ax1.set_title(f"{titulo} - Señal Modulada", fontsize=12, fontweight='bold')
ax1.set_xlabel("Tiempo [s]", fontsize=10)
ax1.set_ylabel("Amplitud", fontsize=10)
ax1.legend(fontsize=9)
ax1.grid(True, linestyle='--', alpha=0.6)

# Gráfico 2: Portadora
ax2.plot(t, portadora, label="Portadora", linestyle="--", color="#ff7f0e", alpha=0.7, linewidth=1.5)
ax2.set_title("Señal Portadora", fontsize=12, fontweight='bold')
ax2.set_xlabel("Tiempo [s]", fontsize=10)
ax2.set_ylabel("Amplitud", fontsize=10)
ax2.legend(fontsize=9)
ax2.grid(True, linestyle='--', alpha=0.6)

# Gráfico 3: Moduladora o señal digital
if seleccion in ["AM", "FM", "PM"]:
    ax3.plot(t, señal_adicional, label="Señal Moduladora", linestyle=":", color="#2ca02c", alpha=0.7, linewidth=1.5)
else:
    ax3.plot(t, señal_adicional, label="Señal Digital", linestyle=":", color="#2ca02c", alpha=0.7, linewidth=1.5)
ax3.set_title("Señal Moduladora/Digital", fontsize=12, fontweight='bold')
ax3.set_xlabel("Tiempo [s]", fontsize=10)
ax3.set_ylabel("Amplitud", fontsize=10)
ax3.legend(fontsize=9)
ax3.grid(True, linestyle='--', alpha=0.6)

# Ajustar espacio entre subplots
plt.tight_layout()

# Mostrar los gráficos en la columna derecha
with col2:
    st.header("📊 Visualización")
    st.pyplot(fig)
    
    # Información adicional
    if seleccion == "AM":
        mu = Am/Ac  # Calculando índice de modulación
        st.info(f"""
        **Parámetros de AM:**
        - Índice de modulación (μ): {mu:.2f} {"(Sobremodulación ⚠️)" if mu > 1 else "(Correcto ✅)"}
        - Ancho de banda teórico: {2*fm:.1f} Hz
        """)
    elif seleccion == "FM":
        kf = 5  # Valor fijo como en la lógica original
        desviacion = kf * Am
        beta = desviacion / fm
        st.info(f"""
        **Parámetros de FM:**
        - Sensibilidad de frecuencia (kf): {kf} Hz/V
        - Desviación de frecuencia (Δf): {desviacion:.1f} Hz
        - Índice de modulación (β): {beta:.2f}
        """)
    elif seleccion == "PM":
        kp = 5  # Valor fijo como en la lógica original
        st.info(f"""
        **Parámetros de PM:**
        - Sensibilidad de fase (kp): {kp} rad/V
        - Desviación de fase máxima: {kp * Am:.2f} rad
        """)

# Explicación teórica
st.markdown("---")
st.subheader("🎓 Explicación Teórica")

if seleccion == "AM":
    st.markdown("""
    **Modulación de Amplitud (AM):**
    - La amplitud de la portadora varía según la señal moduladora.
    - Ecuación: $s(t) = A_c[1 + μ·m(t)]·\sin(2πf_ct)$
    - μ debe ser ≤ 1 para evitar distorsión.
    """)
elif seleccion == "FM":
    st.markdown("""
    **Modulación de Frecuencia (FM):**
    - La frecuencia instantánea varía según la señal moduladora.
    - Ecuación: $s(t) = A_c·\sin(2πf_ct + 2πk_f∫m(t)dt)$
    - Mayor kf → mayor desviación de frecuencia.
    """)
elif seleccion == "PM":
    st.markdown("""
    **Modulación de Fase (PM):**
    - La fase instantánea varía según la señal moduladora.
    - Ecuación: $s(t) = A_c·\sin(2πf_ct + k_p·m(t))$
    - Similar a FM pero proporcional a m(t) en lugar de su integral.
    """)
elif seleccion == "ASK":
    st.markdown("""
    **Modulación por Desplazamiento de Amplitud (ASK):**
    - La amplitud de la portadora cambia según los bits (1 = presencia, 0 = ausencia).
    - Simple pero sensible al ruido.
    """)
elif seleccion == "PSK":
    st.markdown("""
    **Modulación por Desplazamiento de Fase (PSK):**
    - La fase de la portadora cambia según los bits (ej: 0° para 0, 180° para 1).
    - Más eficiente que ASK en ancho de banda.
    """)
elif seleccion == "FSK":
    st.markdown("""
    **Modulación por Desplazamiento de Frecuencia (FSK):**
    - La frecuencia de la portadora cambia según los bits.
    - Más robusta al ruido que ASK pero requiere más ancho de banda.
    """)

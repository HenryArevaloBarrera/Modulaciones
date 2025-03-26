import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

# Configuración de la página
st.set_page_config(layout="wide", page_title="Simulador de Modulaciones")

# Funciones base
def texto_a_binario(texto):
    return ''.join(format(ord(char), '08b') for char in texto)

def generar_senal_digital(binario, t):
    señal = np.zeros_like(t)
    bits_por_segundo = len(binario)
    for i, bit in enumerate(binario):
        inicio = int(i * len(t) / bits_por_segundo)
        fin = int((i + 1) * len(t) / bits_por_segundo)
        señal[inicio:fin] = int(bit)
    return señal

def generar_moduladora_analogica(t, fm, Am):
    return Am * np.sin(2 * np.pi * fm * t)  # Solo forma senoidal

def generar_portadora(t, fc, Ac):
    return Ac * np.sin(2 * np.pi * fc * t)

# Funciones de modulación
def modulacion_AM(t, fc, fm, Ac, Am, mu):
    portadora = generar_portadora(t, fc, Ac)
    moduladora = generar_moduladora_analogica(t, fm, Am)
    modulada = Ac * (1 + mu * (moduladora/Am)) * np.sin(2 * np.pi * fc * t)
    return modulada, portadora, moduladora

def modulacion_FM(t, fc, fm, Ac, Am, kf):
    moduladora = generar_moduladora_analogica(t, fm, Am)
    portadora = generar_portadora(t, fc, Ac)
    modulada = Ac * np.sin(2 * np.pi * fc * t + 2 * np.pi * kf * np.cumsum(moduladora) * (t[1] - t[0]))
    return modulada, portadora, moduladora

def modulacion_PM(t, fc, fm, Ac, Am, kp):
    moduladora = generar_moduladora_analogica(t, fm, Am)
    portadora = generar_portadora(t, fc, Ac)
    modulada = Ac * np.sin(2 * np.pi * fc * t + kp * moduladora)
    return modulada, portadora, moduladora

def modulacion_ASK(t, fc, Ac, señal_digital):
    portadora = generar_portadora(t, fc, Ac)
    modulada = señal_digital * portadora
    return modulada, portadora, señal_digital

def modulacion_PSK(t, fc, Ac, señal_digital):
    portadora = generar_portadora(t, fc, Ac)
    modulada = Ac * np.cos(2 * np.pi * fc * t + np.pi * señal_digital)
    return modulada, portadora, señal_digital

def modulacion_FSK(t, fc, Ac, señal_digital, delta_f=5):
    f1, f2 = fc - delta_f/2, fc + delta_f/2
    portadora = generar_portadora(t, fc, Ac)
    modulada = Ac * np.sin(2 * np.pi * (f1 + (f2 - f1) * señal_digital) * t)
    return modulada, portadora, señal_digital

# Interfaz de usuario
st.title("📡 Simulador de Modulaciones")

# Columnas
col1, col2 = st.columns([1, 3])

# Controles
with col1:
    st.header("⚙️ Parámetros")
    seleccion = st.selectbox(
        "Tipo de modulación:",
        ["AM", "FM", "PM", "ASK", "PSK", "FSK"]
    )
    
    t_duracion = st.slider("Duración (s):", 0.1, 5.0, 1.0, 0.1)
    t = np.linspace(0, t_duracion, 5000)
    
    if seleccion in ["AM", "FM", "PM"]:
        fc = st.slider("Frecuencia portadora (Hz):", 1.0, 100.0, 10.0, 0.1)
        fm = st.slider("Frecuencia moduladora (Hz):", 0.1, 20.0, 1.0, 0.1)
        Ac = st.slider("Amplitud portadora:", 0.1, 2.0, 1.0, 0.1)
        Am = st.slider("Amplitud moduladora:", 0.1, 1.0, 0.5, 0.1)
        
        if seleccion == "AM":
            mu = st.slider("Índice de modulación (μ):", 0.1, 1.5, 0.5, 0.1)
        elif seleccion == "FM":
            kf = st.slider("Sensibilidad de frecuencia (kf):", 0.1, 20.0, 5.0, 0.1)
        elif seleccion == "PM":
            kp = st.slider("Sensibilidad de fase (kp):", 0.1, 10.0, 2.0, 0.1)
            
    elif seleccion in ["ASK", "PSK", "FSK"]:
        mensaje = st.text_input("Mensaje para modulación digital:", "Hola")
        binario = texto_a_binario(mensaje)
        st.write(f"Binario: {binario}")
        fc = st.slider("Frecuencia portadora (Hz):", 1.0, 100.0, 10.0, 0.1)
        Ac = st.slider("Amplitud portadora:", 0.1, 2.0, 1.0, 0.1)
        
        if seleccion == "FSK":
            delta_f = st.slider("Desviación de frecuencia (Hz):", 1.0, 20.0, 5.0, 0.1)
        
        señal_digital = generar_senal_digital(binario, t)

# Generación de señales
if seleccion == "AM":
    modulada, portadora, moduladora = modulacion_AM(t, fc, fm, Ac, Am, mu)
elif seleccion == "FM":
    modulada, portadora, moduladora = modulacion_FM(t, fc, fm, Ac, Am, kf)
elif seleccion == "PM":
    modulada, portadora, moduladora = modulacion_PM(t, fc, fm, Ac, Am, kp)
elif seleccion == "ASK":
    modulada, portadora, señal_digital = modulacion_ASK(t, fc, Ac, señal_digital)
elif seleccion == "PSK":
    modulada, portadora, señal_digital = modulacion_PSK(t, fc, Ac, señal_digital)
elif seleccion == "FSK":
    modulada, portadora, señal_digital = modulacion_FSK(t, fc, Ac, señal_digital, delta_f)

# Gráficos
plt.style.use('seaborn-v0_8')
fig, ax = plt.subplots(figsize=(12, 5))

if seleccion in ["AM", "FM", "PM"]:
    ax.plot(t, modulada, label="Señal modulada", color="#1f77b4", linewidth=2)
    ax.plot(t, portadora, label="Portadora", linestyle="--", color="#ff7f0e", alpha=0.7, linewidth=1.5)
    ax.plot(t, moduladora, label="Moduladora", linestyle=":", color="#2ca02c", alpha=0.7, linewidth=1.5)
else:
    ax.plot(t, modulada, label="Señal modulada", color="#1f77b4", linewidth=2)
    ax.plot(t, portadora, label="Portadora", linestyle="--", color="#ff7f0e", alpha=0.7, linewidth=1.5)
    ax.plot(t, señal_digital, label="Señal digital", linestyle=":", color="#2ca02c", alpha=0.7, linewidth=1.5)

ax.set_title(f"Modulación {seleccion}", fontsize=14, fontweight='bold')
ax.set_xlabel("Tiempo [s]", fontsize=12)
ax.set_ylabel("Amplitud", fontsize=12)
ax.legend(loc='upper right', fontsize=10)
ax.grid(True, linestyle='--', alpha=0.6)

# Mostrar gráfico
with col2:
    st.header("📊 Gráfica")
    st.pyplot(fig)
    
    # Información adicional
    if seleccion == "AM":
        st.info(f"""
        **Parámetros de AM:**
        - Índice de modulación (μ): {mu:.2f} {"(Sobremodulación ⚠️)" if mu > 1 else "(Correcto ✅)"}
        - Ancho de banda teórico: {2*fm:.1f} Hz
        """)
    elif seleccion == "FM":
        desviacion = kf * Am
        beta = desviacion / fm
        st.info(f"""
        **Parámetros de FM:**
        - Desviación de frecuencia (Δf): {desviacion:.1f} Hz
        - Índice de modulación (β): {beta:.2f}
        - Ancho de banda (Carson): {2*(desviacion + fm):.1f} Hz
        """)
    elif seleccion == "PM":
        st.info(f"""
        **Parámetros de PM:**
        - Sensibilidad de fase (kp): {kp} rad/V
        - Desviación de fase máxima: {kp * Am:.2f} rad
        """)
    elif seleccion in ["ASK", "PSK", "FSK"]:
        st.info(f"""
        **Parámetros de {seleccion}:**
        - Bits transmitidos: {len(binario)}
        - Tasa de bits: {len(binario)/t_duracion:.2f} bps
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

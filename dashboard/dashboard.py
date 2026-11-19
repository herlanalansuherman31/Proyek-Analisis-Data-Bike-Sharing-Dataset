from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


DATA_PATH = Path(__file__).resolve().with_name("main_data.csv")
MONTHS = ["Jan", "Feb", "Mar", "Apr", "Mei", "Jun", "Jul", "Agu", "Sep", "Okt", "Nov", "Des"]
SEASONS = {1: "Musim semi", 2: "Musim panas", 3: "Musim gugur", 4: "Musim dingin"}
WEATHER = {
    1: "Cerah / berawan ringan",
    2: "Berkabut / berawan",
    3: "Hujan ringan / salju",
    4: "Hujan lebat / salju",
}
USER_COLUMNS = {"Terdaftar": "registered", "Kasual": "casual"}
COLORS = {
    "blue": "#4f7cff",
    "cyan": "#27c2c1",
    "orange": "#ff9f5a",
    "purple": "#9b7bff",
}

st.set_page_config(
    page_title="BikeShare Insights",
    page_icon="🚲",
    layout="wide",
    initial_sidebar_state="expanded",
)


@st.cache_data
def load_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    if not DATA_PATH.is_file():
        raise FileNotFoundError(f"File data tidak ditemukan: {DATA_PATH}")

    data = pd.read_csv(DATA_PATH, encoding="utf-8-sig")
    required = {
        "dteday",
        "hr",
        "season_hour",
        "workingday_hour",
        "weathersit_hour",
        "casual_hour",
        "registered_hour",
        "cnt_hour",
        "instant_day",
        "season_day",
        "yr_day",
        "mnth_day",
        "weathersit_day",
        "atemp_day",
        "casual_day",
        "registered_day",
        "cnt_day",
    }
    missing = sorted(required.difference(data.columns))
    if missing:
        raise ValueError(f"Kolom wajib tidak tersedia di main_data.csv: {', '.join(missing)}")

    data["dteday"] = pd.to_datetime(data["dteday"], errors="coerce")
    if data["dteday"].isna().any():
        raise ValueError("Kolom dteday berisi tanggal yang tidak valid.")

    hourly_columns = [
        "dteday",
        "hr",
        "season_hour",
        "workingday_hour",
        "weathersit_hour",
        "casual_hour",
        "registered_hour",
        "cnt_hour",
    ]
    daily_columns = [
        "instant_day",
        "dteday",
        "season_day",
        "yr_day",
        "mnth_day",
        "weathersit_day",
        "atemp_day",
        "casual_day",
        "registered_day",
        "cnt_day",
    ]
    hourly = data[hourly_columns].copy()
    daily = data[daily_columns].drop_duplicates(subset="instant_day").copy()
    return hourly, daily


def format_number(value: float) -> str:
    return f"{value:,.0f}".replace(",", ".")


def polish_chart(fig: go.Figure, height: int = 360) -> go.Figure:
    fig.update_layout(
        height=height,
        margin=dict(l=12, r=12, t=26, b=12),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", color="#344054", size=12),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            title_text="",
        ),
        hoverlabel=dict(bgcolor="#172b4d", font_color="white"),
    )
    fig.update_xaxes(showgrid=False, linecolor="#e7eaf0")
    fig.update_yaxes(gridcolor="#edf0f5", zeroline=False)
    return fig


st.markdown(
    """
    <style>
    html, body, [class*="css"] { font-family: 'Aptos', 'Segoe UI', sans-serif; }
    .stApp { background: #f5f7fb; }
    [data-testid="stSidebar"] { background: #111b31; }
    [data-testid="stSidebar"] * { color: #eef2ff; }
    [data-testid="stSidebar"] [data-baseweb="select"] * { color: #263248; }
    .hero {
        padding: 1.6rem 1.8rem; border-radius: 22px; color: white;
        background: radial-gradient(circle at 85% 20%, #5d8dff 0, transparent 32%),
                    linear-gradient(120deg, #162541 0%, #243d69 58%, #3159a8 100%);
        margin: 0.3rem 0 1.35rem;
    }
    .hero h1 { font-family: 'Aptos Display', 'Segoe UI', sans-serif; font-size: 2rem; margin: 0; color: white; }
    .hero p { color: #dce6ff; margin: .4rem 0 0; }
    .eyebrow { color: #b7caff; font-size: .75rem; letter-spacing: .12em; text-transform: uppercase; }
    h2, h3 { font-family: 'Aptos Display', 'Segoe UI', sans-serif; }
    [data-testid="stMetric"] {
        background: white; border: 1px solid #e8ecf3; padding: 1rem 1.15rem;
        border-radius: 16px; box-shadow: 0 5px 18px rgba(27, 44, 75, .04);
    }
    [data-testid="stMetricLabel"] { color: #667085; }
    [data-testid="stMetricValue"] { color: #172b4d; font-family: 'Aptos Display', 'Segoe UI', sans-serif; }
    div[data-testid="stTabs"] button { font-weight: 600; }
    .scope-note { color: #667085; font-size: .88rem; margin-top: -.5rem; }
    </style>
    """,
    unsafe_allow_html=True,
)

try:
    hourly_data, daily_data = load_data()
except (FileNotFoundError, ValueError, pd.errors.ParserError) as error:
    st.error(f"Tidak dapat memuat data: {error}")
    st.stop()

daily_data["tahun"] = daily_data["dteday"].dt.year
daily_data["bulan"] = daily_data["dteday"].dt.month
hourly_data["tahun"] = hourly_data["dteday"].dt.year
hourly_data["bulan"] = hourly_data["dteday"].dt.month

st.sidebar.markdown("## 🚲 BikeShare")
st.sidebar.caption("Panel eksplorasi data penyewaan sepeda")
minimum_date = daily_data["dteday"].min().date()
maximum_date = daily_data["dteday"].max().date()
selected_dates = st.sidebar.date_input(
    "Rentang tanggal",
    value=(minimum_date, maximum_date),
    min_value=minimum_date,
    max_value=maximum_date,
)
if (
    not isinstance(selected_dates, tuple)
    or len(selected_dates) != 2
    or selected_dates[0] is None
    or selected_dates[1] is None
):
    st.sidebar.info("Pilih tanggal mulai dan tanggal akhir untuk melihat analisis.")
    st.stop()
start_date, end_date = selected_dates
selected_seasons = st.sidebar.multiselect(
    "Musim",
    options=list(SEASONS),
    default=list(SEASONS),
    format_func=lambda season: SEASONS[season],
)
available_weather = sorted(hourly_data["weathersit_hour"].dropna().unique().tolist())
selected_weather = st.sidebar.multiselect(
    "Kondisi cuaca",
    options=available_weather,
    default=available_weather,
    format_func=lambda condition: WEATHER[condition],
)
selected_users = st.sidebar.multiselect(
    "Tipe pengguna",
    options=list(USER_COLUMNS),
    default=list(USER_COLUMNS),
)
st.sidebar.markdown("---")
st.sidebar.caption("Semua filter diterapkan ke ringkasan dan grafik analisis.")

st.markdown(
    """
    <div class="hero">
      <div class="eyebrow">Analisis mobilitas • 2011—2012</div>
      <h1>BikeShare Insights</h1>
      <p>Kenali pola permintaan, pengaruh cuaca, dan karakter pengguna dari data penyewaan sepeda.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

if not selected_seasons or not selected_weather or not selected_users:
    st.info("Pilih minimal satu musim, kondisi cuaca, dan tipe pengguna di sidebar.")
    st.stop()

start_timestamp = pd.Timestamp(start_date)
end_timestamp = pd.Timestamp(end_date)
daily_scope = daily_data[
    daily_data["dteday"].between(start_timestamp, end_timestamp)
    & daily_data["season_day"].isin(selected_seasons)
    & daily_data["weathersit_day"].isin(selected_weather)
].copy()
hourly_scope = hourly_data[
    hourly_data["dteday"].between(start_timestamp, end_timestamp)
    & hourly_data["season_hour"].isin(selected_seasons)
    & hourly_data["weathersit_hour"].isin(selected_weather)
].copy()
daily_user_columns = [f"{USER_COLUMNS[user]}_day" for user in selected_users]
hourly_user_columns = [f"{USER_COLUMNS[user]}_hour" for user in selected_users]
daily_scope["selected_rides"] = daily_scope[daily_user_columns].sum(axis=1)
hourly_scope["selected_rides"] = hourly_scope[hourly_user_columns].sum(axis=1)
overview = daily_scope
if overview.empty:
    st.warning("Tidak ada data untuk kombinasi filter yang dipilih.")
    st.stop()

total_rides = overview["selected_rides"].sum()
average_daily = overview["selected_rides"].mean()
registered_rides = overview["registered_day"].sum() if "Terdaftar" in selected_users else 0
registered_share = registered_rides / total_rides * 100 if total_rides else 0
peak_row = overview.loc[overview["selected_rides"].idxmax()]
date_range = f"{overview['dteday'].min():%d %b %Y} — {overview['dteday'].max():%d %b %Y}"

st.caption(f"Ringkasan terpilih · {date_range}")
metric_columns = st.columns(4)
metric_columns[0].metric("Total penyewaan", format_number(total_rides))
metric_columns[1].metric("Rata-rata per hari", format_number(average_daily))
metric_columns[2].metric("Porsi pengguna terdaftar", f"{registered_share:.1f}%")
metric_columns[3].metric("Hari tersibuk", peak_row["dteday"].strftime("%d %b %Y"))
metric_columns[3].caption(f"{format_number(peak_row['selected_rides'])} penyewaan")

overview_tab, hourly_tab, season_tab, temperature_tab = st.tabs(
    ["📈 Ringkasan", "⏱️ Cuaca & jam", "🍂 Musim & pengguna", "🌡️ Suhu"]
)

with overview_tab:
    st.subheader("Perjalanan dari waktu ke waktu")
    st.markdown(
        f'<p class="scope-note">Akumulasi penyewaan harian dalam filter aktif · {len(overview):,} hari</p>',
        unsafe_allow_html=True,
    )
    trend = overview.sort_values("dteday")
    fig = px.area(
        trend,
        x="dteday",
        y="selected_rides",
        color_discrete_sequence=[COLORS["blue"]],
        labels={"dteday": "Tanggal", "selected_rides": "Penyewaan"},
    )
    fig.update_traces(
        line=dict(width=2.5),
        fillcolor="rgba(79,124,255,0.14)",
        hovertemplate="%{x|%d %b %Y}<br>%{y:,.0f} penyewaan<extra></extra>",
    )
    polish_chart(fig, 400)
    st.plotly_chart(fig, width="stretch")

    monthly = (
        overview.assign(periode=overview["dteday"].dt.to_period("M").astype(str))
        .groupby("periode", as_index=False)["selected_rides"]
        .sum()
    )
    monthly_fig = px.bar(
        monthly,
        x="periode",
        y="selected_rides",
        color_discrete_sequence=[COLORS["cyan"]],
        labels={"periode": "Bulan", "selected_rides": "Total penyewaan"},
    )
    monthly_fig.update_traces(hovertemplate="%{x}<br>%{y:,.0f} penyewaan<extra></extra>")
    polish_chart(monthly_fig, 300)
    st.plotly_chart(monthly_fig, width="stretch")

with hourly_tab:
    st.subheader("Apakah cuaca memengaruhi permintaan?")
    st.markdown(
        '<p class="scope-note">Rata-rata penyewaan per jam · sesuai filter aktif</p>',
        unsafe_allow_html=True,
    )
    weather = (
        hourly_scope.groupby("weathersit_hour", as_index=False)["selected_rides"]
        .mean()
        .sort_values("weathersit_hour")
    )
    weather["kondisi"] = weather["weathersit_hour"].map(WEATHER)
    weather_fig = px.bar(
        weather,
        x="kondisi",
        y="selected_rides",
        color="selected_rides",
        color_continuous_scale=["#b8c8ff", COLORS["blue"]],
        labels={"kondisi": "Kondisi cuaca", "selected_rides": "Rata-rata penyewaan / jam"},
    )
    weather_fig.update_coloraxes(showscale=False)
    weather_fig.update_traces(hovertemplate="%{x}<br>%{y:.1f} unit / jam<extra></extra>")
    polish_chart(weather_fig, 340)
    st.plotly_chart(weather_fig, width="stretch")

    st.subheader("Pola perjalanan per jam")
    st.markdown(
        '<p class="scope-note">Hari kerja dibanding hari libur / akhir pekan · sesuai filter aktif</p>',
        unsafe_allow_html=True,
    )
    hourly_trend = (
        hourly_scope.assign(
            tipe_hari=hourly_scope["workingday_hour"].map(
                {0: "Hari libur / akhir pekan", 1: "Hari kerja"}
            )
        )
        .groupby(["hr", "tipe_hari"], as_index=False)["selected_rides"]
        .mean()
    )
    hourly_fig = px.line(
        hourly_trend,
        x="hr",
        y="selected_rides",
        color="tipe_hari",
        markers=True,
        color_discrete_map={
            "Hari libur / akhir pekan": COLORS["orange"],
            "Hari kerja": COLORS["blue"],
        },
        labels={
            "hr": "Jam",
            "selected_rides": "Rata-rata penyewaan / jam",
            "tipe_hari": "Tipe hari",
        },
    )
    hourly_fig.update_xaxes(dtick=2, tick0=0, range=[0, 23])
    hourly_fig.update_traces(hovertemplate="Pukul %{x}:00<br>%{y:.1f} unit / jam<extra></extra>")
    polish_chart(hourly_fig, 380)
    st.plotly_chart(hourly_fig, width="stretch")

with season_tab:
    st.subheader("Musim puncak di tahun 2012")
    st.markdown(
        '<p class="scope-note">Total penyewaan harian · sesuai filter aktif</p>',
        unsafe_allow_html=True,
    )
    daily_2012 = daily_scope[daily_scope["tahun"] == 2012]
    seasonal = (
        daily_2012.groupby("season_day", as_index=False)["selected_rides"]
        .sum()
        .sort_values("season_day")
    )
    seasonal["musim"] = seasonal["season_day"].map(SEASONS)
    if not seasonal.empty:
        season_fig = px.bar(
            seasonal,
            x="musim",
            y="selected_rides",
            color="musim",
            color_discrete_sequence=[
                COLORS["cyan"],
                COLORS["blue"],
                COLORS["purple"],
                COLORS["orange"],
            ],
            category_orders={"musim": list(SEASONS.values())},
            labels={"musim": "Musim", "selected_rides": "Total penyewaan"},
        )
        season_fig.update_traces(hovertemplate="%{x}<br>%{y:,.0f} penyewaan<extra></extra>")
        polish_chart(season_fig, 340)
        st.plotly_chart(season_fig, width="stretch")
        best_season = seasonal.loc[seasonal["selected_rides"].idxmax()]
        st.info(
            f"Permintaan tertinggi pada {best_season['musim'].lower()} "
            f"dengan {format_number(best_season['selected_rides'])} penyewaan."
        )
    else:
        st.info("Tidak ada data tahun 2012 untuk filter yang dipilih.")

    st.subheader("Kasual dan terdaftar sepanjang 2011")
    st.markdown(
        '<p class="scope-note">Total penyewaan bulanan · sesuai filter aktif</p>',
        unsafe_allow_html=True,
    )
    monthly_users = (
        daily_scope[daily_scope["tahun"] == 2011]
        .groupby("bulan", as_index=False)[daily_user_columns]
        .sum()
        .sort_values("bulan")
    )
    if not monthly_users.empty:
        user_fig = go.Figure()
        for user in selected_users:
            column = f"{USER_COLUMNS[user]}_day"
            color = COLORS["blue"] if user == "Terdaftar" else COLORS["orange"]
            user_fig.add_bar(
                x=[MONTHS[int(month) - 1] for month in monthly_users["bulan"]],
                y=monthly_users[column],
                name=user,
                marker_color=color,
                hovertemplate=f"%{{x}}<br>%{{y:,.0f}} penyewaan<extra>{user}</extra>",
            )
        user_fig.update_layout(barmode="stack", yaxis_title="Total penyewaan", xaxis_title="Bulan")
        polish_chart(user_fig, 350)
        st.plotly_chart(user_fig, width="stretch")
    else:
        st.info("Tidak ada data tahun 2011 untuk filter yang dipilih.")

with temperature_tab:
    st.subheader("Suhu yang terasa dan jumlah penyewaan")
    st.markdown(
        '<p class="scope-note">Data harian Juli–September 2012 · sesuai filter aktif · atemp adalah indeks suhu ternormalisasi</p>',
        unsafe_allow_html=True,
    )
    q3_2012 = daily_scope[
        (daily_scope["tahun"] == 2012) & daily_scope["bulan"].between(7, 9)
    ].copy()
    if q3_2012.empty:
        st.warning("Tidak ada data Q3 2012 untuk filter yang dipilih.")
    else:
        correlation = q3_2012["atemp_day"].corr(q3_2012["selected_rides"])
        st.metric("Korelasi Pearson", f"{correlation:.2f}")
        st.caption("Hubungan positif" if correlation > 0 else "Hubungan negatif")
        x_values = q3_2012["atemp_day"]
        y_values = q3_2012["selected_rides"]
        slope, intercept = np.polyfit(x_values, y_values, 1)
        scatter_fig = go.Figure()
        scatter_fig.add_trace(
            go.Scatter(
                x=x_values,
                y=y_values,
                mode="markers",
                name="Hari",
                marker=dict(color=COLORS["cyan"], size=9, opacity=0.72),
                text=q3_2012["dteday"].dt.strftime("%d %b %Y"),
                hovertemplate="%{text}<br>atemp: %{x:.3f}<br>%{y:,.0f} penyewaan<extra></extra>",
            )
        )
        line_x = [float(x_values.min()), float(x_values.max())]
        scatter_fig.add_trace(
            go.Scatter(
                x=line_x,
                y=[slope * value + intercept for value in line_x],
                mode="lines",
                name="Tren linear",
                line=dict(color=COLORS["orange"], width=3),
                hoverinfo="skip",
            )
        )
        scatter_fig.update_layout(
            xaxis_title="Suhu yang terasa (atemp, ternormalisasi)",
            yaxis_title="Total penyewaan harian",
        )
        polish_chart(scatter_fig, 420)
        st.plotly_chart(scatter_fig, width="stretch")
        st.caption(
            f"Perhitungan memakai {len(q3_2012)} hari pada Q3 2012. "
            "Korelasi menggambarkan hubungan, bukan sebab-akibat."
        )

st.markdown("---")
st.caption("Sumber: Bike Sharing Dataset.")
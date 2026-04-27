import random

import pandas as pd
import streamlit as st


st.set_page_config(
    page_title="Monty-Hall-App",
    page_icon="🚪",
    layout="wide",
)


st.markdown(
    """
    <style>
    .hero-shell {
        margin-bottom: 1rem;
    }

    .hero-card {
        padding: 1.4rem 1.5rem;
        border-radius: 18px;
        background: color-mix(in srgb, var(--secondary-background-color) 82%, transparent);
        border: 1px solid color-mix(in srgb, var(--primary-color) 35%, transparent);
        box-shadow: inset 0 0 0 1px color-mix(in srgb, var(--background-color) 55%, transparent);
    }

    .hero-eyebrow {
        color: var(--primary-color);
        font-size: 0.9rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.08em;
    }

    .hero-title {
        color: var(--text-color);
        font-size: 2.2rem;
        font-weight: 800;
        line-height: 1.1;
        margin: 0.35rem 0 0.6rem;
    }

    .hero-copy {
        color: color-mix(in srgb, var(--text-color) 78%, transparent);
        font-size: 1rem;
        margin-bottom: 0;
    }

    .mini-card {
        padding: 1rem 1.1rem;
        border-radius: 20px;
        background: color-mix(in srgb, var(--secondary-background-color) 88%, transparent);
        border: 1px solid color-mix(in srgb, var(--text-color) 10%, transparent);
        box-shadow: 0 12px 28px color-mix(in srgb, var(--text-color) 7%, transparent);
        min-height: 100%;
    }

    .mini-label {
        color: color-mix(in srgb, var(--text-color) 60%, transparent);
        font-size: 0.85rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0.2rem;
    }

    .mini-value {
        color: var(--text-color);
        font-size: 1.7rem;
        font-weight: 800;
        margin: 0;
    }

    .mini-copy {
        color: color-mix(in srgb, var(--text-color) 72%, transparent);
        font-size: 0.92rem;
        margin: 0.35rem 0 0;
    }

    div[data-testid="stExpander"] {
        border: 1px solid color-mix(in srgb, var(--text-color) 10%, transparent);
        border-radius: 18px;
        background: color-mix(in srgb, var(--secondary-background-color) 82%, transparent);
    }

    div[data-testid="stDataFrame"],
    div[data-testid="stDataEditor"] {
        border: 1px solid color-mix(in srgb, var(--text-color) 10%, transparent);
        border-radius: 18px;
        overflow: hidden;
        background: color-mix(in srgb, var(--secondary-background-color) 90%, transparent);
    }

    div[data-testid="stDataFrame"] [role="grid"],
    div[data-testid="stDataEditor"] [role="grid"] {
        background: color-mix(in srgb, var(--secondary-background-color) 94%, transparent);
        color: var(--text-color);
    }

    div[data-testid="stDataFrame"] [role="columnheader"],
    div[data-testid="stDataEditor"] [role="columnheader"] {
        background: color-mix(in srgb, var(--secondary-background-color) 76%, transparent);
        color: var(--text-color);
    }
    </style>
    """,
    unsafe_allow_html=True,
)


STRATEGY_OPTIONS = {
    "Vergleich beider Taktiken": "compare",
    "Nur bleiben": "stay",
    "Nur wechseln": "switch",
}


def play_round(round_number: int) -> dict:
    doors = [1, 2, 3]
    car = random.choice(doors)
    first_choice = random.choice(doors)

    possible_open = [
        door for door in doors
        if door != first_choice and door != car
    ]
    opened = random.choice(possible_open)

    switch_choice = next(
        door for door in doors
        if door != first_choice and door != opened
    )

    stay_win = first_choice == car
    switch_win = switch_choice == car

    return {
        "Runde": round_number,
        "Auto hinter Tür": car,
        "Erste Wahl": first_choice,
        "Von Monty geöffnet": opened,
        "Wahl bei Bleiben": first_choice,
        "Wahl bei Wechseln": switch_choice,
        "Gewinn bei Bleiben": "Ja" if stay_win else "Nein",
        "Gewinn bei Wechseln": "Ja" if switch_win else "Nein",
    }


@st.cache_data(show_spinner=False)
def run_simulation(n_rounds: int) -> tuple[pd.DataFrame, pd.DataFrame]:
    rounds = [play_round(index) for index in range(1, n_rounds + 1)]
    detail_df = pd.DataFrame(rounds)

    stay_wins = (detail_df["Gewinn bei Bleiben"] == "Ja").sum()
    switch_wins = (detail_df["Gewinn bei Wechseln"] == "Ja").sum()

    summary_df = pd.DataFrame(
        {
            "Strategie": ["Bleiben", "Wechseln"],
            "Gewinne": [stay_wins, switch_wins],
            "Verluste": [n_rounds - stay_wins, n_rounds - switch_wins],
            "Gewinnrate": [
                stay_wins / n_rounds * 100,
                switch_wins / n_rounds * 100,
            ],
        }
    )

    return summary_df, detail_df


def build_strategy_view(detail_df: pd.DataFrame, strategy_mode: str) -> tuple[pd.DataFrame, str]:
    if strategy_mode == "stay":
        strategy_df = detail_df[
            [
                "Runde",
                "Auto hinter Tür",
                "Erste Wahl",
                "Von Monty geöffnet",
                "Wahl bei Bleiben",
                "Gewinn bei Bleiben",
            ]
        ].rename(
            columns={
                "Wahl bei Bleiben": "Finale Wahl",
                "Gewinn bei Bleiben": "Gewonnen",
            }
        )
        return strategy_df, "Die Tabelle zeigt genau den Datensatz, der für die Taktik `Bleiben` ausgewertet wird."

    if strategy_mode == "switch":
        strategy_df = detail_df[
            [
                "Runde",
                "Auto hinter Tür",
                "Erste Wahl",
                "Von Monty geöffnet",
                "Wahl bei Wechseln",
                "Gewinn bei Wechseln",
            ]
        ].rename(
            columns={
                "Wahl bei Wechseln": "Finale Wahl",
                "Gewinn bei Wechseln": "Gewonnen",
            }
        )
        return strategy_df, "Die Tabelle zeigt genau den Datensatz, der für die Taktik `Wechseln` ausgewertet wird."

    return detail_df, "Hier siehst du den vollständigen Datensatz mit beiden Strategien pro Runde."


with st.container(border=True):
    st.markdown(
        """
        <div class="hero-shell">
            <div class="hero-card">
                <div class="hero-eyebrow">Monte-Hall-Simulation</div>
                <div class="hero-title">Interaktive Veranschaulichung des Monty-Hall-Problems</div>
                <p class="hero-copy">
                    Wähle zuerst deine Taktik, starte danach die Simulation und verfolge direkt im Datensatz,
                    warum Wechseln langfristig meist besser abschneidet.
                </p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with st.expander("Kurz erklärt: Was passiert beim Monty-Hall-Problem?"):
    st.markdown(
        """
        - Hinter einer von drei Türen steht das Auto, hinter den anderen beiden Ziegen.
        - Du wählst zuerst eine Tür, ohne zu wissen, wo das Auto ist.
        - Monty öffnet danach absichtlich eine andere Tür mit einer Ziege.
        - Jetzt kannst du entweder bei deiner ersten Wahl bleiben oder zur letzten geschlossenen Tür wechseln.
        - Genau diese beiden Taktiken vergleicht die App.
        """
    )

left, right = st.columns([1.15, 0.85], gap="large")

with left:
    strategy_label = st.radio(
        "Mit welcher Taktik möchtest du starten?",
        options=list(STRATEGY_OPTIONS.keys()),
        horizontal=True,
    )
    strategy_mode = STRATEGY_OPTIONS[strategy_label]

with right:
    n_rounds = st.slider(
        "Wie viele Durchläufe sollen simuliert werden?",
        min_value=10,
        max_value=10_000,
        value=1_000,
        step=10,
    )

simulate = st.button("Simulation starten", type="primary", use_container_width=True)

if simulate:
    summary_df, detail_df = run_simulation(n_rounds)
    strategy_df, dataset_hint = build_strategy_view(detail_df, strategy_mode)

    if strategy_mode == "stay":
        selected_summary = summary_df.loc[summary_df["Strategie"] == "Bleiben"].iloc[0]
        highlight_title = "Taktik: Bleiben"
        highlight_copy = "Du hältst immer an deiner ersten Entscheidung fest."
    elif strategy_mode == "switch":
        selected_summary = summary_df.loc[summary_df["Strategie"] == "Wechseln"].iloc[0]
        highlight_title = "Taktik: Wechseln"
        highlight_copy = "Du wechselst nach Montys Hinweis immer zur anderen geschlossenen Tür."
    else:
        best_strategy = summary_df.sort_values("Gewinnrate", ascending=False).iloc[0]
        selected_summary = best_strategy
        highlight_title = f"Beste Taktik in dieser Simulation: {best_strategy['Strategie']}"
        highlight_copy = "Im Vergleich siehst du sofort, welche Strategie im aktuellen Lauf vorne liegt."

    metric_columns = st.columns(3, gap="medium")
    metric_values = [
        ("Durchläufe", f"{n_rounds:,}".replace(",", "."), "So oft wurde das Experiment durchgeführt."),
        ("Gewinne", int(selected_summary["Gewinne"]), highlight_copy),
        ("Gewinnrate", f"{selected_summary['Gewinnrate']:.2f} %", highlight_title),
    ]

    for column, (label, value, copy) in zip(metric_columns, metric_values):
        with column:
            st.markdown(
                f"""
                <div class="mini-card">
                    <div class="mini-label">{label}</div>
                    <p class="mini-value">{value}</p>
                    <p class="mini-copy">{copy}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

    overview_tab, dataset_tab, explanation_tab = st.tabs(
        ["Auswertung", "Datensatz", "Einordnung"]
    )

    with overview_tab:
        st.subheader("Zusammenfassung der Strategien")
        st.dataframe(
            summary_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Gewinnrate": st.column_config.NumberColumn(
                    "Gewinnrate in %",
                    format="%.2f %%",
                )
            },
        )

        st.subheader("Gewinnraten im Vergleich")
        chart_data = summary_df.set_index("Strategie")[["Gewinnrate"]]
        st.bar_chart(chart_data, use_container_width=True)

    with dataset_tab:
        st.subheader("Aktuell ausgewerteter Datensatz")
        st.caption(dataset_hint)

        max_rows = min(len(strategy_df), 250)
        displayed_rows = st.slider(
            "Wie viele Zeilen des Datensatzes möchtest du sehen?",
            min_value=10,
            max_value=max_rows,
            value=min(25, max_rows),
            step=5,
        )

        st.data_editor(
            strategy_df.head(displayed_rows),
            use_container_width=True,
            hide_index=True,
            disabled=True,
        )

        csv_data = strategy_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "Datensatz als CSV herunterladen",
            data=csv_data,
            file_name="monty_hall_datensatz.csv",
            mime="text/csv",
            use_container_width=True,
        )

    with explanation_tab:
        st.subheader("Was bedeutet das Ergebnis?")
        st.markdown(
            f"""
            - Bei **{n_rounds:,} Durchläufen** liegt die Strategie **Wechseln** meist nahe bei **66 % Gewinnchance**.  
            - Die Strategie **Bleiben** landet typischerweise eher bei **33 % Gewinnchance**.  
            - Dein aktueller Lauf zeigt für **Bleiben** eine Gewinnrate von **{summary_df.iloc[0]['Gewinnrate']:.2f} %**.  
            - Für **Wechseln** liegt die aktuelle Gewinnrate bei **{summary_df.iloc[1]['Gewinnrate']:.2f} %**.
            """.replace(",", ".")
        )
else:
    st.info("Wähle oben eine Taktik aus und starte danach die Simulation.")

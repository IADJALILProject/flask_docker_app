import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
from sqlalchemy import create_engine
import os

def create_dash_app(flask_app):
    # 🌈 Thème Dash Bootstrap (peux aussi tester MORPH, LUX, MINTY, etc.)
    external_stylesheets = [dbc.themes.CYBORG]

    dash_app = dash.Dash(
        __name__,
        server=flask_app,
        url_base_pathname="/dashboard/",
        external_stylesheets=external_stylesheets
    )

    # 🔐 Lecture sécurisée des variables d'environnement
    POSTGRES_USER = os.getenv("POSTGRES_USER", "flaskuser")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "flaskpass")
    POSTGRES_DB = os.getenv("POSTGRES_DB", "flaskdb")
    POSTGRES_HOST = os.getenv("POSTGRES_HOST", "db")
    POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")

    # 🔗 URI SQLAlchemy vers PostgreSQL
    db_uri = (
        f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}"
        f"@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
    )
    engine = create_engine(db_uri)

    try:
        df = pd.read_sql_query("SELECT * FROM users_csv", engine)
    except Exception as e:
        print("❌ Erreur lors de la lecture de la table users_csv :", e)
        df = pd.DataFrame()

    if df.empty:
        dash_app.layout = dbc.Container([
            dbc.Alert("⚠️ Aucune donnée à afficher. Exécute d'abord le DAG ETL !", color="warning", className="mt-4")
        ])
        return dash_app

    # 🧱 Layout principal
    dash_app.layout = dbc.Container([
        dbc.Row([
            dbc.Col(html.H1("📊 Dashboard Interactif", className="text-center text-info mb-4"))
        ]),

        dbc.Row([
            dbc.Col([
                html.Label("📦 Filtrer par abonnement"),
                dcc.Dropdown(
                    id='subscription_filter',
                    options=[{"label": i, "value": i} for i in df['subscription_type'].unique()],
                    placeholder="Choisir un abonnement"
                )
            ], width=6),

            dbc.Col([
                html.Label("🌍 Filtrer par pays"),
                dcc.Dropdown(
                    id='country_filter',
                    options=[{"label": i, "value": i} for i in df['country'].unique()],
                    placeholder="Choisir un pays"
                )
            ], width=6)
        ], className="mb-4"),

        dbc.Row([
            dbc.Col(dcc.Graph(id='bar_subscription_count'), width=6),
            dbc.Col(dcc.Graph(id='pie_country_distribution'), width=6)
        ]),

        dbc.Row([
            dbc.Col(dcc.Graph(id='line_avg_age'), width=6),
            dbc.Col(dcc.Graph(id='bar_active_status'), width=6)
        ])
    ], fluid=True)

    # 🔁 Callbacks réactifs
    @dash_app.callback(
        [
            Output('bar_subscription_count', 'figure'),
            Output('pie_country_distribution', 'figure'),
            Output('line_avg_age', 'figure'),
            Output('bar_active_status', 'figure')
        ],
        [
            Input('subscription_filter', 'value'),
            Input('country_filter', 'value')
        ]
    )
    def update_graphs(subscription_type, country):
        filtered_df = df.copy()
        if subscription_type:
            filtered_df = filtered_df[filtered_df['subscription_type'] == subscription_type]
        if country:
            filtered_df = filtered_df[filtered_df['country'] == country]

        # 📊 1. Répartition par abonnement
        df_count = filtered_df['subscription_type'].value_counts().reset_index()
        df_count.columns = ['subscription_type', 'count']
        bar_fig = px.bar(df_count, x='subscription_type', y='count', text='count',
                         title="Utilisateurs par abonnement", template='plotly_dark')

        # 🗺️ 2. Répartition par pays
        df_country = filtered_df['country'].value_counts().reset_index()
        df_country.columns = ['country', 'count']
        pie_fig = px.pie(df_country, names='country', values='count',
                         title="Répartition par pays", template='plotly_dark')

        # 📈 3. Âge moyen par abonnement
        avg_age = filtered_df.groupby('subscription_type')['age'].mean().reset_index()
        line_fig = px.line(avg_age, x='subscription_type', y='age',
                           title="Âge moyen par abonnement", template='plotly_dark')

        # ✅ 4. Actifs vs inactifs
        active_df = filtered_df['is_active'].value_counts().reset_index()
        active_df.columns = ['is_active', 'count']
        bar_active = px.bar(active_df, x='is_active', y='count',
                            title="Utilisateurs actifs vs inactifs", template='plotly_dark')

        return bar_fig, pie_fig, line_fig, bar_active

    return dash_app

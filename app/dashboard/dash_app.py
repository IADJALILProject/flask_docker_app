import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
from app.models import db  # Connexion SQLAlchemy de Flask

def create_dash_app(flask_app):
    external_stylesheets = [dbc.themes.CYBORG]

    dash_app = dash.Dash(
        __name__,
        server=flask_app,
        url_base_pathname="/dashboard/",
        external_stylesheets=external_stylesheets
    )

    dash_app.title = "📊 Dashboard Utilisateurs"

    # Layout principal de l'application (statique)
    dash_app.layout = dbc.Container([
        dbc.Row([
            dbc.Col(html.H1("📊 Dashboard Interactif", className="text-center text-info mb-4"))
        ]),

        dbc.Row([
            dbc.Col([
                html.Label("📦 Filtrer par abonnement"),
                dcc.Dropdown(id='subscription_filter', placeholder="Choisir un abonnement")
            ], width=6),

            dbc.Col([
                html.Label("🌍 Filtrer par pays"),
                dcc.Dropdown(id='country_filter', placeholder="Choisir un pays")
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

    # Callback dynamique qui lit les données à chaque changement de filtre
    @dash_app.callback(
        [
            Output('bar_subscription_count', 'figure'),
            Output('pie_country_distribution', 'figure'),
            Output('line_avg_age', 'figure'),
            Output('bar_active_status', 'figure'),
            Output('subscription_filter', 'options'),
            Output('country_filter', 'options'),
        ],
        [
            Input('subscription_filter', 'value'),
            Input('country_filter', 'value')
        ]
    )
    def update_graphs(subscription_type, country):
        try:
            df = pd.read_sql_query("SELECT * FROM users_csv", db.engine)
        except Exception as e:
            print("❌ Erreur de lecture des données :", e)
            return dash.no_update, dash.no_update, dash.no_update, dash.no_update, [], []

        if df.empty:
            return dash.no_update, dash.no_update, dash.no_update, dash.no_update, [], []

        # Mise à jour dynamique des options
        subscription_opts = [{"label": i, "value": i} for i in sorted(df['subscription_type'].dropna().unique())]
        country_opts = [{"label": i, "value": i} for i in sorted(df['country'].dropna().unique())]

        # Filtres
        filtered_df = df.copy()
        if subscription_type:
            filtered_df = filtered_df[filtered_df['subscription_type'] == subscription_type]
        if country:
            filtered_df = filtered_df[filtered_df['country'] == country]

        # 📊 Graphique 1 : Nombre par abonnement
        df_count = filtered_df['subscription_type'].value_counts().reset_index()
        df_count.columns = ['subscription_type', 'count']
        bar_fig = px.bar(df_count, x='subscription_type', y='count', text='count',
                         title="Utilisateurs par abonnement", template='plotly_dark')

        # 🗺️ Graphique 2 : Répartition par pays
        df_country = filtered_df['country'].value_counts().reset_index()
        df_country.columns = ['country', 'count']
        pie_fig = px.pie(df_country, names='country', values='count',
                         title="Répartition par pays", template='plotly_dark')

        # 📈 Graphique 3 : Âge moyen par abonnement
        avg_age = filtered_df.groupby('subscription_type')['age'].mean().reset_index()
        line_fig = px.line(avg_age, x='subscription_type', y='age',
                           title="Âge moyen par abonnement", template='plotly_dark')

        # ✅ Graphique 4 : Actifs vs Inactifs
        active_df = filtered_df['is_active'].value_counts().reset_index()
        active_df.columns = ['is_active', 'count']
        bar_active = px.bar(active_df, x='is_active', y='count',
                            title="Utilisateurs actifs vs inactifs", template='plotly_dark')

        return bar_fig, pie_fig, line_fig, bar_active, subscription_opts, country_opts

    return dash_app

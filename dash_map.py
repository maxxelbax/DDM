import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
import dash_bootstrap_components as dbc


def rgba_tuple_to_str(rgba):
    r, g, b, a = rgba
    return f"rgba({int(r * 255)}, {int(g * 255)}, {int(b * 255)}, {a})"


df = pd.read_csv('full_clustered_data_real.csv', sep=';', decimal=',')
df['sqft_living'] = df['sqft_above'] + df['sqft_basement']
df['basement_binary'] = 0
df.loc[df['sqft_basement'] > 0, 'basement_binary'] = 1

tab10 = plt.get_cmap("tab10")
clusters = ['New Suburban (Family)', 'Established Housing (w/o Basement)', 'Established Housing (with Basement)', 'Luxurious',
            'Compact Urban Housing', 'Modern/Renovated']
clusters_palette = {clusters[cluster_id]: tab10(cluster_id) for cluster_id in
                    range(len(clusters))}
clusters_palette_plotly = {k: rgba_tuple_to_str(v) for k, v in clusters_palette.items()}

hover_cols = ["id", "price", "age", "renovated", "sqft_living", "sqft_lot", "final_category"]
log_features = ["price", "sqft_living", "sqft_lot", "sqft_above", "sqft_basement", ]
color_features = [{"label": "Final category", "value": "final_category"}, {"label": "Age", "value": "age"},
                  {"label": "Renovated", "value": "renovated"}, ] + [{"label": f.replace("_", " ").title(), "value": f} for f
                                                                     in log_features]

continuous_color_scales = ["Custom",  # used when final_category is selected
                           "RdYlGn", "RdYlGn_r", "Viridis", 'delta', 'edge', ]

age_min, age_max = df.age.min(), df.age.max()

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])
app.title = "Interactive Map"

# layout
app.layout = html.Div(
    style={"padding": "6px"},
    children=[
        html.Div(style={"display": "flex", "gap": "10px"},
                 children=[
                     # left sidebar
                     html.Div(
                         style={"width": "440px", "minWidth": "320px",
                                "border": "1px solid #e5e5e5",
                                "borderRadius": "8px", "padding": "10px",
                                "height": "98vh",
                                "boxSizing": "border-box", }, children=[
                             html.Div(style={"display": "flex",
                                             "flexDirection": "column",
                                             "gap": "12px"},
                                      children=[html.Div(
                                          children=[html.Label("Color by"),
                                                    dcc.Dropdown(
                                                        id="color-feature",
                                                        options=color_features,
                                                        value="final_category",
                                                        clearable=False, ), ], ),
                                          html.Div(children=[
                                              html.Label("Color scale"),
                                              dcc.Dropdown(id="color-scale",
                                                           options=[
                                                               {"label": c,
                                                                "value": c} for
                                                               c in
                                                               continuous_color_scales],
                                                           value="Custom",
                                                           clearable=False,
                                                           disabled=True,
                                                           ), ], ),
                                          html.Div(children=[
                                              html.Label("Categories"),
                                              dcc.Dropdown(id="category-dropdown",
                                                           multi=True,
                                                           options=clusters,
                                                           value=clusters,
                                                           clearable=False,
                                                           disabled=False,
                                                           ), ], ),
                                          html.Div(
                                              style={"display": "flex", "gap": "12px"},
                                              children=[
                                                  html.Div(
                                                      style={"flex": "1", "minWidth": 0},
                                                      children=[
                                                          html.Label("Renovated"),
                                                          dcc.Checklist(
                                                              id="renovated-filter",
                                                              options=[
                                                                  {"label": "Not renovated", "value": 0},
                                                                  {"label": "Renovated", "value": 1},
                                                              ],
                                                              value=[0, 1],
                                                              inline=False,
                                                          ),
                                                      ],
                                                  ),
                                                  html.Div(
                                                      style={"flex": "1", "minWidth": 0},
                                                      children=[
                                                          html.Label("Basement"),
                                                          dcc.Checklist(
                                                              id="basement-filter",
                                                              options=[
                                                                  {"label": "Without Basement", "value": 0},
                                                                  {"label": "With Basement", "value": 1},
                                                              ],
                                                              value=[0, 1],
                                                              inline=False,
                                                          ),
                                                      ],
                                                  ),
                                              ],
                                          )
                                      ], ),
                             html.Hr(style={"margin": "14px 0"}),

                             # sliders
                             html.Div(style={"display": "flex", "flexDirection": "column", "gap": "3px"},
                                      children=[
                                          html.Div(
                                              children=[
                                                  html.Label(
                                                      "Price (log)",
                                                      style={"textAlign": "center", "display": "block"}
                                                  ),
                                                  dcc.RangeSlider(
                                                      id="price-slider",
                                                      vertical=False,
                                                      value=[4.5, 7],
                                                      min=4.5, max=7, step=0.01,
                                                      marks=None,
                                                      tooltip={
                                                          "placement": "bottom",
                                                          "always_visible": True},
                                                  ), ],
                                          ),
                                          html.Div(
                                              children=[
                                                  html.Label(
                                                      "Sqft. Living (log)",
                                                      style={"textAlign": "center", "display": "block"}
                                                  ),
                                                  dcc.RangeSlider(
                                                      id="sqft_living-slider",
                                                      vertical=False,
                                                      value=[2.4, 4.2],
                                                      min=2.4, max=4.2, step=0.01,
                                                      marks=None,
                                                      tooltip={
                                                          "placement": "bottom",
                                                          "always_visible": True}, ), ],
                                          ),
                                          html.Div(
                                              children=[
                                                  html.Label(
                                                      "Sqft. Lot (log)",
                                                      style={"textAlign": "center", "display": "block"}
                                                  ),
                                                  dcc.RangeSlider(
                                                      id="sqft_lot-slider",
                                                      vertical=False,
                                                      value=[2.7, 6.3],
                                                      min=2.7, max=6.3, step=0.01,
                                                      marks=None,
                                                      tooltip={
                                                          "placement": "bottom",
                                                          "always_visible": True}, ), ],
                                          ),
                                          html.Div(
                                              children=[
                                                  html.Label(
                                                      "Age",
                                                      style={"textAlign": "center", "display": "block"}
                                                  ),
                                                  dcc.RangeSlider(
                                                      id="age-slider",
                                                      min=age_min,
                                                      max=age_max,
                                                      value=[
                                                          age_min,
                                                          age_max],
                                                      step=1,
                                                      vertical=False,
                                                      marks=None,
                                                      tooltip={
                                                          "placement": "bottom",
                                                          "always_visible": True},
                                                  ), ],
                                          ),
                                      ], ),
                         ],
                     ),
                     # MAP (RIGHT)
                     html.Div(
                         style={"flex": "1", "minWidth": "0"},
                         children=[
                             dcc.Graph(id="map",
                                       style={"height": "98vh"}),
                         ], ),
                 ], ),
    ], )


# coloring callback
@app.callback(Output("color-scale", "disabled"),
              Output("color-scale", "value"),
              Input("color-feature", "value"),
              Input("color-scale", "value"),
              )
def lock_palette_dropdown(color_feature, current_scale):
    if color_feature == "final_category":
        return True, "Custom"

    # enable for non-final_category; ensure scale is not stuck on Custom
    if current_scale == "Custom":
        return False, "RdYlGn"
    return False, current_scale


# map callback
@app.callback(Output("map", "figure"),
              Input("color-feature", "value"),
              Input("color-scale", "value"),
              Input("price-slider", "value"),
              Input("sqft_living-slider", "value"),
              Input("sqft_lot-slider", "value"),
              Input("age-slider", "value"),
              Input("renovated-filter", "value"),
              Input("basement-filter", "value"),
              Input("category-dropdown", "value"),
              )
def update_map(color_feature, color_scale, price_range_log, sqft_living_range_log, sqft_lot_range_log, age_range,
               renovated_values, basement_filter,
               catetegories):
    price_range = [10 ** price_range_log[0], 10 ** price_range_log[1]]
    sqft_living_range = [10 ** sqft_living_range_log[0], 10 ** sqft_living_range_log[1]]
    sqft_lot_range = [10 ** sqft_lot_range_log[0], 10 ** sqft_lot_range_log[1]]

    dff = df[(df.price >= price_range[0]) & (df.price <= price_range[1]) & (df.sqft_living >= sqft_living_range[0]) & (
            df.sqft_living <= sqft_living_range[1]) & (df.sqft_lot >= sqft_lot_range[0]) & (
                     df.sqft_lot <= sqft_lot_range[1]) & (df.age >= age_range[0]) & (df.age <= age_range[1]) & (
                 df.renovated.isin(renovated_values)) & (df['basement_binary'].isin(basement_filter)) & (
                 df['final_category'].isin(catetegories))].copy()

    # decide coloring behavior
    if color_feature == "final_category":
        color_col = "final_category"
        fig = px.scatter_map(dff, lat="lat", lon="long", color=color_col, zoom=9, size_max=18,
                             center=dict(lat=df.lat.mean(), lon=df.long.mean()), hover_name="final_category",
                             custom_data=hover_cols,
                             map_style="open-street-map",
                             color_discrete_map=clusters_palette_plotly, )
    else:
        # log-color for log-features
        if color_feature in log_features:
            log_col = f"{color_feature}__log10"
            dff[log_col] = np.log10(dff[color_feature].clip(lower=1))
            dff[log_col] = dff[log_col].clip(dff[log_col].min() * 1.05, dff[log_col] * 0.98)
            color_col = log_col
            color_title = f"log10({color_feature})"
        else:
            color_col = color_feature
            color_title = color_feature

        is_categorical = dff[color_feature].dtype == "object" or color_feature == "renovated"

        fig = px.scatter_map(dff, lat="lat", lon="long", color=color_col, zoom=9, size_max=18,
                             center=dict(lat=df.lat.mean(), lon=df.long.mean()), hover_name="final_category",
                             map_style="open-street-map", custom_data=hover_cols,
                             color_continuous_scale=None if is_categorical else color_scale, )

        if not is_categorical:
            fig.update_coloraxes(colorbar_title=color_title)

    fig.update_traces(
        hovertemplate=(
            "<b>%{customdata[6]}</b><br>"
            "ID: %{customdata[0]}<br>"
            "Price: $%{customdata[1]:,.0f}<br>"
            "Age: %{customdata[2]}<br>"
            "Renovated: %{customdata[3]}<br>"
            "Sqft. Living: %{customdata[4]:,.0f}<br>"
            "Sqft. Lot: %{customdata[5]:,.0f}<br>"
            "<extra></extra>"
        ),
        marker=dict(opacity=0.65))
    fig.update_layout(margin=dict(l=0, r=0, t=0, b=0))
    return fig


if __name__ == "__main__":
    app.run(debug=False)

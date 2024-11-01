import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

class BusinessModelProjection:
    def __init__(self, 
                 initial_traffic=1000, 
                 conversion_rate=0.02, 
                 average_basket=80, 
                 initial_capital=10000, 
                 initial_stock=3000, 
                 purchase_price_rate=0.4,
                 monthly_traffic_growth=0.05,
                 tax_rate=0.20,
                 payment_delay_clients=0,  # Délai de paiement clients en jours
                 payment_delay_suppliers=30):  # Délai de paiement fournisseurs en jours
        
        self.initial_traffic = initial_traffic
        self.conversion_rate = conversion_rate
        self.average_basket = average_basket
        self.initial_capital = initial_capital
        self.initial_stock = initial_stock
        self.purchase_price_rate = purchase_price_rate
        self.monthly_traffic_growth = monthly_traffic_growth
        self.tax_rate = tax_rate
        self.payment_delay_clients = payment_delay_clients
        self.payment_delay_suppliers = payment_delay_suppliers
        
        # Fixed Costs
        self.shopify_subscription = 32
        self.seo_consultant = 200
        self.domain_name = 1.25
        self.initial_advertising = 300
        
        # Variable Costs
        self.shipping_cost_per_order = 6
        self.shopify_commission_rate = 0.029
        self.shopify_fixed_commission = 0.30

    def calculate_monthly_data(self):
        # Code existant pour calculate_monthly_data() inchangé
        [...]  # Garder le code existant ici

    def calculate_annual_projections(self):
        # Code existant pour calculate_annual_projections() inchangé
        [...]  # Garder le code existant ici

    def calculate_cash_flow(self):
        monthly_df = self.calculate_monthly_data()
        cash_flow_data = []
        cumulative_cash = self.initial_capital
        
        # Calcul du BFR initial (Besoin en Fonds de Roulement)
        initial_bfr = self.initial_stock
        cumulative_cash -= initial_bfr
        
        for index, row in monthly_df.iterrows():
            month = row['Mois']
            
            # Entrées de trésorerie
            encaissements = row['Chiffre d\'affaires']  # Supposé encaissement immédiat pour simplifier
            
            # Sorties de trésorerie
            decaissements = (
                row['Coût d\'achat'] +  # Achats
                row['Frais de livraison'] +  # Frais de livraison
                row['Commissions'] +  # Commissions Shopify
                row['Coûts fixes']  # Coûts fixes
            )
            
            # Si c'est un mois où on doit payer les impôts (par exemple, le dernier mois)
            impots = 0
            if month == 'M12':
                impots = -row['Résultat d\'exploitation'] * self.tax_rate
            
            # Flux net de trésorerie du mois
            monthly_cash_flow = encaissements - decaissements - impots
            
            # Mise à jour du cumul
            cumulative_cash += monthly_cash_flow
            
            cash_flow_data.append({
                'Mois': month,
                'Encaissements': encaissements,
                'Décaissements': decaissements,
                'Impôts': impots,
                'Flux net': monthly_cash_flow,
                'Solde de trésorerie': cumulative_cash
            })
        
        return pd.DataFrame(cash_flow_data)

def main():
    # Code existant inchangé jusqu'aux graphiques
    [...]  # Garder le code existant ici jusqu'à la section des graphiques

    # Nouvelle section pour la trésorerie
    st.header("Prévisions de Trésorerie")
    
    # Calcul du cash flow
    cash_flow_df = model.calculate_cash_flow()
    
    # Métriques de trésorerie
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Trésorerie initiale", 
            f"{model.initial_capital:,.2f} €"
        )
        st.metric(
            "Total encaissements", 
            f"{cash_flow_df['Encaissements'].sum():,.2f} €"
        )
    
    with col2:
        st.metric(
            "Total décaissements", 
            f"{cash_flow_df['Décaissements'].sum():,.2f} €"
        )
        st.metric(
            "Total impôts", 
            f"{abs(cash_flow_df['Impôts'].sum()):,.2f} €"
        )
    
    with col3:
        st.metric(
            "Solde final de trésorerie", 
            f"{cash_flow_df['Solde de trésorerie'].iloc[-1]:,.2f} €"
        )
        st.metric(
            "Flux net de trésorerie", 
            f"{cash_flow_df['Flux net'].sum():,.2f} €"
        )
    
    # Graphique d'évolution de la trésorerie
    fig_cash = go.Figure()
    
    fig_cash.add_trace(go.Scatter(
        x=cash_flow_df['Mois'],
        y=cash_flow_df['Solde de trésorerie'],
        name='Solde de trésorerie',
        mode='lines+markers',
        line=dict(color='green')
    ))
    
    fig_cash.add_trace(go.Bar(
        x=cash_flow_df['Mois'],
        y=cash_flow_df['Flux net'],
        name='Flux net mensuel',
        marker_color='blue'
    ))
    
    fig_cash.update_layout(
        title='Évolution de la trésorerie',
        xaxis_title='Mois',
        yaxis_title='Euros',
        barmode='group'
    )
    
    st.plotly_chart(fig_cash)
    
    # Tableau détaillé des flux de trésorerie
    st.subheader("Détail mensuel des flux de trésorerie")
    st.dataframe(cash_flow_df.style.format({
        'Encaissements': '{:,.2f} €',
        'Décaissements': '{:,.2f} €',
        'Impôts': '{:,.2f} €',
        'Flux net': '{:,.2f} €',
        'Solde de trésorerie': '{:,.2f} €'
    }))

    # Code existant pour les autres graphiques et tableaux
    [...]  # Garder le code existant ici

if __name__ == "__main__":
    main()

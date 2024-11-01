import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

class BusinessModelProjection:
    def __init__(self, 
                 initial_traffic=1000, 
                 conversion_rate=0.02, 
                 average_basket=80, 
                 initial_capital=10000, 
                 initial_stock=3000, 
                 purchase_price_rate=0.4):
        
        self.initial_traffic = initial_traffic
        self.conversion_rate = conversion_rate
        self.average_basket = average_basket
        self.initial_capital = initial_capital
        self.initial_stock = initial_stock
        self.purchase_price_rate = purchase_price_rate
        
        # Fixed Costs
        self.shopify_subscription = 32
        self.seo_consultant = 200
        self.domain_name = 1.25
        self.initial_advertising = 300
        
        # Variable Costs
        self.shipping_cost_per_order = 6
        self.shopify_commission_rate = 0.029
        self.shopify_fixed_commission = 0.30

    def calculate_monthly_projections(self):
        # Nombre de commandes
        nb_commands = self.initial_traffic * self.conversion_rate
        
        # Chiffre d'affaires
        turnover = nb_commands * self.average_basket
        
        # Coûts variables
        purchase_cost = turnover * self.purchase_price_rate
        shipping_costs = nb_commands * self.shipping_cost_per_order
        payment_fees = (turnover * self.shopify_commission_rate) + (nb_commands * self.shopify_fixed_commission)
        
        # Coûts fixes
        fixed_costs = (
            self.shopify_subscription + 
            self.seo_consultant + 
            self.domain_name + 
            self.initial_advertising
        )
        
        # Marges
        gross_margin = turnover - purchase_cost - shipping_costs - payment_fees
        net_margin = gross_margin - fixed_costs
        
        return {
            'Nombre de commandes': nb_commands,
            'Chiffre d\'affaires': turnover,
            'Coût d\'achat': purchase_cost,
            'Frais de livraison': shipping_costs,
            'Commissions': payment_fees,
            'Coûts fixes': fixed_costs,
            'Marge brute': gross_margin,
            'Marge nette': net_margin
        }

def main():
    st.title("📊 Simulateur de Modèle Économique")
    
    st.sidebar.header("Hypothèses Initiales")
    
    # Input parameters
    initial_traffic = st.sidebar.number_input("Trafic mensuel initial", min_value=100, value=1000)
    conversion_rate = st.sidebar.number_input("Taux de conversion (%)", min_value=0.01, max_value=1.0, value=0.02, format="%.2f")
    average_basket = st.sidebar.number_input("Panier moyen (€)", min_value=10, value=80)
    initial_capital = st.sidebar.number_input("Capital initial (€)", min_value=1000, value=10000)
    initial_stock = st.sidebar.number_input("Stock initial (€)", min_value=1000, value=3000)
    purchase_price_rate = st.sidebar.number_input("Taux de prix d'achat (%)", min_value=0.1, max_value=1.0, value=0.4, format="%.2f")
    
    # Instantiate the model
    model = BusinessModelProjection(
        initial_traffic=initial_traffic,
        conversion_rate=conversion_rate,
        average_basket=average_basket,
        initial_capital=initial_capital,
        initial_stock=initial_stock,
        purchase_price_rate=purchase_price_rate
    )
    
    # Calculate projections
    results = model.calculate_monthly_projections()
    
    # Display results
    st.header("Résultats des Projections")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Résultats Financiers")
        for key, value in results.items():
            st.metric(key, f"{value:.2f} €")
    
    with col2:
        st.subheader("Graphique des Revenus")
        fig = go.Figure(data=[
            go.Bar(name='Revenus', x=['Chiffre d\'affaires'], y=[results['Chiffre d\'affaires']]),
            go.Bar(name='Coûts', x=['Chiffre d\'affaires'], y=[results['Coût d\'achat'] + results['Frais de livraison'] + results['Commissions'] + results['Coûts fixes']])
        ])
        fig.update_layout(barmode='group')
        st.plotly_chart(fig)

if __name__ == "__main__":
    main()

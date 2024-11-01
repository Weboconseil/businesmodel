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
                 monthly_traffic_growth=0.05):  # Ajout d'un taux de croissance mensuel
        
        self.initial_traffic = initial_traffic
        self.conversion_rate = conversion_rate
        self.average_basket = average_basket
        self.initial_capital = initial_capital
        self.initial_stock = initial_stock
        self.purchase_price_rate = purchase_price_rate
        self.monthly_traffic_growth = monthly_traffic_growth
        
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
        monthly_data = []
        current_traffic = self.initial_traffic

        for month in range(1, 13):
            # Calcul du trafic avec croissance
            if month > 1:
                current_traffic = current_traffic * (1 + self.monthly_traffic_growth)
            
            # Nombre de commandes
            nb_commands = current_traffic * self.conversion_rate
            
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
            
            monthly_data.append({
                'Mois': f'M{month}',
                'Trafic': current_traffic,
                'Nombre de commandes': nb_commands,
                'Chiffre d\'affaires': turnover,
                'Coût d\'achat': purchase_cost,
                'Frais de livraison': shipping_costs,
                'Commissions': payment_fees,
                'Coûts fixes': fixed_costs,
                'Marge brute': gross_margin,
                'Marge nette': net_margin
            })
        
        return pd.DataFrame(monthly_data)

    def calculate_annual_projections(self):
        monthly_df = self.calculate_monthly_data()
        
        annual_results = {
            'Chiffre d\'affaires': monthly_df['Chiffre d\'affaires'].sum(),
            'Nombre de commandes': monthly_df['Nombre de commandes'].sum(),
            'Coût d\'achat': monthly_df['Coût d\'achat'].sum(),
            'Frais de livraison': monthly_df['Frais de livraison'].sum(),
            'Commissions': monthly_df['Commissions'].sum(),
            'Coûts fixes': monthly_df['Coûts fixes'].sum(),
            'Marge brute': monthly_df['Marge brute'].sum(),
            'Marge nette': monthly_df['Marge nette'].sum()
        }
        
        # Ajout des ratios
        annual_results['Taux de marge brute'] = (annual_results['Marge brute'] / annual_results['Chiffre d\'affaires']) * 100
        annual_results['Taux de marge nette'] = (annual_results['Marge nette'] / annual_results['Chiffre d\'affaires']) * 100
        
        return annual_results, monthly_df

def main():
    st.title("📊 Simulateur de Modèle Économique Annuel")
    
    st.sidebar.header("Hypothèses Initiales")
    
    # Input parameters
    initial_traffic = st.sidebar.number_input("Trafic mensuel initial", min_value=100, value=1000)
    conversion_rate = st.sidebar.number_input("Taux de conversion (%)", min_value=0.01, max_value=1.0, value=0.02, format="%.2f")
    average_basket = st.sidebar.number_input("Panier moyen (€)", min_value=10, value=80)
    initial_capital = st.sidebar.number_input("Capital initial (€)", min_value=1000, value=10000)
    initial_stock = st.sidebar.number_input("Stock initial (€)", min_value=1000, value=3000)
    purchase_price_rate = st.sidebar.number_input("Taux de prix d'achat (%)", min_value=0.1, max_value=1.0, value=0.4, format="%.2f")
    monthly_traffic_growth = st.sidebar.number_input("Croissance mensuelle du trafic (%)", min_value=0.0, max_value=1.0, value=0.05, format="%.2f")
    
    # Instantiate the model
    model = BusinessModelProjection(
        initial_traffic=initial_traffic,
        conversion_rate=conversion_rate,
        average_basket=average_basket,
        initial_capital=initial_capital,
        initial_stock=initial_stock,
        purchase_price_rate=purchase_price_rate,
        monthly_traffic_growth=monthly_traffic_growth
    )
    
    # Calculate projections
    annual_results, monthly_df = model.calculate_annual_projections()
    
    # Display annual results
    st.header("Résultats Annuels")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Chiffre d'affaires annuel", f"{annual_results['Chiffre d\'affaires']:,.2f} €")
        st.metric("Nombre de commandes", f"{annual_results['Nombre de commandes']:,.0f}")
        st.metric("Marge brute", f"{annual_results['Marge brute']:,.2f} €")
    
    with col2:
        st.metric("Coûts totaux", f"{(annual_results['Coût d\'achat'] + annual_results['Frais de livraison'] + annual_results['Commissions'] + annual_results['Coûts fixes']):,.2f} €")
        st.metric("Taux de marge brute", f"{annual_results['Taux de marge brute']:.1f}%")
        st.metric("Marge nette", f"{annual_results['Marge nette']:,.2f} €")
    
    with col3:
        st.metric("Coûts fixes annuels", f"{annual_results['Coûts fixes']:,.2f} €")
        st.metric("Coûts variables", f"{(annual_results['Coût d\'achat'] + annual_results['Frais de livraison'] + annual_results['Commissions']):,.2f} €")
        st.metric("Taux de marge nette", f"{annual_results['Taux de marge nette']:.1f}%")

    # Graphiques
    st.header("Évolution Mensuelle")
    
    # Graphique 1: Évolution du CA et des marges
    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(x=monthly_df['Mois'], y=monthly_df['Chiffre d\'affaires'], name='CA', mode='lines+markers'))
    fig1.add_trace(go.Scatter(x=monthly_df['Mois'], y=monthly_df['Marge brute'], name='Marge brute', mode='lines+markers'))
    fig1.add_trace(go.Scatter(x=monthly_df['Mois'], y=monthly_df['Marge nette'], name='Marge nette', mode='lines+markers'))
    fig1.update_layout(title='Évolution du CA et des marges', xaxis_title='Mois', yaxis_title='Euros')
    st.plotly_chart(fig1)
    
    # Graphique 2: Répartition des coûts
    costs_data = {
        'Type': ['Coût d\'achat', 'Frais de livraison', 'Commissions', 'Coûts fixes'],
        'Montant': [
            annual_results['Coût d\'achat'],
            annual_results['Frais de livraison'],
            annual_results['Commissions'],
            annual_results['Coûts fixes']
        ]
    }
    fig2 = px.pie(costs_data, values='Montant', names='Type', title='Répartition des coûts annuels')
    st.plotly_chart(fig2)
    
    # Affichage des données mensuelles détaillées
    st.header("Détail Mensuel")
    st.dataframe(monthly_df.style.format({
        'Trafic': '{:,.0f}',
        'Nombre de commandes': '{:,.0f}',
        'Chiffre d\'affaires': '{:,.2f} €',
        'Coût d\'achat': '{:,.2f} €',
        'Frais de livraison': '{:,.2f} €',
        'Commissions': '{:,.2f} €',
        'Coûts fixes': '{:,.2f} €',
        'Marge brute': '{:,.2f} €',
        'Marge nette': '{:,.2f} €'
    }))

if __name__ == "__main__":
    main()

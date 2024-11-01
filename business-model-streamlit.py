import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

def format_fr(value, decimal=2):
    """
    Formate un nombre selon les conventions françaises :
    - Virgule comme séparateur décimal
    - Espace comme séparateur des milliers
    """
    if isinstance(value, (int, float)):
        if decimal == 0:
            return f"{value:,.0f}".replace(",", " ").replace(".", ",")
        return f"{value:,.{decimal}f}".replace(",", " ").replace(".", ",")
    return value

class BusinessModelProjection:
    def __init__(self, 
                 initial_traffic=1000, 
                 conversion_rate=0.02, 
                 average_basket=80, 
                 initial_capital=10000, 
                 initial_stock=3000, 
                 purchase_price_rate=0.4,
                 monthly_traffic_growth=0.05,
                 tax_rate=0.20):  # Ajout du taux d'imposition
        
        self.initial_traffic = initial_traffic
        self.conversion_rate = conversion_rate
        self.average_basket = average_basket
        self.initial_capital = initial_capital
        self.initial_stock = initial_stock
        self.purchase_price_rate = purchase_price_rate
        self.monthly_traffic_growth = monthly_traffic_growth
        self.tax_rate = tax_rate
        
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
            
            # Résultats
            gross_margin = turnover - purchase_cost - shipping_costs - payment_fees
            operating_income = gross_margin - fixed_costs
            net_income = operating_income * (1 - self.tax_rate)
            
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
                'Résultat d\'exploitation': operating_income,
                'Résultat net': net_income
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
            'Résultat d\'exploitation': monthly_df['Résultat d\'exploitation'].sum(),
            'Résultat net': monthly_df['Résultat net'].sum()
        }
        
        # Ajout des ratios
        annual_results['Taux de marge brute'] = (annual_results['Marge brute'] / annual_results['Chiffre d\'affaires']) * 100
        annual_results['Taux de rentabilité d\'exploitation'] = (annual_results['Résultat d\'exploitation'] / annual_results['Chiffre d\'affaires']) * 100
        annual_results['Taux de rentabilité nette'] = (annual_results['Résultat net'] / annual_results['Chiffre d\'affaires']) * 100
        
        return annual_results, monthly_df

    def calculate_break_even(self):
        """Calcule le seuil de rentabilité"""
        # Coûts fixes annuels
        annual_fixed_costs = (
            self.shopify_subscription + 
            self.seo_consultant + 
            self.domain_name + 
            self.initial_advertising
        ) * 12
        
        # Calcul des coûts variables unitaires
        unit_purchase_cost = self.average_basket * self.purchase_price_rate
        unit_shipping_cost = self.shipping_cost_per_order
        unit_commission = (self.average_basket * self.shopify_commission_rate) + self.shopify_fixed_commission
        total_unit_variable_cost = unit_purchase_cost + unit_shipping_cost + unit_commission
        
        # Calcul de la marge unitaire
        unit_margin = self.average_basket - total_unit_variable_cost
        
        # Calcul du seuil de rentabilité en nombre de commandes
        break_even_units = annual_fixed_costs / unit_margin
        
        # Calcul du chiffre d'affaires au point mort
        break_even_revenue = break_even_units * self.average_basket
        
        # Calcul du nombre de mois pour atteindre le point mort
        monthly_orders = self.initial_traffic * self.conversion_rate
        months_to_break_even = break_even_units / (monthly_orders * 12)
        
        return {
            'Seuil de rentabilité (nb commandes)': break_even_units,
            'Chiffre d\'affaires au point mort': break_even_revenue,
            'Marge unitaire': unit_margin,
            'Coûts variables unitaires': total_unit_variable_cost,
            'Coûts fixes annuels': annual_fixed_costs,
            'Mois pour atteindre le point mort': months_to_break_even
        }


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
    tax_rate = st.sidebar.number_input("Taux d'imposition (%)", min_value=0.0, max_value=1.0, value=0.20, format="%.2f")
    
    # Instantiate the model
    model = BusinessModelProjection(
        initial_traffic=initial_traffic,
        conversion_rate=conversion_rate,
        average_basket=average_basket,
        initial_capital=initial_capital,
        initial_stock=initial_stock,
        purchase_price_rate=purchase_price_rate,
        monthly_traffic_growth=monthly_traffic_growth,
        tax_rate=tax_rate
    )
    
    # Calculate projections
    annual_results, monthly_df = model.calculate_annual_projections()
    
    # Display annual results
    st.header("Résultats Annuels")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Chiffre d'affaires annuel", f"{format_fr(annual_results['Chiffre d\'affaires'])} €")
        st.metric("Nombre de commandes", f"{format_fr(annual_results['Nombre de commandes'], 0)}")
        st.metric("Marge brute", f"{format_fr(annual_results['Marge brute'])} €")
    
    with col2:
        total_costs = (annual_results['Coût d\'achat'] + 
                      annual_results['Frais de livraison'] + 
                      annual_results['Commissions'] + 
                      annual_results['Coûts fixes'])
        st.metric("Coûts totaux", f"{format_fr(total_costs)} €")
        st.metric("Résultat d'exploitation", f"{format_fr(annual_results['Résultat d\'exploitation'])} €")
        st.metric("Résultat net", f"{format_fr(annual_results['Résultat net'])} €")
    
    with col3:
        st.metric("Taux de marge brute", f"{format_fr(annual_results['Taux de marge brute'], 1)}%")
        st.metric("Taux de rentabilité d'exploitation", f"{format_fr(annual_results['Taux de rentabilité d\'exploitation'], 1)}%")
        st.metric("Taux de rentabilité nette", f"{format_fr(annual_results['Taux de rentabilité nette'], 1)}%")


    # Graphiques
    st.header("Évolution Mensuelle")
    
    # Graphique 1: Évolution du CA et des résultats
    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(x=monthly_df['Mois'], y=monthly_df['Chiffre d\'affaires'], name='CA', mode='lines+markers'))
    fig1.add_trace(go.Scatter(x=monthly_df['Mois'], y=monthly_df['Résultat d\'exploitation'], name='Résultat d\'exploitation', mode='lines+markers'))
    fig1.add_trace(go.Scatter(x=monthly_df['Mois'], y=monthly_df['Résultat net'], name='Résultat net', mode='lines+markers'))
    fig1.update_layout(title='Évolution du CA et des résultats', xaxis_title='Mois', yaxis_title='Euros')
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
    formatted_df = monthly_df.style.format({
        'Trafic': lambda x: format_fr(x, 0),
        'Nombre de commandes': lambda x: format_fr(x, 0),
        'Chiffre d\'affaires': lambda x: f"{format_fr(x)} €",
        'Coût d\'achat': lambda x: f"{format_fr(x)} €",
        'Frais de livraison': lambda x: f"{format_fr(x)} €",
        'Commissions': lambda x: f"{format_fr(x)} €",
        'Coûts fixes': lambda x: f"{format_fr(x)} €",
        'Marge brute': lambda x: f"{format_fr(x)} €",
        'Résultat d\'exploitation': lambda x: f"{format_fr(x)} €",
        'Résultat net': lambda x: f"{format_fr(x)} €"
    })
    st.dataframe(formatted_df)

    st.header("Analyse du Seuil de Rentabilité")
    
    # Calcul du seuil de rentabilité
    break_even_data = model.calculate_break_even()
    
    # Affichage des métriques du seuil de rentabilité
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Nombre de commandes au point mort", 
                 f"{format_fr(break_even_data['Seuil de rentabilité (nb commandes)'], 0)}")
        st.metric("CA au point mort", 
                 f"{format_fr(break_even_data['Chiffre d\'affaires au point mort'])} €")
        st.metric("Marge unitaire", 
                 f"{format_fr(break_even_data['Marge unitaire'])} €")
    
    with col2:
        st.metric("Coûts variables unitaires", 
                 f"{format_fr(break_even_data['Coûts variables unitaires'])} €")
        st.metric("Coûts fixes annuels", 
                 f"{format_fr(break_even_data['Coûts fixes annuels'])} €")
        st.metric("Mois pour atteindre le point mort", 
                 f"{int(break_even_data['Mois pour atteindre le point mort'])} mois")


    # Graphique du point mort
    order_range = np.linspace(0, break_even_data['Seuil de rentabilité (nb commandes)'] * 2, 100)
    revenue = order_range * model.average_basket
    total_variable_costs = order_range * break_even_data['Coûts variables unitaires']
    total_costs = total_variable_costs + break_even_data['Coûts fixes annuels']
    
    fig_break_even = go.Figure()
    fig_break_even.add_trace(go.Scatter(
        x=order_range, 
        y=revenue,
        name='Chiffre d\'affaires',
        line=dict(color='green')
    ))
    fig_break_even.add_trace(go.Scatter(
        x=order_range, 
        y=total_costs,
        name='Coûts totaux',
        line=dict(color='red')
    ))
    fig_break_even.add_trace(go.Scatter(
        x=order_range,
        y=[break_even_data['Coûts fixes annuels']] * len(order_range),
        name='Coûts fixes',
        line=dict(color='blue', dash='dash')
    ))
    
    # Ajout du point d'intersection
    fig_break_even.add_trace(go.Scatter(
        x=[break_even_data['Seuil de rentabilité (nb commandes)']],
        y=[break_even_data['Chiffre d\'affaires au point mort']],
        name='Point mort',
        mode='markers',
        marker=dict(size=12, symbol='star', color='yellow', line=dict(color='black', width=2))
    ))
    
# Mise à jour du graphique du point mort
    fig_break_even.update_layout(
        annotations=[
            dict(
                x=break_even_data['Seuil de rentabilité (nb commandes)'],
                y=break_even_data['Chiffre d\'affaires au point mort'],
                text=f"Point mort:<br>{format_fr(break_even_data['Seuil de rentabilité (nb commandes)'], 0)} commandes<br>{format_fr(break_even_data['Chiffre d\'affaires au point mort'])} €",
                showarrow=True,
                arrowhead=1
            )
        ]
    )
# Mise à jour des axes des graphiques pour utiliser le format français
    fig1.update_layout(
        yaxis=dict(
            tickformat=",",
            separatethousands=True
        )
    )
    
    fig_break_even.update_layout(
        yaxis=dict(
            tickformat=",",
            separatethousands=True
        )
    )
    
    st.plotly_chart(fig_break_even)

    # Affichage de conseils d'interprétation
    st.subheader("Interprétation")
    st.write("""
    - Le seuil de rentabilité est le point où le chiffre d'affaires couvre exactement tous les coûts (fixes et variables)
    - En dessous de ce point, l'entreprise est en perte
    - Au-dessus de ce point, l'entreprise dégage du profit
    - Plus la marge unitaire est élevée, plus vite le point mort est atteint
    """)


if __name__ == "__main__":
    main()

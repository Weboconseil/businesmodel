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

    def calculate_balance_sheet(self):
        """Calcule le bilan prévisionnel à la fin de l'année."""
        # Récupération des données nécessaires
        cash_flow_df = self.calculate_cash_flow()
        annual_results, monthly_df = self.calculate_annual_projections()
        
        # ACTIF
        actif = {
            'Actif immobilisé': {
                'Immobilisations incorporelles': 0,  # Site web amorti sur l'année
                'Immobilisations corporelles': 0,    # Pas d'immobilisations corporelles dans ce modèle
            },
            'Actif circulant': {
                'Stocks': self.initial_stock,  # Stock final
                'Créances clients': monthly_df['Chiffre d\'affaires'].iloc[-1] * (self.payment_delay_clients / 30),  # Créances du dernier mois
                'Trésorerie': cash_flow_df['Solde de trésorerie'].iloc[-1]
            }
        }
        
        # PASSIF
        passif = {
            'Capitaux propres': {
                'Capital social': self.initial_capital,
                'Résultat de l\'exercice': annual_results['Résultat net']
            },
            'Dettes': {
                'Dettes fournisseurs': monthly_df['Coût d\'achat'].iloc[-1] * (self.payment_delay_suppliers / 30),  # Dettes du dernier mois
                'Dettes fiscales': annual_results['Résultat d\'exploitation'] * self.tax_rate  # Impôts à payer
            }
        }
        
        # Calcul des totaux
        actif['Total actif immobilisé'] = sum(actif['Actif immobilisé'].values())
        actif['Total actif circulant'] = sum(actif['Actif circulant'].values())
        actif['Total actif'] = actif['Total actif immobilisé'] + actif['Total actif circulant']
        
        passif['Total capitaux propres'] = sum(passif['Capitaux propres'].values())
        passif['Total dettes'] = sum(passif['Dettes'].values())
        passif['Total passif'] = passif['Total capitaux propres'] + passif['Total dettes']
        
        return actif, passif


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
        st.metric("Chiffre d'affaires annuel", f"{annual_results['Chiffre d\'affaires']:,.2f} €")
        st.metric("Nombre de commandes", f"{annual_results['Nombre de commandes']:,.0f}")
        st.metric("Marge brute", f"{annual_results['Marge brute']:,.2f} €")
    
    with col2:
        st.metric("Coûts totaux", f"{(annual_results['Coût d\'achat'] + annual_results['Frais de livraison'] + annual_results['Commissions'] + annual_results['Coûts fixes']):,.2f} €")
        st.metric("Résultat d'exploitation", f"{annual_results['Résultat d\'exploitation']:,.2f} €")
        st.metric("Résultat net", f"{annual_results['Résultat net']:,.2f} €")
    
    with col3:
        st.metric("Taux de marge brute", f"{annual_results['Taux de marge brute']:.1f}%")
        st.metric("Taux de rentabilité d'exploitation", f"{annual_results['Taux de rentabilité d\'exploitation']:.1f}%")
        st.metric("Taux de rentabilité nette", f"{annual_results['Taux de rentabilité nette']:.1f}%")

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
    st.dataframe(monthly_df.style.format({
        'Trafic': '{:,.0f}',
        'Nombre de commandes': '{:,.0f}',
        'Chiffre d\'affaires': '{:,.2f} €',
        'Coût d\'achat': '{:,.2f} €',
        'Frais de livraison': '{:,.2f} €',
        'Commissions': '{:,.2f} €',
        'Coûts fixes': '{:,.2f} €',
        'Marge brute': '{:,.2f} €',
        'Résultat d\'exploitation': '{:,.2f} €',
        'Résultat net': '{:,.2f} €'
    }))

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

# Nouvelle section pour le bilan
    st.header("Bilan Prévisionnel")
    
    # Calcul du bilan
    actif, passif = model.calculate_balance_sheet()
    
    # Affichage du bilan en deux colonnes
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("ACTIF")
        
        st.write("Actif immobilisé:")
        for key, value in actif['Actif immobilisé'].items():
            st.write(f"{key}: {value:,.2f} €")
        st.write(f"**Total actif immobilisé: {actif['Total actif immobilisé']:,.2f} €**")
        
        st.write("Actif circulant:")
        for key, value in actif['Actif circulant'].items():
            st.write(f"{key}: {value:,.2f} €")
        st.write(f"**Total actif circulant: {actif['Total actif circulant']:,.2f} €**")
        
        st.write(f"**TOTAL ACTIF: {actif['Total actif']:,.2f} €**")
    
    with col2:
        st.subheader("PASSIF")
        
        st.write("Capitaux propres:")
        for key, value in passif['Capitaux propres'].items():
            st.write(f"{key}: {value:,.2f} €")
        st.write(f"**Total capitaux propres: {passif['Total capitaux propres']:,.2f} €**")
        
        st.write("Dettes:")
        for key, value in passif['Dettes'].items():
            st.write(f"{key}: {value:,.2f} €")
        st.write(f"**Total dettes: {passif['Total dettes']:,.2f} €**")
        
        st.write(f"**TOTAL PASSIF: {passif['Total passif']:,.2f} €**")
    
    # Graphique de répartition du bilan
    st.subheader("Répartition du Bilan")
    
    # Préparation des données pour les graphiques
    actif_data = {
        'Catégorie': ['Actif immobilisé', 'Actif circulant'],
        'Montant': [actif['Total actif immobilisé'], actif['Total actif circulant']]
    }
    
    passif_data = {
        'Catégorie': ['Capitaux propres', 'Dettes'],
        'Montant': [passif['Total capitaux propres'], passif['Total dettes']]
    }
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig_actif = px.pie(actif_data, values='Montant', names='Catégorie', 
                          title='Répartition de l\'actif')
        st.plotly_chart(fig_actif)
    
    with col2:
        fig_passif = px.pie(passif_data, values='Montant', names='Catégorie', 
                           title='Répartition du passif')
        st.plotly_chart(fig_passif)


if __name__ == "__main__":
    main()

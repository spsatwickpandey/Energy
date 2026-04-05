import pandas as pd
from datetime import datetime
from electricity_prediction_model import ElectricityPredictor

def get_current_season():
    month = datetime.now().month
    if month in [12, 1, 2]:
        return 'Winter'
    elif month in [3, 4, 5]:
        return 'Summer'
    elif month in [6, 7, 8]:
        return 'Monsoon'
    else:
        return 'Autumn'

def get_user_input():
    print("\nElectricity Consumption Predictor")
    print("=================================")
    
    # Get family details
    family_members = int(input("\nEnter total number of family members: "))
    male = int(input("Enter number of male members: "))
    female = int(input("Enter number of female members: "))
    children = int(input("Enter number of children: "))
    
    # Get household type
    print("\nHousehold Types: bachelor, couple, nuclear, joint")
    household_type = input("Enter household type: ").lower()
    
    appliances = []
    while True:
        print("\nAvailable Appliance Types:")
        print("1. LED Bulb")
        print("2. Ceiling Fan")
        print("3. Air Conditioner")
        print("4. Refrigerator")
        print("5. Television")
        print("6. Washing Machine")
        print("7. Water Heater")
        print("8. Room Heater")
        print("9. Water Pump")
        print("10. Microwave Oven")
        print("0. Finish adding appliances")
        
        choice = input("\nEnter choice (0-10): ")
        if choice == '0':
            break
            
        appliance_mapping = {
            '1': 'LED Bulb',
            '2': 'Ceiling Fan',
            '3': 'Air Conditioner',
            '4': 'Refrigerator',
            '5': 'Television',
            '6': 'Washing Machine',
            '7': 'Water Heater',
            '8': 'Room Heater',
            '9': 'Water Pump',
            '10': 'Microwave Oven'
        }
        
        appliance_type = appliance_mapping[choice]
        brand = input(f"Enter brand for {appliance_type}: ")
        quantity = int(input("Enter quantity: "))
        power_rating = float(input("Enter power rating (in watts): "))
        energy_star = int(input("Enter energy star rating (2-5): "))
        
        # Get usage hours for each unit
        total_hours = 0
        for i in range(quantity):
            hours = float(input(f"Enter daily usage hours for unit {i+1}: "))
            total_hours += hours
        avg_hours = total_hours / quantity
        
        appliance = {
            'family_members': family_members,
            'male': male,
            'female': female,
            'children': children,
            'household_type': household_type,
            'appliance_type': appliance_type,
            'brand': brand,
            'power_rating_watts': power_rating,
            'daily_usage_hours': avg_hours,
            'quantity': quantity,
            'energy_star_rating': energy_star,
            'season': get_current_season()
        }
        appliances.append(appliance)
    
    return appliances

def main():
    # Load the trained model
    predictor = ElectricityPredictor.load_model('electricity_predictor.joblib')
    
    # Get user input
    appliances = get_user_input()
    
    # Make prediction for each appliance and sum up
    total_consumption = 0
    for appliance in appliances:
        consumption = predictor.predict_consumption(appliance)
        total_consumption += consumption
        
    print(f"\nPredicted monthly electricity consumption: {total_consumption:.2f} kWh")

if __name__ == "__main__":
    main() 
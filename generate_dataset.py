import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def get_power_rating(appliance_type, brand, model):
    specs = APPLIANCE_SPECS[appliance_type]
    try:
        # Try to extract number before 'W' from model name
        power = int(''.join(filter(str.isdigit, model.split('W')[0])))
        # Ensure power is within the specified range
        return min(max(power, specs['power_range'][0]), specs['power_range'][1])
    except:
        # If extraction fails, use range from specs
        return np.random.randint(*specs['power_range'])

# Define appliance specifications with real brands and models
APPLIANCE_SPECS = {
    'LED Bulb': {
        'brands': {
            'Philips': ['9W Essential', '10W Master LED', '12W SceneSwitch'],
            'Havells': ['8W Adore', '10W Lumeno', '12W Bright Bio'],
            'Wipro': ['9W Garnet', '10W Tejas', '12W Prima'],
            'Bajaj': ['9W LEDZ', '10W IVORA', '12W LEDZ Pro'],
            'Syska': ['9W SSK-PAG', '10W SSK-RDL', '12W SSK-BLS']
        },
        'power_range': [7, 15],  # Most common LED bulb ratings
        'typical_hours': [4, 6, 8, 10],  # Realistic daily usage
        'max_quantity': 8  # Maximum bulbs per household
    },
    'Ceiling Fan': {
        'brands': {
            'Havells': ['Andria 62W', 'Leganza 65W', 'Stealth Air 72W'],
            'Orient': ['Ecotech 50W', 'Electric 60W', 'PSPO 65W'],
            'Crompton': ['HS Plus 55W', 'Energion 60W', 'Avancer 65W'],
            'Usha': ['Striker 60W', 'Technix 65W', 'Aerostyle 70W'],
            'Bajaj': ['Regal Gold 65W', 'Maxima 70W', 'Elite 75W']
        },
        'power_range': [50, 80],  # Standard ceiling fan ratings
        'typical_hours': [8, 12, 16, 20],  # Based on climate and season
        'max_quantity': 5  # Maximum fans per household
    },
    'Air Conditioner': {
        'brands': {
            'Daikin': ['1.5T 3Star FTL50', '1.5T 5Star RZF50', '2T Inverter FTKF65'],
            'Voltas': ['1.5T 183V Inverter', '1.5T 185V SAC', '2T 245V Inverter'],
            'Blue Star': ['1.5T 3Star IC318', '1.5T 5Star IC518', '2T IC724'],
            'Hitachi': ['1.5T ZUNOH 3Star', '1.5T RAPG518 5Star', '2T SUGOI RSB524'],
            'LG': ['1.5T MS-Q18YNZA', '1.5T PS-Q18YNZA', '2T RS-Q24YNZA']
        },
        'power_range': [1200, 2000],  # 1.5-2 ton AC power consumption
        'typical_hours': [4, 6, 8, 10],  # Realistic AC usage
        'max_quantity': 3  # Maximum ACs per household
    },
    'Refrigerator': {
        'brands': {
            'LG': ['260L GL-I292RPZL', '308L GL-T322RPZU', '360L GL-T402JPZU'],
            'Samsung': ['253L RT28T3922R8', '324L RT34T4542S8', '386L RT39T5C3EDX'],
            'Whirlpool': ['240L 265 IMPRO', '292L MAGICOOL', '340L INTELLIFRESH'],
            'Godrej': ['236L RD EDGE DUO', '299L RD EPRO', '343L RB CONNEXI'],
            'Haier': ['256L HRD-2706BS', '320L HRB-3404BS', '345L HRB-3654PKG']
        },
        'power_range': [350, 780],  # Actual fridge power consumption
        'typical_hours': [24],  # Always running
        'max_quantity': 2  # Maximum fridges per household
    },
    'Television': {
        'brands': {
            'Sony': ['43X74K', '55X74K', '65X74K'],
            'Samsung': ['43AU7700', '55AU7700', '65AU7700'],
            'LG': ['43UP7550', '55UP7550', '65UP7550'],
            'OnePlus': ['43Y1S Pro', '55Y1S Pro', '65Y1S Pro'],
            'Mi': ['43 5A', '55 5A', '65 5A']
        },
        'power_range': [50, 180],  # LED TV power consumption
        'typical_hours': [3, 4, 6, 8],  # Typical TV watching hours
        'max_quantity': 3  # Maximum TVs per household
    },
    'Washing Machine': {
        'brands': {
            'LG': ['6.5kg FHM1065', '7kg FHM1207', '8kg FHM1408'],
            'Samsung': ['6.5kg WA65A4002VS', '7kg WA70A4002VS', '8kg WA80A4002VS'],
            'Whirlpool': ['6.5kg WhiteMagic', '7kg WhiteMagic Elite', '8kg WhiteMagic Ultra'],
            'IFB': ['6.5kg Elena ZX', '7kg Neo Diva', '8kg Senator Plus'],
            'Bosch': ['6.5kg WOE654W0IN', '7kg WAJ2416WIN', '8kg WAJ2426WIN']
        },
        'power_range': [300, 500],  # Power consumption during wash cycle
        'typical_hours': [1, 1.5, 2, 2.5],  # Typical wash cycle duration
        'max_quantity': 1  # Maximum washing machines per household
    },
    'Water Heater': {
        'brands': {
            'Havells': ['10L Adonia', '15L Monza', '25L Instanio'],
            'Bajaj': ['10L Flora', '15L Juvel', '25L Majesty'],
            'AO Smith': ['15L HSE-VAS', '25L HAS-VAS', '35L HAS-VAS'],
            'Racold': ['10L Altro', '15L Eterno', '25L Omnis'],
            'V-Guard': ['10L Sprinhot', '15L Divino', '25L Pebble']
        },
        'power_range': [1500, 2500],  # Typical geyser wattage
        'typical_hours': [1, 1.5, 2, 3],  # Daily usage hours
        'max_quantity': 2  # Maximum water heaters per household
    },
    'Room Heater': {
        'brands': {
            'Bajaj': ['Majesty RH 9F', 'Majesty RX11', 'Majesty RX14'],
            'Havells': ['Cista 1500W', 'Comforter 2000W', 'Calido 2400W'],
            'Orient': ['Comfort HC2000D', 'Winter HC1500D', 'Cozy HC1200D'],
            'Usha': ['Heat Convector 812T', 'Quartz 3002', 'Fan Heater 3620'],
            'Morphy Richards': ['OFR 09', 'OFR 11F', 'Room Heater 2000W']
        },
        'power_range': [1000, 2400],  # Heater wattage
        'typical_hours': [2, 3, 4, 6],  # Winter usage hours
        'max_quantity': 2  # Maximum heaters per household
    },
    'Water Pump': {
        'brands': {
            'Crompton': ['0.5HP Mini Champ', '1HP Super Champ', '1.5HP Champ'],
            'Kirloskar': ['0.5HP Tiny', '1HP Mega', '1.5HP Ultra'],
            'CRI': ['0.5HP JWEL', '1HP JWEL Plus', '1.5HP JWEL Max'],
            'V-Guard': ['0.5HP Revo', '1HP Revo Plus', '1.5HP Revo Max'],
            'KSB': ['0.5HP Peribloc', '1HP Peribloc Plus', '1.5HP Peribloc Max']
        },
        'power_range': [370, 1100],  # Power in watts (0.5HP to 1.5HP)
        'typical_hours': [0.5, 1, 1.5, 2],  # Daily pumping duration
        'max_quantity': 1  # Maximum pumps per household
    },
    'Microwave Oven': {
        'brands': {
            'LG': ['20L Solo MS2043DB', '28L Conv MC2846BG', '32L Conv MC3286BRUM'],
            'Samsung': ['20L Solo MS23F301TAK', '28L Conv CE1041DSB2', '32L Conv MC32K7056QT'],
            'IFB': ['17L Solo 17PM-MEC1', '23L Conv 23BC4', '30L Conv 30BRC2'],
            'Panasonic': ['20L Solo NN-ST26JMFDG', '27L Conv NN-CT645B', '32L Conv NN-CT66HBFDG'],
            'Whirlpool': ['20L Solo MWX 201', '25L Conv MWX 25BC', '30L Conv MWX 30AC']
        },
        'power_range': [700, 1400],  # Microwave wattage
        'typical_hours': [0.25, 0.5, 0.75, 1],  # Daily usage in hours
        'max_quantity': 1  # Maximum microwaves per household
    }
}

def generate_family_demographics():
    """Generate logical family demographics"""
    # First decide household type
    household_type = np.random.choice(['bachelor', 'couple', 'nuclear', 'joint'], p=[0.15, 0.25, 0.40, 0.20])
    
    if household_type == 'bachelor':
        # Single person
        family_members = 1
        gender = np.random.choice(['male', 'female'], p=[0.6, 0.4])
        male = 1 if gender == 'male' else 0
        female = 1 if gender == 'female' else 0
        children = 0
        
    elif household_type == 'couple':
        # Married couple without children
        family_members = 2
        male = 1
        female = 1
        children = 0
        
    elif household_type == 'nuclear':
        # Parents with children (2-5 members)
        children = np.random.randint(1, 4)  # 1-3 children
        male = 1  # Father
        female = 1  # Mother
        family_members = male + female + children
        
    else:  # joint family
        # Extended family (4-7 members)
        family_members = np.random.randint(4, 8)
        
        # First ensure minimum adults (at least 2)
        min_adults = 2
        max_children = family_members - min_adults
        children = np.random.randint(0, max_children + 1)
        
        # Calculate remaining members for adults
        remaining_adults = family_members - children
        
        # Distribute remaining adults between male and female
        # Ensure at least one of each
        male = np.random.randint(1, remaining_adults)
        female = remaining_adults - male

    # Verify totals
    assert male + female + children == family_members, f"Member mismatch: {male}+{female}+{children}!={family_members}"
    
    return {
        'family_members': family_members,
        'male': male,
        'female': female,
        'children': children,
        'household_type': household_type
    }

def generate_appliance_data(num_samples=1000):
    data = []
    
    for _ in range(num_samples):
        # Generate logical family demographics
        family = generate_family_demographics()
        
        # Generate seasonal data
        date = datetime.now() - timedelta(days=np.random.randint(0, 365))
        season = get_season(date)
        
        household_appliances = []
        
        # Adjust appliance quantities based on household size and type
        for appliance_type, specs in APPLIANCE_SPECS.items():
            max_qty = specs['max_quantity']
            
            # Adjust minimum quantities based on household type and size
            if appliance_type in ['LED Bulb', 'Ceiling Fan']:
                if family['household_type'] == 'bachelor':
                    min_qty = 2  # Minimum 2 bulbs/fans for bachelor
                else:
                    min_qty = max(2, family['family_members'] // 2)
            else:
                if family['household_type'] == 'bachelor' and appliance_type in ['Washing Machine', 'Microwave Oven']:
                    min_qty = np.random.choice([0, 1], p=[0.3, 0.7])  # 70% chance of having these appliances
                else:
                    min_qty = 1
            
            quantity = np.random.randint(min_qty, min(max_qty + 1, min_qty + family['family_members']))
            
            # Skip if quantity is 0 (for bachelor case)
            if quantity == 0:
                continue
            
            brand = np.random.choice(list(specs['brands'].keys()))
            model = np.random.choice(specs['brands'][brand])
            power = max(1, get_power_rating(appliance_type, brand, model))
            base_hours = max(0.5, np.random.choice(specs['typical_hours']))
            adjusted_hours = max(0.5, adjust_usage_by_season(base_hours, appliance_type, season))
            
            household_appliances.append({
                'date': date.strftime('%Y-%m-%d'),
                'family_members': family['family_members'],
                'male': family['male'],
                'female': family['female'],
                'children': family['children'],
                'household_type': family['household_type'],
                'appliance_type': appliance_type,
                'brand': brand,
                'model': model,
                'power_rating_watts': power,
                'daily_usage_hours': adjusted_hours,
                'quantity': quantity,
                'energy_star_rating': np.random.randint(2, 6),
                'peak_hour_usage': np.random.choice([True, False], p=[0.3, 0.7]),
                'season': season
            })

        # Calculate monthly consumption
        monthly_kwh = max(1, calculate_monthly_consumption(household_appliances))
        
        # Add each appliance as a separate row
        for appliance in household_appliances:
            data.append({
                **appliance,
                'monthly_household_kwh': monthly_kwh
            })
    
    # Create DataFrame and handle any remaining null/zero values
    df = pd.DataFrame(data)
    
    # Replace any remaining zeros or nulls with minimum values
    min_values = {
        'power_rating_watts': 1,
        'daily_usage_hours': 0.5,
        'quantity': 1,
        'energy_star_rating': 2,
        'monthly_household_kwh': 1,
        'male': 1,
        'female': 1,
        'children': 0,
        'family_members': 2
    }
    
    for col, min_val in min_values.items():
        df[col] = df[col].replace(0, min_val)
        df[col] = df[col].fillna(min_val)
    
    # Fill any remaining categorical nulls
    categorical_defaults = {
        'appliance_type': 'Unknown',
        'brand': 'Generic',
        'model': 'Standard',
        'season': 'Normal'
    }
    
    for col, default in categorical_defaults.items():
        df[col] = df[col].fillna(default)
    
    return df

def get_season(date):
    month = date.month
    if month in [12, 1, 2]:
        return 'Winter'
    elif month in [3, 4, 5]:
        return 'Summer'
    elif month in [6, 7, 8, 9]:
        return 'Monsoon'
    else:
        return 'Autumn'

def adjust_usage_by_season(hours, appliance_type, season):
    # First ensure hours don't exceed 24
    hours = min(hours, 24)
    
    adjustments = {
        'Summer': {
            'Air Conditioner': 1.3,  # Reduced from 1.5 to avoid exceeding realistic hours
            'Ceiling Fan': 1.2,  # Reduced from 1.3
            'LED Bulb': 0.9,
            'Refrigerator': 1.0,  # Always 24 hours
            'Water Heater': 0.3,    # Less hot water needed
            'Room Heater': 0.0,     # Not used in summer
            'Water Pump': 1.5       # More water usage
        },
        'Winter': {
            'Air Conditioner': 0.3,
            'Ceiling Fan': 0.7,
            'LED Bulb': 1.2,
            'Refrigerator': 1.0,  # Always 24 hours
            'Water Heater': 1.5,    # More hot water needed
            'Room Heater': 1.0,     # Full usage in winter
            'Water Pump': 0.7       # Less water usage
        },
        'Monsoon': {
            'Water Heater': 0.8,
            'Room Heater': 0.0,
            'Water Pump': 0.5       # Less pumping needed due to rain
        }
    }
    
    factor = adjustments.get(season, {}).get(appliance_type, 1.0)
    adjusted_hours = round(hours * factor, 1)
    
    # Ensure hours stay within logical limits
    if appliance_type == 'Refrigerator':
        return 24.0  # Refrigerator always runs 24 hours
    else:
        return min(adjusted_hours, 24.0)  # Cap at 24 hours for all appliances

def calculate_monthly_consumption(appliances):
    total_kwh = 0
    
    # Define typical monthly consumption patterns
    typical_monthly_usage = {
        'bachelor': [50, 150],    # 50-150 kWh/month
        'couple': [100, 250],     # 100-250 kWh/month
        'nuclear': [200, 400],    # 200-400 kWh/month
        'joint': [300, 600]       # 300-600 kWh/month
    }

    for app in appliances:
        appliance_type = app['appliance_type']
        power_watts = app['power_rating_watts']
        hours = app['daily_usage_hours']
        quantity = app['quantity']
        household_type = app['household_type']
        
        # Basic consumption calculation (kWh = Watts × Hours × Days × Quantity ÷ 1000)
        daily_kwh = (power_watts * hours * quantity) / 1000
        monthly_base_kwh = daily_kwh * 30

        # Apply appliance-specific adjustments
        if appliance_type == 'Refrigerator':
            # Refrigerator duty cycle (compressor runs ~45% of time)
            monthly_base_kwh *= 0.45
            
        elif appliance_type == 'Air Conditioner':
            # AC duty cycle and thermostat control
            monthly_base_kwh *= 0.65  # Compressor runs ~65% of time
            if app['season'] == 'Summer':
                monthly_base_kwh *= 1.2
            elif app['season'] == 'Winter':
                monthly_base_kwh *= 0.3
            
        elif appliance_type == 'Washing Machine':
            # Calculate based on number of washes instead of hours
            washes_per_month = {
                'bachelor': 8,
                'couple': 12,
                'nuclear': 20,
                'joint': 30
            }.get(household_type, 15)
            cycle_duration = 1.5  # Average cycle duration in hours
            monthly_base_kwh = (power_watts * cycle_duration * washes_per_month * quantity) / 1000
            
        elif appliance_type == 'Water Heater':
            # Seasonal and thermostat adjustments
            if app['season'] == 'Summer':
                monthly_base_kwh *= 0.3
            elif app['season'] == 'Winter':
                monthly_base_kwh *= 1.2
            monthly_base_kwh *= 0.7  # Thermostat control
            
        elif appliance_type == 'Room Heater':
            if app['season'] in ['Summer', 'Monsoon']:
                monthly_base_kwh = 0
            else:
                monthly_base_kwh *= 0.7  # Thermostat control

        # Apply energy efficiency (star rating)
        efficiency_factor = 1 - ((app['energy_star_rating'] - 1) * 0.1)  # 10% improvement per star
        monthly_base_kwh *= efficiency_factor

        # Apply peak hour adjustment (if applicable)
        if app['peak_hour_usage']:
            monthly_base_kwh *= 1.15

        # Ensure values are within realistic ranges for each appliance type
        appliance_limits = {
            'LED Bulb': [0.2, 1.5],           # 9W × 6hrs × 30 days = ~1.6 kWh
            'Ceiling Fan': [2, 15],            # 75W × 12hrs × 30 days = ~27 kWh
            'Air Conditioner': [30, 300],      # 1500W × 8hrs × 30 days = ~360 kWh
            'Refrigerator': [30, 100],         # 200W × 24hrs × 30 days × 0.45 = ~65 kWh
            'Television': [3, 25],             # 100W × 6hrs × 30 days = ~18 kWh
            'Washing Machine': [8, 30],        # 500W × 1.5hrs × 20 cycles = ~15 kWh
            'Water Heater': [20, 100],         # 2000W × 2hrs × 30 days = ~120 kWh
            'Room Heater': [0, 150],           # 2000W × 4hrs × 30 days = ~240 kWh
            'Water Pump': [5, 25],             # 750W × 1hr × 30 days = ~22.5 kWh
            'Microwave Oven': [2, 12]          # 1000W × 0.5hrs × 30 days = ~15 kWh
        }

        # Apply realistic limits per unit
        range_per_unit = appliance_limits.get(appliance_type, [0, 50])
        monthly_kwh_per_unit = min(max(monthly_base_kwh / quantity, range_per_unit[0]), range_per_unit[1])
        monthly_kwh = monthly_kwh_per_unit * quantity

        total_kwh += monthly_kwh

    # Ensure total household consumption is within realistic range
    household_type = appliances[0]['household_type']
    min_kwh, max_kwh = typical_monthly_usage[household_type]
    total_kwh = min(max(total_kwh, min_kwh), max_kwh)

    return round(total_kwh, 2)

# For ceiling fans
def generate_ceiling_fan_consumption(hours, quantity, power_watts, star_rating):
    # Convert watts to kilowatts
    power_kw = power_watts / 1000
    
    # Direct power calculation
    daily_consumption = power_kw * hours * quantity
    monthly_consumption = daily_consumption * 30
    
    # Example: 75W fan = 0.075kW
    # Running 10 hours = 0.075 * 10 = 0.75 units per day
    # Monthly = 0.75 * 30 = 22.5 units
    return monthly_consumption

if __name__ == "__main__":
    # Generate dataset
    df = generate_appliance_data(num_samples=1000)
    
    # Save to CSV
    df.to_csv('electricity_consumption.csv', index=False)
    print("Dataset generated successfully!")
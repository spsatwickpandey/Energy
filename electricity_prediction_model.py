import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
import joblib

class ElectricityPredictor:
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.label_encoders = {}
        self.feature_columns = None
        
        # Update Ceiling Fan specifications with more realistic and varied power ratings
        self.appliance_specs = {
            'Ceiling Fan': {
                'Havells': {
                    'Andria 75W': {'power': 75, 'star': 5, 'units_per_hour': 0.075},
                    'Nicola 75W': {'power': 75, 'star': 5, 'units_per_hour': 0.075},
                    'Stealth 75W': {'power': 75, 'star': 5, 'units_per_hour': 0.075},
                    'Festiva 75W': {'power': 75, 'star': 4, 'units_per_hour': 0.080}
                },
                'Orient': {
                    'Ecotech 65W': {'power': 65, 'star': 5, 'units_per_hour': 0.065},
                    'Aeroquiet 75W': {'power': 75, 'star': 4, 'units_per_hour': 0.078},
                    'Electric 70W': {'power': 70, 'star': 4, 'units_per_hour': 0.072},
                    'PSPO 75W': {'power': 75, 'star': 3, 'units_per_hour': 0.082}
                },
                'Crompton': {
                    'HS Plus 60W': {'power': 60, 'star': 5, 'units_per_hour': 0.060},
                    'Energion 75W': {'power': 75, 'star': 5, 'units_per_hour': 0.075},
                    'Aura 75W': {'power': 75, 'star': 4, 'units_per_hour': 0.078},
                    'High Speed 75W': {'power': 75, 'star': 3, 'units_per_hour': 0.085}
                },
                'Usha': {
                    'Striker 75W': {'power': 75, 'star': 4, 'units_per_hour': 0.078},
                    'Technix 75W': {'power': 75, 'star': 4, 'units_per_hour': 0.077},
                    'Aerostyle 75W': {'power': 75, 'star': 5, 'units_per_hour': 0.075},
                    'Swift 70W': {'power': 70, 'star': 4, 'units_per_hour': 0.073}
                },
                'Bajaj': {
                    'Maxima 75W': {'power': 75, 'star': 3, 'units_per_hour': 0.085},
                    'Regal 75W': {'power': 75, 'star': 3, 'units_per_hour': 0.084},
                    'New Bahar 75W': {'power': 75, 'star': 4, 'units_per_hour': 0.078},
                    'Cruise 75W': {'power': 75, 'star': 3, 'units_per_hour': 0.083}
                }
            },
            'LED Bulb': {
                'Philips': {
                    'Essential 9W': {'power': 9, 'star': 5, 'units_per_hour': 0.009},
                    'Ultra 9W': {'power': 9, 'star': 5, 'units_per_hour': 0.009},
                    'Smart 9W': {'power': 9, 'star': 4, 'units_per_hour': 0.0095},
                    'Master 10W': {'power': 10, 'star': 5, 'units_per_hour': 0.010}
                },
                'Havells': {
                    'Bright 9W': {'power': 9, 'star': 4, 'units_per_hour': 0.0095},
                    'Neo 9W': {'power': 9, 'star': 4, 'units_per_hour': 0.0095},
                    'Adore 8W': {'power': 8, 'star': 5, 'units_per_hour': 0.008},
                    'Prime 10W': {'power': 10, 'star': 4, 'units_per_hour': 0.0105}
                },
                'Wipro': {
                    'Garnet 9W': {'power': 9, 'star': 4, 'units_per_hour': 0.0095},
                    'Tejas 9W': {'power': 9, 'star': 4, 'units_per_hour': 0.0095},
                    'Next 8W': {'power': 8, 'star': 5, 'units_per_hour': 0.008},
                    'Primo 10W': {'power': 10, 'star': 4, 'units_per_hour': 0.0105}
                },
                'Bajaj': {
                    'LEDZ 9W': {'power': 9, 'star': 3, 'units_per_hour': 0.0098},
                    'Corona 9W': {'power': 9, 'star': 3, 'units_per_hour': 0.0098},
                    'IVORA 8W': {'power': 8, 'star': 4, 'units_per_hour': 0.0085},
                    'Elite 10W': {'power': 10, 'star': 3, 'units_per_hour': 0.0108}
                },
                'Syska': {
                    'SSK-PAG 9W': {'power': 9, 'star': 4, 'units_per_hour': 0.0095},
                    'SSK-BTS 9W': {'power': 9, 'star': 4, 'units_per_hour': 0.0095},
                    'RayCE 8W': {'power': 8, 'star': 5, 'units_per_hour': 0.008},
                    'ProX 10W': {'power': 10, 'star': 4, 'units_per_hour': 0.0105}
                }
            },
            'Air Conditioner': {
                'Daikin': {
                    'FTKF 1.5T': {'power': 1500, 'star': 5, 'units_per_hour': 1.1},  # Most efficient
                    'JTKJ 1.5T': {'power': 1600, 'star': 5, 'units_per_hour': 1.2},
                    'MTKM 1.5T': {'power': 1550, 'star': 4, 'units_per_hour': 1.25},
                    'ATKX 1.5T': {'power': 1650, 'star': 4, 'units_per_hour': 1.3}
                },
                'Voltas': {
                    'SAC 185V': {'power': 1600, 'star': 4, 'units_per_hour': 1.25},
                    'VAC 183V': {'power': 1650, 'star': 3, 'units_per_hour': 1.35},
                    'Adjustable 184V': {'power': 1700, 'star': 3, 'units_per_hour': 1.4},
                    '185V ZZee': {'power': 1550, 'star': 5, 'units_per_hour': 1.2}
                },
                'Blue Star': {
                    'IC318': {'power': 1600, 'star': 3, 'units_per_hour': 1.35},
                    'IC518': {'power': 1500, 'star': 5, 'units_per_hour': 1.15},
                    'LS318': {'power': 1650, 'star': 4, 'units_per_hour': 1.3},
                    'FS318': {'power': 1700, 'star': 3, 'units_per_hour': 1.4}
                },
                'Hitachi': {
                    'RSOG518': {'power': 1500, 'star': 5, 'units_per_hour': 1.1},
                    'KAZE 518': {'power': 1600, 'star': 4, 'units_per_hour': 1.25},
                    'ZUNOH 518': {'power': 1550, 'star': 5, 'units_per_hour': 1.15},
                    'MERAI 518': {'power': 1650, 'star': 4, 'units_per_hour': 1.3}
                },
                'LG': {
                    'MS-Q18': {'power': 1500, 'star': 5, 'units_per_hour': 1.1},
                    'PS-Q18': {'power': 1550, 'star': 5, 'units_per_hour': 1.15},
                    'LS-Q18': {'power': 1600, 'star': 4, 'units_per_hour': 1.25},
                    'KS-Q18': {'power': 1650, 'star': 4, 'units_per_hour': 1.3}
                }
            },
            'Refrigerator': {
                'LG': {
                    'GL-B201': {'power': 180, 'star': 5, 'units_per_hour': 0.180},
                    'GL-T302': {'power': 200, 'star': 5, 'units_per_hour': 0.200},
                    'GL-D241': {'power': 190, 'star': 4, 'units_per_hour': 0.195},
                    'GL-I302': {'power': 210, 'star': 4, 'units_per_hour': 0.215}
                },
                'Samsung': {
                    'RT28': {'power': 185, 'star': 5, 'units_per_hour': 0.185},
                    'RT30': {'power': 200, 'star': 5, 'units_per_hour': 0.200},
                    'RR20': {'power': 175, 'star': 4, 'units_per_hour': 0.180},
                    'RF28': {'power': 195, 'star': 4, 'units_per_hour': 0.200}
                },
                'Whirlpool': {
                    'IF INV278': {'power': 180, 'star': 4, 'units_per_hour': 0.185},
                    'IF INV305': {'power': 195, 'star': 4, 'units_per_hour': 0.200},
                    'NEO IF278': {'power': 185, 'star': 5, 'units_per_hour': 0.185},
                    'PRO 355': {'power': 210, 'star': 3, 'units_per_hour': 0.220}
                },
                'Godrej': {
                    'RD Edge 200': {'power': 170, 'star': 4, 'units_per_hour': 0.175},
                    'RD AXIS 240': {'power': 185, 'star': 4, 'units_per_hour': 0.190},
                    'RB 210': {'power': 175, 'star': 5, 'units_per_hour': 0.175},
                    'RT EON 240': {'power': 190, 'star': 3, 'units_per_hour': 0.200}
                },
                'Haier': {
                    'HRD-1954': {'power': 180, 'star': 4, 'units_per_hour': 0.185},
                    'HRB-2764': {'power': 195, 'star': 4, 'units_per_hour': 0.200},
                    'HRF-2984': {'power': 205, 'star': 3, 'units_per_hour': 0.215},
                    'HED-2054': {'power': 175, 'star': 5, 'units_per_hour': 0.175}
                }
            },
            'Television': {
                'Sony': {
                    'Bravia X75K': {'power': 150, 'star': 5, 'units_per_hour': 0.150},
                    'Bravia X80J': {'power': 160, 'star': 5, 'units_per_hour': 0.160},
                    'Bravia X90J': {'power': 170, 'star': 4, 'units_per_hour': 0.175},
                    'Bravia A80J': {'power': 180, 'star': 4, 'units_per_hour': 0.185}
                },
                'Samsung': {
                    'Crystal 4K': {'power': 140, 'star': 5, 'units_per_hour': 0.140},
                    'QLED Q60A': {'power': 155, 'star': 5, 'units_per_hour': 0.155},
                    'Neo QLED': {'power': 165, 'star': 4, 'units_per_hour': 0.170},
                    'The Frame': {'power': 145, 'star': 5, 'units_per_hour': 0.145}
                },
                'LG': {
                    'UHD 4K': {'power': 145, 'star': 5, 'units_per_hour': 0.145},
                    'NanoCell': {'power': 155, 'star': 5, 'units_per_hour': 0.155},
                    'OLED C1': {'power': 165, 'star': 4, 'units_per_hour': 0.170},
                    'OLED G1': {'power': 175, 'star': 4, 'units_per_hour': 0.180}
                },
                'OnePlus': {
                    'Y Series': {'power': 135, 'star': 4, 'units_per_hour': 0.140},
                    'U Series': {'power': 145, 'star': 4, 'units_per_hour': 0.150},
                    'Q Series': {'power': 155, 'star': 4, 'units_per_hour': 0.160},
                    'TV 55 U1S': {'power': 150, 'star': 4, 'units_per_hour': 0.155}
                },
                'Mi': {
                    'TV 5X': {'power': 130, 'star': 4, 'units_per_hour': 0.135},
                    'TV Q1': {'power': 140, 'star': 4, 'units_per_hour': 0.145},
                    'TV 4X': {'power': 135, 'star': 4, 'units_per_hour': 0.140},
                    'TV P1': {'power': 130, 'star': 4, 'units_per_hour': 0.135}
                }
            },
            'Washing Machine': {
                'LG': {
                    'FHM1207': {'power': 400, 'star': 5, 'units_per_hour': 0.400},
                    'T65SKSF4Z': {'power': 420, 'star': 5, 'units_per_hour': 0.420},
                    'FHD1409': {'power': 440, 'star': 4, 'units_per_hour': 0.450},
                    'THD8524': {'power': 430, 'star': 4, 'units_per_hour': 0.440}
                },
                'Samsung': {
                    'WA65A4002VS': {'power': 410, 'star': 5, 'units_per_hour': 0.410},
                    'WW80T504DAN': {'power': 430, 'star': 5, 'units_per_hour': 0.430},
                    'WA65T4262VS': {'power': 420, 'star': 4, 'units_per_hour': 0.435},
                    'WW70T502DAX': {'power': 425, 'star': 4, 'units_per_hour': 0.440}
                },
                'Whirlpool': {
                    '360 BW9061': {'power': 390, 'star': 4, 'units_per_hour': 0.400},
                    '360 FF7515': {'power': 400, 'star': 4, 'units_per_hour': 0.410},
                    'Supreme 7014': {'power': 410, 'star': 3, 'units_per_hour': 0.430},
                    'Elite 7212': {'power': 405, 'star': 4, 'units_per_hour': 0.415}
                },
                'IFB': {
                    'Senator Plus': {'power': 420, 'star': 5, 'units_per_hour': 0.420},
                    'Executive Plus': {'power': 430, 'star': 5, 'units_per_hour': 0.430},
                    'Senorita Plus': {'power': 410, 'star': 4, 'units_per_hour': 0.425},
                    'Elite Plus': {'power': 425, 'star': 5, 'units_per_hour': 0.425}
                },
                'Bosch': {
                    'WAJ2426WIN': {'power': 430, 'star': 5, 'units_per_hour': 0.430},
                    'WAJ2846WIN': {'power': 440, 'star': 5, 'units_per_hour': 0.440},
                    'WAB16161IN': {'power': 420, 'star': 4, 'units_per_hour': 0.435},
                    'WLJ2016TIN': {'power': 425, 'star': 5, 'units_per_hour': 0.425}
                }
            },
            'Water Heater': {
                'Havells': {
                    'Monza EC 15L': {'power': 2000, 'star': 4, 'units_per_hour': 2.000},
                    'Instanio 3L': {'power': 1800, 'star': 4, 'units_per_hour': 1.800},
                    'Adonia 25L': {'power': 2200, 'star': 5, 'units_per_hour': 2.100},
                    'Primo 15L': {'power': 1900, 'star': 4, 'units_per_hour': 1.900}
                },
                'Bajaj': {
                    'New Shakti 15L': {'power': 1900, 'star': 3, 'units_per_hour': 2.000},
                    'Juvel 3L': {'power': 1800, 'star': 3, 'units_per_hour': 1.900},
                    'Popular 25L': {'power': 2100, 'star': 3, 'units_per_hour': 2.200},
                    'Calenta 15L': {'power': 2000, 'star': 4, 'units_per_hour': 2.000}
                },
                'AO Smith': {
                    'HSE-VAS 15L': {'power': 2000, 'star': 5, 'units_per_hour': 1.900},
                    'EWS-3L': {'power': 1800, 'star': 5, 'units_per_hour': 1.700},
                    'HAS-25L': {'power': 2200, 'star': 5, 'units_per_hour': 2.000},
                    'SDS-15L': {'power': 1900, 'star': 5, 'units_per_hour': 1.800}
                },
                'Racold': {
                    'Pronto Neo 3L': {'power': 1800, 'star': 4, 'units_per_hour': 1.850},
                    'Eterno 2 15L': {'power': 2000, 'star': 4, 'units_per_hour': 2.050},
                    'Omnis 25L': {'power': 2200, 'star': 4, 'units_per_hour': 2.150},
                    'Andris 15L': {'power': 1900, 'star': 4, 'units_per_hour': 1.950}
                },
                'V-Guard': {
                    'Sprinhot 3L': {'power': 1800, 'star': 4, 'units_per_hour': 1.850},
                    'Divino 15L': {'power': 1900, 'star': 4, 'units_per_hour': 1.950},
                    'Pebble 25L': {'power': 2100, 'star': 4, 'units_per_hour': 2.100},
                    'Crystal 15L': {'power': 2000, 'star': 4, 'units_per_hour': 2.000}
                }
            },
            'Room Heater': {
                'Bajaj': {
                    'Majesty RX11': {'power': 2000, 'star': 3, 'units_per_hour': 2.000},
                    'Room Heater 2000': {'power': 2000, 'star': 3, 'units_per_hour': 2.100},
                    'Flashy 1000': {'power': 1000, 'star': 3, 'units_per_hour': 1.000},
                    'Minor 1000': {'power': 1000, 'star': 3, 'units_per_hour': 1.050}
                },
                'Havells': {
                    'Cista 2000W': {'power': 2000, 'star': 4, 'units_per_hour': 1.900},
                    'Comforter 2000W': {'power': 2000, 'star': 4, 'units_per_hour': 1.950},
                    'Calido 2000W': {'power': 2000, 'star': 4, 'units_per_hour': 1.900},
                    'Warmio 1000W': {'power': 1000, 'star': 4, 'units_per_hour': 0.950}
                },
                'Orient': {
                    'HC2003D': {'power': 2000, 'star': 4, 'units_per_hour': 1.900},
                    'HC1801D': {'power': 1800, 'star': 4, 'units_per_hour': 1.750},
                    'HC2000D': {'power': 2000, 'star': 4, 'units_per_hour': 1.950},
                    'HC1501D': {'power': 1500, 'star': 4, 'units_per_hour': 1.450}
                },
                'Usha': {
                    'HC 812T': {'power': 2000, 'star': 3, 'units_per_hour': 2.050},
                    'HC 3620': {'power': 2000, 'star': 3, 'units_per_hour': 2.000},
                    'HC 3820': {'power': 1800, 'star': 3, 'units_per_hour': 1.850},
                    'HC 3420': {'power': 1500, 'star': 3, 'units_per_hour': 1.550}
                },
                'Morphy Richards': {
                    'OFR 09': {'power': 2000, 'star': 4, 'units_per_hour': 1.900},
                    'OFR 11': {'power': 2000, 'star': 4, 'units_per_hour': 1.950},
                    'Room Heater 2000': {'power': 2000, 'star': 4, 'units_per_hour': 2.000},
                    'Heat Convector': {'power': 1800, 'star': 4, 'units_per_hour': 1.750}
                }
            },
            'Water Pump': {
                'Crompton': {
                    'Mini Champ I': {'power': 750, 'star': 4, 'units_per_hour': 0.750},
                    'Mini Champ II': {'power': 750, 'star': 4, 'units_per_hour': 0.760},
                    'Solus': {'power': 740, 'star': 4, 'units_per_hour': 0.740},
                    'Aqua': {'power': 730, 'star': 4, 'units_per_hour': 0.730}
                },
                'Kirloskar': {
                    'Mega 54S': {'power': 740, 'star': 5, 'units_per_hour': 0.720},
                    'Mega 64S': {'power': 750, 'star': 5, 'units_per_hour': 0.730},
                    'Jalraaj': {'power': 730, 'star': 5, 'units_per_hour': 0.710},
                    'Chhotu': {'power': 720, 'star': 5, 'units_per_hour': 0.700}
                },
                'CRI': {
                    'MHBS-2': {'power': 730, 'star': 4, 'units_per_hour': 0.730},
                    'MHBS-3': {'power': 740, 'star': 4, 'units_per_hour': 0.740},
                    'XCHS-2': {'power': 720, 'star': 4, 'units_per_hour': 0.720},
                    'XCHS-3': {'power': 730, 'star': 4, 'units_per_hour': 0.730}
                },
                'V-Guard': {
                    'Revo Plus': {'power': 720, 'star': 4, 'units_per_hour': 0.720},
                    'Stallion Plus': {'power': 730, 'star': 4, 'units_per_hour': 0.730},
                    'Prime': {'power': 710, 'star': 4, 'units_per_hour': 0.710},
                    'Ultron': {'power': 720, 'star': 4, 'units_per_hour': 0.720}
                },
                'KSB': {
                    'Peribloc': {'power': 750, 'star': 5, 'units_per_hour': 0.730},
                    'Etaline': {'power': 740, 'star': 5, 'units_per_hour': 0.720},
                    'Movitec': {'power': 730, 'star': 5, 'units_per_hour': 0.710},
                    'Etanorm': {'power': 740, 'star': 5, 'units_per_hour': 0.720}
                }
            },
            'Microwave Oven': {
                'LG': {
                    'MC2846SL': {'power': 900, 'star': 4, 'units_per_hour': 0.900},
                    'MC3286BRUM': {'power': 950, 'star': 4, 'units_per_hour': 0.950},
                    'MJEN326UH': {'power': 850, 'star': 4, 'units_per_hour': 0.850},
                    'MC2886BFUM': {'power': 900, 'star': 4, 'units_per_hour': 0.900}
                },
                'Samsung': {
                    'CE73JD': {'power': 900, 'star': 4, 'units_per_hour': 0.900},
                    'CE1041DSB2': {'power': 950, 'star': 4, 'units_per_hour': 0.950},
                    'MC28H5013AK': {'power': 850, 'star': 4, 'units_per_hour': 0.850},
                    'CE77JD': {'power': 900, 'star': 4, 'units_per_hour': 0.900}
                },
                'IFB': {
                    '20SC2': {'power': 850, 'star': 4, 'units_per_hour': 0.850},
                    '25SC4': {'power': 900, 'star': 4, 'units_per_hour': 0.900},
                    '30SC4': {'power': 950, 'star': 4, 'units_per_hour': 0.950},
                    '20PM1S': {'power': 850, 'star': 4, 'units_per_hour': 0.850}
                },
                'Panasonic': {
                    'NN-CT353B': {'power': 900, 'star': 5, 'units_per_hour': 0.880},
                    'NN-CT36H': {'power': 950, 'star': 5, 'units_per_hour': 0.930},
                    'NN-GT23H': {'power': 850, 'star': 5, 'units_per_hour': 0.830},
                    'NN-GT45H': {'power': 900, 'star': 5, 'units_per_hour': 0.880}
                },
                'Whirlpool': {
                    'Magicook 20L': {'power': 850, 'star': 4, 'units_per_hour': 0.850},
                    'Magicook 25L': {'power': 900, 'star': 4, 'units_per_hour': 0.900},
                    'Magicook 30L': {'power': 950, 'star': 4, 'units_per_hour': 0.950},
                    'Magicook 23L': {'power': 875, 'star': 4, 'units_per_hour': 0.875}
                }
            }
        }
        
    def preprocess_data(self, df):
        # Initialize feature columns first
        self.feature_columns = [
            'family_members', 'male', 'female', 'children',
            'power_rating_watts', 'daily_usage_hours', 'quantity',
            'energy_star_rating', 'season_encoded',
            'household_type_encoded', 'appliance_type_encoded', 'brand_encoded',
            'power_hours', 'monthly_power_hours', 'efficiency_factor'
        ]

        # Create season_encoded column
        season_mapping = {
            'Winter': 0,
            'Summer': 1,
            'Monsoon': 2,
            'Autumn': 3
        }
        df['season_encoded'] = df['season'].map(season_mapping)
        
        # Create categorical encoders
        categorical_columns = ['household_type', 'appliance_type', 'brand']
        
        for col in categorical_columns:
            if col not in self.label_encoders:
                self.label_encoders[col] = LabelEncoder()
            df[f'{col}_encoded'] = self.label_encoders[col].fit_transform(df[col])
        
        # Add engineered features
        df['power_hours'] = df['power_rating_watts'] * df['daily_usage_hours']
        df['monthly_power_hours'] = df['power_hours'] * 30
        df['efficiency_factor'] = 1 - ((df['energy_star_rating'] - 1) * 0.1)
        
        # Add more engineered features
        df['usage_intensity'] = df['daily_usage_hours'] / 24
        df['power_per_person'] = df['power_rating_watts'] / df['family_members']
        df['total_monthly_hours'] = df['daily_usage_hours'] * 30
        df['power_density'] = df['power_rating_watts'] / df['quantity']
        df['usage_per_person'] = df['daily_usage_hours'] / df['family_members']
        
        # Time-based features
        df['is_peak_hours'] = (df['daily_usage_hours'] >= 6).astype(int)
        
        # Add new features to feature_columns
        additional_features = [
            'usage_intensity', 'power_per_person', 'total_monthly_hours',
            'power_density', 'usage_per_person', 'is_peak_hours'
        ]
        self.feature_columns.extend(additional_features)
        
        X = df[self.feature_columns]
        y = df['monthly_household_kwh']
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        return X_scaled, y
    
    def calculate_base_consumption(self, appliance_data):
        """Calculate base monthly consumption for an appliance"""
        appliance_type = appliance_data['appliance_type']
        
        # Special handling for Ceiling Fan
        if appliance_type == 'Ceiling Fan':
            hours = appliance_data['daily_usage_hours']
            days = 30
            quantity = appliance_data['quantity']
            
            # Direct power calculation for ceiling fan (75W = 0.075kW)
            power_kw = 0.075
            monthly_units = power_kw * hours * days * quantity
            
            # Example calculations:
            # 1 fan, 8 hours daily: 0.075kW × 8h × 30 days = 18 units
            # 2 fans, 12 hours daily: 0.075kW × 12h × 30 days × 2 = 54 units
            
            print(f"\nCeiling Fan Calculation:")
            print(f"Hours per day: {hours}")
            print(f"Quantity: {quantity}")
            print(f"Daily consumption: {power_kw * hours * quantity} units")
            print(f"Monthly consumption: {monthly_units} units")
            
            return monthly_units
        
        # Special handling for AC
        elif appliance_type == 'Air Conditioner':
            hours = appliance_data['daily_usage_hours']
            days = 30
            quantity = appliance_data['quantity']
            
            # Base calculation: 1.2 units per hour
            daily_units = hours * 1.2  # 1.2 units per hour
            monthly_units = daily_units * days * quantity
            
            # Only apply star rating efficiency
            star_rating = appliance_data['energy_star_rating']
            efficiency_factor = 1 - ((star_rating - 1) * 0.06)
            monthly_units *= efficiency_factor
            
            return monthly_units
        
        # For other appliances, use simple power calculation
        power_kw = appliance_data['power_rating_watts'] / 1000
        hours = appliance_data['daily_usage_hours']
        days = 30
        quantity = appliance_data['quantity']
        
        base_consumption = power_kw * hours * days * quantity
        efficiency_factor = 1 - ((appliance_data['energy_star_rating'] - 1) * 0.1)
        base_consumption *= efficiency_factor
        
        return base_consumption
    
    def train(self, df):
        X_scaled, y = self.preprocess_data(df)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X_scaled, y, test_size=0.2, random_state=42
        )
        
        # Initialize model with better parameters
        self.model = RandomForestRegressor(
            n_estimators=200,
            max_depth=15,
            min_samples_split=4,
            min_samples_leaf=2,
            max_features='sqrt',
            bootstrap=True,
            random_state=42,
            n_jobs=-1
        )
        
        # Train with cross-validation
        cv_scores = cross_val_score(self.model, X_scaled, y, cv=5)
        
        # Train final model on full training data
        self.model.fit(X_train, y_train)
        
        # Evaluate
        train_pred = self.model.predict(X_train)
        test_pred = self.model.predict(X_test)
        
        # Calculate metrics
        metrics = {
            'train_rmse': np.sqrt(mean_squared_error(y_train, train_pred)),
            'test_rmse': np.sqrt(mean_squared_error(y_test, test_pred)),
            'train_r2': r2_score(y_train, train_pred),
            'test_r2': r2_score(y_test, test_pred),
            'cv_scores_mean': cv_scores.mean(),
            'cv_scores_std': cv_scores.std()
        }
        
        print("\nModel Performance Metrics:")
        for metric, value in metrics.items():
            print(f"{metric}: {value:.3f}")
        
        # Feature importance analysis
        feature_importance = pd.DataFrame({
            'feature': self.feature_columns,
            'importance': self.model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        print("\nTop 10 Most Important Features:")
        print(feature_importance.head(10))
    
    def predict_consumption(self, input_data):
        appliance_type = input_data['appliance_type']
        brand = input_data['brand']
        model = input_data.get('model', '')

        # Get model-specific consumption rate for all appliances
        specs = self.appliance_specs[appliance_type][brand][model]
        units_per_hour = specs['units_per_hour']
        
        hours = float(input_data['daily_usage_hours'])
        quantity = int(input_data['quantity'])
        
        # Calculate consumption
        daily_units = units_per_hour * hours * quantity
        monthly_units = daily_units * 30
        
        print(f"\n{appliance_type} Calculation:")
        print(f"Brand: {brand}")
        print(f"Model: {model}")
        print(f"Power Rating: {specs['power']}W")
        print(f"Star Rating: {specs['star']} star")
        print(f"Units per hour: {units_per_hour}")
        print(f"Daily Usage: {hours} hours")
        print(f"Quantity: {quantity}")
        print(f"Daily Consumption: {daily_units:.4f} units")
        print(f"Monthly Consumption: {monthly_units:.2f} units")
        
        return round(monthly_units, 2)
    
    def save_model(self, filepath):
        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'label_encoders': self.label_encoders,
            'feature_columns': self.feature_columns
        }
        joblib.dump(model_data, filepath)
    
    @classmethod
    def load_model(cls, filepath):
        predictor = cls()
        model_data = joblib.load(filepath)
        predictor.model = model_data['model']
        predictor.scaler = model_data['scaler']
        predictor.label_encoders = model_data['label_encoders']
        predictor.feature_columns = model_data['feature_columns']
        return predictor 
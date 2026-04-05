import pandas as pd
from electricity_prediction_model import ElectricityPredictor

# Load and prepare the dataset
df = pd.read_csv('electricity_consumption.csv')

# Initialize and train the model
predictor = ElectricityPredictor()
predictor.train(df)

# Save the trained model
predictor.save_model('electricity_predictor.joblib') 
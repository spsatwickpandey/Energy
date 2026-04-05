# This file is robust to missing or extra columns in the electricity_consumption.csv dataset.
# All DataFrame column accesses are checked for existence before use, so the code will never crash due to missing columns.
# If a column is missing, the relevant filter or value is skipped or set to a sensible default.

import os
import json
from groq_client import call_groq_llama_api
import pandas as pd
import sqlite3
import re
import random


def analyze_consumption_patterns(user_data, predictions, dataset):
    try:
        # Use all appliances from the user's prediction breakdown
        appliances = predictions.get('appliance_breakdown', [])
        sorted_appliances = sorted(appliances, key=lambda x: x.get('consumption', 0), reverse=True)
        top_consumers = sorted_appliances[:3]
        # Find alternatives for each high-consumption appliance (same type/brand/model only)
        alternatives = []
        for app in top_consumers:
            app_type = app.get('type') or app.get('appliance_type')
            app_brand = app.get('brand', '')
            app_model = app.get('model', '')
            if not app_type:
                continue
            # Find efficient alternatives in dataset for the same type/brand/model
            df = dataset[dataset['appliance_type'] == app_type] if 'appliance_type' in dataset.columns else dataset.copy()
            if 'brand' in df.columns:
                df = df[df['brand'] == app_brand]
            if 'model' in df.columns and app_model:
                df = df[df['model'] == app_model]
            # Only filter if the column exists
            if 'energy_efficiency_rating' in df.columns:
                df = df[df['energy_efficiency_rating'] >= 4]
            elif 'energy_star_rating' in df.columns:
                df = df[df['energy_star_rating'] >= 4]
            if 'availability_status' in df.columns:
                df = df[df['availability_status'] == 'available']
            if not df.empty:
                sort_cols = [col for col in ['energy_efficiency_rating', 'energy_star_rating', 'eco_friendly_score'] if col in df.columns]
                ascending = [False] * len(sort_cols)
                best = df.sort_values(by=sort_cols, ascending=ascending).iloc[0] if sort_cols else df.iloc[0]
                alternatives.append({
                    'appliance_type': app_type,
                    'brand': app_brand,
                    'model': app_model,
                    'current_model': app_model,
                    'recommended_model': best['model'] if 'model' in best else '',
                    'efficiency': best['energy_efficiency_rating'] if 'energy_efficiency_rating' in best else (best['energy_star_rating'] if 'energy_star_rating' in best else ''),
                    'eco_score': best['eco_friendly_score'] if 'eco_friendly_score' in best else '',
                    'power': best['power'] if 'power' in best else (best['power_rating_watts'] if 'power_rating_watts' in best else ''),
                    'cost_category': best['cost_category'] if 'cost_category' in best else '',
                })
        # Estimate savings (stub: 20% for each replacement)
        savings = {}
        for app, alt in zip(top_consumers, alternatives):
            curr = app.get('consumption', 0)
            savings[app.get('type', app.get('appliance_type', ''))] = round(curr * 0.2, 2)
        return {
            'high_consumption': top_consumers,
            'alternatives': alternatives,
            'savings': savings,
        }
    except Exception as e:
        # print(f'[analyze_consumption_patterns] Error: {e}')
        return {
            'high_consumption': [],
            'alternatives': [],
            'savings': {},
        }


def build_llama_prompt(user_data, predictions, analysis):
    family_size = user_data.get('totalMembers', 1)
    total_cost = predictions.get('bill_details', {}).get('total_bill', predictions.get('total_bill', 0))
    total_consumption = predictions.get('total_consumption', 0)
    total_load = predictions.get('total_load_kw', 0)
    # Build a detailed appliance table for the prompt
    appliance_breakdown = predictions.get('appliance_breakdown', [])
    appliance_table = 'Type | Brand | Model | Qty | Load (kW) | Units | Monthly Cost (₹)\n' + \
        '-----|-------|-------|-----|-----------|-------|--------------\n' + \
        '\n'.join([
            f"{a.get('type', a.get('appliance_type', ''))} | {a.get('brand', '')} | {a.get('model', '')} | {a.get('quantity', 1)} | {a.get('load_kw', 0)} | {a.get('consumption', 0)} | {a.get('total_charges', 0)}" for a in appliance_breakdown
        ])
    # Add a random seed to encourage varied responses
    random_seed = random.randint(1000, 9999)
    prompt = f"""
You are an expert energy consultant. The user below has provided their household and appliance details, including brand, model, load, units consumed, and cost per appliance. Your job is to give highly actionable, personalized, and cost-saving recommendations to optimize their electricity usage and reduce their bill and load.

STRICT INSTRUCTIONS:
- ONLY suggest improvements, optimizations, or replacements for the appliances, brands, and models actually listed below. DO NOT mention or suggest anything for appliances not present in the user's data.
- Your advice must reference the user's real appliance brands, models, loads, units, and costs. Do not give generic or irrelevant advice.
- Use the actual total bill and appliance-wise costs in your suggestions. **All bill costs (total and appliance-wise) are monthly. Reference this in your explanation and recommendations.**
- Avoid repeating the same advice as before. (Randomization seed: {random_seed})
- **Do not suggest or mention any appliance, brand, or model not present in the table below. If you cannot suggest anything for a specific appliance, say so.**

User Profile:
- Family members: {family_size}
- Predicted monthly consumption: {total_consumption} units
- Predicted connected load: {total_load} kW
- Predicted monthly bill: ₹{total_cost}

Appliance Details (all costs are monthly):
{appliance_table}

---

**At the top of your response, include a short, clear explanation (2-4 sentences) summarizing the user's situation and your approach to generating the recommendations. Reference the user's actual input (appliances, brands, loads, costs, bill) and explain how your advice is tailored to their data. Explicitly mention that all bill costs are monthly.**

---

Instructions:
- Give specific, appliance-by-appliance advice to reduce both energy consumption and peak load, referencing the actual brand/model and cost.
- Suggest behavioral changes and usage patterns for each appliance, if relevant.
- Recommend appliance upgrades or replacements ONLY if more efficient models exist for the same type/brand/model.
- Suggest alternative energy sources or smart devices ONLY if relevant to the user's actual appliances.
- Quantify potential cost and energy savings for each recommendation, referencing the user's real bill and appliance costs.
- Prioritize actions by impact and urgency.
- Structure your response in this JSON format:
{{
  "priority_actions": [{{"action": "...", "reason": "...", "potential_savings": "...", "payback_period": "...", "urgency": "..."}}],
  "usage_optimization": [{{"appliance": "...", "current_usage": "...", "recommended_usage": "...", "savings": "...", "tips": "..."}}],
  "behavioral_changes": [{{"change": "...", "impact": "...", "difficulty": "..."}}],
  "long_term_investments": [{{"investment": "...", "cost": "...", "annual_savings": "...", "roi_period": "..."}}]
}}
- Do NOT assume the bill is zero unless explicitly stated. Use the predicted values above.
- Make your advice as practical and tailored as possible for the user's real situation.
"""
    return prompt


def extract_json_from_text(text):
    # Try to extract a JSON block from the model output
    match = re.search(r'```json\s*(\{[\s\S]*?\})\s*```', text)
    if match:
        return match.group(1)
    # Fallback: try to find the first { ... } block
    match = re.search(r'(\{[\s\S]*\})', text)
    if match:
        return match.group(1)
    return None


def generate_ai_recommendations(data):
    try:
        if not data:
            raise ValueError("No data provided to generate recommendations")
        
        user_data = data.get('user_data')
        predictions = data.get('predictions')
        
        if not user_data or not predictions:
            raise ValueError("Missing user_data or predictions in request")
        
        if not predictions.get('appliance_breakdown'):
            raise ValueError("Missing appliance_breakdown in predictions")
        
        dataset = pd.read_csv('electricity_consumption.csv')
        analysis = analyze_consumption_patterns(user_data, predictions, dataset)
        prompt = build_llama_prompt(user_data, predictions, analysis)
        
        # Initialize recommendations_json to avoid undefined variable errors
        recommendations_json = None
        recommendations = None
        
        try:
            recommendations = call_groq_llama_api(prompt)
            if not recommendations:
                raise ValueError("Empty response from Groq API")
            # Try to extract and parse JSON from the response
            json_block = extract_json_from_text(recommendations)
            if json_block:
                try:
                    recommendations_json = json.loads(json_block)
                except json.JSONDecodeError as e:
                    print(f'[generate_ai_recommendations] JSON decode error: {e}')
                    recommendations_json = {'raw': recommendations if recommendations else 'Empty response'}
            else:
                try:
                    recommendations_json = json.loads(recommendations)
                except json.JSONDecodeError as e:
                    print(f'[generate_ai_recommendations] JSON decode error (no block): {e}')
                    recommendations_json = {'raw': recommendations if recommendations else 'Empty response'}
        except Exception as e:
            print(f'[generate_ai_recommendations] Groq API error: {e}')
            import traceback
            traceback.print_exc()
            recommendations_json = {'error': str(e), 'recommendations': []}
        
        # Ensure recommendations_json is always a dict
        if recommendations_json is None:
            recommendations_json = {'error': 'Unknown error occurred', 'recommendations': []}
        
        # Fallback: if not a dict with expected keys, wrap as personalized tip
        expected_keys = ['priority_actions', 'appliance_replacements', 'usage_optimization', 'long_term_investments', 'personalized_tips', 'behavioral_changes']
        if not isinstance(recommendations_json, dict) or not any(k in recommendations_json for k in expected_keys):
            # If we have a raw response, use it; otherwise create error message
            if 'raw' in recommendations_json:
                recommendations_json = {
                    'personalized_tips': [{'action': recommendations_json['raw'] if isinstance(recommendations_json['raw'], str) else str(recommendations_json['raw'])}]
                }
            elif 'error' in recommendations_json:
                recommendations_json['personalized_tips'] = [{'action': f"Error: {recommendations_json['error']}"}]
            else:
                recommendations_json = {
                    'personalized_tips': [{'action': 'Sorry, we could not generate recommendations due to a data or server error.'}]
                }
        
        # Note: MongoDB saving is handled by app.py's /get-recommendations route
        
        return recommendations_json
    except Exception as e:
        print(f'[generate_ai_recommendations] Fatal error: {e}')
        import traceback
        traceback.print_exc()
        return {
            'error': str(e),
            'recommendations': [],
            'personalized_tips': [{'action': 'Sorry, we could not generate recommendations due to a data or server error.'}]
        } 

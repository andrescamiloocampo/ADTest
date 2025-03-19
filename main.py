import requests
import re
import time
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('ACCESS_TOKEN')  
HEADERS = {
    'Authorization': f'Bearer {TOKEN}',
    'Content-Type': 'application/json'
}
CHALLENGE_BASE = os.getenv('CHALLENGE_BASE')
SWAPI_BASE = os.getenv('SWAPI_BASE')
POKEAPI_BASE = os.getenv('POKEAPI_BASE')


ENTITY_PATTERN = re.compile(r'(StarWarsPlanet|StarWarsCharacter|Pokemon)\(([^)]+)\)\.(\w+)')

TIME_LIMIT = 180  

def fetch_sw_character(name):
    response = requests.get(f"{SWAPI_BASE}/people/?search={name}")
    data = response.json()
    if data['count'] == 0:
        raise ValueError(f"Personaje no encontrado: {name}")
    return data['results'][0]

def fetch_sw_planet(name):
    response = requests.get(f"{SWAPI_BASE}/planets/?search={name}")
    data = response.json()
    if data['count'] == 0:
        raise ValueError(f"Planeta no encontrado: {name}")
    return data['results'][0]

def fetch_pokemon(name):
    name = name.strip().lower()
    response = requests.get(f"{POKEAPI_BASE}/pokemon/{name}")
    if response.status_code != 200:
        raise ValueError(f"Pokémon no encontrado: {name}")
    return response.json()

def get_attribute_value(entity_type, entity_data, attribute):
    try:
        if entity_type == 'StarWarsCharacter':
            if attribute == 'homeworld':
                homeworld_url = entity_data.get('homeworld')
                if not homeworld_url:
                    return 'unknown'
                response = requests.get(homeworld_url)
                planet_data = response.json()
                return planet_data.get('name', 'unknown')
            else:
                value = entity_data.get(attribute, '0')
                return float(value) if value != 'unknown' else 0.0
        elif entity_type == 'StarWarsPlanet':
            value = entity_data.get(attribute, '0')
            return float(value) if value != 'unknown' else 0.0
        elif entity_type == 'Pokemon':
            return entity_data.get(attribute, 0)
        else:
            return 0.0
    except Exception as e:
        print(f"Error obteniendo atributo {attribute}: {e}")
        return 0.0

def get_entity_value(entity_type, entity_name, attribute):
    try:
        if entity_type == 'StarWarsCharacter':
            data = fetch_sw_character(entity_name)
        elif entity_type == 'StarWarsPlanet':
            data = fetch_sw_planet(entity_name)
        elif entity_type == 'Pokemon':
            data = fetch_pokemon(entity_name)
        else:
            return 0.0
        return get_attribute_value(entity_type, data, attribute)
    except Exception as e:
        print(f"Error obteniendo entidad {entity_type} {entity_name}: {e}")
        return 0.0

def parse_formula(formula):
    entities = ENTITY_PATTERN.findall(formula)
    substituted = formula
    for ent_type, ent_name, attr in entities:
        value = get_entity_value(ent_type, ent_name, attr)
        substituted = substituted.replace(f"{ent_type}({ent_name}).{attr}", str(value))
    return substituted

def evaluate_expression(expression):
    try:
        return round(eval(expression), 10)
    except:
        return None

def get_chat_completion(problem_text):
    messages = [
        {
            "role": "system",
            "content": """Traduce problemas a expresiones matemáticas usando atributos de:
- StarWarsPlanet: rotation_period, orbital_period, diameter, surface_water, population
- StarWarsCharacter: height, mass, homeworld
- Pokemon: base_experience, height, weight
Usa formato: [TipoEntidad(Nombre).atributo] [operador] ... Ejemplo: StarWarsCharacter(Luke Skywalker).mass * Pokemon(Vulpix).base_experience"""
        },
        {
            "role": "user",
            "content": problem_text
        }
    ]
    response = requests.post(
        f"{CHALLENGE_BASE}/chat_completion",
        headers=HEADERS,
        json={
            "model": "gpt-4o-mini",
            "messages": messages
        }
    )
    if response.status_code == 200:
        return response.json()['choices'][0]['message']['content']
    else:
        raise Exception("Error en chat_completion")

def main():
    start_time = time.time()
    end_time = start_time + TIME_LIMIT

    
    response = requests.get(f"{CHALLENGE_BASE}/challenge/start", headers=HEADERS)
    print('RESPONSE:',response)
    if response.status_code != 200:
        print("Error al iniciar")
        return

    current_data = response.json()
    
    problem_id = current_data['id']
    problem_text = current_data['problem']

    while time.time() < end_time:
        try:
            print('Here:',problem_text)
            
            formula = get_chat_completion(problem_text)
            print(f"Fórmula generada: {formula}")

            
            substituted = parse_formula(formula)
            print(f"Expresión sustituida: {substituted}")

            
            answer = evaluate_expression(substituted)
            if answer is None:
                answer = 0.0

            
            response = requests.post(
                f"{CHALLENGE_BASE}/challenge/solution",
                headers=HEADERS,
                json={
                    "problem_id": problem_id,
                    "answer": answer
                }
            )
            if response.status_code != 200:
                print("Error enviando solución")
                break

            
            next_data = response.json()
            if 'problem_id' not in next_data:
                print("Prueba completada")
                break
            problem_id = next_data['problem_id']
            problem_text = next_data['problem']
            print(f"Nuevo problema ID: {problem_id}")

        except Exception as e:
            print(f"Error en el ciclo: {e}")
            break

    print("Tiempo agotado")

if __name__ == "__main__":
    main()

import requests
import re
import time
from datetime import datetime, timedelta


TOKEN = 'fc2223f4-98f6-4875-8a1d-42b504778224'  
HEADERS = {
    'Authorization': f'Bearer {TOKEN}',
    'Content-Type': 'application/json'
}
CHALLENGE_BASE = 'https://recruiting.adere.so'
SWAPI_BASE = 'https://swapi.dev/api'
POKEAPI_BASE = 'https://pokeapi.co/api/v2'


ENTITY_PATTERN = re.compile(r'(StarWarsPlanet|StarWarsCharacter|Pokemon)\(([^)]+)\)\.(\w+)')


TIME_LIMIT = 180  

def fetch_sw_character(name):
    response = requests.get(f"{SWAPI_BASE}/people/?search={name}")
    data = response.json()
    if data['count'] == 0:
        raise ValueError(f"Personaje no encontrado: {name}")
    return data['results'][0]

def fetch_sw_planet(name):
    response = requests.get(f"{SWAPI_BASE}/planets/?search={name}")
    data = response.json()
    if data['count'] == 0:
        raise ValueError(f"Planeta no encontrado: {name}")
    return data['results'][0]

def fetch_pokemon(name):
    name = name.strip().lower()
    response = requests.get(f"{POKEAPI_BASE}/pokemon/{name}")
    if response.status_code != 200:
        raise ValueError(f"Pokémon no encontrado: {name}")
    return response.json()

def get_attribute_value(entity_type, entity_data, attribute):
    try:
        if entity_type == 'StarWarsCharacter':
            if attribute == 'homeworld':
                homeworld_url = entity_data.get('homeworld')
                if not homeworld_url:
                    return 'unknown'
                response = requests.get(homeworld_url)
                planet_data = response.json()
                return planet_data.get('name', 'unknown')
            else:
                value = entity_data.get(attribute, '0')
                return float(value) if value != 'unknown' else 0.0
        elif entity_type == 'StarWarsPlanet':
            value = entity_data.get(attribute, '0')
            return float(value) if value != 'unknown' else 0.0
        elif entity_type == 'Pokemon':
            return entity_data.get(attribute, 0)
        else:
            return 0.0
    except Exception as e:
        print(f"Error obteniendo atributo {attribute}: {e}")
        return 0.0

def get_entity_value(entity_type, entity_name, attribute):
    try:
        if entity_type == 'StarWarsCharacter':
            data = fetch_sw_character(entity_name)
        elif entity_type == 'StarWarsPlanet':
            data = fetch_sw_planet(entity_name)
        elif entity_type == 'Pokemon':
            data = fetch_pokemon(entity_name)
        else:
            return 0.0
        return get_attribute_value(entity_type, data, attribute)
    except Exception as e:
        print(f"Error obteniendo entidad {entity_type} {entity_name}: {e}")
        return 0.0

def parse_formula(formula):
    entities = ENTITY_PATTERN.findall(formula)
    substituted = formula
    for ent_type, ent_name, attr in entities:
        value = get_entity_value(ent_type, ent_name, attr)
        substituted = substituted.replace(f"{ent_type}({ent_name}).{attr}", str(value))
    return substituted

def evaluate_expression(expression):
    try:
        return round(eval(expression), 10)
    except:
        return None

def get_chat_completion(problem_text):
    messages = [
        {
            "role": "system",
            "content": """Traduce problemas a expresiones matemáticas usando atributos de:
- StarWarsPlanet: rotation_period, orbital_period, diameter, surface_water, population
- StarWarsCharacter: height, mass, homeworld
- Pokemon: base_experience, height, weight
Usa formato: [TipoEntidad(Nombre).atributo] [operador] ... Ejemplo: StarWarsCharacter(Luke Skywalker).mass * Pokemon(Vulpix).base_experience"""
        },
        {
            "role": "user",
            "content": problem_text
        }
    ]
    response = requests.post(
        f"{CHALLENGE_BASE}/chat_completion",
        headers=HEADERS,
        json={
            "model": "gpt-4o-mini",
            "messages": messages
        }
    )
    if response.status_code == 200:
        return response.json()['choices'][0]['message']['content']
    else:
        raise Exception("Error en chat_completion")

def main():
    start_time = time.time()
    end_time = start_time + TIME_LIMIT

    
    response = requests.get(f"{CHALLENGE_BASE}/challenge/start", headers=HEADERS)
    print('RESPONSE:',response)
    if response.status_code != 200:
        print("Error al iniciar")
        return

    current_data = response.json()
    
    problem_id = current_data['id']
    problem_text = current_data['problem']

    while time.time() < end_time:
        try:
            print('Here:',problem_text)
            
            formula = get_chat_completion(problem_text)
            print(f"Fórmula generada: {formula}")

            
            substituted = parse_formula(formula)
            print(f"Expresión sustituida: {substituted}")

            
            answer = evaluate_expression(substituted)
            if answer is None:
                answer = 0.0

            
            response = requests.post(
                f"{CHALLENGE_BASE}/challenge/solution",
                headers=HEADERS,
                json={
                    "problem_id": problem_id,
                    "answer": answer
                }
            )
            if response.status_code != 200:
                print("Error enviando solución")
                break

            next_data = response.json()
            if 'problem_id' not in next_data:
                print("Prueba completada")
                break
            problem_id = next_data['problem_id']
            problem_text = next_data['problem']
            print(f"Nuevo problema ID: {problem_id}")

        except Exception as e:
            print(f"Error en el ciclo: {e}")
            break

    print("Tiempo agotado")

if __name__ == "__main__":
    main()

"""
FI9_NAYEK v12.1 — Analyse structure DB réelle vs FI9 attendue
Génère les migrations ALTER TABLE nécessaires
"""
import os
import sys
import socket
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.dialects import postgresql
from dotenv import load_dotenv

# Chargement environnement
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
load_dotenv(os.path.join(BASE_DIR, ".env"))

def detect_database_url():
    env_url = os.getenv("DATABASE_URL")
    if env_url:
        return env_url
    try:
        socket.gethostbyname("konan_db")
        return "postgresql+psycopg2://postgres:pass123@konan_db:5432/konan_db"
    except socket.error:
        return "postgresql+psycopg2://postgres:pass123@localhost:5432/konan_db"

def analyze_table_structure(engine, table_name):
    """Analyse complète de la structure d'une table"""
    inspector = inspect(engine)
    
    if table_name not in inspector.get_table_names():
        return None
    
    columns = {}
    for col in inspector.get_columns(table_name):
        col_info = {
            'type': str(col['type']),
            'nullable': col['nullable'],
            'default': str(col['default']) if col['default'] else None,
            'autoincrement': col.get('autoincrement', False),
        }
        columns[col['name']] = col_info
    
    pk_constraint = inspector.get_pk_constraint(table_name)
    primary_keys = pk_constraint['constrained_columns'] if pk_constraint else []
    
    unique_constraints = []
    for uq in inspector.get_unique_constraints(table_name):
        unique_constraints.append({
            'name': uq['name'],
            'columns': uq['column_names']
        })
    
    indexes = []
    for idx in inspector.get_indexes(table_name):
        indexes.append({
            'name': idx['name'],
            'columns': idx['column_names'],
            'unique': idx['unique']
        })
    
    foreign_keys = []
    for fk in inspector.get_foreign_keys(table_name):
        foreign_keys.append({
            'name': fk['name'],
            'constrained_columns': fk['constrained_columns'],
            'referred_table': fk['referred_table'],
            'referred_columns': fk['referred_columns'],
            'ondelete': fk.get('ondelete', None)
        })
    
    return {
        'columns': columns,
        'primary_keys': primary_keys,
        'unique_constraints': unique_constraints,
        'indexes': indexes,
        'foreign_keys': foreign_keys
    }

def get_fi9_expected_structure():
    """Retourne la structure FI9 attendue pour chaque table"""
    return {
        'users': {
            'columns': {
                'id': {'type': 'INTEGER', 'nullable': False, 'primary_key': True, 'autoincrement': True},
                'supabase_id': {'type': 'VARCHAR(255)', 'nullable': False, 'unique': True, 'index': True},
                'email': {'type': 'VARCHAR(255)', 'nullable': False, 'unique': True, 'index': True},
                'full_name': {'type': 'VARCHAR(255)', 'nullable': True},
                'role': {'type': 'VARCHAR(50)', 'nullable': True, 'default': "'user'"},
                'plan': {'type': 'plan_type', 'nullable': False, 'default': "'FREE'"},
                'is_active': {'type': 'BOOLEAN', 'nullable': False, 'default': 'true'},
                'created_at': {'type': 'TIMESTAMP WITH TIME ZONE', 'nullable': False, 'default': 'now()'},
                'updated_at': {'type': 'TIMESTAMP WITH TIME ZONE', 'nullable': False, 'default': 'now()'},
            },
            'indexes': [
                {'name': 'ix_users_supabase_id', 'columns': ['supabase_id'], 'unique': True},
                {'name': 'ix_users_email', 'columns': ['email'], 'unique': True},
            ],
            'unique_constraints': [
                {'columns': ['supabase_id']},
                {'columns': ['email']},
            ]
        },
        'conversations': {
            'columns': {
                'id': {'type': 'INTEGER', 'nullable': False, 'primary_key': True, 'autoincrement': True},
                'user_id': {'type': 'INTEGER', 'nullable': False, 'foreign_key': 'users.id'},
                'session_id': {'type': 'VARCHAR(255)', 'nullable': False, 'index': True},
                'title': {'type': 'VARCHAR(500)', 'nullable': True},
                'created_at': {'type': 'TIMESTAMP WITH TIME ZONE', 'nullable': False, 'default': 'now()'},
                'updated_at': {'type': 'TIMESTAMP WITH TIME ZONE', 'nullable': False, 'default': 'now()'},
            },
            'indexes': [
                {'name': 'ix_conversations_user_id', 'columns': ['user_id'], 'unique': False},
                {'name': 'ix_conversations_session_id', 'columns': ['session_id'], 'unique': False},
            ],
            'foreign_keys': [
                {'columns': ['user_id'], 'referred_table': 'users', 'referred_columns': ['id'], 'ondelete': 'CASCADE'}
            ]
        },
        'messages': {
            'columns': {
                'id': {'type': 'INTEGER', 'nullable': False, 'primary_key': True, 'autoincrement': True},
                'conversation_id': {'type': 'INTEGER', 'nullable': False, 'foreign_key': 'conversations.id'},
                'role': {'type': 'VARCHAR(50)', 'nullable': False},
                'content': {'type': 'TEXT', 'nullable': False},
                'metadata': {'type': 'JSON', 'nullable': True},
                'created_at': {'type': 'TIMESTAMP WITH TIME ZONE', 'nullable': False, 'default': 'now()'},
            },
            'indexes': [
                {'name': 'ix_messages_conversation_id', 'columns': ['conversation_id'], 'unique': False},
                {'name': 'ix_messages_created_at', 'columns': ['created_at'], 'unique': False},
            ],
            'foreign_keys': [
                {'columns': ['conversation_id'], 'referred_table': 'conversations', 'referred_columns': ['id'], 'ondelete': 'CASCADE'}
            ]
        },
        'user_settings': {
            'columns': {
                'id': {'type': 'INTEGER', 'nullable': False, 'primary_key': True, 'autoincrement': True},
                'user_id': {'type': 'INTEGER', 'nullable': False, 'foreign_key': 'users.id', 'unique': True},
                'language': {'type': 'VARCHAR(10)', 'nullable': True, 'default': "'fr'"},
                'theme': {'type': 'VARCHAR(20)', 'nullable': True, 'default': "'light'"},
                'notifications_enabled': {'type': 'BOOLEAN', 'nullable': False, 'default': 'true'},
                'preferences': {'type': 'JSON', 'nullable': True},
                'created_at': {'type': 'TIMESTAMP WITH TIME ZONE', 'nullable': False, 'default': 'now()'},
                'updated_at': {'type': 'TIMESTAMP WITH TIME ZONE', 'nullable': False, 'default': 'now()'},
            },
            'indexes': [
                {'name': 'ix_user_settings_user_id', 'columns': ['user_id'], 'unique': True},
            ],
            'foreign_keys': [
                {'columns': ['user_id'], 'referred_table': 'users', 'referred_columns': ['id'], 'ondelete': 'CASCADE'}
            ],
            'unique_constraints': [
                {'columns': ['user_id']}
            ]
        },
        'audit_logs': {
            'columns': {
                'id': {'type': 'INTEGER', 'nullable': False, 'primary_key': True, 'autoincrement': True},
                'user_id': {'type': 'INTEGER', 'nullable': True, 'foreign_key': 'users.id'},
                'action': {'type': 'VARCHAR(100)', 'nullable': False},
                'resource_type': {'type': 'VARCHAR(100)', 'nullable': True},
                'resource_id': {'type': 'INTEGER', 'nullable': True},
                'ip_address': {'type': 'VARCHAR(45)', 'nullable': True},
                'user_agent': {'type': 'VARCHAR(500)', 'nullable': True},
                'metadata': {'type': 'JSON', 'nullable': True},
                'created_at': {'type': 'TIMESTAMP WITH TIME ZONE', 'nullable': False, 'default': 'now()'},
            },
            'indexes': [
                {'name': 'ix_audit_logs_user_id', 'columns': ['user_id'], 'unique': False},
                {'name': 'ix_audit_logs_action', 'columns': ['action'], 'unique': False},
                {'name': 'ix_audit_logs_created_at', 'columns': ['created_at'], 'unique': False},
            ],
            'foreign_keys': [
                {'columns': ['user_id'], 'referred_table': 'users', 'referred_columns': ['id'], 'ondelete': 'SET NULL'}
            ]
        },
        'legal_search_history': {
            'columns': {
                'id': {'type': 'INTEGER', 'nullable': False, 'primary_key': True, 'autoincrement': True},
                'user_id': {'type': 'INTEGER', 'nullable': False, 'foreign_key': 'users.id'},
                'query': {'type': 'TEXT', 'nullable': False},
                'results_count': {'type': 'INTEGER', 'nullable': True},
                'filters': {'type': 'JSON', 'nullable': True},
                'created_at': {'type': 'TIMESTAMP WITH TIME ZONE', 'nullable': False, 'default': 'now()'},
            },
            'indexes': [
                {'name': 'ix_legal_search_history_user_id', 'columns': ['user_id'], 'unique': False},
                {'name': 'ix_legal_search_history_created_at', 'columns': ['created_at'], 'unique': False},
            ],
            'foreign_keys': [
                {'columns': ['user_id'], 'referred_table': 'users', 'referred_columns': ['id'], 'ondelete': 'CASCADE'}
            ]
        }
    }

def compare_structures(actual, expected, table_name):
    """Compare la structure réelle avec la structure attendue"""
    differences = {
        'missing_columns': [],
        'missing_indexes': [],
        'missing_unique_constraints': [],
        'missing_foreign_keys': [],
        'column_differences': [],
        'alter_statements': []
    }
    
    if actual is None:
        differences['table_missing'] = True
        return differences
    
    differences['table_missing'] = False
    
    # Comparer colonnes
    actual_cols = set(actual['columns'].keys())
    expected_cols = set(expected['columns'].keys())
    
    missing_cols = expected_cols - actual_cols
    differences['missing_columns'] = list(missing_cols)
    
    # Comparer colonnes existantes
    for col_name in actual_cols & expected_cols:
        actual_col = actual['columns'][col_name]
        expected_col = expected['columns'][col_name]
        
        # Vérifier nullable
        if expected_col.get('nullable') is not None:
            if actual_col['nullable'] != expected_col['nullable']:
                differences['column_differences'].append({
                    'column': col_name,
                    'issue': f"nullable: actual={actual_col['nullable']}, expected={expected_col['nullable']}"
                })
    
    # Comparer index
    actual_idx_names = {idx['name'] for idx in actual['indexes']}
    expected_idx_names = {idx['name'] for idx in expected['indexes']}
    missing_idx_names = expected_idx_names - actual_idx_names
    
    for idx in expected['indexes']:
        if idx['name'] in missing_idx_names:
            differences['missing_indexes'].append(idx)
    
    # Comparer unique constraints
    actual_uq_cols = {tuple(sorted(uq['columns'])) for uq in actual['unique_constraints']}
    expected_uq_cols = {tuple(sorted(uq['columns'])) for uq in expected.get('unique_constraints', [])}
    missing_uq = expected_uq_cols - actual_uq_cols
    
    for uq in expected.get('unique_constraints', []):
        if tuple(sorted(uq['columns'])) in missing_uq:
            differences['missing_unique_constraints'].append(uq)
    
    # Comparer foreign keys
    actual_fk_keys = {(tuple(fk['constrained_columns']), fk['referred_table'], tuple(fk['referred_columns'])) 
                       for fk in actual['foreign_keys']}
    expected_fk_keys = {(tuple(fk['columns']), fk['referred_table'], tuple(fk['referred_columns'])) 
                        for fk in expected.get('foreign_keys', [])}
    missing_fk = expected_fk_keys - actual_fk_keys
    
    for fk in expected.get('foreign_keys', []):
        fk_key = (tuple(fk['columns']), fk['referred_table'], tuple(fk['referred_columns']))
        if fk_key in missing_fk:
            differences['missing_foreign_keys'].append(fk)
    
    return differences

def main():
    """Fonction principale d'analyse"""
    DATABASE_URL = detect_database_url()
    print(f"[FI9] Connexion à la base de données: {DATABASE_URL}")
    
    engine = create_engine(DATABASE_URL)
    inspector = inspect(engine)
    
    expected = get_fi9_expected_structure()
    results = {}
    
    for table_name in expected.keys():
        print(f"\n[FI9] Analyse de la table: {table_name}")
        actual = analyze_table_structure(engine, table_name)
        differences = compare_structures(actual, expected[table_name], table_name)
        results[table_name] = {
            'actual': actual,
            'expected': expected[table_name],
            'differences': differences
        }
        
        if actual:
            print(f"  [OK] Table existe")
            print(f"  Colonnes: {len(actual['columns'])}")
            print(f"  Index: {len(actual['indexes'])}")
            print(f"  Foreign Keys: {len(actual['foreign_keys'])}")
        else:
            print(f"  [MISSING] Table n'existe pas")
        
        if differences['missing_columns']:
            print(f"  [DIFF] Colonnes manquantes: {differences['missing_columns']}")
        if differences['missing_indexes']:
            print(f"  [DIFF] Index manquants: {len(differences['missing_indexes'])}")
        if differences['missing_foreign_keys']:
            print(f"  [DIFF] Foreign Keys manquantes: {len(differences['missing_foreign_keys'])}")
    
    # Sauvegarder les résultats
    import json
    output_file = os.path.join(BASE_DIR, 'fi9_db_analysis.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\n[FI9] Résultats sauvegardés dans: {output_file}")
    
    return results

if __name__ == '__main__':
    main()


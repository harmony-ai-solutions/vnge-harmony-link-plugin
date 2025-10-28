import json
import re
import argparse
from difflib import SequenceMatcher
from typing import Dict, Tuple, Optional, List

# Configuration: Category name transformations
CATEGORY_TRANSFORMATIONS = {
    'Emotions': 'Emotions',
    'Walking-Running': 'Walking & Running',
    'Sitting-at-desk': 'Sitting At Desk',
    'Sitting-on-floor': 'Sitting On Floor',
    'Live-concert': 'Live Concert',
    'Additional-1': 'Additional 1',
}

# Configuration: Animation name prefix transformations
ANIMATION_PREFIX_RULES = [
    # Gravure subcategory patterns
    (r'^Gravure-Kneeling-(\d+)$', r'Kneeling \1'),
    (r'^Gravure-Standing-(\d+)$', r'Standing \1'),
    (r'^Gravure-Bridging-(\d+)$', r'Bridging \1'),
    (r'^Gravure-Squatting-(\d+)$', r'Squatting \1'),
    (r'^Gravure_Hands-and-knees-(\d+)$', r'Hands & Knees \1'),
    (r'^Gravure_Laying-(\d+)$', r'Laying \1'),
    (r'^Gravure_Seated-(\d+)$', r'Seated \1'),
    (r'^Gravure_Sitting-(\d+)$', r'Sitting \1'),
    
    # Fantasy subcategory patterns
    (r'^Fantasy_Animations$', r'Animations'),
    (r'^Fantasy_Pose-(\d+)$', r'Pose \1'),
    
    # Calm subcategory patterns
    (r'^Calm_Pose-(\d+)$', r'Pose \1'),
    
    # Dancing subcategory patterns
    (r'^Dancing_Dance-(\d+)$', r'Dance \1'),
    (r'^Dancing_Pole-dance$', r'Pole Dance'),
]

# Configuration: Specific animation name transformations
ANIMATION_NAME_TRANSFORMATIONS = {
    'Surprise-Shame-etc': 'Surprise/Shame/Etc.',
    'Hiding-face-1': 'Hiding Face From View',
    'Hiding-chest-from-embarrasment': 'Hiding Chest From Embarrassment',
    'Embarassed-from-hand-touch': 'Embarrassed From Hand Touch',
    'Covering-self-up-loop': 'Covering Self Up Loop',
    'Swimming-frontal-1': 'Swimming Front Crawl',
    'Using-lib-balm': 'Using Lip Balm',
    'lapping': 'Flapping',  # Typo correction
    'Onee-San-sitting': 'Onee-san Sitting',
    'Live-concert-Scene-1': 'Scene 1',
    'Live-concert-Loop': 'Loop',
}

def simple_normalize(text: str) -> str:
    """Normalize strings by removing special characters and converting to lowercase."""
    return re.sub(r'[^a-zA-Z0-9]', '', text).lower()

def apply_prefix_rules(text: str) -> str:
    """Apply regex-based prefix transformation rules to animation names."""
    for pattern, replacement in ANIMATION_PREFIX_RULES:
        match = re.match(pattern, text)
        if match:
            return re.sub(pattern, replacement, text)
    return text

def transform_category_name(raw_category: str) -> str:
    """Transform category name using configuration rules or generic pattern."""
    # Check if we have a specific transformation rule
    if raw_category in CATEGORY_TRANSFORMATIONS:
        return CATEGORY_TRANSFORMATIONS[raw_category]
    
    # Check if it starts with a known prefix
    for pattern in ['Gravure', 'Dancing', 'Fantasy', 'Calm']:
        if raw_category.startswith(pattern):
            return pattern
    
    # Generic transformation: replace hyphens with spaces
    return raw_category.replace('-', ' ')

def transform_animation_name(raw_name: str) -> str:
    """Transform animation name using multi-stage rules."""
    # Stage 1: Check specific transformations
    if raw_name in ANIMATION_NAME_TRANSFORMATIONS:
        return ANIMATION_NAME_TRANSFORMATIONS[raw_name]
    
    # Stage 2: Apply prefix rules
    transformed = apply_prefix_rules(raw_name)
    if transformed != raw_name:
        return transformed
    
    # Stage 3: Generic transformations
    # Handle numbered patterns like "Idle-1" -> "Idle 1"
    transformed = re.sub(r'-(\d+)$', r' \1', transformed)
    
    # Replace hyphens/underscores with spaces
    transformed = transformed.replace('-', ' ').replace('_', ' ')
    
    # Apply title case
    transformed = transformed.title()
    
    return transformed

def calculate_similarity(s1: str, s2: str) -> float:
    """Calculate similarity ratio between two strings."""
    return SequenceMatcher(None, s1, s2).ratio()

def build_animation_index(animation_list: Dict) -> Dict[Tuple[str, str, str], Dict]:
    """
    Build a searchable index from animation_list.
    Returns: {(normalized_archetype, normalized_category, normalized_name): item_reference}
    """
    index = {}
    
    for archetype_id, archetype_data in animation_list.items():
        archetype_name = archetype_data['name']
        
        for category_id, category_data in archetype_data.get('categories', {}).items():
            category_name = category_data['name']
            
            for item in category_data.get('animation_items', []):
                key = (
                    simple_normalize(archetype_name),
                    simple_normalize(category_name),
                    simple_normalize(item['name'])
                )
                index[key] = item
    
    return index

def find_best_match(
    archetype: str,
    category: str,
    animation: str,
    index: Dict[Tuple[str, str, str], Dict],
    threshold: float = 0.8
) -> Tuple[Optional[Dict], float, Optional[str]]:
    """
    Find the best matching animation item.
    Returns: (matched_item, similarity_score, match_type)
    match_type can be: 'exact', 'fuzzy', or None
    """
    norm_archetype = simple_normalize(archetype)
    norm_category = simple_normalize(category)
    norm_animation = simple_normalize(animation)
    
    # Try exact match first
    exact_key = (norm_archetype, norm_category, norm_animation)
    if exact_key in index:
        return index[exact_key], 1.0, 'exact'
    
    # Try fuzzy matching within same archetype and category
    best_match = None
    best_similarity = threshold
    
    for (idx_arch, idx_cat, idx_anim), item in index.items():
        if idx_arch == norm_archetype and idx_cat == norm_category:
            similarity = calculate_similarity(norm_animation, idx_anim)
            if similarity > best_similarity:
                best_similarity = similarity
                best_match = item
    
    if best_match:
        return best_match, best_similarity, 'fuzzy'
    
    return None, 0.0, None

def parse_kks_key(kks_key: str) -> Tuple[str, str, str]:
    """
    Parse KKS key format: Archetype_Category_Animation-Name
    Returns: (archetype, category, animation_name)
    """
    parts = kks_key.split('_', 2)  # Split on first 2 underscores only
    
    if len(parts) < 3:
        raise ValueError(f"Invalid KKS key format: {kks_key}")
    
    archetype = parts[0]
    category = parts[1]
    animation_name = parts[2]
    
    return archetype, category, animation_name

def update_animation_descriptions(descriptions_path, animation_list_path, error_log_path, simple_error_log_path):
    """Main function to update animation descriptions from KKS format to animation_list format."""
    unmapped_animations = {}
    simple_unmapped_animations = {}
    mapping_stats = {
        'exact_matches': 0,
        'fuzzy_matches': 0,
        'unmapped': 0,
        'total': 0
    }

    # Load source descriptions
    try:
        with open(descriptions_path, 'r', encoding='utf-8') as f:
            descriptions_kks = json.load(f)
    except FileNotFoundError:
        print(f"Error: Source file not found at {descriptions_path}")
        return
    except json.JSONDecodeError as e:
        print(f"Error: Could not decode JSON from {descriptions_path}: {e}")
        return

    # Load target animation list
    try:
        with open(animation_list_path, 'r', encoding='utf-8') as f:
            animation_list = json.load(f)
    except FileNotFoundError:
        print(f"Error: Target file not found at {animation_list_path}")
        return
    except json.JSONDecodeError as e:
        print(f"Error: Could not decode JSON from {animation_list_path}: {e}")
        return

    # Build searchable index
    print("Building animation index...")
    animation_index = build_animation_index(animation_list)
    print(f"Index built with {len(animation_index)} animation entries")

    # Process each KKS description
    print("\nProcessing animations...")
    for kks_key, description in descriptions_kks.items():
        mapping_stats['total'] += 1
        
        try:
            # Parse the KKS key
            raw_archetype, raw_category, raw_animation = parse_kks_key(kks_key)
            
            # Transform to match animation_list naming
            transformed_archetype = raw_archetype  # Usually stays the same
            transformed_category = transform_category_name(raw_category)
            transformed_animation = transform_animation_name(raw_animation)
            
            # Find best match
            matched_item, similarity, match_type = find_best_match(
                transformed_archetype,
                transformed_category,
                transformed_animation,
                animation_index
            )
            
            if matched_item:
                # Update description
                matched_item['description'] = description
                
                if match_type == 'exact':
                    mapping_stats['exact_matches'] += 1
                    print(f"✓ Exact: {kks_key} -> {matched_item['name']}")
                elif match_type == 'fuzzy':
                    mapping_stats['fuzzy_matches'] += 1
                    print(f"≈ Fuzzy ({similarity:.2f}): {kks_key} -> {matched_item['name']}")
            else:
                # No match found
                mapping_stats['unmapped'] += 1
                unmapped_animations[kks_key] = {
                    'description': description,
                    'parsed_as': {
                        'archetype': transformed_archetype,
                        'category': transformed_category,
                        'animation': transformed_animation
                    }
                }
                simple_unmapped_animations[kks_key] = description
                print(f"✗ Unmapped: {kks_key} (as: {transformed_archetype}/{transformed_category}/{transformed_animation})")
        
        except ValueError as e:
            mapping_stats['unmapped'] += 1
            unmapped_animations[kks_key] = {
                'description': description,
                'error': str(e)
            }
            simple_unmapped_animations[kks_key] = description
            print(f"✗ Parse Error: {kks_key} - {e}")

    # Print statistics
    print("\n" + "="*60)
    print("MAPPING STATISTICS")
    print("="*60)
    print(f"Total animations processed: {mapping_stats['total']}")
    print(f"Exact matches:             {mapping_stats['exact_matches']} ({mapping_stats['exact_matches']/mapping_stats['total']*100:.1f}%)")
    print(f"Fuzzy matches:             {mapping_stats['fuzzy_matches']} ({mapping_stats['fuzzy_matches']/mapping_stats['total']*100:.1f}%)")
    print(f"Unmapped:                  {mapping_stats['unmapped']} ({mapping_stats['unmapped']/mapping_stats['total']*100:.1f}%)")
    print("="*60)

    # Write updated animation list
    try:
        with open(animation_list_path, 'w', encoding='utf-8') as f:
            json.dump(animation_list, f, indent=2, ensure_ascii=False)
        print(f"\n✓ Animation list updated successfully: {animation_list_path}")
    except IOError as e:
        print(f"\n✗ Error writing to {animation_list_path}: {e}")
        return

    # Write unmapped animations log
    if unmapped_animations:
        try:
            with open(error_log_path, 'w', encoding='utf-8') as f:
                json.dump(unmapped_animations, f, indent=2, ensure_ascii=False)
            print(f"✓ Unmapped animations logged: {error_log_path}")
        except IOError as e:
            print(f"✗ Error writing unmapped log: {e}")
    else:
        print("✓ All animations mapped successfully - no errors to log!")

    # Write simple unmapped animations file (same format as input)
    if simple_unmapped_animations:
        try:
            with open(simple_error_log_path, 'w', encoding='utf-8') as f:
                json.dump(simple_unmapped_animations, f, indent=2, ensure_ascii=False)
            print(f"✓ Simple unmapped animations file created: {simple_error_log_path}")
        except IOError as e:
            print(f"✗ Error writing simple unmapped file: {e}")

if __name__ == '__main__':
    # Define default file paths relative to the vnge-harmony-link-plugin workspace
    DESCRIPTIONS_PATH = 'animation_descriptions_kks.json'
    ANIMATION_LIST_PATH = 'animation_list_updated.json'
    ERROR_LOG_PATH = 'unmapped_animations_error.json'
    SIMPLE_ERROR_LOG_PATH = 'unmapped_animations_simple.json'

    parser = argparse.ArgumentParser(
        description='Update animation descriptions from KKS format to animation_list format.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python update_animations.py
  python update_animations.py --descriptions custom_descriptions.json --animation-list custom_list.json
        """
    )
    parser.add_argument(
        '--descriptions',
        default=DESCRIPTIONS_PATH,
        help=f'Path to the source descriptions JSON file (default: {DESCRIPTIONS_PATH})'
    )
    parser.add_argument(
        '--animation-list',
        default=ANIMATION_LIST_PATH,
        help=f'Path to the target animation list JSON file (default: {ANIMATION_LIST_PATH})'
    )
    parser.add_argument(
        '--error-log',
        default=ERROR_LOG_PATH,
        help=f'Path to the error log for unmapped animations (default: {ERROR_LOG_PATH})'
    )
    parser.add_argument(
        '--simple-error-log',
        default=SIMPLE_ERROR_LOG_PATH,
        help=f'Path to the simple error log for unmapped animations (default: {SIMPLE_ERROR_LOG_PATH})'
    )
    
    args = parser.parse_args()

    update_animation_descriptions(args.descriptions, args.animation_list, args.error_log, args.simple_error_log)

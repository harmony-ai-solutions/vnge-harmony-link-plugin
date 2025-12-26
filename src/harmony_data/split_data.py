import json
import os
import re

def slugify(text):
    """Convert text to a valid filename."""
    text = text.replace(' & ', '_').replace('&', '_')
    text = re.sub(r'[^\w\s-]', '', text).strip().lower()
    return re.sub(r'[-\s]+', '_', text)

def split_actions(data_dir):
    actions_file = os.path.join(data_dir, 'actions.json')
    actions_out_dir = os.path.join(data_dir, 'actions')
    
    if not os.path.exists(actions_file):
        print(f"Skipping actions: {actions_file} not found")
        return

    with open(actions_file, 'r', encoding='utf-8') as f:
        actions = json.load(f)

    for action in actions:
        name = action.get('name')
        if not name:
            continue
        
        out_file = os.path.join(actions_out_dir, f"{slugify(name)}.json")
        with open(out_file, 'w', encoding='utf-8') as f:
            json.dump(action, f, indent=2)
    
    print(f"Split {len(actions)} actions into {actions_out_dir}")

def split_animations(data_dir):
    anim_file = os.path.join(data_dir, 'animation_list_wip.json')
    # Use KKS_charastudio subfolder as per get_engine_id2()
    anim_out_dir = os.path.join(data_dir, 'animations', 'KKS_charastudio')
    
    if not os.path.exists(anim_out_dir):
        os.makedirs(anim_out_dir)
        
    if not os.path.exists(anim_file):
        print(f"Skipping animations: {anim_file} not found")
        return

    with open(anim_file, 'r', encoding='utf-8') as f:
        groups = json.load(f)

    count = 0
    for group_id, group_data in groups.items():
        group_name = group_data.get('name', f'Group_{group_id}')
        categories = group_data.get('categories', {})
        
        # Even if categories are empty, create a placeholder if needed? 
        # Requirement says: "create entries for groups and categories which have no description yet"
        # The wip file seems to have empty descriptions for many.
        
        for cat_id, cat_data in categories.items():
            cat_name = cat_data.get('name', f'Category_{cat_id}')
            
            # Combine Group + Category for filename
            filename = f"{slugify(group_name)}_{slugify(cat_name)}.json"
            out_file = os.path.join(anim_out_dir, filename)
            
            # Prepare the data for this category
            out_data = {
                "group_id": int(group_id),
                "group_name": group_name,
                "category_id": int(cat_id),
                "category_name": cat_name,
                "animation_items": cat_data.get('animation_items', [])
            }
            
            with open(out_file, 'w', encoding='utf-8') as f:
                json.dump(out_data, f, indent=2)
            count += 1
            
    print(f"Split {count} animation categories into {anim_out_dir}")

if __name__ == "__main__":
    data_dir = os.path.dirname(os.path.abspath(__file__))
    split_actions(data_dir)
    split_animations(data_dir)

# Minecraft Mod Downloader & Searcher
# Copyright (C) 2024 Original Author (Modrinth API Integration)
# Modifications Copyright (C) 2026 Rza
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


import hashlib
import pathlib
import urllib.request
import urllib.parse
import json

print("Make a selection:")
print("1. Check and update current mods (Old code)")
print("2. Search and show server-side mods/plugins")
CHOICE = input("Your selection (1 or 2): ").strip()

LOADER = input("Enter the mod/plugin platform you use (loader) (e.g., fabric, forge, paper): ").strip().lower()
TARGET = input("Enter the Minecraft version you want to check for (target): ").strip()

MODS_DIR = None
if CHOICE == '1':
    INSTANCE = input("Enter the path to your minecraft installation directory (instance): ").strip()
    if LOADER in ['fabric', 'quilt', 'forge', 'neoforge']:
        MODS_DIR = pathlib.Path(INSTANCE) / 'mods'
    elif LOADER in ['paper', 'purpur', 'spigot', 'bukkit', 'sponge']:
        MODS_DIR = pathlib.Path(INSTANCE) / 'plugins'
    else:
        print(f"Unknown loader: '{LOADER}'. Did you make a typo?")
        exit(1)
elif CHOICE != '2':
    print("Invalid selection.")
    exit(1)

# Standard User-Agent header required by Modrinth API
HEADERS = {
    'User-Agent': 'MinecraftModDownloader/1.0 (contact@example.com)'
}

def get_file_hash(file_path: pathlib.Path) -> str:
    """Calculate the SHA-1 hash of a file."""
    sha1 = hashlib.sha1()
    with open(file_path, 'rb') as f:
        while chunk := f.read(8192):
            sha1.update(chunk)
    return sha1.hexdigest()

def get_current_files() -> dict:
    """Get current mod files in the mods directory with their hashes."""
    if not MODS_DIR.exists():
        print(f"Directory does not exist: {MODS_DIR}")
        return {}
    return {get_file_hash(file): file.name for file in MODS_DIR.glob('*.jar')}

def get_project_ids(hashes: list, algorithm="sha1") -> dict:
    """Post mod hashes to Modrinth API."""
    if not hashes:
        return {}
        
    url = "https://api.modrinth.com/v2/version_files"
    data = {
        "hashes": hashes,
        "algorithm": algorithm
    }
    
    headers = HEADERS.copy()
    headers['Content-Type'] = 'application/json'
    
    json_data = json.dumps(data).encode('utf-8')
    req = urllib.request.Request(url, data=json_data, headers=headers)

    try:
        with urllib.request.urlopen(req) as response:
            response_data = response.read().decode('utf-8')
            response_json: dict = json.loads(response_data)
            return {k: v['project_id'] for k, v in response_json.items()}
    except Exception as e:
        print(f"Error fetching project IDs: {e}")
        return {}

def get_project_info(ids: list):
    """Get project information from Modrinth API."""
    if not ids:
        return []
        
    url = "https://api.modrinth.com/v2/projects"
    ids_json_str = json.dumps(ids)
    full_url = f"{url}?ids={urllib.parse.quote(ids_json_str)}"
    req = urllib.request.Request(full_url, headers=HEADERS)

    try:
        with urllib.request.urlopen(req) as response:
            response_data = response.read().decode('utf-8')
            response_json: list = json.loads(response_data)
            return response_json
    except Exception as e:
        print(f"Error fetching project info: {e}")
        return []
    
def get_unidentified_files(current_files: dict, project_ids: dict) -> list:
    """Get a list of unidentified files."""
    return [file_name for file_hash, file_name in current_files.items() if file_hash not in project_ids]

def get_unavailable_in_target(project_info: list, target: str, loader: str) -> list:
    """Get a list of projects not available in the target version."""
    unavailable_projects = [
        info for info in project_info
        if target not in info['game_versions'] or loader not in info['loaders']
    ]
    unavailable_projects.sort(key=lambda x: x['title'].lower())
    return unavailable_projects

def get_available_in_target(project_info: list, target: str, loader: str) -> list:
    """Get a list of projects available in the target version."""
    available_projects = [
        info for info in project_info
        if target in info['game_versions'] and loader in info['loaders']
    ]
    available_projects.sort(key=lambda x: x['title'].lower())
    return available_projects

def download_mod_files(project_info_list: list, target: str, loader: str):
    """Downloads .jar files of mods matching the target version."""
    download_dir = pathlib.Path('./downloaded_mods')
    download_dir.mkdir(exist_ok=True)
    
    print(f"\n--- Download Process Started (to directory `{download_dir.resolve()}`) ---")
    
    for info in project_info_list:
        project_id = info['id']
        title = info['title']
        
        # Request URL to check all versions of the mod
        url = f"https://api.modrinth.com/v2/project/{project_id}/version"
        req = urllib.request.Request(url, headers=HEADERS)
        
        try:
            with urllib.request.urlopen(req) as response:
                versions = json.loads(response.read().decode('utf-8'))
                
                # Finding the latest file matching the required version and loader
                suitable_file_url = None
                filename = None
                
                for v in versions:
                    if target in v['game_versions'] and loader in v['loaders']:
                        # The first one found is the newest (sorted by date in Modrinth)
                        suitable_file_url = v['files'][0]['url']
                        filename = v['files'][0]['filename']
                        break
                
                if suitable_file_url and filename:
                    file_path = download_dir / filename
                    print(f"Downloading: {title} ({filename})...")
                    
                    # Download the file and write to storage
                    urllib.request.urlretrieve(suitable_file_url, file_path)
                else:
                    print(f"Warning: No suitable file link found for {title}.")
                    
        except Exception as e:
            print(f"An error occurred (while downloading {title}): {e}")

def search_server_side_mods(target: str, loader: str):
    print(f"\n--- Searching Server-Side mods for {target} and {loader} ---")
    
    if loader in ['fabric', 'quilt', 'forge', 'neoforge']:
        project_type = 'mod'
    else:
        project_type = 'plugin'
        
    facets = [
        [f'categories:{loader}'],
        [f'versions:{target}'],
        [f'project_type:{project_type}'],
        ['server_side:required', 'server_side:optional']
    ]
    
    url = "https://api.modrinth.com/v2/search?limit=50&facets=" + urllib.parse.quote(json.dumps(facets))
    req = urllib.request.Request(url, headers=HEADERS)
    
    try:
        with urllib.request.urlopen(req) as response:
            res = json.loads(response.read().decode('utf-8'))
            hits = res.get('hits', [])
            
            if not hits:
                print("No matching server-side mod/plugin found.")
                return
                
            print(f"\nFound results ({len(hits)} items):")
            for hit in hits:
                title = hit.get('title')
                slug = hit.get('slug')
                p_type = hit.get('project_type')
                desc = hit.get('description', '')
                url_link = f"https://modrinth.com/{p_type}/{slug}"
                print(f"\n- {title}")
                print(f"  Link: {url_link}")
                print(f"  Info: {desc}")
                
    except Exception as e:
        print(f"An error occurred during search: {e}")


if __name__ == "__main__":
    if CHOICE == '1':
        current_files = get_current_files()
        
        if not current_files:
            print("No .jar files found in the target directory.")
            exit(0)
            
        project_ids = get_project_ids(list(current_files.keys()))
        project_info = get_project_info(list(project_ids.values()))

        unidentified = get_unidentified_files(current_files, project_ids)
        no_target = get_unavailable_in_target(project_info, TARGET, LOADER)
        yes_target = get_available_in_target(project_info, TARGET, LOADER)

        print(f"Current mods: {len(current_files)}")
        
        print(f"\n--- Available and Compatible in {TARGET} {LOADER}: {len(yes_target)} ---")
        for info in yes_target:
            url = f"https://modrinth.com/{info['project_type']}/{info['slug']}"
            print(f"\t{info['title']} - {url}")

        print(f"\n--- Unavailable in {TARGET} {LOADER}: {len(no_target)} ---")
        for info in no_target:
            url = f"https://modrinth.com/{info['project_type']}/{info['slug']}"
            print(f"\t{info['title']} - {url}")

        print(f"\n--- Unable to find project info (Local/Custom mods): {len(unidentified)} ---")
        for file_name in unidentified:
            print(f"\t{file_name}")
            
        # Start downloading if suitable mods were found
        if yes_target:
            download_mod_files(yes_target, TARGET, LOADER)
        else:
            print("\nNo mod matching the target version found to download.")
            
    elif CHOICE == '2':
        search_server_side_mods(TARGET, LOADER)
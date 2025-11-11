import re
from typing import overload, Any, Mapping, Optional
from jinja2 import Environment, FileSystemLoader, StrictUndefined
import yaml
from pathlib import Path


def load_values(
        values_path: str, 
    ) -> Mapping[dict, any]:
    
    values_path = Path(values_path)
    data = {}

    if not values_path.is_file():
        raise FileNotFoundError(f"values file not found: {values_path}")
    
    with values_path.open('r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    return data

def _build_env(source_path: Path) -> Environment:
    return Environment(
        loader=FileSystemLoader(str(source_path)),
        undefined=StrictUndefined,
        trim_blocks=True,
        lstrip_blocks=True,
    )

def _ensure_dir_exists(dir: Path):
     dir.parent.mkdir(parents=True, exist_ok=True)


def render_resource(
        source_path: Path, 
        template_name: Path, 
        values: dict, 
        output_path: Path
    ) -> None:
    
    resource = values.get("name")
    env = _build_env(source_path)
    template = env.get_template(template_name)
    output_path = Path(f"{output_path}/")
    output = Path(f"{output_path}/{resource}.xml")
    xml = template.render(**values)
    
    _ensure_dir_exists(output)
    output.write_text(xml, encoding='utf-8')
    print(f"Generated {output}")       
